# Part VI — Advanced Design & Tooling

---

## Chapter 32: Custom & Wrapped Errors

> 📊 **Slide Reference:** `slides/go-32-errors-slides.pdf`

In basic Go code, errors are often created as simple strings using `errors.New` or `fmt.Errorf`. However, real-world systems need structured errors to convey diagnostic metadata and support programmatic error inspection without fragile string parsing.

### 1. Creating Custom Error Types

An error in Go is any value that implements the built-in `error` interface:

```go
type error interface {
    Error() string
}
```

By defining a custom struct type that implements this interface, we can attach arbitrary metadata (like codes, timestamps, offset indices, or HTTP status codes).

#### Wave File Parser Error Example
Here we define a structured error type to describe problems encountered while parsing WAV files:

```go
package main

import (
    "fmt"
)

// WaveErrKind classifies the type of WAV error
type WaveErrKind int

const (
    ErrHeaderMissing WaveErrKind = iota
    ErrHeaderCorrupt
    ErrUnsupportedFormat
    ErrDataMissing
)

func (k WaveErrKind) String() string {
    switch k {
    case ErrHeaderMissing:
        return "header missing"
    case ErrHeaderCorrupt:
        return "header corrupt"
    case ErrUnsupportedFormat:
        return "unsupported format"
    case ErrDataMissing:
        return "data missing"
    default:
        return "unknown error kind"
    }
}

// WaveError implements the error interface with metadata
type WaveError struct {
    Kind WaveErrKind
    Pos  int64 // Byte position where error occurred
    Err  error // Underlying cause (if any)
}

func (e WaveError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("wave error at byte %d: %s (%v)", e.Pos, e.Kind, e.Err)
    }
    return fmt.Sprintf("wave error at byte %d: %s", e.Pos, e.Kind)
}
```

#### Copy-On-Write Prototype Helper Methods
We declare standard exported package prototypes of our errors. In our functions, we copy these prototypes and append specific runtime offsets:

```go
// Exported prototypes
var (
    ErrNoHeader     = WaveError{Kind: ErrHeaderMissing}
    ErrBadHeader    = WaveError{Kind: ErrHeaderCorrupt}
    ErrBadFormat    = WaveError{Kind: ErrUnsupportedFormat}
)

// Private builder helpers that perform a copy
func (e WaveError) at(pos int64) WaveError {
    e.Pos = pos
    return e
}

func (e WaveError) wrap(err error) WaveError {
    e.Err = err
    return e
}

// Usage in parsing logic:
func readHeader(data []byte) error {
    if len(data) < 12 {
        return ErrNoHeader.at(0)
    }
    
    var format int
    // ... decode format ...
    if format != 1 {
        // Wrap an underlying error or format limitation
        return ErrBadFormat.at(8).wrap(fmt.Errorf("unsupported format tag %d", format))
    }
    return nil
}
```

---

### 2. Error Wrapping & Unwrapping (Go 1.13+)

Before Go 1.13, wrapping an error meant using `fmt.Errorf("context: %v", err)`, which discarded the original error's structure, merging it into a single string. 

Go 1.13 introduced structured wrapping using the `%w` verb in `fmt.Errorf` and the `Unwrap` interface method.

#### Implementing Unwrap on Custom Types
To make our custom `WaveError` chain-compatible, we implement the `Unwrap` method:

```go
func (e WaveError) Unwrap() error {
    return e.Err // Returns nil if there is no underlying error
}
```

When an error implements `Unwrap() error`, standard library helper functions (`errors.Is` and `errors.As`) can recursively traverse the error chain (like a linked list) to inspect underlying errors.

```
+------------------------------------------+
| WaveError (pos: 8, kind: ErrBadFormat)   |
|   - Err: --------------------------------+---> +----------------------------------+
+------------------------------------------+     | pathError (file: "audio.wav")    |
                                                 |   - Err: ------------------------+---> +-----------------------+
                                                 +----------------------------------+     | os.ErrPermission      |
                                                                                          +-----------------------+
```

---

### 3. Programmatic Inspection: `errors.Is` and `errors.As`

#### checking by Value: `errors.Is`
`errors.Is` checks if any error in the chain matches a target error variable. This replaces fragile string matches (e.g. `strings.Contains(err.Error(), "permission denied")`).

