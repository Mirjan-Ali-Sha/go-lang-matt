## Chapter 47: RESTful Services — Reading and Writing JSON

<VideoPlayer videoId="UZbHLVsjpF0" chapter="47" />  
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
