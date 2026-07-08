## Chapter 6: Control Statements, Declarations & Types

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-06-controls-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-06-controls-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="qpHLhmoV3BY" chapter="06" />

In this segment I want to talk about some basic things in Go that we've already seen — control statements, packages, declarations, and operators — but go into them a little more detail.

### If Statements

In Go, if braces are allowed, braces are required. The form is not a choice:

```go
if x > 0 {
    fmt.Println("positive")
} else {
    fmt.Println("non-positive")
}
```

The braces have to be laid out in this style — sometimes known as "One True Brace Style" (1TBS) — which is enforced by the compiler. You can also have a short declaration before the condition:

```go
if err := doSomething(); err != nil {
    fmt.Println("error:", err)
}
```

### For Loops

Go only has one type of loop — the `for` loop. There's no `while`, no `do while`, no `repeat until`.

The classic three-part form:

```go
for i := 0; i < 10; i++ {
    fmt.Println(i)
}
```

The range form, which is much more common:

```go
for i, v := range mySlice {
    fmt.Println(i, v)
}
```

The range operator gives one or two values. With one variable, you get the index. With two, you get the index and a **copy** of the value. If you don't want the index:

```go
for _, v := range mySlice {
    fmt.Println(v)
}
```

> ⚠️ **Common Mistake:** If I just write one variable in a range, the variable is the **index**, not the value. If you want the value without the index, you must use the `_` placeholder.

The infinite loop form:

```go
for {
    // do something
    if done {
        break
    }
}
```

There's also `break` and `continue` for controlling loops, and labeled loops for breaking or continuing outer loops from inner ones:

```go
outer:
for _, key := range keys {
    for _, item := range items {
        if item == key {
            continue outer
        }
    }
    fmt.Println("missing:", key)
}
```

### Switch Statements

A switch statement is syntactic sugar for a bunch of if-else statements:

```go
switch a := someValue(); a {
case 1, 2:
    fmt.Println("small")
case 3:
    // no-op
default:
    fmt.Println("other")
}
```

Important differences from C/Java: cases break automatically — no need for `break` statements. There's no fall-through by default. If you want fall-through (which is rare), there's an explicit `fallthrough` keyword.

The "switch on true" form uses logical tests:

```go
switch {
case a <= 2:
    fmt.Println("small")
case a <= 8:
    fmt.Println("medium")
default:
    fmt.Println("large")
}
```

### Packages

Everything in Go lives inside a package. Every Go source file starts with a package declaration. There are two kinds of scope: **package scope** (outside a function) and **function scope** (inside a function).

**Exporting:** If an identifier starts with a capital letter, it's exported. If it starts with a lowercase letter, it's private to the package. This is simpler than languages where you need separate header/specification files.

**Imports:** Every file in a package must import the things it needs and nothing it doesn't. Imports are per file, not per package.

**No cyclic dependencies:** If package A uses package B, then B cannot use A. The dependency graph must be a tree. This enables fast compilation and clear initialization order.

**The `init` function:** You can have a private function called `init()` in your package that gets called implicitly when the package is loaded. It's useful but controversial — some people say you shouldn't overuse them because they can make programs harder to understand.

### What Makes a Good Package

There's a professor named Ousterhout at Stanford who wrote a book called *A Philosophy of Software Design*. One of the ideas is that a good package encapsulates deep, complex functionality behind a simple API. The Unix file API — `open`, `close`, `read`, `write`, `seek` — is a great example. What actually happens when you write data to a file is enormously complicated (buffering, device drivers, file systems, disk interfaces), but the API is simple and has been battle-tested for 50 years.

### Declarations

Variables can be declared with `var` or the short declaration operator:

```go
var a int        // type explicit, value defaults to 0
var b uint = 1   // type and value both specified
var c = 1        // type inferred as int
d := 1.0         // short declaration, type inferred as float64
```

There's a **style convention**: use `var` when you want the zero value, use `:=` when you're initializing to a non-default value.

### Type Declarations

Go allows you to create new named types:

```go
type Celsius float64
type Fahrenheit float64
```

Even though both are `float64` underneath, `Celsius` and `Fahrenheit` are different types. You can't accidentally assign one to the other. This is a way of making the type system work for you.

### Operators

Go's operators are similar to C with a few important differences:

- The increment operator `i++` is a **statement**, not an expression. It has to be on a line by itself. There's no `++i` in Go.
- The `+=` operator works as expected: `sum += val` is the same as `sum = sum + val`.

---
