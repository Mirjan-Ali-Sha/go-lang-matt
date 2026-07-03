## Chapter 30: Concurrency Gotchas

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-30-gotchas-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-30-gotchas-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="K1hwpNnCJgY" chapter="30" />

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