```go
package main

import (
    "errors"
    "fmt"
    "os"
)

func processAudio(filename string) error {
    f, err := os.Open(filename)
    if err != nil {
        // Return a wrapped error
        return ErrBadHeader.at(0).wrap(err)
    }
    defer f.Close()
    return nil
}

func main() {
    err := processAudio("restricted.wav")
    
    // Check if the underlying failure was due to permission issues
    if errors.Is(err, os.ErrPermission) {
        fmt.Println("Security Warning: Permission denied on audio file.")
    }
}
```

#### Customizing `Is` Matching
If we want custom comparison logic (such as checking matching error kinds regardless of offset position), we can implement the `Is(target error) bool` method on our custom type:

```go
func (e WaveError) Is(target error) bool {
    // Assert target is of the same type (or pointer)
    t, ok := target.(WaveError)
    if !ok {
        return false
    }
    // Match based on Kind, ignoring position or wrapped details
    return e.Kind == t.Kind
}
```

#### Extracting by Type: `errors.As`
`errors.As` attempts to downcast an error in the chain to a specific concrete error type. If a match is found, it copies the value into a target pointer and returns `true`.

```go
func main() {
    err := processAudio("corrupt.wav")

    var waveErr WaveError
    // errors.As requires the address of the target variable pointer
    if errors.As(err, &waveErr) {
        fmt.Printf("Wave parse failed at position %d due to %s\n", waveErr.Pos, waveErr.Kind)
    }
}
```

---

### 4. Errors vs. Panics: Architectural Philosophy

Go enforces a strict distinction between **normal** (expected) errors and **abnormal** (bug) conditions:

1. **Normal Errors (Values):** Used for foreseeable edge cases (e.g., IO timeouts, database connection loss, invalid user input). These should be returned as normal values and handled explicitly.
2. **Abnormal Errors (Panics):** Used for developer/logic bugs that violate invariants (e.g., dereferencing a nil pointer, array index out of bounds, internal structure corruption). A panic crashes the program.

#### Fail-Fast/Crash-First Principle
In distributed systems, recovering from logic bugs or internal corruption in-place is highly dangerous. Running with a corrupted memory state risks **Byzantine failures**:
- Writing corrupted records to a SQL database.
- Consuming 100% CPU in an infinite loop (creating a resource denial-of-service).
- Sending incorrect state messages on queues, causing cascading failures.

A clean **crash failure** (process termination) is the safest mode of failure:
- Container orchestrators (Kubernetes) or supervisors automatically restart the dead container.
- Load balancers redirect traffic to healthy nodes.
- Logs capture a precise stack trace showing where the invariant was violated.

#### Recover: The Code Smell
Go provides `recover()` inside `defer` blocks to stop a panic's propagation. Except for framework boundaries (like catching client HTTP panics to avoid crashing the entire web server) or unit test runners, **using `recover` is a code smell**. It sweeps corruption bugs under the rug.

```go
defer func() {
    if r := recover(); r != nil {
        log.Printf("Recovered from logic bug: %v", r)
        // Danger: Program state is undefined/corrupted!
    }
}()
```

---

## Chapter 33: Reflection

> 📊 **Slide Reference:** `slides/go-33-reflect-slides.pdf`

Reflection is the ability of a program to inspect and manipulate its own types, variables, and structure at runtime. Go is a statically typed language, but it embeds type descriptors in the compiled binary, allowing the `reflect` package to decode interface values.

### 1. The Empty Interface (`interface{}`) and Type Assertions

An empty interface (`interface{}`) holds values of any concrete type since it declares zero methods. To convert it back to a concrete type, we perform a **Type Assertion**:

```go
var x interface{} = "hello"

// Single-value type assertion (panics if assertion fails)
s := x.(string)

// Two-value type assertion (fails safely without panicking)
s, ok := x.(string)
if !ok {
    // Handle failure
}
```

---

### 2. The Type Switch

A type switch permits multiple type assertions to be evaluated in a top-down switch block. We use the syntax `value.(type)` within the switch guard:

```go
func printValue(x interface{}) {
    switch v := x.(type) {
    case int:
        fmt.Printf("Integer: %d\n", v) // v is treated as type int
    case string:
        fmt.Printf("String: %q\n", v)  // v is treated as type string
    case fmt.Stringer:
        fmt.Printf("Stringer: %s\n", v.String()) // v is stringer interface
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}
```

