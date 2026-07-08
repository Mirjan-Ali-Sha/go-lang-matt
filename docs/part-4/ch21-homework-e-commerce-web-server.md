## Chapter 21: Homework — E-Commerce Web Server

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-21-hw4-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-21-hw4-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="YUaruvHkXio" chapter="21" />

In this homework, we implement Exercise 7.11 from *The Go Programming Language* book. We build a simple web database server for a store, implementing listing, reading, creating, updating, and deleting items.

### Implementation

We define a custom type `database` wrapping a map, and use **method values** to register handlers.

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "strconv"
)

type dollars float64

func (d dollars) String() string {
    return fmt.Sprintf("$%.2f", d)
}

type database map[string]dollars

// /list
func (db database) list(w http.ResponseWriter, req *http.Request) {
    for item, price := range db {
        fmt.Fprintf(w, "%s: %s\n", item, price)
    }
}

// /read?item=shoes
func (db database) read(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    price, ok := db[item]
    if !ok {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }
    fmt.Fprintf(w, "%s: %s\n", item, price)
}

// /create?item=shoes&price=50
func (db database) create(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    if _, exists := db[item]; exists {
        http.Error(w, fmt.Sprintf("duplicate item: %q", item), http.StatusBadRequest)
        return
    }

    price, err := strconv.ParseFloat(priceStr, 64)
    if err != nil {
        http.Error(w, fmt.Sprintf("invalid price: %q", priceStr), http.StatusBadRequest)
        return
    }

    db[item] = dollars(price)
    fmt.Fprintf(w, "added %s with price %s\n", item, db[item])
}

// /update?item=shoes&price=55
func (db database) update(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    if _, exists := db[item]; !exists {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }

    price, err := strconv.ParseFloat(priceStr, 64)
    if err != nil {
        http.Error(w, fmt.Sprintf("invalid price: %q", priceStr), http.StatusBadRequest)
        return
    }

    db[item] = dollars(price)
    fmt.Fprintf(w, "updated %s to %s\n", item, db[item])
}

// /delete?item=shoes
func (db database) delete(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    if _, exists := db[item]; !exists {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }
    delete(db, item)
    fmt.Fprintf(w, "deleted item: %q\n", item)
}

func main() {
    db := database{"shoes": 50, "socks": 5}

    // Using method values (db.list, db.read, etc.)
    // These close over the db map descriptor receiver.
    http.HandleFunc("/list", db.list)
    http.HandleFunc("/read", db.read)
    http.HandleFunc("/create", db.create)
    http.HandleFunc("/update", db.update)
    http.HandleFunc("/delete", db.delete)

    fmt.Println("Server listening on :8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### Concurrency Warning

Go's built-in web server executes handlers concurrently on separate goroutines. Since maps in Go are **not safe for concurrent read and write operations**, concurrent access to the `db` map (e.g., calling `/create` and `/list` simultaneously) will result in a fatal runtime panic: `fatal error: concurrent map writes`.

We will address how to safely synchronize this shared state in Part V.
