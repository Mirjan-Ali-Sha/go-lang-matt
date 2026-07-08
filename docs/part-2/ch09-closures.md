## Chapter 9: Closures

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-09-closures-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-09-closures-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="US3TGA-Dpqo" chapter="09" />

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
