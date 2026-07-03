## Chapter 14: Reference & Value Semantics

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-14-semantics-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-14-semantics-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="904pyovPvXM" chapter="14" />

One of the most important decisions you make when writing Go code is choosing between **value semantics** and **pointer (reference) semantics**. This determines whether you copy data or share it when passing it to functions or defining methods.

### Value Semantics (Copying)

Under value semantics, variables are passed by copying their value. This ensures that the function receiving the value has its own isolated copy and cannot mutate the original variable.

- **Safer:** Essential for concurrent programming because isolation prevents race conditions.
- **Efficient for small data:** Copies of integers, floats, small structs, and descriptors (like slice or string descriptors) are very cheap.
- **Rule of thumb:** If the data structure is smaller than 64 bytes, copying is usually the default choice.

```go
type Point struct {
    X, Y float64
}

// Value semantics: receives a copy
func MovePoint(p Point, dx, dy float64) Point {
    p.X += dx
    p.Y += dy
    return p // original point is untouched, must return the new copy
}
```

### Reference/Pointer Semantics (Sharing)

Under reference semantics, we pass the memory address of the variable (using a pointer). The receiving function shares the exact same memory location and can mutate the original data.

- **Necessary for mutation:** When you need a function or method to permanently update a value.
- **Efficient for large data:** Copying a 4KB block of data across a deep call chain is extremely expensive. Passing a 64-bit pointer is always cheap.
- **Uncopyable types:** Types like `sync.Mutex` or `sync.WaitGroup` contain internal state that must never be copied. They *must* be shared via pointers.

```go
type DatabaseConnection struct {
    mu   sync.Mutex
    data map[string]string
}

// Pointer semantics: shares the database connection
func (db *DatabaseConnection) Set(key, val string) {
    db.mu.Lock()
    defer db.mu.Unlock()
    db.data[key] = val
}
```

### Consistency is Critical

If you choose a semantic type for a struct, be consistent! Mixing value and pointer semantics across the same struct's methods or call chains leads to subtle bugs.

```go
// BAD: mixing semantics
func Step1(e *Employee) { e.Salary += 1000 }
func Step2(e Employee)  { e.Address = "New York" } // MODIFIES A COPY!
func Step3(e *Employee) { fmt.Println(e.Salary, e.Address) }
```
If `Step2` accepts a value copy, any modification to the employee's address is discarded when `Step2` returns. `Step3` will see the salary increase, but the address change will be lost.

### The Loop Variable Gotcha

When iterating over elements using `range`, the iteration variable is a **single pre-allocated variable** that gets reused on every iteration. Each loop iteration overwrites the value of this variable.

Taking a pointer to this iteration variable is a classic Go bug:

```go
// BAD: Storing pointers to the loop variable
items := [3][2]byte{{1, 2}, {3, 4}, {5, 6}}
var list []*[2]byte

for _, item := range items {
    list = append(list, &item) // Capturing pointer to the same variable!
}

// When the loop ends, 'item' retains the last value: {5, 6}
// list now contains three pointers pointing to the exact same memory address!
// Printing list yields: [{5, 6}, {5, 6}, {5, 6}]
```

**The Fix:** Create a unique local variable inside the loop block to force fresh allocations:

```go
for _, item := range items {
    itemCopy := item // unique variable in this iteration's scope
    list = append(list, &itemCopy)
}
// list now correctly holds: [{1, 2}, {3, 4}, {5, 6}]
```

---
