## Chapter 3: Basic Types

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-03-basics-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-03-basics-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="NNLpEPb2ddE" chapter="03" />

I'd like to start talking about basic types in Go. We'll start with integers and other numbers, then we'll move on to strings and then some composite types like slices and maps.

Before I start talking about types, I just want to point out a list of keywords and operators — I'm putting this up for reference. There's no reason to memorize it. I do want to point out one interesting thing, and that is how few keywords Go actually has. It's another sign of how simple the language is. There are also some built-in types, constants, and built-in functions — this is just a summary list; I won't talk about them all now.

### Numbers: Compiled vs. Interpreted

When I start talking about numbers, what I want to do first is discuss the difference between numbers in some interpreted languages and the way numbers are represented in Go, because it gets to the fundamentals of how the type system works.

In an interpreted environment — think of Python — I have some variable `a`, and I'm going to give it the value `2`. What is `a`? Well, `a` is not a number in the sense the computer thinks of a number. `a` is an object that represents or masquerades as a number in the interpreter. Eventually the interpreter, being a program written in C, will use the underlying hardware to do actual math. But when you're working at the level of Python, the variable `a`, although it represents a number, is not immediately something that the machine knows about.

In Go, when I declare a variable `a` initialized to the value of two:

```go
a := 2
```

`a` is purely the name or address of a memory location in the machine. We're dealing directly with machine numbers in machine memory. There's no interpreter, there's no JVM. This is part of what gives Go its performance advantage — the compiler generates machine code, the numbers are all represented in the machine representation, and these operations are a lot faster.

### Integer Types

