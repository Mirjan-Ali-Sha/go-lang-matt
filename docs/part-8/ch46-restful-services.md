## Chapter 46: RESTful Services

<VideoPlayer videoId="eBeqtmrvVpg" chapter="46" />  
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
