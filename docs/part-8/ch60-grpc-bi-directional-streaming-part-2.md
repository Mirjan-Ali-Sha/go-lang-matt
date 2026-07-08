## Chapter 60: gRPC Bi-Directional Streaming — Part 2

<VideoPlayer videoId="MT5tXSKa-KY" chapter="60" />  
> 🔗 **Source Code:** [GitHub - Episode 17 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_17)

To read and write concurrently on a bi-directional stream, the client must manage connections using asynchronous routines (goroutines).

### 1. Implementing Client Stream Routines
We spawn separate goroutines to send updates and process incoming messages asynchronously without blocking execution.

```go
package main

import (
    "context"
    "io"
    "log"
    "google.golang.org/grpc"
    "protos"
)

func main() {
    conn, _ := grpc.Dial("localhost:9092", grpc.WithInsecure())
    c := protos.NewCurrencyClient(conn)

    // Open connection stream
    stream, _ := c.SubscribeRates(context.Background())

    // Goroutine for handling incoming stream messages
    go func() {
        for {
            resp, err := stream.Recv()
            if err == io.EOF {
                log.Println("Server closed stream")
                break
            }
            if err != nil {
                log.Fatal("Error reading stream: ", err)
            }
            log.Printf("Received live rate update: %.2f\n", resp.Rate)
        }
    }()

    // Main thread writes subscription requests to the stream
    for {
        req := &protos.RateRequest{Base: "USD", Destination: "GBP"}
        stream.Send(req)
    }
}
```
