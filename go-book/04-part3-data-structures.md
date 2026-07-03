# Part III — Data Structures & Networking

---

## Chapter 12: Structs, Struct tags & JSON

> 📊 **Slide Reference:** `slides/go-12-structs-json-slides.pdf`

In this segment, we are going to look at structs in more detail, how we can declare them, how pointers interact with structs, and then how we can use them to serialize and deserialize data to and from JSON using struct tags.

### Struct Basics

A struct is a sequence of named fields of specific types. It is a way of grouping related data together into a single, cohesive unit.

```go
type Employee struct {
    ID        int
    Name      string
    Address   string
    Position  string
    Salary    int
}
```

We can create an instance of a struct using a struct literal:

```go
// Using field names (recommended)
emp := Employee{
    ID:       1,
    Name:     "Alice",
    Position: "Software Engineer",
}

// Positional (not recommended, fragile if fields change)
emp2 := Employee{2, "Bob", "123 Main St", "Manager", 80000}
```

### Structs and Pointers

When you have a pointer to a struct, Go provides syntactic sugar so you don't have to write `(*emp).Name` to access a field. You can simply write `emp.Name`. Go automatically dereferences the pointer for you.

```go
empPtr := &emp
empPtr.Salary = 90000 // Automatically dereferenced under the hood
```

### JSON Serialization & Struct Tags

One of the most common uses of structs in modern Go applications is to represent JSON objects. Go's standard library provides the `encoding/json` package to convert structs to JSON (**marshaling**) and JSON back to structs (**unmarshaling**).

To map struct fields to specific JSON keys, we use **struct tags**:

```go
type User struct {
    ID       int    `json:"id"`
    Username string `json:"username"`
    Email    string `json:"email,omitempty"`
    Password string `json:"-"` // Ignored by JSON encoder
}
```

- **Field visibility:** Struct fields must be **exported** (start with an uppercase letter) for the JSON encoder/decoder to see them. If a field starts with a lowercase letter, it is private to the package and will be ignored by `encoding/json`.
- **`omitempty`:** If a field has the `omitempty` tag and contains its zero value (like `0`, `""`, `nil`, or `false`), it will be omitted from the generated JSON output.
- **`-`:** The hyphen tag tells the encoder to always skip this field.

```go
// Marshaling (Struct -> JSON bytes)
u := User{ID: 1, Username: "bob"}
data, err := json.Marshal(u)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(data)) // {"id":1,"username":"bob"} (Email omitted, Password skipped)
```

```go
// Unmarshaling (JSON bytes -> Struct)
rawJSON := []byte(`{"id":2,"username":"alice","email":"alice@example.com"}`)
var alice User
if err := json.Unmarshal(rawJSON, &alice); err != nil {
    log.Fatal(err)
}
fmt.Printf("%+v\n", alice)
```

> ⚠️ **Pointer Requirement:** You must pass a **pointer** to `json.Unmarshal` (e.g., `&alice`) so that the function can modify the struct's fields. If you pass it by value, the function receives a copy, updates the copy, and the original remains unchanged.

---

## Chapter 13: Regular Expressions & Search

> 📊 **Slide Reference:** `slides/go-13-regex-slides.pdf`

We have already talked about basic string searches using the `strings` package (like `strings.Contains` or `strings.HasPrefix`). However, when your search patterns are more dynamic or complex, you need regular expressions.

As the famous quote by Jamie Zawinski goes:
> "Some people, when confronted with a problem, think 'I know, I'll use regular expressions.' Now they have two problems."

Regular expressions are incredibly concise and powerful, but that means they can easily become unreadable and difficult to test. Additionally, poorly written regular expressions can cause serious performance issues due to **backtracking**.

### RE2 Engine and Performance Safety

To prevent catastrophic backtracking and Denial of Service (DoS) attacks, Go’s regular expression engine (the `regexp` package) is built on **RE2**. 

Unlike standard PCRE (Perl-Compatible Regular Expressions) engines, RE2 runs in time linear to the size of the input string. To guarantee this linear performance, RE2 does not support certain features like backreferences or look-arounds (look-ahead/look-behind), which require exponential backtracking in the worst-case.

### Standard String Searching vs. Regexp

Whenever possible, prefer the `strings` package because it is significantly faster and easier to understand.

**Example: Finding a path suffix**
```go
// Fast, simple strings approach
index := strings.LastIndexByte(filename, '/')
if index != -1 {
    basename := filename[index+1:]
}
```

