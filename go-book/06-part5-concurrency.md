# Part V — Concurrency

---

## Chapter 22: What is Concurrency

> 📊 **Slide Reference:** `slides/go-22-what-is-concurrency-slides.pdf`

Concurrency is one of Go's most celebrated features. However, before writing concurrent code, we must clearly define what concurrency is, how it differs from parallelism, and the unique challenges it introduces.

### Concurrency vs. Parallelism

Many programmers conflate concurrency and parallelism, but they are distinct concepts:
- **Concurrency** is about **structure**. It is the composition of independently executing processes. A program is concurrent if it is divided into discrete components that *can* run out of order or in a non-deterministic sequence without affecting the final result.
- **Parallelism** is about **execution**. It is the simultaneous execution of multiple entities at the exact same physical instant.

As Rob Pike famously stated:
> *"Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once."*

#### The Road Bridge Analogy

To visualize this, imagine a two-lane road:
1. **Parallelism (Independent Execution):** A highway with a northbound lane and a southbound lane. Cars in both directions travel at the same time without interfering with each other.
2. **Concurrency with Shared State (Stoplight Control):** The road encounters a narrow one-way bridge. To prevent a head-on collision (a data race), we must install stoplights at both ends. The stoplights enforce safety, but traffic must now back up (synchronization overhead), reducing performance.

Concurrency is a property of the software design; parallelism is a property of the runtime hardware. A concurrent program can run in parallel on a multi-core processor, but it can also run sequentially (via time-slicing) on a single-core processor.

### Partial Ordering & Non-Determinism

In sequential programming, we have a **total ordering**: step A executes, then step B, then step C. In concurrent programming, we have a **partial ordering**:

```
[Step 1]
   /\
  /  \
[2A] [3A]
 |    |
[2B] [3B]
  \  /
   \/
[Step 4]
```

Step 1 must happen first, and Step 4 must happen last. However, there is no defined relationship between the `2` branch and the `3` branch. The runtime scheduler can execute them in several valid sequences:
- `1 -> 2A -> 2B -> 3A -> 3B -> 4`
- `1 -> 3A -> 3B -> 2A -> 2B -> 4`
- `1 -> 2A -> 3A -> 2B -> 3B -> 4`

Because of this partial ordering, execution is **non-deterministic**. The scheduler's choices depend on CPU load, thread sleep states, and OS thread scheduling.

### The Race Condition

A **race condition** occurs when the program's correctness depends on the non-deterministic order of execution. If any of the possible scheduling outcomes produces an incorrect result, the program has a bug—even if it runs correctly 99% of the time.

#### Read-Modify-Write Cycles

The classic example of a race condition is a concurrent counter increment (`x++`). At the hardware level, this is not a single instruction; it is a **read-modify-write cycle**:
1. **Read:** Copy the value of `x` from memory into a CPU register.
2. **Modify:** Add `1` to the register.
3. **Write:** Copy the register value back to memory.

If two concurrent threads attempt to increment `x` (initial value: 100) simultaneously without synchronization, their operations may interleave:

| Time | Thread A | Thread B | Memory Value |
| :--- | :--- | :--- | :--- |
| $T_1$ | Reads `x` (100) | | 100 |
| $T_2$ | | Reads `x` (100) | 100 |
| $T_3$ | Increments to 101 | | 100 |
| $T_4$ | Writes `x` = 101 | | 101 |
| $T_5$ | | Increments to 101 | 101 |
| $T_6$ | | Writes `x` = 101 | **101** |

Two increments occurred, but the final value is 101. One increment evaporated because the read-modify-write cycle was divided.

### Solving Race Conditions

To prevent race conditions, we must make critical sections **atomic** (indivisible). We have four primary design strategies:
1. **Do not share state:** If data is local to a single thread, it cannot have a race condition.
2. **Share state, but make it read-only:** Concurrent reads are always safe.
3. **Impose a total order:** Restrict concurrency so that operations must run sequentially.
4. **Use synchronization primitives:** Coordinate access using tools like channels or mutual exclusion locks (mutexes) to protect read-modify-write cycles.

---

## Chapter 23: CSP, Goroutines, and Channels

> 📊 **Slide Reference:** `slides/go-23-csp-goroutines-channels-slides.pdf`

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

## Chapter 24: The Select Statement

> 📊 **Slide Reference:** `slides/go-24-select-slides.pdf`

The `select` statement is a control structure designed specifically for coordinating channel operations. It is Go's tool for channel multiplexing.

### Multiplexing Channels

