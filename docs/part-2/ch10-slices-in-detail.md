## Chapter 10: Slices in Detail

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-10-slices-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-10-slices-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="pHl9r3B2DFI" chapter="10" />

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
