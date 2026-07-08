## Chapter 48: The Gorilla Framework

<VideoPlayer videoId="DD3JlT_u0DM" chapter="48" />  
> 🔗 **Source Code:** [GitHub - Episode 5 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_5)

Parsing IDs manually using regular expressions is verbose and error-prone. The **Gorilla Mux** framework simplifies route registrations, parameter extraction, and middleware integration.

### 1. Configuring Gorilla Mux Routing (`main.go`)
We define a new router, group routes by resource, and restrict them by HTTP verbs.

```go
package main

import (
    "context"
    "log"
    "net/http"
    "os"
    "os/signal"
    "time"
    "github.com/gorilla/mux"
    "handlers"
)

func main() {
    l := log.New(os.Stdout, "product-api ", log.LstdFlags)
    ph := handlers.NewProducts(l)

    sm := mux.NewRouter()

    // Subrouters for distinct HTTP verbs
    getRouter := sm.Methods(http.MethodGet).Subrouter()
    getRouter.HandleFunc("/products", ph.GetProducts)

    putRouter := sm.Methods(http.MethodPut).Subrouter()
    putRouter.HandleFunc("/products/{id:[0-9]+}", ph.UpdateProduct)

    postRouter := sm.Methods(http.MethodPost).Subrouter()
    postRouter.HandleFunc("/products", ph.AddProduct)

    s := &http.Server{
        Addr:         ":9090",
        Handler:      sm,
        IdleTimeout:  120 * time.Second,
        ReadTimeout:  1 * time.Second,
        WriteTimeout: 1 * time.Second,
    }

    // Server execution and graceful shutdown setup...
}
```

### 2. Extracting Variables in the Handler (`handlers/products.go`)
Gorilla Mux handles validation at the routing layer. Inside our handler, we use `mux.Vars` to extract parsed variables safely.

```go
package handlers

import (
    "log"
    "net/http"
    "strconv"
    "github.com/gorilla/mux"
    "data"
)

type Products struct {
    l *log.Logger
}

func NewProducts(l *log.Logger) *Products {
    return &Products{l: l}
}

func (p *Products) GetProducts(w http.ResponseWriter, r *http.Request) {
    lp := data.GetProducts()
    w.Header().Add("Content-Type", "application/json")
    lp.ToJSON(w)
}

func (p *Products) AddProduct(w http.ResponseWriter, r *http.Request) {
    prod := &data.Product{}
    prod.FromJSON(r.Body)
    data.AddProduct(prod)
}

func (p *Products) UpdateProduct(w http.ResponseWriter, r *http.Request) {
    vars := mux.Vars(r)
    id, _ := strconv.Atoi(vars["id"])

    prod := &data.Product{}
    prod.FromJSON(r.Body)

    err := data.UpdateProduct(id, prod)
    if err == data.ErrProductNotFound {
        http.Error(w, "Product not found", http.StatusNotFound)
        return
    }
}
```
