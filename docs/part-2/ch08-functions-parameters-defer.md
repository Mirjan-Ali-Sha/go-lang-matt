## Chapter 8: Functions, Parameters & Defer

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-08-funcs-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-08-funcs-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="wj0hUjRHkPs" chapter="08" />

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