Only reach for the `regexp` package when you need to match pattern classes (like "one or more digits") rather than exact substrings.

### Compilation and Matching

To use a regular expression, you compile the pattern string into a `regexp.Regexp` object.

```go
// Compile returns an error if the pattern is invalid
re, err := regexp.Compile(`[a-z]+`)

// MustCompile panics if the pattern is invalid.
// Use this for package-level global constants where a syntax error is a programmer bug.
var emailRE = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
```

### Common Regexp Methods

- **`MatchString`**: Returns a boolean indicating if the string matches the pattern.
- **`FindString`**: Returns the first matching substring.
- **`FindAllString`**: Returns a slice of all matching substrings.
- **`FindAllStringIndex`**: Returns a slice of pairs indicating the start and end indexes of matches in the original string.

```go
re := regexp.MustCompile(`b+`)
matches := re.FindAllString("ab bbb abbb", -1)
fmt.Println(matches) // [b bbb bbb]
```

### Capture Groups and Submatches

Parentheses `()` in a regular expression pattern define **capture groups**. When you perform a match, you can extract the exact sub-portions of the match:

```go
// Matching phone number: (123) 456-7890
phoneRE := regexp.MustCompile(`\((\d{3})\)\s*(\d{3})-(\d{4})`)

matches := phoneRE.FindStringSubmatch("My number is (800) 555-1212 today.")
// matches[0] = "(800) 555-1212" (full match)
// matches[1] = "800" (first capture group)
// matches[2] = "555" (second capture group)
// matches[3] = "1212" (third capture group)
```

We can use capture groups to easily reformat text using `ReplaceAllString`:

```go
// Reformat to international layout: +1 800-555-1212
result := phoneRE.ReplaceAllString("Call (800) 555-1212", "+1 $1-$2-$3")
fmt.Println(result) // "Call +1 800-555-1212"
```

---

## Chapter 14: Reference & Value Semantics

> 📊 **Slide Reference:** `slides/go-14-semantics-slides.pdf`

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

## Chapter 15: Networking with HTTP

> 📊 **Slide Reference:** `slides/go-15-http-slides.pdf`

Go was designed from the ground up for cloud computing, rest APIs, and microservices. Because of this, it has an incredibly robust, production-grade HTTP server and client built directly into the standard library via `net/http`.

### Writing a Simple Web Server

Here is a basic HTTP server that listens on port `8080` and echoes the URL path:

```go
package main

import (
    "fmt"
    "net/http"
    "strings"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    // Trim the leading slash from the path
    name := strings.TrimPrefix(r.URL.Path, "/")
    if name == "" {
        name = "World"
    }
    // Write the response directly into the ResponseWriter (which implements io.Writer)
    fmt.Fprintf(w, "Hello, %s!", name)
}

func main() {
    http.HandleFunc("/", helloHandler)
    // Starts the server. ListenAndServe block is blocking and handles connections concurrently.
    if err := http.ListenAndServe(":8080", nil); err != nil {
        panic(err)
    }
}
```

Go's HTTP server is fully concurrent. Under the hood, the server spawns a new goroutine for every TCP connection, allowing it to process thousands of requests simultaneously.

### Writing a Simple HTTP Client

We can make client requests using `http.Get`:

```go
resp, err := http.Get("http://localhost:8080/Matt")
if err != nil {
    log.Fatal(err)
}
// CRITICAL: Always close the response body!
defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
    log.Fatalf("received status: %s", resp.Status)
}

bodyBytes, err := io.ReadAll(resp.Body)
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(bodyBytes)) // "Hello, Matt!"
```

> ⚠️ **Resource Leak Danger:** You **must** close `resp.Body`. If you do not close it, the underlying TCP connection remains open, and the program will eventually leak sockets and crash when it runs out of file descriptors.

### Parsing JSON from a Response Body

If a network endpoint returns JSON, you can decode it directly from the response body. 

While you can read all bytes into memory with `io.ReadAll` and then call `json.Unmarshal`, it is cleaner and more memory-efficient to stream it directly using a `json.Decoder`:

```go
type Todo struct {
    ID        int    `json:"id"`
    Title     string `json:"title"`
    Completed bool   `json:"completed"`
}

resp, err := http.Get("https://jsonplaceholder.typicode.com/todos/1")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

var item Todo
// Decode directly from the streaming body reader
if err := json.NewDecoder(resp.Body).Decode(&item); err != nil {
    log.Fatal(err)
}

fmt.Printf("Todo ID %d: %q (Completed: %t)\n", item.ID, item.Title, item.Completed)
```

