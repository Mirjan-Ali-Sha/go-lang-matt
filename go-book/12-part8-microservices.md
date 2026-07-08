# Part VIII — Building Microservices with Go

> A practical, project-based series by **Nic Jackson** (Developer Advocate, HashiCorp) teaching microservice architecture with Go. This series builds a real-world multi-tier microservice application week by week, covering RESTful APIs, gRPC services, file handling, and advanced streaming patterns.

---

## Chapter 44: Introduction to Microservices

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=VzBGi_n65iU)  
> 🔗 **Source Code:** [GitHub - Episode 1 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_1)

Building microservices in Go is supported by the language's high concurrency, small memory footprint, and powerful standard library. We begin by constructing a basic HTTP server using only the standard `net/http` package.

### 1. The Standard HTTP Server
Go provides a robust HTTP server implementation in `net/http`. The most basic server uses `http.HandleFunc` to register a function callback to a path, and `http.ListenAndServe` to bind to an address and start listening.

```go
package main

import (
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
)

func main() {
    // Registering our path handler
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        log.Println("Hello World")
        
        // Reading data from the request body
        d, err := ioutil.ReadAll(r.Body)
        if err != nil {
            // Replying with a standard HTTP error
            http.Error(w, "Oops", http.StatusBadRequest)
            return
        }
        
        // Writing a formatted string back to the client
        fmt.Fprintf(w, "Hello %s", d)
    })

    // Binding to all interfaces on port 9090
    log.Println("Starting server on port 9090...")
    err := http.ListenAndServe(":9090", nil)
    if err != nil {
        log.Fatal(err)
    }
}
```

### 2. Testing the Server
You can run the server using the standard `go run` command:

```bash
go run main.go
```

To test the server, use `curl` to send a POST request containing data in the body:

```bash
curl -v -d "World" http://localhost:9090/
```

### 3. Understanding the Default Serve MUX
*   `http.ListenAndServe(":9090", nil)`: Passing `nil` as the second argument causes the server to use Go's default multiplexer, `http.DefaultServeMux`.
*   `http.HandleFunc` registers handlers to this global `DefaultServeMux`. While convenient, relying on global state is discouraged in production environments due to security risks and testability challenges.


## Chapter 45: Structuring Microservice Code

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=hodOppKJm5Y)  
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


## Chapter 46: RESTful Services

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=eBeqtmrvVpg)  
> 🔗 **Source Code:** [GitHub - Episode 3 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_3)

REST (Representational State Transfer) structures APIs around resources using standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`). We establish our online coffee shop product catalog service using clean JSON models.

### 1. Designing the Product Model (`data/products.go`)
Struct tags (`json:"name"`) configure output keys during JSON serialization. We can omit internal tracking fields from public payloads by utilizing the special field ignore tag (`json:"-"`).

```go
package data

import (
    "encoding/json"
    "io"
    "time"
)

type Product struct {
    ID          int     `json:"id"`
    Name        string  `json:"name"`
    Description string  `json:"description"`
    Price       float32 `json:"price"`
    SKU         string  `json:"sku"`
    CreatedOn   string  `json:"-"`
    UpdatedOn   string  `json:"-"`
    DeletedOn   string  `json:"-"`
}

type Products []*Product

// ToJSON serializes Products to JSON directly onto an io.Writer stream
func (p *Products) ToJSON(w io.Writer) error {
    e := json.NewEncoder(w)
    return e.Encode(p)
}

// Statically defined product catalog
var productList = Products{
    &Product{
        ID:          1,
        Name:        "Latte",
        Description: "Frothy milky coffee",
        Price:       2.45,
        SKU:         "abc323",
        CreatedOn:   time.Now().UTC().String(),
        UpdatedOn:   time.Now().UTC().String(),
    },
    &Product{
        ID:          2,
        Name:        "Espresso",
        Description: "Short and strong coffee without milk",
        Price:       1.99,
        SKU:         "fjd34",
        CreatedOn:   time.Now().UTC().String(),
        UpdatedOn:   time.Now().UTC().String(),
    },
}

