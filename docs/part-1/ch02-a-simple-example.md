## Chapter 2: A Simple Example

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-02-example1-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-02-example1-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="-EYNVEv-snE" chapter="02" />

Now I want to walk through a simple example of a program a little more complicated than Hello World. With that, we're also going to do some unit tests as a starting point.

### Command-Line Arguments

I'm going to go back to the Playground and start over with Hello World, but we're going to make it a little more complicated.

In some languages, the function `main` takes parameters that represent the command-line arguments, but Go doesn't do that. Instead, we're going to import another package — the `os` package — and use `os.Args`.

```go
package main

import (
    "fmt"
    "os"
)

func main() {
    if len(os.Args) > 1 {
        fmt.Println("Hello", os.Args[1])
    } else {
        fmt.Println("Hello, World!")
    }
}
```

What you get with `os.Args` is a list of parameters. We don't want the first one — the first one is indexed by zero, and on most systems the zeroth argument is the name of the program. So the first thing after the program you typed on the command line is `os.Args[1]`.

If there aren't any command-line arguments, this will crash because there is no `os.Args[1]`. That's why we check the length first with the `if` statement. If the length is greater than one, we use the argument. If not, we print the default "Hello, World!".

### Creating a Package

I'm going to create my own little package. It's going to include a function to do our greeting for us. I'll call it `hello.go`:

```go
package hello

import "fmt"

func Say(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}
```

Our little function takes a string and returns a string. One of the things I want to show here is that the parameter order — the type order — is after the variable name. If you're familiar with C-like languages, this actually goes all the way back to Fortran: first you give the type like `int` and then you give a name like `a`. But in Go, we do it in the order of languages like Pascal and Modula, where the type name comes afterwards. It turns out to be a little easier to parse that way, and it avoids one of the embarrassing mistakes that people make in C using pointers.

Now I'm going to modify the main program to import and use our package:

```go
package main

import (
    "fmt"
    "os"
    "hello"
)

func main() {
    if len(os.Args) > 1 {
        fmt.Println(hello.Say(os.Args[1]))
    } else {
        fmt.Println(hello.Say("World"))
    }
}
```

### Unit Testing

I want to add a test file. I'm going to call it `hello_test.go` using a Go convention — `_test.go`:

```go
package hello

import "testing"

func TestSay(t *testing.T) {
    want := "Hello, Test!"
    got := Say("Test")
    if got != want {
        t.Errorf("got %q, want %q", got, want)
    }
}
```

The test function starts with the word `Test` with an uppercase T, and these always take a pointer to a `testing.T`. They don't return anything — if I want to fail the test, I'm going to call something on `t` to make that happen.

The way I run tests is:

```bash
go test
```

If the tests pass, Go doesn't tell me anything because they passed. If I put a deliberate mistake in, it's going to fail and report that the test failed.

### Handling Multiple Arguments

I want to deal with more than one command-line argument. I want to be able to say `hello matt kathy adam`. So I'm going to make my `Say` function take a slice of strings:

```go
package hello

import "strings"

func Say(names []string) string {
    if len(names) == 0 {
        names = []string{"World"}
    }
    return "Hello, " + strings.Join(names, ", ") + "!"
}
```

I'm going to return a made-up string with the word "Hello," comma, and then I'm going to join the various names with commas between them and put an exclamation mark at the end. I need to import the `strings` package for the `Join` function.

Here's the thing about Go: we're not using `fmt` anymore, and because we're not using it, we're not allowed to import things we don't use. A Go file has to import everything it uses and nothing that it doesn't.

Now I need to update `main` as well:

```go
func main() {
    fmt.Println(hello.Say(os.Args[1:]))
}
```

This little expression — `os.Args[1:]` — says start with the second item till the end. It has a very neat property: if there isn't a second item, then it'll just be an empty slice of length zero, and it's perfectly legal. We won't crash the program because of that.

### Table-Driven Subtests

I want to build out my unit test with some subtests. This demonstrates a very useful technique in Go:

```go
func TestSay(t *testing.T) {
    subtests := []struct {
        items  []string
        result string
    }{
        {
            result: "Hello, World!",
        },
        {
            items:  []string{"Matt"},
            result: "Hello, Matt!",
        },
        {
            items:  []string{"Matt", "Kathy"},
            result: "Hello, Matt, Kathy!",
        },
    }

    for _, st := range subtests {
        got := Say(st.items)
        if got != st.result {
            t.Errorf("Say(%v) = %q, want %q", st.items, got, st.result)
        }
    }
}
```

The `subtests` variable has a type that is a slice of structures, and I'm creating it literally on the fly — it's anonymous, I didn't give it an actual type name. What's also interesting is I don't have to fill in all the fields. In the first subtest, `items` will be empty by default, and we should get the default behavior.

This is a good test — we've covered the special cases of zero, one, and more than one argument. I could try it with three or four, but it wouldn't really change anything.

### Go Modules

I want to circle back and do one more thing. We had a textbook that I recommended at the beginning, and I want to talk about what's changed since the textbook was printed. That book was published — well, it was probably written in 2014, when Go was three or four years old in terms of its public release from 1.0. There are some things in there that have changed.

If you go back and read the book, it's going to talk about this environment variable called `GOPATH`. It used to be that you had to install in your home directory, create a `go` directory, and under that create directories like `bin` and `src`, and your projects had to be under that.

That was confining. What's happened over time, from about Go 1.11 to 1.14, is `GOPATH` is there but it's vestigial. Instead, what we have is **Go modules**, and that was one of the big developments in helping people version and manage dependencies.

You create a directory, put a `go.mod` file in it, and create a module name for the stuff you're building:

```
module hello

go 1.16
```

Once you create that and then start building your software, you're fine. If you do pull in a third-party package, Go will automatically add it to your `go.mod` file and show that as a dependency at a certain version. With that, Go will be able to rebuild your software later.

The presence of a `go.mod` also allows you to ignore `GOPATH`. You can have a directory anywhere — I can create a directory in any arbitrary place, put a `go.mod` file in it, start building out my source, and I don't have to worry about setting a `GOPATH`. Go will know what to do with that file.
