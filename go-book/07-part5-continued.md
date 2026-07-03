# Part V Continued — Concurrency & Language Details

---

## Chapter 27: Exercise — Concurrent File Processing

> 📊 **Slide Reference:** `slides/go-27-walk-slides.pdf`

In this chapter, we take a sequential program and refactor it into a high-performance concurrent application using the CSP (Communicating Sequential Processes) model.

### The Problem: Finding Duplicate Files

Suppose we have a large directory structure (e.g., a Dropbox folder with 50,000+ files) containing duplicate files with different names or timestamps. To find duplicates by their actual byte content, we must compute a secure cryptographic hash (such as MD5) of every file.

We represent the hash as a `string` (so it can be used as a map key) and group files by their hash in a `map[string][]string`.

#### 1. The Sequential Implementation

The standard library `path/filepath` package provides `filepath.Walk`, which recursively visits every file and directory under a starting path using a visitor closure.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
)

type FilePair struct {
    Path string
    Hash string
}

func hashFile(path string) (FilePair, error) {
    f, err := os.Open(path)
    if err != nil {
        return FilePair{}, err
    }
    // Defer close immediately after successful open to avoid leaking file descriptors
    defer f.Close()

    h := md5.New()
    if _, err := io.Copy(h, f); err != nil {
        return FilePair{}, err
    }

    hashStr := fmt.Sprintf("%x", h.Sum(nil))
    return FilePair{Path: path, Hash: hashStr}, nil
}

func searchTree(dir string) (map[string][]string, error) {
    results := make(map[string][]string)

    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        // Process regular non-empty files only
        if info.Mode().IsRegular() && info.Size() > 0 {
            pair, err := hashFile(path)
            if err != nil {
                return err
            }
            results[pair.Hash] = append(results[pair.Hash], pair.Path)
        }
        return nil
    }

    err := filepath.Walk(dir, visit)
    return results, err
}
```

Running this sequentially on a large drive is slow because it is bound by disk read latency and sequential hashing CPU usage.

---

###Refactoring 1: The Worker Pool Model

The worker pool model splits the work into three parts:
1. **The Generator (Main Thread):** Walks the directory tree and sends file paths down a channel.
2. **The Worker Pool (Goroutines):** A fixed number of goroutines read paths, read/hash the files, and send `FilePair` results down a pairs channel.
3. **The Collector (Goroutine):** Rages over the pairs channel and inserts them into the final map.

```
                  [Paths Channel]
                        |
            +-----------+-----------+
            |           |           |
        [Worker 1]  [Worker 2]  [Worker 3]  (Fixed Pool)
            |           |           |
            +-----------+-----------+
                        |
                  [Pairs Channel]
                        |
                  [Collector] ---> [Results Channel]
```

#### Synchronization Rules for the Worker Pool
- The main thread closes the `paths` channel when the directory walk is finished.
- When the `paths` channel closes, the workers finish their remaining work and signal completion on a shared `done` channel.
- The main thread reads from the `done` channel exactly $N$ times (where $N$ is the number of workers) to know all workers have exited.
- Once all workers are finished, the main thread safely closes the `pairs` channel.
- The `collector` finishes ranging over `pairs`, sends the final map down the `results` channel, and exits.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "runtime"
)

type FilePair struct {
    Path string
    Hash string
}

func hashWorker(paths <-chan string, pairs chan<- FilePair, done chan<- bool) {
    for path := range paths {
        f, err := os.Open(path)
        if err != nil {
            continue
        }
        h := md5.New()
        _, err = io.Copy(h, f)
        f.Close()
        if err != nil {
            continue
        }
        pairs <- FilePair{Path: path, Hash: fmt.Sprintf("%x", h.Sum(nil))}
    }
    done <- true
}

func collectHashes(pairs <-chan FilePair, results chan<- map[string][]string) {
    hashes := make(map[string][]string)
    for pair := range pairs {
        hashes[pair.Hash] = append(hashes[pair.Hash], pair.Path)
    }
    results <- hashes
}

func searchConcurrent(dir string) map[string][]string {
    // Determine pool size based on logical CPU cores
    numWorkers := runtime.NumCPU() * 2
    
    paths := make(chan string)
    pairs := make(chan FilePair, 100) // Buffered to remove friction
    done := make(chan bool)
    results := make(chan map[string][]string)

    // Start collector
    go collectHashes(pairs, results)

    // Start workers
    for i := 0; i < numWorkers; i++ {
        go hashWorker(paths, pairs, done)
    }

    // Walk directory and feed paths
    filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
        if err == nil && info.Mode().IsRegular() && info.Size() > 0 {
            paths <- path
        }
        return nil
    })
    close(paths) // Signal workers to stop

    // Wait for all workers to finish
    for i := 0; i < numWorkers; i++ {
        <-done
    }
    close(pairs) // Signal collector we are done

    return <-results
}
```