---

### 3. Custom JSON Unmarshalling with Reflection

Standard library JSON parsing uses reflection to map properties to struct tags. If we have a nested JSON format with dynamic keys, we can write a custom unmarshaller combining maps of empty interfaces and reflection.

#### dynamic Schema:
```json
{
  "item": "album",
  "album": {
    "title": "A Night at the Opera",
    "artist": "Queen"
  }
}
```

#### Custom Unmarshal Implementation
```go
package main

import (
    "encoding/json"
    "fmt"
)

type Response struct {
    Item   string
    Title  string
    Artist string
}

// ResponseWrapper prevents recursive unmarshal loops
type ResponseWrapper struct {
    Response
}

func (r *ResponseWrapper) UnmarshalJSON(data []byte) error {
    // 1. Decode first-level properties (extract 'item' tag)
    type Alias ResponseWrapper
    var aux Alias
    if err := json.Unmarshal(data, &aux); err != nil {
        return err
    }
    r.Item = aux.Item

    // 2. Decode raw data into a map of empty interfaces
    var raw map[string]interface{}
    if err := json.Unmarshal(data, &raw); err != nil {
        return err
    }

    // 3. Extract properties by probing maps with type assertions
    switch r.Item {
    case "album":
        if albumVal, ok := raw["album"]; ok {
            if albumObj, ok := albumVal.(map[string]interface{}); ok {
                if title, ok := albumObj["title"].(string); ok {
                    r.Title = title
                }
                if artist, ok := albumObj["artist"].(string); ok {
                    r.Artist = artist
                }
            }
        }
    case "song":
        if songVal, ok := raw["song"]; ok {
            if songObj, ok := songVal.(map[string]interface{}); ok {
                if title, ok := songObj["title"].(string); ok {
                    r.Title = title
                }
            }
        }
    }
    return nil
}
```

---

### 4. Recursive Value Probe: `contains` function

In unit tests, we often want to verify if a JSON payload matches a specific subset of expected fields, without comparing the entire payload (which contains dynamic timestamps or IDs).

We write a recursive `contains` utility that validates if `expected` exists as a subset inside `got`:

```go
package main

import (
    "errors"
    "strings"
)

// Match numerical values (JSON decodes numbers to float64 by default)
func matchNum(key string, expected float64, data map[string]interface{}) bool {
    val, ok := data[key]
    if !ok {
        return false
    }
    actual, ok := val.(float64)
    return ok && actual == expected
}

// Match string values case-insensitively
func matchString(key string, expected string, data map[string]interface{}) bool {
    val, ok := data[key]
    if !ok {
        return false
    }
    actual, ok := val.(string)
    return ok && strings.EqualFold(actual, expected)
}

func contains(expected, got map[string]interface{}) error {
    for k, ev := range expected {
        switch evTyped := ev.(type) {
        case float64:
            if !matchNum(k, evTyped, got) {
                return errors.New("mismatched number field: " + k)
            }
        case string:
            if !matchString(k, evTyped, got) {
                return errors.New("mismatched string field: " + k)
            }
        case map[string]interface{}:
            // Recursive check for nested objects
            gv, ok := got[k]
            if !ok {
                return errors.New("missing expected object key: " + k)
            }
            gotSubMap, ok := gv.(map[string]interface{})
            if !ok {
                return errors.New("type mismatch on nested object: " + k)
            }
            if err := contains(evTyped, gotSubMap); err != nil {
                return err
            }
        default:
            return errors.New("unsupported type in expected comparison: " + k)
        }
    }
    return nil
}
```

---

## Chapter 34: Mechanical Sympathy

> 📊 **Slide Reference:** `slides/go-34-sympathy-slides.pdf`

Mechanical Sympathy means understanding the underlying hardware architecture (CPU cache hierarchies, memory layouts, pipelines) and writing software that cooperates with the machine rather than fighting it.

### The Memory Hierarchy and the CPU Gap

Since the 1980s, the speed of CPU arithmetic registers has grown exponentially, while main memory (DRAM) read latency has remained relatively flat. 

```
Register Speed  : ~0.5ns (1 clock cycle)
L1 Cache Read   : ~1-2ns
L2 Cache Read   : ~4-5ns
L3 Cache Read   : ~15-20ns
Main DRAM Read  : ~60-100ns (Hundreds of cycles stalled waiting for data!)
```