func GetProducts() Products {
    return productList
}
```

### 2. JSON Encoding Performance: Encoder vs Marshaller
*   `json.Marshal` buffers the entire serialised data block into RAM, returning a slice of bytes (`[]byte`).
*   `json.NewEncoder(w).Encode(v)` writes the serialized output directly to an open stream (`io.Writer`). This avoids internal buffer allocations, improving speed and scaling efficiently under high throughput.

### 3. Implementing the REST Products Handler (`handlers/products.go`)
We check `r.Method` inside the `ServeHTTP` method to route the request accordingly.

```go
package handlers

import (
    "log"
    "net/http"
    "data"
)

type Products struct {
    l *log.Logger
}

func NewProducts(l *log.Logger) *Products {
    return &Products{l: l}
}

func (p *Products) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if r.Method == http.MethodGet {
        p.getProducts(w, r)
        return
    }

    // Catch-all for unsupported HTTP verbs
    w.WriteHeader(http.StatusMethodNotAllowed)
}

func (p *Products) getProducts(w http.ResponseWriter, r *http.Request) {
    lp := data.GetProducts()
    err := lp.ToJSON(w)
    if err != nil {
        http.Error(w, "Unable to marshal json", http.StatusInternalServerError)
    }
}
```


## Chapter 47: RESTful Services — Reading and Writing JSON

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=UZbHLVsjpF0)  
> 🔗 **Source Code:** [GitHub - Episode 4 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_4)

To support complete CRUD semantics, we implement JSON deserialization, validation, and request routing to handle product updates and additions.

### 1. Parsing Incoming JSON JSON Payload (`data/products.go`)
We define a deserialization function to extract JSON request bodies directly from an `io.Reader` stream.

```go
// FromJSON deserializes the JSON from the reader into the current Product
func (p *Product) FromJSON(r io.Reader) error {
    d := json.NewDecoder(r)
    return d.Decode(p)
}

func AddProduct(p *Product) {
    p.ID = getNextID()
    productList = append(productList, p)
}

func getNextID() int {
    lp := productList[len(productList)-1]
    return lp.ID + 1
}
```

### 2. Manual URL Parameter Parsing and Updates
We parse IDs directly from the path string using standard library tools, validating and updating matching data fields.

```go
func UpdateProduct(id int, p *Product) error {
    pos, err := findProduct(id)
    if err != nil {
        return err
    }
    p.ID = id
    productList[pos] = p
    return nil
}

var ErrProductNotFound = fmt.Errorf("Product not found")

func findProduct(id int) (int, error) {
    for i, p := range productList {
        if p.ID == id {
            return i, nil
        }
    }
    return -1, ErrProductNotFound
}
```

### 3. Products Handler Routing (`handlers/products.go`)
We use regular expressions to parse route variables manually in standard `net/http` handlers.

```go
func (p *Products) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if r.Method == http.MethodGet {
        p.getProducts(w, r)
        return
    }

    if r.Method == http.MethodPost {
        p.addProduct(w, r)
        return
    }

    if r.Method == http.MethodPut {
        // Ex: Expecting "/products/1"
        reg := regexp.MustCompile(`/([0-9]+)`)
        g := reg.FindAllStringSubmatch(r.URL.Path, -1)

        if len(g) != 1 || len(g[0]) != 2 {
            http.Error(w, "Invalid URI", http.StatusBadRequest)
            return
        }

        idString := g[0][1]
        id, _ := strconv.Atoi(idString)

        p.updateProduct(id, w, r)
        return
    }

    w.WriteHeader(http.StatusMethodNotAllowed)
}

func (p *Products) addProduct(w http.ResponseWriter, r *http.Request) {
    prod := &data.Product{}
    err := prod.FromJSON(r.Body)
    if err != nil {
        http.Error(w, "Failed to decode product", http.StatusBadRequest)
        return
    }
    data.AddProduct(prod)
}

