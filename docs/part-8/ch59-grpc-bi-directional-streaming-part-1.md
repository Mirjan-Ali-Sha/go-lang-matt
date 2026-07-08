## Chapter 59: gRPC Bi-Directional Streaming — Part 1

<VideoPlayer videoId="4ohwkWVgEZM" chapter="59" />  
> 🔗 **Source Code:** [GitHub - Episode 16 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_16)

gRPC supports streaming connections over HTTP/2, allowing clients and servers to send continuous message streams concurrently over a single TCP connection.

### 1. Defining a Streaming RPC in Protobuf (`protos/currency.proto`)
We define a bi-directional streaming RPC method in our Protobuf schema file.

```protobuf
syntax = "proto3";

option go_package = "./protos";

service Currency {
    // Bi-directional stream RPC
    rpc SubscribeRates(stream RateRequest) returns (stream RateResponse);
}
```

### 2. Implementing the Stream Handler on the Server
We implement the server handler, reading and writing messages in a loop using the stream's `Recv` and `Send` methods.

```go
package server

import (
    "io"
    "log"
    "protos"
)

func (c *Currency) SubscribeRates(stream protos.Currency_SubscribeRatesServer) error {
    for {
        // Read incoming request from the stream
        req, err := stream.Recv()
        if err == io.EOF {
            // Client closed the send stream gracefully
            return nil
        }
        if err != nil {
            return err
        }

        // Process request and write response to the stream
        resp := &protos.RateResponse{Rate: 0.82}
        err = stream.Send(resp)
        if err != nil {
            return err
        }
    }
}
```
