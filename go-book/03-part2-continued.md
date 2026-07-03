# Part II — Language Fundamentals (Continued)

---

## Chapter 8: Functions, Parameters & Defer

> 📊 **Slide Reference:** `slides/go-08-funcs-slides.pdf`

In this segment I want to talk about functions, how parameters are passed, and then introduce a new statement called `defer`.

### Functions Are First-Class Objects

Functions in Go are first-class objects. You can do almost anything with them that you can do with an integer or a string — you can assign a function to a variable, pass it as a parameter, return it from a function. We can make functions that return functions, and we're going to find that's very useful.

Functions have what's called a **signature** — the order and types of parameters and return values. The name of the parameter doesn't matter because that's local to the function; what matters are the types in a certain order.

### Parameter Passing

I want to use a couple of important terms. When you declare a function, the parameters in the declaration are called **formal parameters**. When you call the function, the values you pass in are called **actual parameters**.

There are two models: **pass by value** (you get a copy) and **pass by reference** (the function sees the same data).

In Go, **everything is passed by value** from a technical standpoint. But practically, we think of slices and maps as "by reference" because the descriptor gets copied but the underlying data is shared.

Let me show what happens with each type:

**Arrays — pure value copy:**

```go
func do(b [3]int) int {
    b[0] = 0
    return b[1]
}

func main() {
    a := [3]int{1, 2, 3}
    v := do(a)
    fmt.Println(a, v) // [1 2 3] 2 — a is unchanged
}
```

**Slices — descriptor copied, data shared:**

```go
func do(b []int) int {
    b[0] = 0
    return b[1]
}

func main() {
    a := []int{1, 2, 3}
    v := do(a)
    fmt.Println(a, v) // [0 2 3] 2 — a IS changed!
}
```

The slice descriptor is copied, but both `a` and `b` point to the same underlying array. Changes through `b` are visible through `a`.

**Maps — same behavior as slices:**

If you modify a map through its formal parameter, the original map sees the changes because they share the same hash table. But if you reassign the parameter to a new map, only the local variable changes — the original is unaffected.

**Replacing a map entirely requires a pointer:**

```go
func do(m1 *map[int]int) {
    *m1 = map[int]int{4: 4}
}

func main() {
    m := map[int]int{7: 2, 8: 3}
    do(&m)
    fmt.Println(m) // map[4:4] — m was replaced
}
```

### Multiple Return Values

Go allows one or more return values:

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}
```

With two or more return types, you need parentheses around them. You also must return all values in every return statement.

### Recursion

Go allows recursion — a function can call itself. Anything you can do recursively can be done with a `for` loop, but sometimes recursion is much more natural, especially with tree and graph data structures. The only catch: you need a stopping condition, just like a loop needs to stop.

### The defer Statement

The `defer` statement is a contribution of the Go language. Sometimes we need to make sure things happen when a function exits — closing a file, unlocking a mutex:

```go
f, err := os.Open("data.txt")
if err != nil {
    log.Fatal(err)
}
defer f.Close()

// ... use f ... the Close will happen when the function returns
```

Key behaviors of `defer`:

1. **Function scope, not block scope.** The deferred call runs when the enclosing function exits, not at the end of the nearest block. This is important — if defer were block-scoped, a defer inside an `if` would close the file before you used it.

2. **LIFO order.** If you have multiple defers, they execute in reverse order (last in, first out).

3. **Parameters are captured at defer time.** The values in the deferred call are copied when the defer is set up, not when it executes:

```go
a := 10
defer fmt.Println(a) // will print 10
a = 11
fmt.Println(a)       // prints 11 first
// then deferred call prints 10
```

4. **Don't use defer in a loop** if you're opening resources. The defers won't execute until the function returns, so you could run out of file descriptors:

```go
// BAD — files stay open until function returns
for _, name := range files {
    f, err := os.Open(name)
    if err != nil { continue }
    defer f.Close()  // won't close until end of function!
    // process f...
}

