## Chapter 57: gRPC Client Connections

<VideoPlayer videoId="oTBcd5J0VYU" chapter="57" />  
> 🔗 **Source Code:** [GitHub - Episode 14 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_14)

Microservices often need to call other microservices. We establish a client connection from our HTTP Product API to our gRPC Currency API.

### 1. Initializing a gRPC Client Connection (`main.go`)
We dial the gRPC server and instantiate a type-safe client client stub.

```go
package main

import (
    "log"
    "net/http"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "protos"
)

func main() {
    // Establish connection channel
    conn, err := grpc.Dial("localhost:9092", grpc.WithTransportCredentials(insecure.NewCredentials()))
    if err != nil {
        log.Fatal("Could not connect to gRPC server: ", err)
    }
    defer conn.Close()

    // Instantiate service client stub
    cc := protos.NewCurrencyClient(conn)

    // Inject client stub into HTTP handlers
    // ...
}
```

### 2. Consuming the gRPC Client in HTTP Handlers
Our REST product handler consumes the gRPC currency client to fetch live exchange rates and calculate product prices.

```go
package handlers

import (
    "context"
    "net/http"
    "protos"
)

type Products struct {
    cc protos.CurrencyClient
}

func (p *Products) GetProducts(w http.ResponseWriter, r *http.Request) {
    // Query currency exchange rate via gRPC
    req := &protos.RateRequest{
        Base:        "USD",
        Destination: "GBP",
    }
    
    resp, err := p.cc.GetRate(context.Background(), req)
    if err != nil {
        http.Error(w, "Failed to fetch currency rates", http.StatusInternalServerError)
        return
    }

    // Multiply base prices by response rate...
}
```
