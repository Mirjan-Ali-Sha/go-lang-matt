## Chapter 36: Profiling

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-36-profile-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-36-profile-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="MDB2x1Di5uM" chapter="36" />

Profiling is the measurement of execution indicators (such as CPU, Memory, or Goroutines) during run-time. Go includes a built-in profiling engine `runtime/pprof` and a visualization tool `go tool pprof`.

### 1. Enabling Profiling in Web Apps

To expose profiling endpoints in an HTTP server, import `net/http/pprof` for its side-effects:

```go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof" // Registers endpoints under /debug/pprof
)

func main() {
    log.Println("Server starting on :8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

This exposes endpoints including:
- `/debug/pprof/goroutine` — Stack traces of all active goroutines (useful for finding leaks).
- `/debug/pprof/profile?seconds=30` — Downloads a 30-second CPU execution profile.
- `/debug/pprof/heap` — Memory allocation profiles.

---

### 2. Tracking Goroutine Leaks

A goroutine leak happens when a routine remains blocked indefinitely (e.g., on a socket read without a close, or writing to an unbuffered channel without a reader).

#### Example: Leaking Sockets via Missing Body Close
```go
package main

import (
    "io/ioutil"
    "net/http"
    _ "net/http/pprof"
)

func leakHandler(w http.ResponseWriter, r *http.Request) {
    resp, err := http.Get("https://jsonplaceholder.typicode.com/todos/1")
    if err != nil {
        return
    }
    // Defer resp.Body.Close() is missing! The socket connection leaks,
    // and the HTTP client goroutine remains stuck on the network poll.
    _, _ = ioutil.ReadAll(resp.Body)
}
```

If we hit `/debug/pprof/goroutine` repeatedly after querying this endpoint, we will see the active goroutine count increase linearly and remain high.

---

### 3. CPU Profiling: The Sorting Animator Example

We can profile an application that generates animated sorting GIFs to identify CPU hotspots.

#### Step 1: Paint Square (Slow Version)
This version calls `SetColorIndex` on every pixel of the square, incurring function call overhead, index calculations, and redundant bounds checks:

```go
func paintSquareSlow(img *image.Paletted, x, y, scale, colorIndex int) {
    for dy := 0; dy < scale; dy++ {
        for dx := 0; dx < scale; dx++ {
            // Checks bounds and calculates offsets for every single pixel!
            if dx == 0 || dy == 0 || dx == scale-1 || dy == scale-1 {
                img.SetColorIndex(x*scale+dx, y*scale+dy, 0) // Gray Border
            } else {
                img.SetColorIndex(x*scale+dx, y*scale+dy, uint8(colorIndex))
            }
        }
    }
}
```

#### Step 2: Running pprof
Build the binary with debug info:
```powershell
go build -o sort.exe
```

Start the server and capture a CPU profile for 10 seconds:
```powershell
go tool pprof -http=:8082 sort.exe http://localhost:8080/debug/pprof/profile?seconds=10
```
This opens a web UI showing a **Call Graph** and a **Flame Graph** where the widest boxes represent functions taking the most CPU time.

#### Step 3: Strength Reduction & Bounds Optimization (Fastest Version)
Using reflection, we inspect the layout of `image.Paletted`. Since rows are stored contiguously in a single `Pix` slice, we can precompute row offsets and copy entire rows using the built-in `copy` function, eliminating loop bounds checks:

```go
func paintSquareFastest(img *image.Paletted, x, y, scale, colorIndex int) {
    // 1. Calculate top-left and bottom-left offsets in the image Pix buffer
    startY := y * scale
    startX := x * scale
    startOffset := startY*img.Stride + startX
    
    // 2. Pre-create templates for border and fill rows
    borderRow := make([]uint8, scale) // Defaults to 0 (gray border)
    
    fillRow := make([]uint8, scale)
    fillRow[0] = 0
    fillRow[scale-1] = 0
    for i := 1; i < scale-1; i++ {
        fillRow[i] = uint8(colorIndex)
    }

    // 3. Copy templates directly into the image's raw pixel buffer
    // Top Border
    copy(img.Pix[startOffset:startOffset+scale], borderRow)
    
    // Middle Rows
    for dy := 1; dy < scale-1; dy++ {
        offset := startOffset + dy*img.Stride
        copy(img.Pix[offset:offset+scale], fillRow)
    }
    
    // Bottom Border
    bottomOffset := startOffset + (scale-1)*img.Stride
    copy(img.Pix[bottomOffset:bottomOffset+scale], borderRow)
}
```

Using this approach:
- Redundant multiplications are moved outside the loop.
- Individual pixel boundary checks are replaced by a single boundary check during slice copying.
- This yielded a **6x speedup** on the image painting pipeline.

---
