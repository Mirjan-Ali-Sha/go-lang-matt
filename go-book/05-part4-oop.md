# Part IV — Object-Oriented Programming in Go

---

## Chapter 17: Go does OOP

> 📊 **Slide Reference:** `slides/go-17-go-oop-slides.pdf`

Object-oriented programming (OOP) is often defined in textbooks as the combination of four core features:
1. **Abstraction**
2. **Encapsulation**
3. **Polymorphism**
4. **Inheritance**

While Go supports the first three features, it completely lacks the fourth: **inheritance**. In this chapter, we explore how Go manages to be a powerful object-oriented language without classes or type hierarchies.

### Abstraction & Encapsulation

**Abstraction** is the logical simplification of a system. A classic example is the file system API: we want to open, read, and write files without worrying about OS buffers, page boundaries, or magnetic sector layouts.

**Encapsulation** is the physical enforcement of abstraction by hiding internal details. In Go, encapsulation is package-level and controlled by capitalization:
- Identifiers starting with an **uppercase letter** (e.g., `ExportedType`, `Field`) are visible to other packages.
- Identifiers starting with a **lowercase letter** (e.g., `internalField`, `privateStruct`) are hidden, protecting the package’s internal state from external tampering.

### Polymorphism

Polymorphism ("many shapes") allows a single interface to represent multiple underlying concrete types. There are several forms of polymorphism:
1. **Ad-hoc Polymorphism:** Function overloading or operator overloading (not supported in Go).
2. **Parametric Polymorphism:** Generics (type parameters, supported in Go 1.18+).
3. **Subtype Polymorphism:** Class inheritance hierarchies where a subclass replaces a superclass (not supported in Go).
4. **Interface Polymorphism:** Also called *protocol-oriented programming*, where types are grouped based on what they can *do* (behavior) rather than what they *are* (lineage). This is Go's primary mechanism for polymorphism.

### The Inheritance Tax

Many mainstream languages tie polymorphism directly to class inheritance. However, inheritance can lead to fragile, bloated systems:
- **Tight Coupling:** Subclasses often depend on the internal details of their superclasses. Changing a superclass can break subclasses unexpectedly.
- **Deep Hierarchies:** Deep, parallel inheritance hierarchies are notoriously hard to reason about.
- **Leaky Abstractions:** Subtyping can force child types to inherit behaviors that do not make sense for them (e.g., a `Line` class inheriting from `Shape` but having to panic or return zero for a `.Area()` method).

Because of these pitfalls, the software engineering industry has moved toward the mantra: **"Prefer composition over inheritance."**

### Alan Kay's Vision of OOP

Alan Kay, who coined the term "object-oriented programming" and developed Smalltalk, wrote in the late 1990s about his original vision:

> "I'm sorry that I long ago coined the term 'objects' for this topic because it gets many people to focus on the lesser idea. The big idea is 'messaging'..."
>
> Kay’s core pillars:
> 1. Message passing (dynamic dispatch).
> 2. Local retention and protection of state (encapsulation).
> 3. Extreme late-binding of all things.

Notice that classes and inheritance are completely absent from this list. Go adheres closely to this philosophy: objects have protected state, communicate via methods, and establish relationships dynamically through interfaces.

In Go:
- **There are no classes.** There are only types.
- **There is no inheritance.** There is only composition.
- **Methods can be defined on any user-declared type**—not just structs. You can add methods to strings, integers, slices, and even functions.

---

## Chapter 18: Methods & Receivers

> 📊 **Slide Reference:** `slides/go-18-methods-interfaces-slides.pdf`

A **method** is a function with an implicit extra parameter called the **receiver**, which is declared before the function name. Go's method syntax was inspired by the Oberon-2 programming language.

### Defining Methods

Unlike languages where methods must be declared inside a class block, Go methods are declared at the package level alongside the type definition.

```go
package main

import (
    "fmt"
    "strconv"
    "strings"
)

// A user-declared named type whose underlying type is a slice of ints
type IntSlice []int

// String implements the fmt.Stringer interface for IntSlice
func (s IntSlice) String() string {
    var parts []string
    for _, val := range s {
        parts = append(parts, strconv.Itoa(val))
    }
    return strings.Join(parts, "; ")
}

func main() {
    v := IntSlice{3, 5, 7, 11}
    // fmt.Println automatically checks if the type implements fmt.Stringer
    fmt.Println(v) // Output: 3; 5; 7; 11
}
```

### Value Receivers vs. Pointer Receivers

When declaring a method, you must choose between a **value receiver** and a **pointer receiver**. This choice matches the value and reference semantics discussed in Chapter 14.

