## Chapter 22: What is Concurrency

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-22-what-is-concurrency-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-22-what-is-concurrency-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="A3R-4ZYBqvE" chapter="22" />

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
