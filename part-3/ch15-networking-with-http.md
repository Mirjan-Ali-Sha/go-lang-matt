## Chapter 15: Networking with HTTP

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-15-http-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-15-http-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="Q-uy0FS6RwU" chapter="15" />

Go was designed from the ground up for cloud computing, rest APIs, and microservices. Because of this, it has an incredibly robust, production-grade HTTP server and client built directly into the standard library via `net/http`.

### Writing a Simple Web Server

Here is a basic HTTP server that listens on port `8080` and echoes the URL path:

```go
package main

import (
    "fmt"
    "net/http"
    "strings"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    // Trim the leading slash from the path
    name := strings.TrimPrefix(r.URL.Path, "/")
    if name == "" {
        name = "World"
    }
    // Write the response directly into the ResponseWriter (which implements io.Writer)
    fmt.Fprintf(w, "Hello, %s!", name)
}

func main() {
    http.HandleFunc("/", helloHandler)
    // Starts the server. ListenAndServe block is blocking and handles connections concurrently.
    if err := http.ListenAndServe(":8080", nil); err != nil {
        panic(err)
    }
}
```

Go's HTTP server is fully concurrent. Under the hood, the server spawns a new goroutine for every TCP connection, allowing it to process thousands of requests simultaneously.

### Writing a Simple HTTP Client

We can make client requests using `http.Get`:

```go
resp, err := http.Get("http://localhost:8080/Matt")
if err != nil {
    log.Fatal(err)
}
// CRITICAL: Always close the response body!
defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
    log.Fatalf("received status: %s", resp.Status)
}

bodyBytes, err := io.ReadAll(resp.Body)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(bodyBytes)) // "Hello, Matt!"
```

> ⚠️ **Resource Leak Danger:** You **must** close `resp.Body`. If you do not close it, the underlying TCP connection remains open, and the program will eventually leak sockets and crash when it runs out of file descriptors.

### Parsing JSON from a Response Body

If a network endpoint returns JSON, you can decode it directly from the response body. 

While you can read all bytes into memory with `io.ReadAll` and then call `json.Unmarshal`, it is cleaner and more memory-efficient to stream it directly using a `json.Decoder`:

```go
type Todo struct {
    ID        int    `json:"id"`
    Title     string `json:"title"`
    Completed bool   `json:"completed"`
}

resp, err := http.Get("https://jsonplaceholder.typicode.com/todos/1")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

var item Todo
// Decode directly from the streaming body reader
if err := json.NewDecoder(resp.Body).Decode(&item); err != nil {
    log.Fatal(err)
}

fmt.Printf("Todo ID %d: %q (Completed: %t)\n", item.ID, item.Title, item.Completed)
```

This works because `resp.Body` implements `io.ReadCloser` (which embeds `io.Reader`), and `json.NewDecoder` accepts any `io.Reader`.

---