---

### Refactoring 2: Parallel Directory Traversals

To speed up path discovery, we can walk directories in parallel. Since the number of subdirectories is unknown, we cannot use a fixed-size loop. Instead, we use `sync.WaitGroup` to coordinate completion.

We start a goroutine for each directory. In the visitor function:
- If a visitor encounters a subdirectory, it increments the WaitGroup (`wg.Add(1)`), spawns a new goroutine to walk that subdirectory, and returns `filepath.SkipDir` to prevent the current walker from descending into it.

```go
package main

import (
    "os"
    "path/filepath"
    "sync"
)

func walkDir(dir string, wg *sync.WaitGroup, paths chan<- string) {
    defer wg.Done()

    // visit closure captures the WaitGroup and paths channel
    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return nil
        }
        if info.IsDir() && path != dir {
            // Found a subdirectory: spawn a new walk routine
            wg.Add(1)
            go walkDir(path, wg, paths)
            return filepath.SkipDir // Do not descend on this routine
        }
        if info.Mode().IsRegular() && info.Size() > 0 {
            paths <- path
        }
        return nil
    }

    filepath.Walk(dir, visit)
}
```

---

### Refactoring 3: A Goroutine per File (Counting Semaphore)

What if we spawn a goroutine for *every* file? If we do this naively on a directory tree with 50,000 files, the operating system will crash because it will exceed the limit of open file descriptors or active OS threads (typically 1,000 per process).

To prevent this, we use a **Counting Semaphore** (implemented via a buffered channel) to limit active disk I/O operations, while still spawning goroutines freely.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "sync"
)

type FilePair struct {
    Path string
    Hash string
}

func processFile(path string, wg *sync.WaitGroup, limits chan bool, pairs chan<- FilePair) {
    defer wg.Done()

    limits <- true // Acquire token (blocks if buffer is full)
    defer func() { <-limits }() // Release token when function exits

    f, err := os.Open(path)
    if err != nil {
        return
    }
    defer f.Close()

    h := md5.New()
    if _, err := io.Copy(h, f); err != nil {
        return
    }
    pairs <- FilePair{Path: path, Hash: fmt.Sprintf("%x", h.Sum(nil))}
}

func walkDir(dir string, wg *sync.WaitGroup, limits chan bool, pairs chan<- FilePair) {
    defer wg.Done()

    limits <- true // Walk directories within resource limits too
    defer func() { <-limits }()

    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return nil
        }
        if info.IsDir() && path != dir {
            wg.Add(1)
            go walkDir(path, wg, limits, pairs)
            return filepath.SkipDir
        }
        if info.Mode().IsRegular() && info.Size() > 0 {
            wg.Add(1)
            go processFile(path, wg, limits, pairs)
        }
        return nil
    }
    filepath.Walk(dir, visit)
}

func search(dir string) map[string][]string {
    var wg sync.WaitGroup
    limits := make(chan bool, 32) // Allow maximum 32 active disk operations
    pairs := make(chan FilePair, 100)
    results := make(chan map[string][]string)

    // Start collector
    go func() {
        hashes := make(map[string][]string)
        for pair := range pairs {
            hashes[pair.Hash] = append(hashes[pair.Hash], pair.Path)
        }
        results <- hashes
    }()

    wg.Add(1)
    go walkDir(dir, &wg, limits, pairs)

    wg.Wait() // Wait for all directories and files to finish
    close(pairs)

    return <-results
}
```

### Amdahl's Law

Refactoring a program to run concurrently does not yield linear performance speedups forever. **Amdahl's Law** states that the maximum speedup $S$ of a program is limited by the sequential fraction of that program ($1 - P$):

$$S = \frac{1}{(1 - P) + \frac{P}{s}}$$

Where:
- $P$ is the parallelizable fraction of the program.
- $s$ is the speedup factor of the parallel part (typically the number of CPU cores).

If $5\%$ of a program must run sequentially (such as final collection into a map, file path generation, or filesystem lookup), the maximum theoretical speedup is $20\text{x}$, even with an infinite number of processors. In practice, I/O bottlenecks (SATA/NVMe drive read limit) will cap the performance benefits much earlier.

---

## Chapter 28: Conventional Synchronization

> 📊 **Slide Reference:** `slides/go-28-mutex-slides.pdf`

While CSP (Go routines and channels) is the preferred concurrency model in Go, the standard library provides traditional mutual exclusion primitives in the `sync` and `sync/atomic` packages. These primitives are the foundation upon which channels and `select` are built.

### Mutual Exclusion (Mutex)

A **mutual exclusion lock (Mutex)** ensures that only one goroutine can execute a critical section of code at a time. Go provides `sync.Mutex` with two primary methods:
- `Lock()`
- `Unlock()`

#### The Thread-Safe Map Example

Standard Go maps are not goroutine-safe. If two goroutines attempt to read and write to the same map concurrently, the Go runtime will crash immediately with a `panic: concurrent map writes`.

We can construct a thread-safe map by enclosing a map and a `sync.Mutex` inside a struct:

```go
package main