When a CPU needs a variable, it halts processing until the data is fetched from RAM. To hide this latency, modern processors use cache lines (typically 64-byte chunks) to pre-fetch contiguous memory.

---

### Locality of Reference
1. **Temporal Locality:** If a memory location is accessed, it is likely to be accessed again soon.
2. **Spatial Locality:** If a memory location is accessed, nearby memory locations are likely to be accessed soon.

#### Slice vs. Linked List Layouts

- **Slice / Array (Contiguous Memory):** Sequential reads of a slice yield perfect spatial locality. Reading `slice[0]` fetches the next few elements into L1 cache in a single hardware load.
- **Linked List (Pointer Chasing):** Linked list nodes are allocated dynamically on the heap. Traversing pointers (`node.Next`) requires jumping to arbitrary memory addresses, causing frequent cache misses.

```
Slice:       [ Val1 ][ Val2 ][ Val3 ][ Val4 ][ Val5 ]  (Contiguous Cache Line)
             ^-- Sequentially read

Linked List: [ Val1 | Ptr ] ---> [ Val2 | Ptr ] (Jumps to random heap locations)
```

---

### Over-Abstraction and Method Dispatch Overhead

Modern design patterns often advocate for deep layers of abstractions and short forwarding methods (methods that do nothing but delegate to another method). 

In Go, interface method calls are **dynamically dispatched** via lookup tables (v-tables). This blocks compiler inlining optimizations. A function call that takes 100ns of overhead to do 1ns of addition is inefficient. A simpler structure with fewer layers performs better.

---

### False Sharing

CPUs manage cache consistency at the granularity of **cache lines**, not individual bytes or variables. 

Suppose we have two independent variables `A` and `B` stored next to each other in memory, fitting inside the same 64-byte cache line. 
- Core 1 updates `A` constantly.
- Core 2 updates `B` constantly.

Even though there is no logical race condition (the variables are distinct), the hardware must bounce ownership of the entire cache line back and forth between Core 1 and Core 2. This creates massive serialization overhead known as **False Sharing**.

```
[ Cache Line (64 Bytes) ]
|  Variable A (Core 1)  |  Variable B (Core 2)  |
+-----------------------+-----------------------+
   |                       |
   V                       V
  Core 1 Writes           Core 2 Writes
  (Invalidates Cache)     (Invalidates Cache)
```

---

## Chapter 35: Benchmarking

> 📊 **Slide Reference:** `slides/go-35-bench-slides.pdf`

Go includes a first-class benchmarking framework inside the `testing` package. Benchmarks reside in `_test.go` files and begin with the prefix `Benchmark`.

### 1. Writing a Benchmark

Every benchmark takes a parameter `*testing.B` and runs a loop counting up to `b.N`. The runner dynamically adjusts `b.N` until the loop takes approximately 1 second to execute.

```go
package fib

// Recursive implementation (Inefficient: O(2^N))
func FibRecursive(n int) int {
    if n <= 1 {
        return n
    }
    return FibRecursive(n-1) + FibRecursive(n-2)
}

// Iterative implementation (Efficient: O(N))
func FibIterative(n int) int {
    if n <= 1 {
        return n
    }
    current, prev := 1, 0
    for i := 2; i <= n; i++ {
        current, prev = current+prev, current
    }
    return current
}
```

```go
package fib

import "testing"

func BenchmarkFibRecursive(b *testing.B) {
    for i := 0; i < b.N; i++ {
        FibRecursive(20)
    }
}

func BenchmarkFibIterative(b *testing.B) {
    for i := 0; i < b.N; i++ {
        FibIterative(20)
    }
}
```

#### Running Benchmarks
Run all benchmarks using the `-bench` flag:

```powershell
go test -bench=. -benchmem
```

`-benchmem` reports allocation stats:
- Nanoseconds per operation (`ns/op`).
- Allocated bytes per operation (`B/op`).
- Heap allocations per operation (`allocs/op`).

---

### 2. Controlling the Timer: `b.ResetTimer()`

If a benchmark requires expensive setup (like loading files or pre-populating maps), we call `b.ResetTimer()` to exclude setup latency from the benchmark results.

