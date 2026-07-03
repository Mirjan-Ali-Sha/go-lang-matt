## Chapter 20: Reader, Writer & Interface Details

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-20-interfaces-details-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-20-interfaces-details-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="AXCIEiebVfI" chapter="20" />

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