// GOOD — close explicitly in the loop
for _, name := range files {
    f, err := os.Open(name)
    if err != nil { continue }
    // process f...
    f.Close()
}
```

---

## Chapter 9: Closures

> 📊 **Slide Reference:** `slides/go-09-closures-slides.pdf`

I just talked about functions, and now I want to talk about closures — where a closure is really about functions that live inside functions and refer to the enclosing function's data.

### Scope vs. Lifetime

Before I talk about closures, I want to bring out the idea of variable scope versus lifetime. Scope is static — it's about the text of the program, who can see the variable name at compile time. Lifetime is about how long the variable actually exists at runtime.

In Go, a variable's lifetime can exceed its scope. If you return a pointer to a local variable, Go's **escape analysis** detects this at compile time and allocates the variable on the heap instead of the stack:

```go
func doIt() *int {
    b := 42
    return &b  // perfectly safe in Go — b escapes to heap
}
```

In C, this would be a dangling pointer bug. In Go, it just works because the compiler automatically allocates `b` on the heap when it sees the pointer escaping.

### What Is a Closure?

A closure involves a function that uses variables from an outer function's scope. The inner function "closes over" those variables:

```go
func fib() func() int {
    a, b := 0, 1
    return func() int {
        a, b = b, a+b
        return b
    }
}
```

The return type of `fib` is "a function that returns an `int`." The inner anonymous function changes `a` and `b`, which were declared in `fib`. When we return that inner function, it continues to refer to `a` and `b` even after `fib` returns.

A closure is not just the function — it's the function plus its captured environment. Think of it like a string descriptor: there's a pointer to the code and a pointer to the environment (the captured variables).

```go
f := fib()
for x := f(); x <= 100; x = f() {
    fmt.Println(x) // 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
}
```

Each call to `fib()` creates a new, independent generator:

```go
f := fib()
g := fib()
// f and g have their own copies of a and b
```

### Practical Use: sort.Slice

We've already seen closures in practice with `sort.Slice`:

```go
sort.Slice(ss, func(i, j int) bool {
    return ss[i] < ss[j]
})
```

The closure's parameters are fixed by `sort.Slice`'s API — it only gets `i` and `j`. But it needs to access `ss`, which it does by closing over it.

### The Closure Gotcha

Closures capture variables **by reference**, not by value. This can cause problems when the closure is called later:

```go
s := make([]func(), 4)
for i := 0; i < 4; i++ {
    s[i] = func() {
        fmt.Println(i) // captures reference to i
    }
}
for _, f := range s {
    f() // prints 4, 4, 4, 4 — NOT 0, 1, 2, 3!
}
```

By the time the closures are called, `i` has its final value of 4. All closures reference the same `i`.

**The fix:** Create a local copy:

```go
for i := 0; i < 4; i++ {
    i2 := i // closure capture — each iteration gets its own copy
    s[i] = func() {
        fmt.Println(i2) // prints 0, 1, 2, 3
    }
}
```

This bug is not specific to Go — it happens in any language with closures (Swift, JavaScript, etc.). You'll see articles saying there's a problem with goroutines, but it has nothing to do with goroutines; it's about closures.

---

## Chapter 10: Slices in Detail

> 📊 **Slide Reference:** `slides/go-10-slices-slides.pdf`

In this section I want to drill down into slices in more detail — specifically the difference between a nil slice and an empty slice, and the relationship between length and capacity.

### nil vs. Empty Slices

```go
var s []int              // nil slice
t := []int{}             // empty slice (not nil)
u := make([]int, 5)      // length 5, capacity 5, filled with zeros
v := make([]int, 0, 5)   // length 0, capacity 5 (space reserved)
```

The slice descriptor has three fields: pointer, length, and capacity.

| Variable | Length | Capacity | nil? | Pointer |
|----------|--------|----------|------|---------|
| `s` | 0 | 0 | yes | null |
| `t` | 0 | 0 | no | sentinel |
| `u` | 5 | 5 | no | → [0,0,0,0,0] |
| `v` | 0 | 5 | no | → [_,_,_,_,_] |

**This matters for JSON encoding:**

```go
json.Marshal(s) // → null
json.Marshal(t) // → []
```

**Always check length, not nil:**

```go
// WRONG — misses empty slices
if s == nil { ... }

// RIGHT — covers both nil and empty
if len(s) == 0 { ... }
```

It's perfectly safe to call `len()` on a nil slice — it returns 0. You can also `append` to a nil slice; Go will allocate storage automatically.

### A Common Mistake with make

```go
s := make([]int, 5)  // length 5 — has five zeros
s = append(s, 42)    // s is now [0, 0, 0, 0, 0, 42] — probably not what you wanted!