import "sync"

type SafeMap struct {
    mu   sync.Mutex // Protects the map field below
    data map[string]int
}

func (m *SafeMap) Increment(key string) {
    m.mu.Lock()
    // Defer the unlock immediately to guarantee release regardless of return branches
    defer m.mu.Unlock()

    m.data[key]++
}
```

> [!IMPORTANT]
> A `sync.Mutex` must **never be copied**. Doing so copies its internal state (whether it is locked or unlocked), which breaks mutual exclusion. Always pass structs containing a Mutex by pointer.

### Read/Write Mutex (`sync.RWMutex`)

If a resource is read frequently but written to rarely, a standard Mutex creates unnecessary bottlenecks. A **Read/Write Mutex** allows multiple readers to acquire a read lock simultaneously, but restricts write access to a single writer.

- **For Readers:** Use `RLock()` and `RUnlock()`.
- **For Writers:** Use `Lock()` and `Unlock()`.

```go
package main

import (
    "sync"
    "time"
)

type TokenStore struct {
    mu        sync.RWMutex
    token     string
    expiresAt time.Time
}

func (s *TokenStore) GetToken() string {
    s.mu.RLock() // Multiple readers can read simultaneously
    defer s.mu.RUnlock()
    return s.token
}

func (s *TokenStore) UpdateToken(newToken string, lifespan time.Duration) {
    s.mu.Lock() // Exclusive lock; blocks readers and other writers
    defer s.mu.Unlock()
    s.token = newToken
    s.expiresAt = time.Now().Add(lifespan)
}
```

### Atomic Operations (`sync/atomic`)

For simple numeric updates (like counters), locks introduce significant operating system context-switching overhead. The `sync/atomic` package leverages CPU hardware-level atomic instructions (such as Compare-And-Swap) to execute lockless updates.

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

func main() {
    var counter int64
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            // Atomic increment directly at the CPU register level
            atomic.AddInt64(&counter, 1)
        }()
    }

    wg.Wait()
    fmt.Println("Counter:", atomic.LoadInt64(&counter)) // Output: 1000
}
```

### Guaranteeing Single Execution (`sync.Once`)

In concurrent programs, we often need to initialize a singleton resource (like a database connection pool or log file) lazily on the first request. Checking if a pointer is nil without synchronization is a data race. `sync.Once` guarantees that a function is executed exactly once, regardless of how many goroutines invoke it simultaneously.

```go
package main

import (
    "net/http"
    "sync"
)

type Logger struct{}

var (
    instance *Logger
    once     sync.Once
)

func GetLoggerInstance() *Logger {
    // once.Do guarantees the anonymous function runs exactly once
    once.Do(func() {
        instance = &Logger{}
    })
    return instance
}
```

### Temporary Object Pool (`sync.Pool`)

In high-throughput network servers, frequently allocating and garbage-collecting temporary objects (like read/write buffers) degrades performance. `sync.Pool` provides a thread-safe repository of temporary objects that can be reused.

```go
package main

import (
    "bytes"
    "sync"
)

var bufferPool = sync.Pool{
    // New defines how to allocate a new object if the pool is empty
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process(data []byte) {
    // Get returns an empty interface{}; downcast it with type assertion
    buf := bufferPool.Get().(*bytes.Buffer)
    
    // Always reset the object's state before reuse!
    buf.Reset()
    buf.Write(data)

    // Put it back in the pool for other goroutines
    bufferPool.Put(buf)
}
```

