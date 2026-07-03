## Chapter 29: Exercise — Thread-Safe Web Server

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-29-hw5-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-29-hw5-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="juBGb6rvoec" chapter="29" />

This exercise revisits the REST-based storefront web server created in Chapter 21. The original implementation used a plain map `map[string]dollars` to track prices. Because HTTP handlers are run concurrently on separate goroutines, concurrent price updates and list requests caused data races.

### The Race Driver Code

To expose the race condition, we write a concurrent test driver that drives traffic into the server by issuing random HTTP requests (`create`, `update`, `delete`, and `list`) concurrently.

```go
// Run with: go run -race server.go
```

If the server is started with the Go race detector enabled (`go run -race`), the server will report data races and crash when the driver program runs.

### The Solution: Protecting the Database Map

We refactor the database to wrap the map inside a struct alongside a `sync.Mutex`.

```diff
- type database map[string]dollars
+ type database struct {
+     mu sync.Mutex
+     db map[string]dollars
+ }
```

#### Thread-Safe Server Code

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "strconv"
    "sync"
)

type dollars float32

func (d dollars) String() string {
    return fmt.Sprintf("$%.2f", d)
}

type database struct {
    mu sync.Mutex
    db map[string]dollars
}

func (db *database) list(w http.ResponseWriter, req *http.Request) {
    db.mu.Lock()
    defer db.mu.Unlock() // Safe release

    for item, price := range db.db {
        fmt.Fprintf(w, "%s: %s\n", item, price)
    }
}

func (db *database) price(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    
    db.mu.Lock()
    price, ok := db.db[item]
    db.mu.Unlock() // Release as early as possible before network writing

    if !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "no such item: %q\n", item)
        return
    }
    fmt.Fprintf(w, "%s\n", price)
}

func (db *database) create(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    p, err := strconv.ParseFloat(priceStr, 32)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "invalid price: %q\n", priceStr)
        return
    }

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; ok {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "item already exists: %q\n", item)
        return
    }

    db.db[item] = dollars(p)
    w.WriteHeader(http.StatusCreated)
    fmt.Fprintf(w, "created %s: %s\n", item, dollars(p))
}

func (db *database) update(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    p, err := strconv.ParseFloat(priceStr, 32)
    if err != nil {
        w.WriteHeader(http.StatusBadRequest)
        fmt.Fprintf(w, "invalid price: %q\n", priceStr)
        return
    }

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "item does not exist: %q\n", item)
        return
    }

    db.db[item] = dollars(p)
    fmt.Fprintf(w, "updated %s to: %s\n", item, dollars(p))
}

func (db *database) deleteItem(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")

    db.mu.Lock()
    defer db.mu.Unlock()

    if _, ok := db.db[item]; !ok {
        w.WriteHeader(http.StatusNotFound)
        fmt.Fprintf(w, "item does not exist: %q\n", item)
        return
    }

    delete(db.db, item)
    fmt.Fprintf(w, "deleted %s\n", item)
}

func main() {
    handler := &database{
        db: map[string]dollars{"shoes": 50, "socks": 5},
    }

    // Register routes
    http.HandleFunc("/list", handler.list)
    http.HandleFunc("/price", handler.price)
    http.HandleFunc("/create", handler.create)
    http.HandleFunc("/update", handler.update)
    http.HandleFunc("/delete", handler.deleteItem)

    log.Fatal(http.ListenAndServe("localhost:8000", nil))
}
```

---
