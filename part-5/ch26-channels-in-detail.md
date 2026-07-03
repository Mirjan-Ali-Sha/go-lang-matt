## Chapter 26: Channels in Detail

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-26-channels-in-detail-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-26-channels-in-detail-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="fCkxKGd6CVQ" chapter="26" />

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
