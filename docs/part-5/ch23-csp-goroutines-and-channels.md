## Chapter 23: CSP, Goroutines, and Channels

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-23-csp-goroutines-channels-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-23-csp-goroutines-channels-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="zJd7Dvg3XCk" chapter="23" />

Go’s concurrency model is based on **Communicating Sequential Processes (CSP)**, a formal language described by C.A.R. Hoare in 1978.

### The CSP Philosophy

In traditional concurrent programming, threads share memory, and we write complex synchronization code (locks, semaphores) to protect that memory. Go turns this around:
> **"Do not communicate by sharing memory; instead, share memory by communicating."**

In Go's CSP implementation:
- **Sequential Processes** are represented by **Goroutines**.
- **Communication Pipelines** are represented by **Channels**.

### Goroutines

A **goroutine** is a lightweight thread of execution managed by the Go runtime scheduler, not the operating system.

| Property | OS Thread | Goroutine |
| :--- | :--- | :--- |
| **Stack Size** | Fixed size (typically 1–8 MB) | Dynamically resizing (starts at ~2 KB) |
| **Creation Cost** | Expensive (requires OS system call) | Very cheap (simple allocation) |
| **Context Switch** | Expensive (saves/restores CPU registers) | Cheap (handled in user space by Go runtime) |
| **Scalability** | Thousands per system | Millions per system |

To spawn a goroutine, prefix any function call with the `go` keyword:
```go
go doWork(param)
```

#### Goroutine Leaks

Because goroutines are cheap, developers sometimes forget to clean them up. A **goroutine leak** occurs when a goroutine is started but gets permanently blocked waiting on a channel or resource that will never arrive. The leaked goroutine remains in memory, causing a slow resource drain that will eventually crash a long-running server. Always design goroutines with a clear termination condition.

### Channels

A **channel** is a typed, synchronized pipe through which goroutines can send and receive values safely. Channels are first-class types created using `make`:

```go
ch := make(chan int) // Unbuffered channel of integers
```

- **Send operator (`<-`):** `ch <- 42` (puts a value into the channel).
- **Receive operator (`<-`):** `val := <-ch` (extracts a value from the channel).
- **Closing a channel:** `close(ch)` (signals that no more values will be sent).

#### Unidirectional Channel Constraints

Channels can be restricted to send-only or receive-only types, typically in function signatures:

```go
func produce(out chan<- int) { // Send-only channel
    out <- 42
}

func consume(in <-chan int) {  // Receive-only channel
    val := <-in
    fmt.Println(val)
}
```

### Example 1: Parallel HTTP GET

Here is an example of fetching multiple web pages concurrently and collecting their latency statistics using a channel:

```go
package main

import (
    "fmt"
    "net/http"
    "time"
)

type Result struct {
    URL     string
    Latency time.Duration
    Err     error
}

func getURL(url string, ch chan<- Result) {
    start := time.Now()
    resp, err := http.Get(url)
    if err != nil {
        ch <- Result{URL: url, Err: err}
        return
    }
    defer resp.Body.Close()
    
    ch <- Result{
        URL:     url,
        Latency: time.Since(start).Round(time.Millisecond),
        Err:     nil,
    }
}

func main() {
    urls := []string{
        "https://google.com",
        "https://golang.org",
        "https://github.com",
    }

    ch := make(chan Result)

    for _, url := range urls {
        go getURL(url, ch)
    }

    // Read exactly len(urls) results from the channel
    for i := 0; i < len(urls); i++ {
        res := <-ch
        if res.Err != nil {
            fmt.Printf("Error fetching %s: %v\n", res.URL, res.Err)
        } else {
            fmt.Printf("%s responded in %v\n", res.URL, res.Latency)
        }
    }
}
```

### Example 2: Thread-Safe Counter (Channel-Based State)

Instead of sharing an integer variable across multiple HTTP handlers, we can encapsulate a channel to coordinate thread-safe state increments:

```go
package main

import (
    "fmt"
    "net/http"
)

type counter chan int

func (c counter) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    id := <-c
    fmt.Fprintf(w, "You are visitor #%d\n", id)
}

func generateIDs(c chan<- int) {
    for i := 1; ; i++ {
        c <- i // Blocks until a handler reads
    }
}

func main() {
    c := make(counter)
    go generateIDs(c)

    http.Handle("/count", c)
    http.ListenAndServe(":8080", nil)
}
```

### Example 3: Concurrent Sieve of Eratosthenes

This classic algorithm constructs a dynamic pipeline of channels and filtering goroutines to output prime numbers.

```go
package main

import "fmt"

// Generate sends sequence 2, 3, 4, ... to channel 'ch'.
func Generate(ch chan<- int, limit int) {
    for i := 2; i <= limit; i++ {
        ch <- i
    }
    close(ch)
}

// Filter copies values from 'in' to 'out', discarding multiples of 'prime'.
func Filter(in <-chan int, out chan<- int, prime int) {
    for val := range in {
        if val%prime != 0 {
            out <- val
        }
    }
    close(out)
}

func main() {
    ch := make(chan int)
    go Generate(ch, 100)

    for {
        prime, ok := <-ch
        if !ok {
            break // Domino effect: input channel closed
        }
        fmt.Printf("%d ", prime)

        chOut := make(chan int)
        go Filter(ch, chOut, prime)
        ch = chOut // Chain the new filter output
    }
    fmt.Println()
}
```

---