| Receiver Type | Signature Example | Behavior |
| :--- | :--- | :--- |
| **Value Receiver** | `func (p Point) Offset(x, y float64)` | Receives a **copy** of the object. Modifications do not affect the caller. |
| **Pointer Receiver** | `func (p *Point) Move(x, y float64)` | Receives a **pointer** to the object. Modifications affect the original object. |

```go
type Point struct {
    X, Y float64
}

// Value receiver: copy-by-value
func (p Point) Offset(dx, dy float64) Point {
    p.X += dx
    p.Y += dy
    return p
}

// Pointer receiver: mutates in-place
func (p *Point) Move(dx, dy float64) {
    p.X += dx
    p.Y += dy
}
```

### Compiler Syntactic Sugar

Go provides syntactic sugar so you don't have to manually dereference pointers or take addresses when calling methods.

```go
p := Point{1, 2}
pPtr := &p

// 1. Calling a value receiver method on a pointer:
// Go automatically dereferences pPtr -> (*pPtr).Offset(...)
pPtr.Offset(3, 4)

// 2. Calling a pointer receiver method on a value:
// Go automatically takes the address of p -> (&p).Move(...)
p.Move(5, 6)
```

This automatic referencing only works if the value is **addressable** (i.e., it is stored in a variable, slice element, or struct field). It does not work for temporary values or literals (see Chapter 20).

### The Distancer Interface Example

Let's look at a concrete example using lines and paths to demonstrate how multiple types satisfy a common interface.

```go
package main

import (
    "fmt"
    "math"
)

type Point struct {
    X, Y float64
}

type Line struct {
    Begin, End Point
}

// Distance calculates the length of a straight line (value receiver)
func (l Line) Distance() float64 {
    return math.Hypot(l.End.X-l.Begin.X, l.End.Y-l.Begin.Y)
}

type Path []Point

// Distance calculates the cumulative length of all path segments
func (p Path) Distance() float64 {
    sum := 0.0
    for i := 1; i < len(p); i++ {
        // Construct line segments on the fly
        sum += Line{p[i-1], p[i]}.Distance()
    }
    return sum
}

// Define the consumer-side interface
type Distancer interface {
    Distance() float64
}

func PrintDistance(d Distancer) {
    fmt.Printf("Distance: %.2f\n", d.Distance())
}

func main() {
    l := Line{Point{0, 0}, Point{3, 4}}
    path := Path{
        Point{0, 0},
        Point{3, 0},
        Point{3, 4},
    }

    PrintDistance(l)    // Distance: 5.00
    PrintDistance(path) // Distance: 7.00
}
```

Both `Line` and `Path` implicitly satisfy the `Distancer` interface because they implement the `Distance()` method. There is no `implements` keyword; interface satisfaction is resolved structurally by the compiler.

---

## Chapter 19: Struct Composition

> 📊 **Slide Reference:** `slides/go-19-composition-slides.pdf`

Go supports **composition** through struct embedding. By nesting a type inside a struct without giving it a field name, we embed the type.

### Field & Method Promotion

When a type is embedded, its fields and methods are **promoted** to the outer struct, meaning they can be accessed directly without chaining selectors.

```go
type Pair struct {
    Path string
    Hash string
}

func (p Pair) String() string {
    return fmt.Sprintf("%s (%s)", p.Path, p.Hash)
}

// PairWithLength embeds Pair
type PairWithLength struct {
    Pair   // Anonymous/embedded field
    Length int
}
```

For literals, you must still initialize the inner type explicitly:
```go
pl := PairWithLength{
    Pair:   Pair{Path: "/etc/passwd", Hash: "abc123d"},
    Length: 45,
}
```

However, access to fields and methods is promoted:
```go
// Direct field access (promoted)
fmt.Println(pl.Path) // Instead of pl.Pair.Path

// Direct method access (promoted)
fmt.Println(pl.String()) // Output: /etc/passwd (abc123d)
```

### Composition is NOT Inheritance

While promotion resembles subclassing, **composition is not inheritance**. The outer struct is not a subtype of the embedded struct.

```go
func InspectPair(p Pair) {
    fmt.Println(p.Path)
}

// This will fail to compile:
// InspectPair(pl) // PairWithLength is not a Pair!

// To make it work, you must pass the embedded field explicitly:
InspectPair(pl.Pair)
```

If we define a custom `String()` method on `PairWithLength`, it shadows the promoted method:
```go
func (pl PairWithLength) String() string {
    return fmt.Sprintf("%s [%d bytes]", pl.Pair.String(), pl.Length)
}
```
Now, `pl.String()` calls the outer method, which calls `pl.Pair.String()` internally.

