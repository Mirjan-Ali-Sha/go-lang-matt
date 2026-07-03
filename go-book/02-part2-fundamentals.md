# Part II — Language Fundamentals

---

## Chapter 3: Basic Types

> 📊 **Slide Reference:** `slides/go-03-basics-slides.pdf`

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

## Chapter 4: Strings

> 📊 **Slide Reference:** `slides/go-04-strings-slides.pdf`

Strings are a little bit of a curious type in Go because they have two natures — we need to think about strings in a logical way and a physical way.

### Unicode, Runes, and UTF-8

In the old days, U.S. programming languages all used something called ASCII — it represented characters with seven bits and basically only represented the characters of American English. When we move to international languages, we get accent marks, and then we get non-Roman languages like Chinese or Arabic, and we need very different techniques.

Unicode is a way to represent them, and it uses numbers bigger than what fits into a byte. A **rune** is the Go equivalent of what you think of as a character — it's a synonym for a 32-bit `int` (`int32`). That four bytes is big enough to represent any Unicode code point.

But in order to make programs efficient, we don't want to represent every character with four bytes, because a lot of programs are going to have just ASCII characters. So there's a technique called **UTF-8** — a way of representing Unicode in bytes. Coincidentally, UTF-8 was invented by a couple of the guys who also worked on the Go programming language years ago at Bell Labs.

So when we think about strings in Go: **physically**, they are the UTF-8 encoding of Unicode characters. **Logically**, they represent Unicode characters (runes).

```go
s := "élite"

fmt.Printf("%T %v\n", s, s)               // string, élite
fmt.Printf("%T %v\n", []rune(s), []rune(s))   // []int32, [233 108 105 116 101]
fmt.Printf("%T %v\n", []byte(s), []byte(s))   // []uint8, [195 169 108 105 116 101]
```

When cast to runes, we get 5 values — that makes sense for a five-character string. But when cast to bytes, we get 6 values, because the `é` (code point 233) takes two bytes in UTF-8 encoding.

### Length of a String

The length of a string is the number of bytes required to represent the Unicode characters, **not** the number of characters:

```go
s := "élite"
fmt.Println(len(s)) // 6, not 5
```

This is the right answer because at some point your program has to deal with actual memory.

### String Descriptors

A string in Go is represented by a **string descriptor** — a small struct with a pointer to the actual bytes in memory and a length. There's no null terminator like in C.

When you create a substring, it can reuse the same underlying memory:

```go
s := "hello, world"
hello := s[:5]   // shares storage with s
world := s[7:]   // also shares storage
```

Both `hello` and `world` are descriptors pointing into parts of `s`'s memory. This is possible because strings are immutable.

### String Immutability

Strings in Go are immutable — they can't change once created. You can't modify a character:

```go
s[0] = 'H' // compile error
```

When you do `s += "es"`, Go creates a new chunk of memory, copies the old string into it, appends the new characters, and `s` now points to this new block. The original memory doesn't change because other substrings might still reference it. Go is a garbage-collected language — if nobody else is using the old string, it will eventually get reclaimed.

### String Functions

There's an enormous number of string functions. Things like `strings.Contains`, `strings.HasPrefix`, `strings.HasSuffix`, and `strings.ToUpper`. When you call `strings.ToUpper(s)`, it creates a new string in a new piece of memory with uppercase letters — the original string doesn't change.

### Example: Simple Search and Replace

```go
package main

import (
    "bufio"
    "fmt"
    "os"
    "strings"
)

func main() {
    if len(os.Args) < 3 {
        fmt.Fprintln(os.Stderr, "usage: replace old new")
        os.Exit(1)
    }

    old, new := os.Args[1], os.Args[2]
    scan := bufio.NewScanner(os.Stdin)

    for scan.Scan() {
        s := strings.Split(scan.Text(), old)
        fmt.Println(strings.Join(s, new))
    }
}
```

The scanner reads one line at a time from standard input. We split the line around the old string, then join it back together with the new string. Run it like:

```bash
go run . Matt Ed < test.txt
```

---

## Chapter 5: Arrays, Slices, and Maps

> 📊 **Slide Reference:** `slides/go-05-complex-slides.pdf`

In this section I want to talk about three composite types: arrays, slices, and maps.

### Arrays

An array in Go is a fixed-size, contiguous block of memory:

```go
var a [3]int           // array of 3 ints, all zero
b := [3]int{1, 2, 3}  // initialized with values
```

The size of the array is part of the type. A `[3]int` is a different type from a `[4]int`. You can't assign one to the other.

Importantly, an array is a value type in Go. When you assign an array to another variable, it copies the entire array:

```go
a := [3]int{1, 2, 3}
b := a  // copies all 3 elements
```

