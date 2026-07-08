## Chapter 4: Strings

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-04-strings-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-04-strings-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="nxWqANttAdA" chapter="04" />

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