### Interface Composition

Interfaces can also embed other interfaces. This is how Go encourages the creation of small, modular APIs.

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// ReadWriter is the composition of Reader and Writer
type ReadWriter interface {
    Reader
    Writer
}
```

### The Organs Sorting Example

Go's standard `sort` package is designed around composition. To sort any slice, it must satisfy `sort.Interface`:

```go
type Interface interface {
    Len() int
    Less(i, j int) bool
    Swap(i, j int)
}
```

We can use struct embedding to sort the same data using different comparison strategies:

```go
package main

import (
    "fmt"
    "sort"
)

type Organ struct {
    Name   string
    Weight int
}

type Organs []Organ

func (s Organs) Len() int           { return len(s) }
func (s Organs) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }

// byName embeds Organs to reuse Len and Swap, but overrides Less
type byName struct{ Organs }
func (s byName) Less(i, j int) bool { return s.Organs[i].Name < s.Organs[j].Name }

// byWeight embeds Organs to reuse Len and Swap, but overrides Less
type byWeight struct{ Organs }
func (s byWeight) Less(i, j int) bool { return s.Organs[i].Weight < s.Organs[j].Weight }

func main() {
    list := Organs{
        {"Brain", 1400},
        {"Heart", 300},
        {"Liver", 1500},
    }

    // Sort by Weight
    sort.Sort(byWeight{list})
    fmt.Println("By weight:", list)

    // Sort by Name
    sort.Sort(byName{list})
    fmt.Println("By name:", list)
}
```

### Making Nil Useful: The Linked List Example

In Go, methods can be called on `nil` receivers. This allows us to write elegant, safe recursive logic without needing defensive `nil` checks at the call site.

```go
package main

import "fmt"

type Node struct {
    Value int
    Next  *Node
}

// Sum calculates the sum of this node and all subsequent nodes.
// Calling this on a nil pointer is perfectly safe.
func (n *Node) Sum() int {
    if n == nil {
        return 0
    }
    return n.Value + n.Next.Sum()
}

func main() {
    // Build a linked list: 1 -> 2 -> 3 -> nil
    list := &Node{1, &Node{2, &Node{3, nil}}}
    fmt.Println(list.Sum()) // Output: 6

    var emptyList *Node
    fmt.Println(emptyList.Sum()) // Output: 0 (No crash!)
}
```

---

## Chapter 20: Reader, Writer & Interface Details

> 📊 **Slide Reference:** `slides/go-20-interfaces-details-slides.pdf`

To write high-quality Go code, you must understand how interfaces are represented in memory and how to navigate method set constraints.

### Under the Hood: The Interface Descriptor

An interface variable is not a simple pointer. It is represented as a two-pointer descriptor:
1. **Type Pointer (`tab`):** Points to the concrete type information (metadata, method table).
2. **Value Pointer (`data`):** Points to the actual concrete value.

```
Interface Variable
+-------+-------+
|  tab  | data  |
+-------+-------+
    |       |
    v       v
 [Type]  [Value]
```

An interface is only considered `nil` if **both** the type pointer and the value pointer are `nil`.

#### The Nil Pointer Gotcha

This design leads to a common, subtle bug where a concrete `nil` pointer is wrapped in an interface, making the interface itself **non-nil**:

```go
package main

import "fmt"

type CustomError struct {
    Msg string
}

func (e *CustomError) Error() string {
    return e.Msg
}

// Returns a concrete pointer type
func returnsConcreteError() *CustomError {
    return nil // concrete nil pointer
}

func main() {
    var err error // interface type
    err = returnsConcreteError()

    // err is NOT nil! 
    // The type pointer points to *CustomError, even though the value pointer is nil.
    if err != nil {
        fmt.Println("Error detected (Oops!):", err) // Output: Error detected (Oops!): <nil>
    }
}
```

**The Fix:** Always return the generic `error` interface directly instead of concrete error pointers:

```go
func returnsInterfaceError() error {
    return nil // returns nil interface directly
}
```

### Method Set Rules: L-Values and R-Values

In programming, we refer to:
- **L-Values (Left values):** Variables that are **addressable** in memory (they have a specific location).
- **R-Values (Right values):** Temporary values or literal expressions (they do not have a fixed address).

Go determines method sets based on addressability:
1. **Value receivers** accept both values and pointers.
2. **Pointer receivers** accept **only pointers** or **addressable values** (which the compiler can automatically take the address of).

You cannot call a pointer receiver method on an R-value literal:

```go
type IntSet struct{}
func (s *IntSet) String() string { return "{}" }

