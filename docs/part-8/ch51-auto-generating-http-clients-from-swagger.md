## Chapter 51: Auto-Generating HTTP Clients from Swagger

<VideoPlayer videoId="Zn4joNjqBFc" chapter="51" />  
> 🔗 **Source Code:** [GitHub - Episode 8 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_8)

Instead of manually writing HTTP client integrations, we can auto-generate type-safe client wrappers from the Swagger spec using the `swagger` CLI.

### 1. Generating Client Packages
Using the compiled `swagger.yaml` file, execute the following command to generate a Go client:

```bash
# Create client folder
mkdir sdk

# Generate client SDK
swagger generate client -f ./swagger.yaml -A product-api -t ./sdk
```

This command generates a client package with type-safe methods, models, and request parameters mapping directly to your API routes.

### 2. Using the Generated SDK Client
We write a simple program to consume the client, showing how it abstracts HTTP networking into standard Go function calls.

```go
package main

import (
    "fmt"
    "log"
    "github.com/go-openapi/strfmt"
    "sdk/client"
    "sdk/client/products"
)

func main() {
    // Configure client transport address
    cfg := client.DefaultTransportConfig().WithHost("localhost:9090")
    c := client.NewHTTPClientWithConfig(strfmt.Default, cfg)

    // Call the listing endpoint
    params := products.NewListProductsParams()
    resp, err := c.Products.ListProducts(params)
    if err != nil {
        log.Fatal("Request failed: ", err)
    }

    // Access returned objects with compiler-enforced types
    for _, p := range resp.Payload {
        fmt.Printf("Product ID: %d, Name: %s, Price: %.2f\n", p.ID, p.Name, p.Price)
    }
}
```
