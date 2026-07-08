## Chapter 49: JSON Validation

<VideoPlayer videoId="gE8_-8KoOLc" chapter="49" />  
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
