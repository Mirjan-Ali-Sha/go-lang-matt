## Chapter 12: Structs, Struct tags & JSON

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-12-structs-json-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-12-structs-json-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="0m6iFd9N_CY" chapter="12" />

In this segment, we are going to look at structs in more detail, how we can declare them, how pointers interact with structs, and then how we can use them to serialize and deserialize data to and from JSON using struct tags.

### Struct Basics

A struct is a sequence of named fields of specific types. It is a way of grouping related data together into a single, cohesive unit.

```go
type Employee struct {
    ID        int
    Name      string
    Address   string
    Position  string
    Salary    int
}
```

We can create an instance of a struct using a struct literal:

```go
// Using field names (recommended)
emp := Employee{
    ID:       1,
    Name:     "Alice",
    Position: "Software Engineer",
}

// Positional (not recommended, fragile if fields change)
emp2 := Employee{2, "Bob", "123 Main St", "Manager", 80000}
```

### Structs and Pointers

When you have a pointer to a struct, Go provides syntactic sugar so you don't have to write `(*emp).Name` to access a field. You can simply write `emp.Name`. Go automatically dereferences the pointer for you.

```go
empPtr := &emp
empPtr.Salary = 90000 // Automatically dereferenced under the hood
```

### JSON Serialization & Struct Tags

One of the most common uses of structs in modern Go applications is to represent JSON objects. Go's standard library provides the `encoding/json` package to convert structs to JSON (**marshaling**) and JSON back to structs (**unmarshaling**).

To map struct fields to specific JSON keys, we use **struct tags**:

```go
type User struct {
    ID       int    `json:"id"`
    Username string `json:"username"`
    Email    string `json:"email,omitempty"`
    Password string `json:"-"` // Ignored by JSON encoder
}
```

- **Field visibility:** Struct fields must be **exported** (start with an uppercase letter) for the JSON encoder/decoder to see them. If a field starts with a lowercase letter, it is private to the package and will be ignored by `encoding/json`.
- **`omitempty`:** If a field has the `omitempty` tag and contains its zero value (like `0`, `""`, `nil`, or `false`), it will be omitted from the generated JSON output.
- **`-`:** The hyphen tag tells the encoder to always skip this field.

```go
// Marshaling (Struct -> JSON bytes)
u := User{ID: 1, Username: "bob"}
data, err := json.Marshal(u)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data)) // {"id":1,"username":"bob"} (Email omitted, Password skipped)
```

```go
// Unmarshaling (JSON bytes -> Struct)
rawJSON := []byte(`{"id":2,"username":"alice","email":"alice@example.com"}`)
var alice User
if err := json.Unmarshal(rawJSON, &alice); err != nil {
    log.Fatal(err)
}
fmt.Printf("%+v\n", alice)
```

> ⚠️ **Pointer Requirement:** You must pass a **pointer** to `json.Unmarshal` (e.g., `&alice`) so that the function can modify the struct's fields. If you pass it by value, the function receives a copy, updates the copy, and the original remains unchanged.

---
