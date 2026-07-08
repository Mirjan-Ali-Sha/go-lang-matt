## Chapter 35: Benchmarking

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-35-bench-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-35-bench-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="nk4rALKLQkc" chapter="35" />

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