---

## Chapter 29: Exercise — Thread-Safe Web Server

> 📊 **Slide Reference:** `slides/go-29-hw5-slides.pdf`

This exercise revisits the REST-based storefront web server created in Chapter 21. The original implementation used a plain map `map[string]dollars` to track prices. Because HTTP handlers are run concurrently on separate goroutines, concurrent price updates and list requests caused data races.

### The Race Driver Code

To expose the race condition, we write a concurrent test driver that drives traffic into the server by issuing random HTTP requests (`create`, `update`, `delete`, and `list`) concurrently.

```go
// Run with: go run -race server.go
```

If the server is started with the Go race detector enabled (`go run -race`), the server will report data races and crash when the driver program runs.

### The Solution: Protecting the Database Map

We refactor the database to wrap the map inside a struct alongside a `sync.Mutex`.

```diff
- type database map[string]dollars
+ type database struct {
+     mu sync.Mutex
+     db map[string]dollars
+ }
```

#### Thread-Safe Server Code

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "strconv"
    "sync"
)

type dollars float32

func (d dollars) String() string {
    return fmt.Sprintf("$%.2f", d)
}

type database struct {
    mu sync.Mutex
    db map[string]dollars
}

func (db *database) list(w http.ResponseWriter, req *http.Request) {
    db.mu.Lock()
    defer db.mu.Unlock() // Safe release

    for item, price := range db.db {
        fmt.Fprintf(w, "%s: %s\n", item, price)
    }
}

func (db *database) price(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    
    db.mu.Lock()
    price, ok := db.db[item]
    db.mu.Unlock() // Release as early as possible before network writing

    if !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "no such item: %q\n", item)
        return
    }
    fmt.Fprintf(w, "%s\n", price)
}

func (db *database) create(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    p, err := strconv.ParseFloat(priceStr, 32)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "invalid price: %q\n", priceStr)
        return
    }

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; ok {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "item already exists: %q\n", item)
        return
    }

    db.db[item] = dollars(p)
    w.WriteHeader(http.StatusCreated)
    fmt.Fprintf(w, "created %s: %s\n", item, dollars(p))
}

func (db *database) update(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    p, err := strconv.ParseFloat(priceStr, 32)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "invalid price: %q\n", priceStr)
        return
    }

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "item does not exist: %q\n", item)
        return
    }

    db.db[item] = dollars(p)
    fmt.Fprintf(w, "updated %s to: %s\n", item, dollars(p))
}

func (db *database) deleteItem(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "item does not exist: %q\n", item)
        return
    }

    delete(db.db, item)
    fmt.Fprintf(w, "deleted %s\n", item)
}

func main() {
    handler := &database{
        db: map[string]dollars{"shoes": 50, "socks": 5},
    }

    // Register routes
    http.HandleFunc("/list", handler.list)
    http.HandleFunc("/price", handler.price)
    http.HandleFunc("/create", handler.create)
    http.HandleFunc("/update", handler.update)
    http.HandleFunc("/delete", handler.deleteItem)

    log.Fatal(http.ListenAndServe("localhost:8000", nil))
}
```

---

## Chapter 30: Concurrency Gotchas

> 📊 **Slide Reference:** `slides/go-30-gotchas-slides.pdf`

Writing concurrent software exposes developers to unique pitfalls. Below is a structured breakdown of concurrency errors in Go and how to avoid them.

### 1. Simple Deadlocks

A deadlock occurs when goroutines are blocked waiting for each other, and none can make progress. In an unbuffered channel:

```go
ch := make(chan int)
ch <- 42 // Blocks forever; no concurrent goroutine is receiving!
```

Go’s runtime features a built-in static deadlock detector. If all goroutines are blocked, the program crashes with: `fatal error: all goroutines are asleep - deadlock!`.

### 2. Lock Ordering (Dining Philosophers)

If your code must acquire more than one Mutex simultaneously, you must **always acquire them in the exact same order** and **release them in reverse order**.

#### Deadlock Scenario:
- Goroutine A locks `M1` and waits for `M2`.
- Goroutine B locks `M2` and waits for `M1`.

```go
// Thread A
mu1.Lock()
mu2.Lock()