```go
func BenchmarkMapLookup(b *testing.B) {
    // Expensive Setup
    m := make(map[int]string)
    for i := 0; i < 10000; i++ {
        m[i] = "value"
    }

    b.ResetTimer() // Exclude map creation from timing!
    
    for i := 0; i < b.N; i++ {
        _ = m[5000]
    }
}
```

---

### 3. Measuring False Sharing

We can write a benchmark to demonstrate false sharing by allocating an array of counters where each worker writes to adjacent cells.

#### Bad Version: False Sharing
```go
package share

import (
    "sync"
    "testing"
)

func BenchmarkFalseSharing(b *testing.B) {
    var wg sync.WaitGroup
    // 8 integers (64 bytes total) fit on exactly one cache line
    var counters [8]int64 

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        for core := 0; core < 8; core++ {
            wg.Add(1)
            go func(idx int) {
                defer wg.Done()
                for j := 0; j < 1000; j++ {
                    counters[idx]++ // Writing concurrently to same cache line!
                }
            }(core)
        }
        wg.Wait()
    }
}
```

#### Fixed Version: Local Variables
By accumulating counts in local variables (allocated on the separate stacks of each goroutine) and updating the shared struct only once at the end, we avoid cache thrashing:

```go
func BenchmarkNoSharing(b *testing.B) {
    var wg sync.WaitGroup
    var counters [8]int64

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        for core := 0; core < 8; core++ {
            wg.Add(1)
            go func(idx int) {
                defer wg.Done()
                var localCounter int64 // Stack local variable
                for j := 0; j < 1000; j++ {
                    localCounter++
                }
                counters[idx] = localCounter // Write exactly once at completion
            }(core)
        }
        wg.Wait()
    }
}
```

---

## Chapter 36: Profiling

> 📊 **Slide Reference:** `slides/go-36-profile-slides.pdf`

Profiling is the measurement of execution indicators (such as CPU, Memory, or Goroutines) during run-time. Go includes a built-in profiling engine `runtime/pprof` and a visualization tool `go tool pprof`.

### 1. Enabling Profiling in Web Apps

To expose profiling endpoints in an HTTP server, import `net/http/pprof` for its side-effects:

```go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof" // Registers endpoints under /debug/pprof
)

func main() {
    log.Println("Server starting on :8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

This exposes endpoints including:
- `/debug/pprof/goroutine` — Stack traces of all active goroutines (useful for finding leaks).
- `/debug/pprof/profile?seconds=30` — Downloads a 30-second CPU execution profile.
- `/debug/pprof/heap` — Memory allocation profiles.

---

### 2. Tracking Goroutine Leaks

A goroutine leak happens when a routine remains blocked indefinitely (e.g., on a socket read without a close, or writing to an unbuffered channel without a reader).

#### Example: Leaking Sockets via Missing Body Close
```go
package main

import (
    "io/ioutil"
    "net/http"
    _ "net/http/pprof"
)

