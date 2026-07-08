## Chapter 44: Introduction to Microservices

<VideoPlayer videoId="VzBGi_n65iU" chapter="44" />  
> 🔗 **Source Code:** [GitHub - Episode 1 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_1)

Building microservices in Go is supported by the language's high concurrency, small memory footprint, and powerful standard library. We begin by constructing a basic HTTP server using only the standard `net/http` package.

### 1. The Standard HTTP Server
Go provides a robust HTTP server implementation in `net/http`. The most basic server uses `http.HandleFunc` to register a function callback to a path, and `http.ListenAndServe` to bind to an address and start listening.

```go
package main

import (
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
)

func main() {
    // Registering our path handler
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        log.Println("Hello World")
        
        // Reading data from the request body
        d, err := ioutil.ReadAll(r.Body)
        if err != nil {
            // Replying with a standard HTTP error
            http.Error(w, "Oops", http.StatusBadRequest)
            return
        }
        
        // Writing a formatted string back to the client
        fmt.Fprintf(w, "Hello %s", d)
    })

    // Binding to all interfaces on port 9090
    log.Println("Starting server on port 9090...")
    err := http.ListenAndServe(":9090", nil)
    if err != nil {
        log.Fatal(err)
    }
}
```

### 2. Testing the Server
You can run the server using the standard `go run` command:

```bash
go run main.go
```

To test the server, use `curl` to send a POST request containing data in the body:

```bash
curl -v -d "World" http://localhost:9090/
```

### 3. Understanding the Default Serve MUX
*   `http.ListenAndServe(":9090", nil)`: Passing `nil` as the second argument causes the server to use Go's default multiplexer, `http.DefaultServeMux`.
*   `http.HandleFunc` registers handlers to this global `DefaultServeMux`. While convenient, relying on global state is discouraged in production environments due to security risks and testability challenges.
