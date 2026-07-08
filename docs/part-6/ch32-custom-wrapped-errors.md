## Chapter 32: Custom & Wrapped Errors

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-32-errors-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-32-errors-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="oIxXp0OgK_0" chapter="32" />

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