s := make([]int, 0, 5) // length 0, capacity 5
s = append(s, 42)      // s is now [42] — correct
```

If you want to reserve space, make sure the first argument (length) is zero.

### Length vs. Capacity and the Slice Operator

The two-index slice operator inherits the underlying capacity:

```go
a := [3]int{1, 2, 3}
b := a[:1]              // b = [1], len=1, cap=3
c := b[:2]              // c = [1, 2], len=2, cap=3  ← this works!
```

This is counterintuitive — `b` has length 1, but I can slice it to length 2 because it still has capacity 3 from the underlying array `a`.

### The Three-Index Slice Operator

Go 1.2 added a three-index slice operator to control capacity:

```go
// a[low:high:max]
// length = high - low
// capacity = max - low

d := a[0:1:1]  // d = [1], len=1, cap=1
e := d[:2]     // PANIC — capacity is only 1
```

This is safer. When you limit the capacity, subsequent `append` operations will allocate new memory instead of silently overwriting the underlying array:

```go
a := [3]int{1, 2, 3}
c := a[:2:2]       // length 2, capacity 2
c = append(c, 5)   // forces reallocation — a is NOT modified
fmt.Println(a)      // [1 2 3] — unchanged
fmt.Println(c)      // [1 2 5] — in new memory
```

Without the three-index operator, the append would have overwritten `a[2]` with `5`, silently mutating the original array.

---

## Chapter 11: Exercise — HTML Word & Image Counter

> 📊 **Slide Reference:** `slides/go-11-hw2-slides.pdf`

In this segment I'm not going to introduce any new material. Instead, I want to take one of the exercises out of *The Go Programming Language* book — Exercise 5.5 — and we're going to work through it with a small modification.

The exercise is to get some HTML, parse it, and count the words and images. Instead of going out on the network (we haven't done that yet), I'm going to copy a snippet of HTML into the program as a raw string.

### The Program

```go
package main

import (
    "bytes"
    "fmt"
    "os"
    "strings"

    "golang.org/x/net/html"
)

const rawHTML = `<html><body>
<h1>My Page</h1>
<p>My first paragraph</p>
<p>My second paragraph has <b>bold</b> text</p>
<img src="photo.jpg">
</body></html>`

func main() {
    r := bytes.NewReader([]byte(rawHTML))
    doc, err := html.Parse(r)
    if err != nil {
        fmt.Fprintf(os.Stderr, "parse failed: %s\n", err)
        os.Exit(1)
    }
    words, pics := countWordsAndImages(doc)
    fmt.Printf("%d words, %d images\n", words, pics)
}
```

We take the raw string, convert it to a byte slice, create a reader around it so the HTML parser can treat it the same way it would treat a network socket. The `golang.org/x/net/html` package is from the extended standard library.

### The Counting Functions

The strategy is recursive: visit every node in the HTML tree, count text nodes as words and element nodes with tag `img` as images.

```go
func countWordsAndImages(doc *html.Node) (int, int) {
    var words, pics int
    visit(doc, &words, &pics)
    return words, pics
}

func visit(n *html.Node, pWords, pPics *int) {
    if n.Type == html.TextNode {
        *pWords += len(strings.Fields(n.Data))
    } else if n.Type == html.ElementNode && n.Data == "img" {
        *pPics++
    }

    for c := n.FirstChild; c != nil; c = c.NextSibling {
        visit(c, pWords, pPics)
    }
}
```

The `countWordsAndImages` function is a "landing spot" — it creates the two accumulator variables and passes their pointers into the recursive `visit` function. This way, every call to `visit` modifies the same `words` and `pics`.

The tree traversal is **depth-first**: we go to the first child, and if it has a first child, we go there too — going as deep as we can, then up and over.

The `strings.Fields(n.Data)` call breaks text into words (splitting on whitespace), and `len()` gives us the word count.

> 💡 **Exercise Extension:** If you pull a real web page, you'll discover text nodes that contain JavaScript. You'll need to add logic to skip those subtrees, or you'll get an enormous word count from embedded scripts.