func leakHandler(w http.ResponseWriter, r *http.Request) {
    resp, err := http.Get("https://jsonplaceholder.typicode.com/todos/1")
    if err != nil {
        return
    }
    // Defer resp.Body.Close() is missing! The socket connection leaks,
    // and the HTTP client goroutine remains stuck on the network poll.
    _, _ = ioutil.ReadAll(resp.Body)
}
```

If we hit `/debug/pprof/goroutine` repeatedly after querying this endpoint, we will see the active goroutine count increase linearly and remain high.

---

### 3. CPU Profiling: The Sorting Animator Example

We can profile an application that generates animated sorting GIFs to identify CPU hotspots.

#### Step 1: Paint Square (Slow Version)
This version calls `SetColorIndex` on every pixel of the square, incurring function call overhead, index calculations, and redundant bounds checks:

```go
func paintSquareSlow(img *image.Paletted, x, y, scale, colorIndex int) {
    for dy := 0; dy < scale; dy++ {
        for dx := 0; dx < scale; dx++ {
            // Checks bounds and calculates offsets for every single pixel!
            if dx == 0 || dy == 0 || dx == scale-1 || dy == scale-1 {
                img.SetColorIndex(x*scale+dx, y*scale+dy, 0) // Gray Border
            } else {
                img.SetColorIndex(x*scale+dx, y*scale+dy, uint8(colorIndex))
            }
        }
    }
}
```

#### Step 2: Running pprof
Build the binary with debug info:
```powershell
go build -o sort.exe
```

Start the server and capture a CPU profile for 10 seconds:
```powershell
go tool pprof -http=:8082 sort.exe http://localhost:8080/debug/pprof/profile?seconds=10
```
This opens a web UI showing a **Call Graph** and a **Flame Graph** where the widest boxes represent functions taking the most CPU time.

#### Step 3: Strength Reduction & Bounds Optimization (Fastest Version)
Using reflection, we inspect the layout of `image.Paletted`. Since rows are stored contiguously in a single `Pix` slice, we can precompute row offsets and copy entire rows using the built-in `copy` function, eliminating loop bounds checks:

```go
func paintSquareFastest(img *image.Paletted, x, y, scale, colorIndex int) {
    // 1. Calculate top-left and bottom-left offsets in the image Pix buffer
    startY := y * scale
    startX := x * scale
    startOffset := startY*img.Stride + startX
    
    // 2. Pre-create templates for border and fill rows
    borderRow := make([]uint8, scale) // Defaults to 0 (gray border)
    
    fillRow := make([]uint8, scale)
    fillRow[0] = 0
    fillRow[scale-1] = 0
    for i := 1; i < scale-1; i++ {
        fillRow[i] = uint8(colorIndex)
    }

    // 3. Copy templates directly into the image's raw pixel buffer
    // Top Border
    copy(img.Pix[startOffset:startOffset+scale], borderRow)
    
    // Middle Rows
    for dy := 1; dy < scale-1; dy++ {
        offset := startOffset + dy*img.Stride
        copy(img.Pix[offset:offset+scale], fillRow)
    }
    
    // Bottom Border
    bottomOffset := startOffset + (scale-1)*img.Stride
    copy(img.Pix[bottomOffset:bottomOffset+scale], borderRow)
}
```

Using this approach:
- Redundant multiplications are moved outside the loop.
- Individual pixel boundary checks are replaced by a single boundary check during slice copying.
- This yielded a **6x speedup** on the image painting pipeline.

---

## Chapter 37: Static Analysis & Linting

> 📊 **Slide Reference:** `slides/go-37-static-slides.pdf`

Static Analysis (or linting) is the inspection of code without executing it. It provides automatic guardrails to verify code correctness and style consistency before checking it into source control.

### 1. Key Linting Tools in Go

| Tool | Focus | Description |
| :--- | :--- | :--- |
| `gofmt` / `goimports` | Formatting | Standardizes whitespace, syntax brackets, and handles auto-formatting imports. |
| `go vet` | Correctness | Checks for common compiler-legal bugs (e.g. format verb mismatches in printf, copying mutexes, unkeyed struct initializers). |
| `ineffassign` | Correctness | Detects variables that are written to but never read before being overwritten. |
| `gosimple` | Style | Suggests simplifications (e.g. replacing `if x == true` with `if x`). |
| `gocyclo` | Complexity | Measures cyclomatic complexity of functions based on logic branches. |

---

### 2. Multi-Linter runner: `golangci-lint`

Instead of running separate tools, the Go community uses `golangci-lint`, a unified runner that coordinates dozens of linters concurrently.

#### Example Config (`.golangci.yml`)
Create a configuration file in the project root to manage active linters:

```yaml
linters:
  enable:
    - errcheck      # Checks that returned errors are handled
    - govetted      # Runs go vet
    - ineffassign   # Detects unused assignments
    - staticcheck   # Applies advanced static analysis checks
    - gocyclo       # Warns about high-complexity methods
    - unused        # Finds unused variables/constants/functions
linters-settings:
  gocyclo:
    min-complexity: 15 # Flag functions with complexity score > 15
```

#### Running golangci-lint
```powershell
golangci-lint run
```

---

### 3. Common Static Errors Detected

#### Ineffectual Assignment (Shadowing / Overwriting)
```go
func parseData(r io.Reader) error {
    data, err := ioutil.ReadAll(r)
    // err is assigned but never checked before overwriting below
    
    data, err = decrypt(data) 
    if err != nil {
        return err
    }
    return nil
}
```
*Linter output:* `[ineffassign] ineffectual assignment to err`

#### Printf Verb Mismatches
```go
package main

import "fmt"

func main() {
    count := 42
    fmt.Printf("Count is: %s\n", count) // %s expects string, got int
}
```
*Linter output:* `[govet] printf: Printf format %s has arg count of wrong type int`