// Thread B (Deadlock Risk)
mu2.Lock()
mu1.Lock()
```

#### Correct Strategy:
Always enforce a total ordering on mutex acquisition throughout the codebase. If Thread B is updated to acquire `mu1` then `mu2`, the deadlock is impossible.

### 3. Goroutine Leaks

A goroutine leak occurs when a goroutine is started but blocked permanently on a channel send or receive. The memory allocated for its stack and captured variables is never garbage collected.

```go
func QueryService() string {
    ch := make(chan string) // Unbuffered
    
    go func() {
        res := fetchFromRemote()
        ch <- res // Leaked! If parent times out, no one reads from ch.
    }()

    select {
    case res := <-ch:
        return res
    case <-time.After(500 * time.Millisecond):
        return "timeout"
    }
}
```

**The Fix:** Make the channel buffered (`make(chan string, 1)`). This allows the background goroutine to write its result and exit, even if the parent function has already returned.

### 4. WaitGroup Placement

A common bug is placing the `wg.Add(1)` call *inside* the spawned goroutine.

```go
// INCORRECT
for _, work := range list {
    go func() {
        wg.Add(1) // Race! Loop may finish and wg.Wait() runs before this executes.
        defer wg.Done()
        process(work)
    }()
}
wg.Wait()
```

**The Rule:** Always call `wg.Add(1)` in the **parent** goroutine *before* spawning the child.

```go
// CORRECT
for _, work := range list {
    wg.Add(1)
    go func(w Work) {
        defer wg.Done()
        process(w)
    }(work)
}
wg.Wait()
```

### 5. Loop Closure Capture

Because loop variables in Go are updated in-place during iteration, capturing a loop variable in a goroutine closure results in all goroutines referencing the same variable.

```go
// INCORRECT
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i) // Likely prints '10' ten times
    }()
}
```

**The Fixes:**
1. Pass the loop variable as an argument to the anonymous function:
   ```go
   for i := 0; i < 10; i++ {
       go func(val int) {
           fmt.Println(val)
       }(i)
   }
   ```
2. Redefine a local variable inside the loop scope:
   ```go
   for i := 0; i < 10; i++ {
       i := i // local copy
       go func() {
           fmt.Println(i)
       }()
   }
   ```

### 6. Select Priority Gotcha

When multiple channels in a `select` statement are ready, Go selects a case **pseudo-randomly**.
If a worker reads from an input channel and check for cancellation via a `done` channel, the worker may skip the `done` cancellation if the input channel is consistently flooded.

```go
select {
case msg := <-input:
    process(msg)
case <-done:
    cleanup()
    return
}
```

**The Fix:** If cancellation takes priority, perform a double-check select:

```go
select {
case <-done:
    cleanup()
    return
default:
    select {
    case msg := <-input:
        process(msg)
    case <-done:
        cleanup()
        return
    }
}
```

---

## Chapter 31: Odds & Ends

> 📊 **Slide Reference:** `slides/go-31-misc-slides.pdf`

This chapter covers smaller, miscellaneous syntax features and details in the Go language.

### 1. Custom Enumerations (`iota`)

Go does not have a formal `enum` keyword. Instead, we define a custom type (typically based on `int`) and use a constant block with the predefined identifier `iota` to generate auto-incrementing numbers.

#### Basic Custom Enum
```go
package main

import "fmt"

type Shoe int

const (
    Tennis Shoe = iota // Starts at 0
    Dress              // Automatically gets Shoe(1)
    Sandal             // Automatically gets Shoe(2)
    Clog               // Automatically gets Shoe(3)
)
```

#### Bit Flags
We can construct bit flags by shifting a bit left by `iota` spaces:

```go
type Permission int

const (
    Read   Permission = 1 << iota // 1 << 0 = 0001 (1)
    Write                         // 1 << 1 = 0010 (2)
    Execute                       // 1 << 2 = 0100 (4)
)
```

#### Skipping Values (Prefix/Unused Zero Value)
In some systems, we want the zero value of a custom type to represent an invalid or unitialized state. We can use the blank identifier `_` to skip `iota` indices:

```go
type ByteSize int64

const (
    _           = iota // Ignore zero value
    KB ByteSize = 1 << (10 * iota) // 1 << (10 * 1) = 1024
    MB                             // 1 << (10 * 2) = 1048576
    GB                             // 1 << (10 * 3) = 1073741824
)
```

---

### 2. Variadic Functions (Variable Argument Lists)

A variadic function accepts any number of trailing arguments. We define it using the `...` operator in front of the parameter type.

#### Defining and Unpacking Variadic Parameters
Inside the function, the variadic parameter behaves as a standard slice:

```go
package main

