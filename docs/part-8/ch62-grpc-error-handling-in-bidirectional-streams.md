## Chapter 62: gRPC Error Handling in Bidirectional Streams

<VideoPlayer videoId="IT4OfN27D4c" chapter="62" />  
> 🔗 **Source Code:** [GitHub - Episode 19 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_19)

Error handling inside persistent streams requires care, as returning an error terminates the connection. We handle stream errors gracefully to prevent connections from dropping unexpectedly.

### 1. Propagating Validation Errors Without Closing Streams
Instead of returning a terminal gRPC error, we can include validation status fields inside our response messages, allowing the stream to remain open.

```protobuf
message RateResponse {
    double Rate = 1;
    string ErrorMessage = 2; // Optional error messages
}
```

### 2. Implementing Server-Side Error Handling
We catch invalid inputs, format validation errors, and send them back to the client without terminating the stream loop.

```go
func (c *Currency) SubscribeRates(stream protos.Currency_SubscribeRatesServer) error {
    for {
        req, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }

        // Validate request parameters without breaking the stream loop
        if req.Base == "" {
            resp := &protos.RateResponse{
                Rate:         0,
                ErrorMessage: "Currency base must not be empty",
            }
            stream.Send(resp)
            continue
        }

        // Send normal response
        stream.Send(&protos.RateResponse{Rate: 0.82})
    }
}
```
