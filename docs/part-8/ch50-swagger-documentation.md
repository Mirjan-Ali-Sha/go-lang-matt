## Chapter 50: Swagger Documentation

<VideoPlayer videoId="07XhTqE-j8k" chapter="50" />  
> 🔗 **Source Code:** [GitHub - Episode 7 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_7)

APIs are only useful if they are documented. OpenAPI/Swagger standardizes API specifications, and the `go-swagger` tool allows us to generate docs directly from Go source comments.

### 1. Writing Swagger Annotations
We document API metadata, request models, parameters, and routes directly in our Go source files using comments.

#### Documenting the Server Configuration (`handlers/docs.go`)
```go
// Package classification Product API
//
// Documentation for Product API
//
//  Schemes: http
//  Host: localhost
//  BasePath: /
//  Version: 1.0.0
//
//  Consumes:
//  - application/json
//
//  Produces:
//  - application/json
//
// swagger:meta
package handlers
```

#### Documenting Request and Response Payload Structures
```go
// A list of products returned in the response
// swagger:response productsResponse
type productsResponseWrapper struct {
    // All products in the system
    // in: body
    Body []data.Product
}

// swagger:parameters updateProduct
type productIDParameterWrapper struct {
    // The id of the product to update
    // in: path
    // required: true
    ID int `json:"id"`
}
```

### 2. Generating the Swagger Spec
Install the `go-swagger` tool and run the generation command inside the project root:

```bash
# Generate the swagger spec file
swagger generate spec -o ./swagger.yaml
```

### 3. Serving the Documentation UI
We can serve the Swagger documentation UI (Redoc) directly using the standard `github.com/go-openapi/runtime/middleware` package:

```go
import "github.com/go-openapi/runtime/middleware"

func main() {
    // ...
    sm := mux.NewRouter()
    
    // Serve the swagger spec file
    sm.Handle("/swagger.yaml", http.FileServer(http.Dir("./")))
    
    // Serve Redoc UI pointing to the spec
    opts := middleware.RedocOpts{SpecURL: "/swagger.yaml"}
    sh := middleware.Redoc(opts, nil)
    sm.Handle("/docs", sh)
}
```