func (p *Products) updateProduct(id int, w http.ResponseWriter, r *http.Request) {
    prod := &data.Product{}
    err := prod.FromJSON(r.Body)
    if err != nil {
        http.Error(w, "Failed to decode product", http.StatusBadRequest)
        return
    }

    err = data.UpdateProduct(id, prod)
    if err == data.ErrProductNotFound {
        http.Error(w, "Product not found", http.StatusNotFound)
        return
    }

    if err != nil {
        http.Error(w, "Product update failed", http.StatusInternalServerError)
        return
    }
}
```


## Chapter 48: The Gorilla Framework

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=DD3JlT_u0DM)  
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


## Chapter 49: JSON Validation

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=gE8_-8KoOLc)  
> 🔗 **Source Code:** [GitHub - Episode 6 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_6)

Validating input prevents corruption and security vulnerabilities. We integrate the `go-playground/validator` package to enforce struct parameters declaratively.

### 1. Declaring Validation Tags on the Model (`data/products.go`)
We assign validation tags (such as `required`, `gt`, and custom tags) to the fields of our `Product` struct.

```go
package data

import (
    "regexp"
    "github.com/go-playground/validator/v10"
)

type Product struct {
    ID          int     `json:"id"`
    Name        string  `json:"name" validate:"required"`
    Description string  `json:"description"`
    Price       float32 `json:"price" validate:"gt=0"`
    SKU         string  `json:"sku" validate:"required,sku"`
}

// Validate executes struct tag rules against the object instance
func (p *Product) Validate() error {
    validate := validator.New()
    validate.RegisterValidation("sku", validateSKU)
    return validate.Struct(p)
}

// Custom validator implementing validator.Func
func validateSKU(fl validator.FieldLevel) bool {
    re := regexp.MustCompile(`^[a-z]+-[a-z]+-[a-z]+$`)
    matches := re.FindAllString(fl.Field().String(), -1)
    return len(matches) == 1
}
```

### 2. Validation Execution in Gorilla Middleware
We implement a middleware pattern to parse and validate incoming payloads before they reach the handler logic.

```go
// MiddlewareProductValidation validates the product in the request body
func (p *Products) MiddlewareProductValidation(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        prod := &data.Product{}

        err := prod.FromJSON(r.Body)
        if err != nil {
            http.Error(w, "Error reading product", http.StatusBadRequest)
            return
        }

        // Validate product
        err = prod.Validate()
        if err != nil {
            http.Error(w, fmt.Sprintf("Error validating product: %s", err), http.StatusBadRequest)
            return
        }

        // Add the product to the context
        ctx := context.WithValue(r.Context(), KeyProduct{}, prod)
        r = r.WithContext(ctx)

        // Call the next handler
        next.ServeHTTP(w, r)
    })
}
```


## Chapter 50: Swagger Documentation

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=07XhTqE-j8k)  
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


## Chapter 51: Auto-Generating HTTP Clients from Swagger

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=Zn4joNjqBFc)  
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


## Chapter 52: CORS — Cross-Origin Resource Sharing

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=RlYoy_RiYPw)  
> 🔗 **Source Code:** [GitHub - Episode 9 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_9)

Web browsers enforce CORS (Cross-Origin Resource Sharing) security policies to block client scripts on one origin from accessing resources on another. We configure CORS support in our service using standard Gorilla middleware.

### 1. Understanding CORS Headers
*   `Access-Control-Allow-Origin`: Defines which client domains are permitted to retrieve data.
*   `Access-Control-Allow-Methods`: Lists approved request verbs (`GET`, `POST`, `PUT`, etc.).
*   `Access-Control-Allow-Headers`: Approves custom headers (such as `Content-Type` or `Authorization`).

### 2. Implementing CORS Middleware
Using the `github.com/gorilla/handlers` package, we wrap our main server router to configure allowed origins, headers, and HTTP methods.

```go
package main