import "fmt"

func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

func main() {
    fmt.Println(sum(1, 2, 3)) // Output: 6
    fmt.Println(sum())        // Output: 0

    // Unpacking a slice into a variadic function call:
    values := []int{4, 5, 6}
    fmt.Println(sum(values...)) // Output: 15
}
```

The standard library `append` function is variadic, allowing you to join two slices together using the unpack operator:
```go
s1 := []int{1, 2}
s2 := []int{3, 4}
s1 = append(s1, s2...) // s1 becomes []int{1, 2, 3, 4}
```

---

### 3. Bitwise Operators

Go provides standard low-level bitwise operations. All shifts in Go are **logical** (always filling empty bits with zeros), not arithmetic.

| Operator | Operation | Description |
| :--- | :--- | :--- |
| `&` | AND | Returns 1 if both bits are 1 |
| `\|` | OR | Returns 1 if either bit is 1 |
| `^` | XOR / NOT | Binary: XOR (1 if bits are different). Unary: Bitwise NOT (flips bits). |
| `&^` | AND NOT | Bit clear (clears bits set in the second operand) |
| `<<` | Left Shift | Shifts bits left, fills with 0 |
| `>>` | Right Shift | Shifts bits right, fills with 0 (logical shift) |

#### TCP Flag Masking Example
```go
package main

import "fmt"

const (
    SYN = 1 << 0
    ACK = 1 << 1
    FIN = 1 << 2
)

func main() {
    // Combine SYN and ACK
    flags := SYN | ACK

    // Test if both SYN and ACK are set
    mask := SYN | ACK
    if flags&mask == mask {
        fmt.Println("Packet is a SYN-ACK")
    }
}
```

---

### 4. Sized Integers & Two's Complement Gotchas

Go supports sized integer types:
- **Signed:** `int8`, `int16`, `int32`, `int64`.
- **Unsigned:** `uint8`, `uint16`, `uint32`, `uint64`.

#### The Downcasting Gotcha
Converting a larger integer type to a smaller type discards the high-order bits.

```go
var a int32 = 0x12345678
var b int16 = int16(a) // b becomes 0x5678 (discards high 16 bits)
```

If the high bit of the remaining bits is $1$, the number becomes negative (if signed):
```go
var a int32 = 32768        // binary: 00000000 00000000 10000000 00000000
var b int16 = int16(a)     // b becomes -32768 (high bit is 1)
```

#### Two's Complement Range Contraction
Signed integers are stored in two's complement form. The range of an 8-bit signed integer (`int8`) is $-128$ to $+127$. There is one more negative value than positive value because zero is non-negative.

Because of this asymmetry, multiplying or dividing the minimum value by $-1$ results in silent overflow:

```go
package main

import "fmt"

func main() {
    var x int8 = -128
    
    // -128 * -1 should be 128, which exceeds int8 limit (+127)
    x = x * -1 
    fmt.Println(x) // Output: -128 (silent overflow back to min value!)

    var y int8 = -128
    y = y - 1
    fmt.Println(y) // Output: 127 (wraps around to maximum positive!)
}
```

To avoid silent bugs, Go enforces explicit conversions. You cannot perform mathematical operations on mixed integer types (e.g., `int32 + int16`) without converting them to matching types.

---

### 5. The `goto` Statement

Although `goto` can create unreadable "spaghetti code", it is occasionally useful to bypass nested conditions or retry loops cleanly.

#### WAV File Junk Header Skip Example
```go
package main

import (
    "bytes"
    "encoding/binary"
    "fmt"
)

func parseWav(data []byte) {
    buf := bytes.NewReader(data)

readHeader:
    var headerID [4]byte
    if err := binary.Read(buf, binary.BigEndian, &headerID); err != nil {
        return
    }

    if string(headerID[:]) == "JUNK" {
        // Skip junk bytes and retry header parse
        var size int32
        binary.Read(buf, binary.LittleEndian, &size)
        buf.Seek(int64(size), 1)
        goto readHeader // Jump back to try reading the format header again
    }

    fmt.Println("Header:", string(headerID[:]))
}
```
In this scenario, `goto` provides a clean, single-point retry loop without the indentation overhead of recursive calls or stateful nested loops.
