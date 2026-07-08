## Chapter 61: gRPC Error Messages in Unary RPCs

<VideoPlayer videoId="9QS33m8vnag" chapter="61" />  
> 🔗 **Source Code:** [GitHub - Episode 18 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_18)

Standard Go errors returned over gRPC are serialized as generic internal errors. We use the `status` package to return rich, structured error codes.

### 1. Returning Status Errors from the Server
We construct structured error payloads using standard gRPC codes (such as `InvalidArgument` or `NotFound`) and attach custom error messages.

```go
package server

import (
    "context"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
    "protos"
)

func (c *Currency) GetRate(ctx context.Context, req *protos.RateRequest) (*protos.RateResponse, error) {
    if req.Base == "" || req.Destination == "" {
        // Create error status
        s := status.New(codes.InvalidArgument, "Base and Destination currencies must be specified")
        
        // Attach additional error metadata if needed
        return nil, s.Err()
    }

    return &protos.RateResponse{Rate: 0.82}, nil
}
```

### 2. Parsing Status Errors in the Client
Clients parse errors using `status.FromError` to inspect status codes and handle errors appropriately.

```go
resp, err := client.GetRate(context.Background(), req)
if err != nil {
    // Check if error is a gRPC status error
    s, ok := status.FromError(err)
    if ok {
        // Inspect the status code
        if s.Code() == codes.InvalidArgument {
            log.Println("Invalid parameters sent to server:", s.Message())
        }
    } else {
        log.Println("Generic connection error:", err)
    }
}
```