import (
    "net/http"
    "os"
    "github.com/gorilla/handlers"
    "github.com/gorilla/mux"
)

func main() {
    sm := mux.NewRouter()

    // Configure CORS origins and parameters
    ch := handlers.CORS(
        handlers.AllowedOrigins([]string{"http://localhost:3000"}),
        handlers.AllowedHeaders([]string{"X-Requested-With", "Content-Type", "Authorization"}),
        handlers.AllowedMethods([]string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}),
    )

    // Wrap the router with the CORS middleware
    server := &http.Server{
        Addr:    ":9090",
        Handler: ch(sm),
    }

    server.ListenAndServe()
}
```


## Chapter 53: Handling Files with the Go Standard Library

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=ctmhYJpGsgU)  
> 🔗 **Source Code:** [GitHub - Episode 10 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_10)

Microservice architectures separate responsibilities. We construct a dedicated file storage service to handle, store, and serve image uploads independently of the primary database logic.

### 1. Writing the File Store Utility (`files/local.go`)
We implement a local file storage utility that creates path directories dynamically and writes file streams to disk safely.

```go
package files

import (
    "io"
    "os"
    "path/filepath"
)

type Local struct {
    maxFileSize int
    basePath    string
}

func NewLocal(basePath string, maxFileSize int) (*Local, error) {
    return &Local{basePath: basePath, maxFileSize: maxFileSize}, nil
}

func (l *Local) Save(path string, r io.Reader) error {
    // Construct target file path
    fp := filepath.Join(l.basePath, path)
    
    // Ensure parent directories exist
    err := os.MkdirAll(filepath.Dir(fp), os.ModePerm)
    if err != nil {
        return err
    }

    // If file exists, delete it first
    os.Remove(fp)

    // Create target file
    f, err := os.Create(fp)
    if err != nil {
        return err
    }
    defer f.Close()

    // Stream write from reader
    _, err = io.Copy(f, r)
    return err
}
```

### 2. Designing the File Upload Handler (`handlers/files.go`)
We define a handler to handle HTTP PUT requests containing raw file streams.

```go
package handlers

import (
    "net/http"
    "path/filepath"
    "files"
)

type Files struct {
    store files.Storage
}

func NewFiles(s files.Storage) *Files {
    return &Files{store: s}
}

func (f *Files) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Extract file name from URL path
    fn := filepath.Base(r.URL.Path)
    if fn == "." || fn == "/" {
        http.Error(w, "Invalid filename", http.StatusBadRequest)
        return
    }

    // Save the file stream directly from r.Body
    err := f.store.Save(fn, r.Body)
    if err != nil {
        http.Error(w, "Failed to save file", http.StatusInternalServerError)
        return
    }

    w.Write([]byte("File uploaded successfully"))
}
```


## Chapter 54: HTTP Multi-Part Requests

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=_7-IhHMptNo)  
> 🔗 **Source Code:** [GitHub - Episode 11 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_11)

Raw PUT streams only upload one file at a time. To support complex form submissions (like metadata alongside files), we implement multi-part form handling.

### 1. Reading Multi-Part Payloads
Instead of caching the entire payload in RAM, we stream parts sequentially using Go's `mime/multipart` package.

```go
package handlers

import (
    "io"
    "net/http"
    "files"
)

type Multipart struct {
    store files.Storage
}

