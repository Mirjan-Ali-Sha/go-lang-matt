## Chapter 31: Odds & Ends

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-31-misc-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-31-misc-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="oTtYtrFv3gw" chapter="31" />

This chapter covers smaller, miscellaneous syntax features and details in the Go language.

### 1. Custom Enumerations (`iota`)

Go does not have a formal `enum` keyword. Instead, we define a custom type (typically based on `int`) and use a constant block with the predefined identifier `iota` to generate auto-incrementing numbers.

#### Basic Custom Enum
```go
package main

import "fmt"

type Shoe int

const (
    Tennis Shoe = iota // Starts at 0
    Dress              // Automatically gets Shoe(1)
    Sandal             // Automatically gets Shoe(2)
    Clog               // Automatically gets Shoe(3)
)
```

#### Bit Flags
We can construct bit flags by shifting a bit left by `iota` spaces:

```go
type Permission int

const (
    Read   Permission = 1 << iota // 1 << 0 = 0001 (1)
    Write                         // 1 << 1 = 0010 (2)
    Execute                       // 1 << 2 = 0100 (4)
)
```

#### Skipping Values (Prefix/Unused Zero Value)
In some systems, we want the zero value of a custom type to represent an invalid or unitialized state. We can use the blank identifier `_` to skip `iota` indices:

```go
type ByteSize int64

const (
    _           = iota // Ignore zero value
    KB ByteSize = 1 << (10 * iota) // 1 << (10 * 1) = 1024
    MB                             // 1 << (10 * 2) = 1048576
    GB                             // 1 << (10 * 3) = 1073741824
)
```

---

### 2. Variadic Functions (Variable Argument Lists)

A variadic function accepts any number of trailing arguments. We define it using the `...` operator in front of the parameter type.

#### Defining and Unpacking Variadic Parameters
Inside the function, the variadic parameter behaves as a standard slice:

```go
package main

import "fmt"

func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

func main() {
    fmt.Println(sum(1, 2, 3)) // Output: 6
    fmt.Println(sum())        // Output: 0

    // Unpacking a slice into a variadic function call:
    values := []int{4, 5, 6}
    fmt.Println(sum(values...)) // Output: 15
}
```

The standard library `append` function is variadic, allowing you to join two slices together using the unpack operator:
```go
s1 := []int{1, 2}
s2 := []int{3, 4}
s1 = append(s1, s2...) // s1 becomes []int{1, 2, 3, 4}
```

---

### 3. Bitwise Operators

Go provides standard low-level bitwise operations. All shifts in Go are **logical** (always filling empty bits with zeros), not arithmetic.

| Operator | Operation | Description |
| :--- | :--- | :--- |
| `&` | AND | Returns 1 if both bits are 1 |
| `\|` | OR | Returns 1 if either bit is 1 |
| `^` | XOR / NOT | Binary: XOR (1 if bits are different). Unary: Bitwise NOT (flips bits). |
| `&^` | AND NOT | Bit clear (clears bits set in the second operand) |
| `<<` | Left Shift | Shifts bits left, fills with 0 |
| `>>` | Right Shift | Shifts bits right, fills with 0 (logical shift) |

#### TCP Flag Masking Example
```go
package main

import "fmt"

const (
    SYN = 1 << 0
    ACK = 1 << 1
    FIN = 1 << 2
)

func main() {
    // Combine SYN and ACK
    flags := SYN | ACK

    // Test if both SYN and ACK are set
    mask := SYN | ACK
    if flags&mask == mask {
        fmt.Println("Packet is a SYN-ACK")
    }
}
```

---

### 4. Sized Integers & Two's Complement Gotchas

Go supports sized integer types:
- **Signed:** `int8`, `int16`, `int32`, `int64`.
- **Unsigned:** `uint8`, `uint16`, `uint32`, `uint64`.

#### The Downcasting Gotcha
Converting a larger integer type to a smaller type discards the high-order bits.

```go
var a int32 = 0x12345678
var b int16 = int16(a) // b becomes 0x5678 (discards high 16 bits)
```

If the high bit of the remaining bits is $1$, the number becomes negative (if signed):
```go
var a int32 = 32768        // binary: 00000000 00000000 10000000 00000000
var b int16 = int16(a)     // b becomes -32768 (high bit is 1)
```

#### Two's Complement Range Contraction
Signed integers are stored in two's complement form. The range of an 8-bit signed integer (`int8`) is $-128$ to $+127$. There is one more negative value than positive value because zero is non-negative.

Because of this asymmetry, multiplying or dividing the minimum value by $-1$ results in silent overflow:

```go
package main

import "fmt"

func main() {
    var x int8 = -128
    
    // -128 * -1 should be 128, which exceeds int8 limit (+127)
    x = x * -1 
    fmt.Println(x) // Output: -128 (silent overflow back to min value!)

    var y int8 = -128
    y = y - 1
    fmt.Println(y) // Output: 127 (wraps around to maximum positive!)
}
```

To avoid silent bugs, Go enforces explicit conversions. You cannot perform mathematical operations on mixed integer types (e.g., `int32 + int16`) without converting them to matching types.

---

### 5. The `goto` Statement

Although `goto` can create unreadable "spaghetti code", it is occasionally useful to bypass nested conditions or retry loops cleanly.

#### WAV File Junk Header Skip Example
```go
package main

import (
    "bytes"
    "encoding/binary"
    "fmt"
)

func parseWav(data []byte) {
    buf := bytes.NewReader(data)

readHeader:
    var headerID [4]byte
    if err := binary.Read(buf, binary.BigEndian, &headerID); err != nil {
        return
    }

    if string(headerID[:]) == "JUNK" {
        // Skip junk bytes and retry header parse
        var size int32
        binary.Read(buf, binary.LittleEndian, &size)
        buf.Seek(int64(size), 1)
        goto readHeader // Jump back to try reading the format header again
    }

    fmt.Println("Header:", string(headerID[:]))
}
```
In this scenario, `goto` provides a clean, single-point retry loop without the indentation overhead of recursive calls or stateful nested loops.
