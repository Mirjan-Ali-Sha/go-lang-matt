## Chapter 45: Structuring Microservice Code

<VideoPlayer videoId="hodOppKJm5Y" chapter="45" />  
> 🔗 **Source Code:** [GitHub - Episode 2 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_2)

To move past toy examples, we must organize handlers into dedicated objects, configure safe server timeouts, and ensure graceful shutdown.

### 1. Refactoring Handlers into Structs
Implementing the `http.Handler` interface (which requires a `ServeHTTP` method) allows us to inject dependencies (like loggers or database connections) into our handlers.

#### The Hello Handler (`handlers/hello.go`)
```go
package handlers

import (
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
)

type Hello struct {
    l *log.Logger
}

func NewHello(l *log.Logger) *Hello {
    return &Hello{l: l}
}

func (h *Hello) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    h.l.Println("Hello World Handler Executed")
    
    d, err := ioutil.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Oops", http.StatusBadRequest)
        return
    }
    
    fmt.Fprintf(w, "Hello %s", d)
}
```

### 2. Custom Serve Multiplexers and Server Configs
Instead of using global state, we instantiate a custom `http.NewServeMux()` and explicitly define timeout settings on `http.Server` to prevent resource leakage (slowloris attacks).

#### The Main Entrypoint (`main.go`)
```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "time"
    "handlers"
)

func main() {
    l := log.New(os.Stdout, "product-api ", log.LstdFlags)
    
    // Initialize handlers
    hh := handlers.NewHello(l)
    
    // Create new serve multiplexer
    sm := http.NewServeMux()
    sm.Handle("/", hh)
    
    // Explicit server configuration
    s := &http.Server{
        Addr:         ":9090",
        Handler:      sm,
        IdleTimeout:  120 * time.Second,
        ReadTimeout:  1 * time.Second,
        WriteTimeout: 1 * time.Second,
    }
    
    // Run the server in a goroutine so it doesn't block main
    go func() {
        l.Println("Starting server on port 9090...")
        err := s.ListenAndServe()
        if err != nil {
            l.Fatal(err)
        }
    }()
    
    // Channel to receive OS signals for graceful shutdown
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, os.Interrupt)
    signal.Notify(sigChan, os.Kill)
    
    // Block until signal is received
    sig := <-sigChan
    l.Println("Received terminate, graceful shutdown", sig)
    
    // Graceful shutdown context
    tc, _ := context.WithTimeout(context.Background(), 30*time.Second)
    s.Shutdown(tc)
}
```