func (mp *Multipart) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Parse the multipart form, allocating max 2MB in memory buffer
    err := r.ParseMultipartForm(128 * 1024 * 1024) // 128MB max payload
    if err != nil {
        http.Error(w, "Expected multipart form data", http.StatusBadRequest)
        return
    }

    // Retrieve form text field
    idStr := r.FormValue("id")
    
    // Retrieve the file header
    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "Missing file payload", http.StatusBadRequest)
        return
    }
    defer file.Close()

    // Save the file using our storage utility
    err = mp.store.Save(header.Filename, file)
    if err != nil {
        http.Error(w, "Failed to save file", http.StatusInternalServerError)
        return
    }

    w.Write([]byte("Successfully saved part: " + header.Filename))
}
```


## Chapter 55: Gzip Compression for HTTP Responses

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=GtSg1H7SU5Y)  
> 🔗 **Source Code:** [GitHub - Episode 12 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_12)

Compressing text payloads (like JSON) reduces bandwidth usage and improves transfer speeds. We implement a Gzip middleware using Go's `compress/gzip` package.

### 1. Creating a Gzip response writer wrapper
To support compression, we wrap `http.ResponseWriter` in a custom struct that intercepts writes and redirects them through a `gzip.Writer`.

```go
package middleware

import (
    "compress/gzip"
    "io"
    "net/http"
)

type GzipResponseWriter struct {
    gw  *gzip.Writer
    w   http.ResponseWriter
}

func NewGzipResponseWriter(w http.ResponseWriter) *GzipResponseWriter {
    gw := gzip.NewWriter(w)
    return &GzipResponseWriter{gw: gw, w: w}
}

func (grw *GzipResponseWriter) Header() http.Header {
    return grw.w.Header()
}

func (grw *GzipResponseWriter) WriteHeader(statusCode int) {
    grw.w.WriteHeader(statusCode)
}

func (grw *GzipResponseWriter) Write(b []byte) (int, error) {
    return grw.gw.Write(b)
}

func (grw *GzipResponseWriter) Flush() {
    grw.gw.Close()
}
```

### 2. The Gzip Middleware
The middleware intercepts requests, checks the client's `Accept-Encoding` header for Gzip support, and wraps the response writer accordingly.

```go
func GzipMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Check client support for gzip
        if !strings.Contains(r.Header.Get("Accept-Encoding"), "gzip") {
            next.ServeHTTP(w, r)
            return
        }

        // Prepare compression headers
        w.Header().Set("Content-Encoding", "gzip")
        
        gWriter := NewGzipResponseWriter(w)
        defer gWriter.Flush()

        // Execute handler chain using our compressed writer
        next.ServeHTTP(gWriter, r)
    })
}
```


## Chapter 56: Introduction to gRPC and Protocol Buffers

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=pMgty_RYIOc)  
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


## Chapter 57: gRPC Client Connections

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=oTBcd5J0VYU)  
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


## Chapter 58: Refactoring the Codebase

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=Vl88R9acq-Y)  
> 🔗 **Source Code:** [GitHub - Episode 15 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_15)

To prepare our project for containerization and deployment, we refactor it into separate microservice modules.

### 1. Monorepo vs Multi-module Structure
*   **Monolith structure**: A single package where all services share imports and build configurations.
*   **Multi-module structure**: Separate root folders, each with its own `go.mod` file. This allows services to manage their dependencies and scale independently.

```text
building-microservices/
├── currency/
│   ├── go.mod
│   ├── main.go
│   └── server/
├── product-api/
│   ├── go.mod
│   ├── main.go
│   └── handlers/
└── sdk/
```

### 2. Managing Dependencies and Module Scopes
When working with multiple modules, you can use Go workspace config files (`go.work`) or local module replacements in your `go.mod` file to resolve local imports during development:

```text
// product-api/go.mod
module product-api

go 1.20

replace github.com/nicholasjackson/protos => ../protos
```


## Chapter 59: gRPC Bi-Directional Streaming — Part 1

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=4ohwkWVgEZM)  
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


## Chapter 60: gRPC Bi-Directional Streaming — Part 2

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=MT5tXSKa-KY)  
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


## Chapter 61: gRPC Error Messages in Unary RPCs

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=9QS33m8vnag)  
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


## Chapter 62: gRPC Error Handling in Bidirectional Streams

> 🎥 **Lecture Video:** [Watch on YouTube](https://www.youtube.com/watch?v=IT4OfN27D4c)  
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

