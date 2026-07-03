## Chapter 5: Arrays, Slices, and Maps

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-05-complex-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-05-complex-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="T0Xymg0_aSU" chapter="05" />

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
