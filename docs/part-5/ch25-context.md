## Chapter 25: Context

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-25-context-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-25-context-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="0x_oUlxzw5A" chapter="25" />

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
