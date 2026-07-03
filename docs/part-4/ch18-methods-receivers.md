## Chapter 18: Methods & Receivers

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-18-methods-interfaces-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-18-methods-interfaces-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="W3ZWbhQF6wg" chapter="18" />

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
