## Chapter 42: Parametric Polymorphism (Generics)

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-42-parametric-polymorphism-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-42-parametric-polymorphism-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="Si0rAE8yT9g" chapter="42" />

Generics in Go represent the concept of **Parametric Polymorphism**. They allow you to write algorithms and data structures where the types of variables are parameters.

### 1. Types of Polymorphism
- **Inheritance Polymorphism:** Common in class-based languages (like Java/C++), where one type derives from another and inherits its behavior. Go does not support class inheritance.
- **Ad hoc Polymorphism:** Function overloading, where multiple functions share the same name but accept different parameters. Go does not support function overloading.
- **Parametric Polymorphism (Generics):** Types or functions are parameterised with a type argument. You define a template, and the compiler generates concrete type implementations at compile time.

---

### 2. Syntax: Why Square Brackets?

While C++, Java, and C# use angle brackets (e.g., `List<T>`), Go uses **square brackets** (e.g., `Vector[T]`). 

During language design, using angle brackets (`<` and `>`) proved parsing-ambiguous for Go's fast single-pass compiler. For instance, in an expression like `a, b = w<x, y>(z)`, it is ambiguous whether `<` is a less-than comparison or the start of a generic parameter list. Parentheses were trialed but rejected for readability (avoiding Lisp-like parenthetical noise). Square brackets resolved both compiler ambiguity and developer readability concerns.

---

### 3. Basic Generic Structs & Methods

To define a generic type, list the type parameters inside square brackets immediately after the type name:

```go
package generics

import "fmt"

// Vector is a generic slice container holding elements of type T.
// 'any' is a built-in constraint that is an alias for 'interface{}'.
type Vector[T any] []T

// Push appends an item of type T to the Vector.
// We receive v as a pointer to allow the underlying slice's header to update.
func (v *Vector[T]) Push(item T) {
    *v = append(*v, item)
}
```

---

### 4. Writing a Generic Map Function

A generic mapping function transforms a slice of source elements of type `F` (From) into a slice of target elements of type `T` (To) using a mapper function:

```go
package main

import (
    "fmt"
    "strconv"
)

// Map transforms a slice from type F to type T.
func Map[F any, T any](s []F, fn func(F) T) []T {
    result := make([]T, len(s))
    for i, v := range s {
        result[i] = fn(v)
    }
    return result
}

func main() {
    ints := []int{1, 2, 3}

    // Example 1: Explicit instantiation of type parameters
    strsExplicit := Map[int, string](ints, func(x int) string {
        return strconv.Itoa(x)
    })
    fmt.Printf("Explicit: %#v\n", strsExplicit)

    // Example 2: Implicit compiler type inference
    // Because the arguments are concrete, the compiler infers F = int and T = string.
    // The type parameters [int, string] can be omitted at the call site.
    strsImplicit := Map(ints, func(x int) string {
        return strconv.Itoa(x)
    })
    fmt.Printf("Implicit: %#v\n", strsImplicit)
}
```

> [!NOTE]
> During type inference, the compiler only analyzes function input arguments. Return type variables cannot be used to infer type parameters.

---

### 5. Constraints & Custom Interfaces

Sometimes we need to restrict type arguments. For example, if we want to print elements in a generic container, we can constrain the parameter type `T` to types that implement the standard `fmt.Stringer` interface.

```go
package main

import (
    "fmt"
    "strconv"
    "strings"
)

// MyInt implements the fmt.Stringer interface
type MyInt int

func (i MyInt) String() string {
    return strconv.Itoa(int(i))
}

// StringableVector requires type T to satisfy fmt.Stringer.
// Only types containing a String() string method are accepted.
type StringableVector[T fmt.Stringer] []T

// String joins all string representations with custom angle brackets
func (sv StringableVector[T]) String() string {
    var sb strings.Builder
    sb.WriteString("«")
    for i, v := range sv {
        if i > 0 {
            sb.WriteString(", ")
        }
        sb.WriteString(v.String())
    }
    sb.WriteString("»")
    return sb.String()
}

func main() {
    // We must instantiate StringableVector explicitly with the type parameter
    sv := StringableVector[MyInt]{MyInt(1), MyInt(2), MyInt(3)}
    fmt.Println(sv.String()) // Prints: «1, 2, 3»
}
```

---