If we read from multiple channels sequentially, one slow channel can block all others. `select` solves this by listening to multiple channels simultaneously, executing the first case that becomes ready:

```go
select {
case val := <-ch1:
    fmt.Println("Received from ch1:", val)
case ch2 <- 42:
    fmt.Println("Sent to ch2")
}
```

If multiple cases are ready at the same time, `select` chooses one **pseudo-randomly** to ensure fairness and prevent resource starvation.

### Code Example: Multiple Rates

Let's look at an example where two concurrent goroutines produce data at different rates, coordinated by a `select` block inside a `for` loop:

```go
package main

import (
    "fmt"
    "time"
)

func worker(id int, delay time.Duration, ch chan<- int) {
    for i := 1; ; i++ {
        time.Sleep(delay)
        ch <- id
    }
}

func main() {
    ch1 := make(chan int)
    ch2 := make(chan int)

    go worker(1, 1*time.Second, ch1)
    go worker(2, 2*time.Second, ch2)

    // Collect 10 ticks multiplexed
    for i := 0; i < 10; i++ {
        select {
        case msg := <-ch1:
            fmt.Printf("Received %d (every 1s)\n", msg)
        case msg := <-ch2:
            fmt.Printf("Received %d (every 2s)\n", msg)
        }
    }
}
```

### Timeouts with `time.After`

A common concurrent design pattern is to set an upper bound on how long we are willing to wait for a channel operation:

```go
select {
case res := <-results:
    fmt.Println("Got response:", res)
case <-time.After(3 * time.Second):
    fmt.Println("Timeout! Operation aborted.")
}
```

### Periodic Work with `time.Ticker`

To perform a task at regular intervals, use `time.Ticker`:

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ticker := time.NewTicker(500 * time.Millisecond)
    defer ticker.Stop()

    stopper := time.After(2 * time.Second)

loop:
    for {
        select {
        case t := <-ticker.C:
            fmt.Println("Tick at", t.Format("15:04:05.000"))
        case <-stopper:
            fmt.Println("Stop!")
            break loop // Breaks the labeled loop, not the select
        }
    }
}
```

### Non-Blocking Sends & Receives

If a `select` statement includes a `default` case, it becomes non-blocking. If no channel operation is ready, the `default` case executes immediately.

```go
select {
case msg := <-ch:
    fmt.Println("Received:", msg)
default:
    fmt.Println("No message available (moving on)")
}
```

> [!WARNING]
> Placing a `default` case inside an infinite `for { select { ... } }` loop without a pause will cause **busy-waiting**. The CPU will run at 100% load continuously. Only use `default` for immediate, single-attempt checks.

---

## Chapter 25: Context

> 📊 **Slide Reference:** `slides/go-25-context-slides.pdf`

The standard library `context` package provides a structured way to propagate cancellation signals, deadlines, and request-scoped values down a call stack and across goroutine boundaries.

### The Context Tree Structure

A context is represented as an immutable node in a tree. The tree is built from a root context pointing downwards, but nodes point **upwards** to their parents.

```
      [Background] (Root)
           ^
           |
      [WithValue] (Trace ID)
           ^
           |
     [WithTimeout] (3 Seconds)
```

We create new contexts by wrapping parent contexts:
- `context.Background()`: Returns a non-nil, empty root context.
- `context.WithCancel(parent)`: Returns a copy of parent with a new `Done` channel.
- `context.WithTimeout(parent, duration)`: Automatically cancels after a duration.
- `context.WithValue(parent, key, val)`: Associates a key-value pair with the context.

When a parent context is cancelled, all of its children in the tree are automatically cancelled as well.

### Cancellation & The Done Channel

A context exposes a `Done()` method that returns a channel. When the context is cancelled or times out, this channel is closed, serving as a broadcast signal to all listening goroutines.

```go
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            // Cleanup and exit
            return
        default:
            // Do work
        }
    }
}
```

### Example: HTTP Requests with Context

We can pass a context into an HTTP request. If the context times out, the HTTP library automatically cancels the network request:

```go
package main

import (
    "context"
    "fmt"
    "net/http"
    "time"
)

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel() // Always call cancel to release resources!

    req, err := http.NewRequestWithContext(ctx, "GET", "https://httpbin.org/delay/3", nil)
    if err != nil {
        panic(err)
    }

    _, err = http.DefaultClient.Do(req)
    if err != nil {
        fmt.Println("Request failed:", err) // Output: context deadline exceeded
    }
}
```

### Request-Scoped Values

Context can store key-value pairs. This is useful for passing metadata (such as authentication tokens or request trace IDs) through middleware chains.

To prevent keys from colliding with other packages, define a private, unexported custom type for context keys:

```go
package trace

