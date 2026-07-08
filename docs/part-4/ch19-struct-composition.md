## Chapter 19: Struct Composition

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-19-composition-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-19-composition-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="0X6AcnwocbM" chapter="19" />

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
