## Chapter 28: Conventional Synchronization

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-28-mutex-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-28-mutex-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="DtXNSE3Yejg" chapter="28" />

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