For small arrays this is fine, but for large arrays this can be expensive.

### Slices

A slice is like a variable-length array. It's described by a **slice descriptor** (similar to a string descriptor) with three fields: a pointer to the underlying array, a length, and a capacity.

```go
s := []int{1, 2, 3}  // a slice (no size in brackets)
```

The distinction is subtle: `[3]int` is an array, `[]int` is a slice. A slice can grow using `append`:

```go
s := []int{1, 2, 3}
s = append(s, 4)  // s is now [1, 2, 3, 4]
```

When you `append` and the capacity is exhausted, Go allocates a new, larger underlying array, copies the data, and returns a new slice descriptor. This is why `append` returns a value that you must assign back.

You can also create a sub-slice:

```go
s := []int{1, 2, 3, 4, 5}
t := s[1:3]  // t is [2, 3], shares underlying storage with s
```

Just like with strings, sub-slices share the underlying memory. Changes to `t` will affect `s` and vice versa.

### The make Function

You can also create a slice with `make`:

```go
s := make([]int, 5)     // length 5, capacity 5
s := make([]int, 0, 10) // length 0, capacity 10
```

This is useful when you know approximately how big the slice will be and want to avoid multiple reallocations from `append`.

### Maps

A map in Go is a hash table. It maps keys to values:

```go
m := map[string]int{
    "alice": 42,
    "bob":   37,
}
```

You can also create a map with `make`:

```go
m := make(map[string]int)
m["alice"] = 42
```

Looking up a value that doesn't exist returns the zero value. You can test whether a key exists:

```go
v, ok := m["alice"]
if ok {
    fmt.Println("found:", v)
}
```

The `ok` will be `true` if the key was found, `false` otherwise. This is the "comma ok" idiom in Go.

Maps have **no order**. If you range over a map, the keys come out in a random order. If you need sorted keys, extract them, sort them, and then iterate:

```go
keys := make([]string, 0, len(m))
for k := range m {
    keys = append(keys, k)
}
sort.Strings(keys)
for _, k := range keys {
    fmt.Println(k, m[k])
}
```

### Deleting from a Map

To delete an entry, use the `delete` built-in:

```go
delete(m, "alice")
```

### nil Slices and Maps

A `nil` slice and a `nil` map are both usable to some extent. You can `append` to a nil slice — Go will allocate storage. But you cannot store values in a nil map; it will panic. You must initialize a map before writing to it.

---

## Chapter 6: Control Statements, Declarations & Types

> 📊 **Slide Reference:** `slides/go-06-controls-slides.pdf`

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

## Chapter 7: Formatted & File I/O

> 📊 **Slide Reference:** `slides/go-07-io-slides.pdf`

In this segment I want to talk about formatted I/O and file I/O.

### The fmt Package

The `fmt` package provides formatted I/O. The key functions are:

- `fmt.Println` — prints values with spaces between them, adds a newline
- `fmt.Printf` — formatted printing with verbs
- `fmt.Sprintf` — same as `Printf` but returns a string instead of printing

Common verbs:

| Verb | Meaning |
|------|---------|
| `%v` | Default format for the value |
| `%T` | Type of the value |
| `%d` | Integer in decimal |
| `%s` | String |
| `%q` | Quoted string |
| `%f` | Floating point |
| `%t` | Boolean |
| `%x` | Hexadecimal |
| `%p` | Pointer |

The `%v` verb is very useful because it will print anything regardless of type. For debugging, `%T` shows the type.

### Reading Input

For reading input, we have:

- `fmt.Scan`, `fmt.Scanf`, `fmt.Scanln` — read from standard input
- `fmt.Fscan`, `fmt.Fscanf`, `fmt.Fscanln` — read from any `io.Reader`

```go
var name string
fmt.Print("Enter your name: ")
fmt.Scanln(&name)
fmt.Println("Hello,", name)
```

Note the `&` — scan functions need a pointer to the variable so they can put a value into it.

### File I/O

To read a file, you use `os.Open`:

```go
f, err := os.Open("data.txt")
if err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
}
defer f.Close()
```

The `defer` keyword schedules `f.Close()` to run when the function returns. This is important — we always want to close files when we're done with them, and `defer` makes sure that happens even if there's an error later.

For reading lines, use `bufio.Scanner`:

```go
scan := bufio.NewScanner(f)
for scan.Scan() {
    fmt.Println(scan.Text())
}
```

For writing, use `os.Create`:

```go
f, err := os.Create("output.txt")
if err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
}
defer f.Close()

fmt.Fprintln(f, "Hello, file!")
```

### Standard Streams

Go provides `os.Stdin`, `os.Stdout`, and `os.Stderr`. It's good style in a command-line program to print errors to `os.Stderr`, which might be going to a different place than normal output.