// This will fail to compile:
// _ = IntSet{}.String() // Error: cannot call pointer method on IntSet literal (non-addressable)

// The Fix:
s := IntSet{} // s is an L-value variable (addressable)
_ = s.String() // Complies: compiler automatically rewrites to (&s).String()
```

### API Design: Accept Interfaces, Return Concrete Types

A key tenet of Go architecture is:
> **"Accept interfaces, return concrete types."**
> *(This is Go's version of Postel's Law: "Be conservative in what you send, be liberal in what you accept.")*

1. **Parameters (Accept Interfaces):** Keep inputs as abstract and minimal as possible. If your function only needs to read bytes, accept an `io.Reader`. This allows callers to pass in files, network sockets, or in-memory buffers interchangeably.
2. **Return Values (Return Concrete Types):** Keep outputs concrete. If you return an interface, you force the caller into a narrow set of methods. Returning a concrete type (like `*os.File`) gives the caller the freedom to use all of its methods (like `.Stat()`, `.Seek()`), or implicitly assign it to interfaces like `io.Reader` or `io.Writer` as needed.

### The Empty Interface: `interface{}` (`any`)

An interface with an empty method set is satisfied by any type:
```go
type any = interface{}
```

Because it defines no behavior, you cannot call any methods on an `any` variable directly. You must use **type assertions** or **reflection** to inspect and extract the underlying concrete value.

---

## Chapter 21: Homework — E-Commerce Web Server

> 📊 **Slide Reference:** `slides/go-21-hw4-slides.pdf`

In this homework, we implement Exercise 7.11 from *The Go Programming Language* book. We build a simple web database server for a store, implementing listing, reading, creating, updating, and deleting items.

### Implementation

We define a custom type `database` wrapping a map, and use **method values** to register handlers.

```go
package main

import (
    "fmt"
    "log"
    "net/http"
    "strconv"
)

type dollars float64

func (d dollars) String() string {
    return fmt.Sprintf("$%.2f", d)
}

type database map[string]dollars

// /list
func (db database) list(w http.ResponseWriter, req *http.Request) {
    for item, price := range db {
        fmt.Fprintf(w, "%s: %s\n", item, price)
    }
}

// /read?item=shoes
func (db database) read(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    price, ok := db[item]
    if !ok {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }
    fmt.Fprintf(w, "%s: %s\n", item, price)
}

// /create?item=shoes&price=50
func (db database) create(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    if _, exists := db[item]; exists {
        http.Error(w, fmt.Sprintf("duplicate item: %q", item), http.StatusBadRequest)
        return
    }

    price, err := strconv.ParseFloat(priceStr, 64)
    if err != nil {
        http.Error(w, fmt.Sprintf("invalid price: %q", priceStr), http.StatusBadRequest)
        return
    }

    db[item] = dollars(price)
    fmt.Fprintf(w, "added %s with price %s\n", item, db[item])
}

// /update?item=shoes&price=55
func (db database) update(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    priceStr := req.URL.Query().Get("price")

    if _, exists := db[item]; !exists {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }

    price, err := strconv.ParseFloat(priceStr, 64)
    if err != nil {
        http.Error(w, fmt.Sprintf("invalid price: %q", priceStr), http.StatusBadRequest)
        return
    }

    db[item] = dollars(price)
    fmt.Fprintf(w, "updated %s to %s\n", item, db[item])
}

// /delete?item=shoes
func (db database) delete(w http.ResponseWriter, req *http.Request) {
    item := req.URL.Query().Get("item")
    if _, exists := db[item]; !exists {
        http.Error(w, fmt.Sprintf("no such item: %q", item), http.StatusNotFound)
        return
    }
    delete(db, item)
    fmt.Fprintf(w, "deleted item: %q\n", item)
}

func main() {
    db := database{"shoes": 50, "socks": 5}

    // Using method values (db.list, db.read, etc.)
    // These close over the db map descriptor receiver.
    http.HandleFunc("/list", db.list)
    http.HandleFunc("/read", db.read)
    http.HandleFunc("/create", db.create)
    http.HandleFunc("/update", db.update)
    http.HandleFunc("/delete", db.delete)

    fmt.Println("Server listening on :8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### Concurrency Warning

Go's built-in web server executes handlers concurrently on separate goroutines. Since maps in Go are **not safe for concurrent read and write operations**, concurrent access to the `db` map (e.g., calling `/create` and `/list` simultaneously) will result in a fatal runtime panic: `fatal error: concurrent map writes`.

We will address how to safely synchronize this shared state in Part V.