import (
    "context"
)

// Private unexported type prevents collision
type contextKey struct{}

var traceKey contextKey

// NewContext returns a new context containing the trace ID
func NewContext(ctx context.Context, traceID string) context.Context {
    return context.WithValue(ctx, traceKey, traceID)
}

// FromContext extracts the trace ID from the context
func FromContext(ctx context.Context) (string, bool) {
    traceID, ok := ctx.Value(traceKey).(string) // Type assertion
    return traceID, ok
}
```

---

## Chapter 26: Channels in Detail

> 📊 **Slide Reference:** `slides/go-26-channels-in-detail-slides.pdf`

To write correct concurrent software, you must understand the exact mechanics of unbuffered and buffered channels under various states.

### Rendezvous Model vs. Buffering

1. **Unbuffered Channels (Rendezvous):**
   - Direct hand-off. The sender and receiver must meet.
   - Analogy: A delivery driver who must wait at the door for you to sign for a package.
   - **Behavior:** Whichever goroutine arrives first (sender or receiver) blocks until the second goroutine arrives.
2. **Buffered Channels:**
   - Decoupled hand-off.
   - Analogy: A mailbox. The mail carrier drops the letter off and drives away; you retrieve it later.
   - **Behavior:** The sender only blocks if the buffer is full. The receiver only blocks if the buffer is empty.

### The Rendezvous Race Demonstration

The following code illustrates rendezvous synchronization. By sending pointers through an unbuffered channel and modifying the data immediately after sending, we show that the receiver successfully copies the original data before the sender can mutate it:

```go
package main

import (
    "fmt"
    "time"
)

type Data struct {
    Val  byte
    Flag bool
}

func sender(ch chan<- *Data) {
    d := &Data{Val: 42, Flag: false}
    ch <- d        // Blocks until receiver reads
    d.Flag = true  // Modifies data AFTER hand-off finishes
}

func main() {
    ch := make(chan *Data) // Unbuffered (Rendezvous)

    go sender(ch)
    time.Sleep(100 * time.Millisecond) // Guarantee sender is waiting

    dPtr := <-ch
    copied := *dPtr // Copy dereferenced value immediately

    fmt.Println("Copied flag:", copied.Flag) // Output: false (safe hand-off)
    time.Sleep(100 * time.Millisecond)
    fmt.Println("Final flag:", dPtr.Flag)    // Output: true
}
```

If we change `ch` to a buffered channel (`make(chan *Data, 1)`), the sender executes `ch <- d`, immediately updates `d.Flag = true`, and returns. The main goroutine wakes up and copies the mutated value, printing `Copied flag: true`. This demonstrates that **buffered channels do not guarantee synchronization**.

### Channel States Reference

The behavior of send, receive, and close operations depends entirely on the channel's current state:

| Channel State | Send (`ch <- v`) | Receive (`<-ch`) | Close (`close(ch)`) |
| :--- | :--- | :--- | :--- |
| **Nil** | Blocks forever | Blocks forever | Panics |
| **Open & Empty** | Blocks (if unbuffered) / Succeeds (if buffer space) | Blocks | Succeeds |
| **Open & Loaded** | Blocks (if buffer full) | Succeeds (returns value) | Succeeds |
| **Closed** | Panics | Succeeds (returns zero value, `ok = false`) | Panics |

- **Closing a closed channel** panics immediately.
- **Sending to a closed channel** panics immediately.
- **Reading from a closed channel** never blocks; it yields the type's zero value with the second boolean return parameter set to `false`.

### The Counting Semaphore Pattern

We can use a buffered channel to limit the number of concurrent operations in progress (work-in-progress/occupancy limit).

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func process(id int, sem chan struct{}, wg *sync.WaitGroup) {
    defer wg.Done()

    sem <- struct{}{} // Acquire token (blocks if sem is full)
    fmt.Printf("Worker %d entering store\n", id)
    time.Sleep(1 * time.Second) // Perform work
    
    fmt.Printf("Worker %d leaving store\n", id)
    <-sem // Release token
}

func main() {
    const maxOccupancy = 3
    const totalWorkers = 7

    sem := make(chan struct{}, maxOccupancy)
    var wg sync.WaitGroup

    for i := 1; i <= totalWorkers; i++ {
        wg.Add(1)
        go process(i, sem, &wg)
    }

    wg.Wait()
}
```
In this pattern, the capacity of the buffered channel acts as the maximum concurrency limit.