This works because `resp.Body` implements `io.ReadCloser` (which embeds `io.Reader`), and `json.NewDecoder` accepts any `io.Reader`.

---

## Chapter 16: Homework — xkcd Comic Indexer & Searcher

> 📊 **Slide Reference:** `slides/go-16-hw3-slides.pdf`

In this homework, we implement Exercise 4.12 from *The Go Programming Language* book. We will build an offline search tool for xkcd comics.

The project is split into two programs:
1. **`fetcher`**: Downloads the metadata for every comic sequentially using xkcd's JSON API and saves it to a single local file (`xkcd.json`) as a JSON array.
2. **`searcher`**: Reads the local `xkcd.json` index file, parses it, and searches for comics matching keywords provided as command-line arguments.

### Part 1: The Fetcher Program

The fetcher queries xkcd endpoints (e.g., `https://xkcd.com/123/info.0.json`) to collect comic metadata. It builds a JSON array file on disk incrementally.

```go
package main

import (
    "fmt"
    "io"
    "net/http"
    "os"
)

func getComicBytes(id int) ([]byte, error) {
    url := fmt.Sprintf("https://xkcd.com/%d/info.0.json", id)
    resp, err := http.Get(url)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("status %d", resp.StatusCode)
    }

    return io.ReadAll(resp.Body)
}

func main() {
    out, err := os.Create("xkcd.json")
    if err != nil {
        log.Fatal(err)
    }
    defer out.Close()

    // Write start of JSON array
    out.WriteString("[\n")

    fails := 0
    count := 0

    for id := 1; fails < 2; id++ {
        // xkcd has no comic #404 (an Easter egg returning 404 Not Found)
        // We skip single missing files but stop if we hit two consecutive failures.
        data, err := getComicBytes(id)
        if err != nil {
            fails++
            fmt.Fprintf(os.Stderr, "Skipping comic #%d (%v)\n", id, err)
            continue
        }
        fails = 0 // Reset consecutive failures on success

        if count > 0 {
            out.WriteString(",\n")
        }
        out.Write(data)
        count++
    }

    // Write end of JSON array
    out.WriteString("\n]")
    fmt.Printf("Downloaded %d comics.\n", count)
}
```

### Part 2: The Searcher Program

The searcher reads `xkcd.json`, unmarshals it into a slice of structs, and prints matching comics. It performs a case-insensitive check against both the title and the transcript.

```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "os"
    "strings"
)

type Comic struct {
    Num        int    `json:"num"`
    Title      string `json:"title"`
    Transcript string `json:"transcript"`
    Img        string `json:"img"`
    Year       string `json:"year"`
    Month      string `json:"month"`
    Day        string `json:"day"`
}

func main() {
    if len(os.Args) < 3 {
        fmt.Fprintln(os.Stderr, "Usage: searcher <index_file> <term1> <term2> ...")
        os.Exit(1)
    }

    filename := os.Args[1]
    searchTerms := os.Args[2:]

    // Open index file
    file, err := os.Open(filename)
    if err != nil {
        log.Fatal(err)
    }
    defer file.Close()

    // Decode entire index directly from file reader
    var comics []Comic
    if err := json.NewDecoder(file).Decode(&comics); err != nil {
        log.Fatal(err)
    }

    // Lowercase all search terms
    for i := range searchTerms {
        searchTerms[i] = strings.ToLower(searchTerms[i])
    }

    foundCount := 0

OuterLoop:
    for _, comic := range comics {
        titleLower := strings.ToLower(comic.Title)
        transcriptLower := strings.ToLower(comic.Transcript)

        // Comic must match ALL search terms
        for _, term := range searchTerms {
            if !strings.Contains(titleLower, term) && !strings.Contains(transcriptLower, term) {
                continue OuterLoop // Skip this comic entirely if any term is missing
            }
        }

        // Print match details
        fmt.Printf("Comic #%d: %s/%s/%s\n", comic.Num, comic.Month, comic.Day, comic.Year)
        fmt.Printf("Title: %s\n", comic.Title)
        fmt.Printf("Image: %s\n", comic.Img)
        fmt.Println(strings.Repeat("-", 40))
        foundCount++
    }

    fmt.Printf("Found %d matching comics.\n", foundCount)
}
```

Using labeled loop control (`continue OuterLoop`) allows us to cleanly prune results early as soon as any term fails to match, avoiding deep nested state logic.
