## Chapter 7: Formatted & File I/O

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-07-io-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-07-io-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="dqEtGT-dxoY" chapter="07" />

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