The most important thing I want to point out is there's a default type for `int`, which is literally the word `int`. There are several types of integers with specific sizes, signed or unsigned, but for all practical purposes, the numbers you're going to deal with (unless they're fractional) are going to be `int`s.

On almost all the machines you're ever going to work with — cloud software, laptops — they're going to be 64-bit machines, so an `int` is an eight-byte object. It's so big you can literally count all the stars in the sky as 64-bit numbers.

### Floating-Point Numbers

If I ask the question "how many students are in my class?", that has to be an integer, because I can't have any half students (at least not bodily). But if I ask "what is the average number of students in my class per week?", that's likely to be a floating-point number — it could be 7.3 or something, and that's not an integer.

Unfortunately Go does not have a generic type for float — they're either `float32` or `float64`. By default they're `float64`. I'm not going to spend time talking about the difference because we're not going to do mathematical software.

> ⚠️ **Warning:** It's really bad practice to try to represent money using the built-in floating-point types, and this is not just true of Go — it's pretty much true of any language. Floating-point numbers are designed for scientific calculations. They don't do money very well. One of the reasons is that 10 cents — 0.1 dollar — when represented in floating-point binary, is a repeating fraction that's never completely accurate. If I take a dollar and split it three ways, I get three chunks of 33 cents, but that's only 99 cents with a penny left over. You should use a package designed to do money.

### Variable Declarations

There are two ways to declare a variable. You can use the `var` keyword:

```go
var a int
```

Or you can group several declarations:

```go
var (
    b = 2
    f = 2.01
)
```

Here I declared `b` and `f` without giving them types explicitly, but Go can infer the type by looking at the number. For `b`, the number `2` is an `int`, therefore `b` is an `int`. For `f`, the value `2.01` is not an integer, so Go assumes `float64`.

Within a function (and only within a function), there's the **short declaration operator**:

```go
a := 2
```

Its purpose is to declare a variable and give it a value at the same time. Whatever that number is — in this case `2` — we know the type of `2` is `int`, so `a` is given the value `2` and typed as `int` right there. This is very convenient. One of the ideas of Go was to make it type-safe in a statically typed, compiled way, but to make it easy to use like a dynamically typed language where you just say `a = 2`.

### Debugging with Printf Verbs

There's a very handy debugging technique using `fmt.Printf`:

```go
a := 2
b := 3.1

fmt.Printf("a: %T %v\n", a, a)
fmt.Printf("b: %T %v\n", b, b)
```

The `%T` verb shows the type of something, and `%v` shows the value. When I run this, it tells me `a` is an `int` and `b` is a `float64`. You can also use positional arguments like `%[1]T %[1]v` to reuse the same parameter without repeating it.

### Type Conversions

Go is a pretty strict language as far as types are concerned. You can't just assign a float to an `int` or an `int` to a float — you have to explicitly convert:

```go
a := 2
b := 3.1

a = int(b)     // a is now 3 — fractional part is removed
b = float64(a) // b is now 3.0 — the .1 is gone forever
```

When you go from a float to an `int`, the fractional part has to be removed. And once you've truncated it, the fractional part went away and it's never coming back.

### Booleans

The `bool` type is a boolean — true or false — named after George Boole who invented boolean logic. What's very important in Go is that there's no easy way to convert it back and forth to an integer. In many languages going back to C, `0` is logically false and any non-zero value is true. In Go, booleans and integers are just separate things. You have to use an actual expression:

```go
isZero := (a == 0)  // boolean expression
```

### The Error Type

Technically speaking, the error type isn't simple, but I want to treat it right now like a simple type. An error is either `nil` or it's not. If it's not `nil`, then the error holds an error message that we can print out:

```go
y, err := f(x)
if err != nil {
    // handle the error
}
```

For the first few segments, we're just going to treat errors that way.

### Pointers (Preview)

A pointer is just an address of something. I'm going to have another segment where I talk about pointers in more detail. The important things: a pointer is either `nil` or not. If it has the value `nil`, it doesn't point at anything. There's a package called `unsafe` in Go which I'm not going to talk about anytime soon — it allows you to do dangerous things with pointers if you need to interface Go with the C language.

### Zero Values

In Go, every variable is initialized at its point of declaration. Either you do it or Go will do it. There are no uninitialized variables in Go.

This is great. One of the worst production disasters I've ever seen in my career involved a very large telephone switch in Hawaii. It went down for like 13 hours. The first thing that happened was part of the program had an uninitialized pointer which picked up some random memory address. Go prevents that kind of disaster — it gives every variable a zero value. The value is literally zero for integers, an empty string for strings, `nil` for pointers. Every type in Go is initialized to some zero value.

### Constants

Constants in Go are kind of limited. The only things you can make a constant out of are numbers, booleans, and strings. Go has a particular idea of what "constant" should mean — it's immutable, absolutely, completely immutable. It can never change. It's something I could put into read-only memory.

The reason Go does that has to do with concurrency. Go is a concurrent programming language from the get-go, and it's good to have constants that are truly immutable to be safe in a concurrent program. Languages that allow a "constant" struct — if you look at C++, the `const` tag is almost wishful thinking. It is `const` except when it isn't. That's not safe, and it's certainly not safe in a concurrent program.

```go
const a = 1           // int
const s = "hello"     // string
const n = a + 1       // simple arithmetic is allowed
const l = len(s)      // len of a string constant is allowed
```

### Example: Average Calculator

Let me work through a program that calculates averages:

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    var sum float64
    var n int

    for {
        var val float64
        if _, err := fmt.Fscanln(os.Stdin, &val); err != nil {
            break
        }
        sum += val
        n++
    }

    if n == 0 {
        fmt.Fprintln(os.Stderr, "no values")
        os.Exit(1)
    }

    fmt.Println("The average is", sum/float64(n))
}
```

Notice: `sum` is a `float64` and `n` is an `int`. In Go, these are separate types and they don't mix — there's no automatic conversion or promotion. We have to explicitly cast `n` to `float64` with `float64(n)`.

The `&val` is the address-of operator — the `Fscanln` function needs a pointer to `val` so it can put a value into it. The program reads one number per line, adds them up, and when it gets to end of file (or any error), it breaks out and prints the average.

You can run this interactively (type numbers, then Ctrl-D), or redirect from a file:

```bash
go run . < nums.txt
```

---
