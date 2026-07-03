## Chapter 24: The Select Statement

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-24-select-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-24-select-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="tG7gII0Ax0Q" chapter="24" />

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
