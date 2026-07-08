## Chapter 56: Introduction to gRPC and Protocol Buffers

<VideoPlayer videoId="pMgty_RYIOc" chapter="56" />  
> 🔗 **Source Code:** [GitHub - Episode 13 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_13)

JSON over HTTP is readable, but it is slow and lacks schema safety. **gRPC** uses **HTTP/2** transport and **Protocol Buffers** serialization to provide high-performance, type-safe RPC (Remote Procedure Call) interfaces.

### 1. Defining a Protobuf Schema (`protos/currency.proto`)
We define a Protobuf schema file to declare our API structures and service interfaces.

```protobuf
syntax = "proto3";

option go_package = "./protos";

service Currency {
    rpc GetRate(RateRequest) returns (RateResponse);
}

message RateRequest {
    string Base = 1;
    string Destination = 2;
}

message RateResponse {
    double Rate = 1;
}
```

### 2. Compiling Protobuf to Go Code
To compile the schema into Go files, install the Protocol Buffer compiler (`protoc`) and plugins:

```bash
# Install packages
go get google.golang.org/protobuf/cmd/protoc-gen-go
go get google.golang.org/grpc/cmd/protoc-gen-go-grpc

# Execute the compiler
protoc --go_out=. --go-grpc_out=. protos/currency.proto
```

### 3. Implementing the gRPC Service Server
We implement the generated Go interface in our service package.

```go
package server

import (
    "context"
    "log"
    "protos"
)

type Currency struct {
    l *log.Logger
    protos.UnimplementedCurrencyServer
}

func NewCurrency(l *log.Logger) *Currency {
    return &Currency{l: l}
}

func (c *Currency) GetRate(ctx context.Context, req *protos.RateRequest) (*protos.RateResponse, error) {
    c.l.Printf("Received rate request: Base=%s, Dest=%s\n", req.Base, req.Destination)
    
    // Static return rate for demo
    return &protos.RateResponse{Rate: 0.82}, nil
}
```
