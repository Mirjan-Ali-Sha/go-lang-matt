# Part I — Getting Started

---

## Chapter 0: Introduction & Why Use Go

> 📊 **Slide Reference:** `slides/go-00-intro-slides.pdf`

Before I get into Go, I'd like to answer the question: why use Go?

There are really a couple of reasons to pick Go. One is that it's a simple and readable language that makes software engineering easier. The other is that it makes software perform better in the cloud.

### Software Engineering

Let me talk about the software engineering part first. What is software engineering? Well, it's really about programming in the large — programming with lots of time and lots of people. We need programs that are reliable and maintainable. We need to be able to change them over the years. We need to go back and read what we wrote in the past. We need to be able to hire new people and have them come on and understand our programs quickly. We don't want to be clever.

There's a phrase, "to out-clever yourself," and it really reminds me of the Roadrunner cartoon. Wile E. Coyote, Super Genius — he's constantly building traps to try to catch the Road Runner, usually with dynamite, and constantly blowing himself up. We don't want to go down that road. That's why we want to do things that are simple. Simplicity is the key to building good software.

To do that, it's not enough to write a simple program — we need to use a language that's simple and readable, because we spend a lot of time reading programs. A lot of languages like C++ just keep growing. Every few years a whole bunch more features get dumped in, and over time it just becomes harder and harder to understand, or you get different versions of code written in different versions of the language.

Go was designed from the get-go to be easy to use. It was designed, as this quote says from the original Go FAQ, to be as easy to use as some dynamically typed interpreted languages but to have the safety and speed of a compiled language.

Simplicity has been one of the key design criteria from the beginning, and the focus of the last ten or eleven years has been on keeping it simple and improving the runtime and the tools — making garbage collection better, not dumping new features into the language.

I really want to call out this quote by Erik that Go is a language that fits in your head. The benefit of that is instead of using a language subset or constantly turning to experts, Go is a language that's open to new people coming into the field. It's a language that's easy to learn and easy to use, and actually perfectly suitable as an introductory programming language for learning to code.

John Bodner wrote this blog post, "Go is Boring," and it turned into a GopherCon 2020 presentation. The key point is that simplicity is a key language feature all by itself. We talk about does the language have this or that or the other, but it's really about what the language *doesn't* have that helps make it so powerful.

### Performance in the Cloud

Now I want to flip to the other side and talk about the changes that have happened over the last fifteen years. If I draw a line on this chart about 2005, we see that cores don't get faster — instead we get more cores per CPU.

Unfortunately, a lot of the languages and techniques for building software that we have come from the other side of this line. The popular languages today — and it doesn't matter the order, it depends on what survey you look at — they're all about twenty years old or more. We can actually even say they're from the last century. They date from a time when machines had one CPU with one core, they were getting faster every year, and concurrency and distributed programming were research topics, not practical necessities.

Going forward, there's really only a couple of ways to make software faster. We can either make it concurrent to take advantage of those cores, or we can make it suck less — and by that I really mean we can waste less.

There's a saying that "the cloud doesn't exist — it's just somebody else's computer." Well, yes, and my point would be you rent it by the hour, by the second, whatever. So if Go can run significantly faster — and against some languages we're talking an order of magnitude faster — you're going to save an enormous amount of rent.

I don't want to point the finger at any particular language (in this case it's Ruby), but if you look at some of the interpreted languages — when I was younger, back in the '80s, nobody would have built production software in an interpreted language. Then over time we ended up with CPU cycles we thought we could waste. The reality is we can't waste them anymore, and so it's probably time to go back and think about: yes, we do want software that's simple, but we also want software that doesn't waste.

### Go in the Cloud

Go is becoming the go-to language for cloud development, particularly infrastructure but also apps. Performance is one aspect. There's another one, and that is that Go is simple to deploy. You can put a Go program by itself in a container. You don't need a JVM or an interpreter. You don't need libc or the rest of what typically shows up in an operating system. What that means is the container is very small, and it's also going to be more secure because you've just left out an enormous source of vulnerabilities.

I think this quote from the Bitly engineering blog really helps drive some of the key points here: it's a language that's easy to use, it's fast, it's safe, and it comes with tools that make software engineering easier. Now, I can't promise that Bitly is still doing Go or is still excited — time moves on — but I think it was a really good blog article when it was written, because it captures the things that are still true today, that these things are still valuable when you contrast Go against some of the other popular languages for cloud development.

I want to offer you this quote from the late Dennis Ritchie, inventor of the C language:

> *"A programming language that doesn't have everything can be easier to use than one that does."*

I think that's again a pretty valuable reason to pick Go.

---

## Chapter 1: Hello World

> 📊 **Slide Reference:** `slides/go-01-hello-slides.pdf`

I want to start by talking about the simplest program.

### The Go Playground

I'm going to start by using the Go Playground. I'm not going to install Go yet — I'm just going to use this very simple environment that the Go team provided us. I'm going to go to `play.golang.org` and make a small change. We'll call this "Hello World" — that's the prototypical original program. I'm just going to click the Run button, and when I do that, the program actually executes and provides some output right in the web browser.

The Playground is great for running simple programs, but it has a couple of limitations. It's really all about I/O — you can't read or write a file, you can't open a network socket, run a web server, anything like that. Of course, part of that's for security.

The Playground is actually useful in another context. If we go to the Go documentation page and look at the packages — the standard library — we'll find the `fmt` package that does formatted I/O. If we look at examples, we can click on an example and we get a description of the `Println` function, but it has an example that builds in the Playground. I can actually run that example just by clicking on the Run button. And it's editable — I can actually change this program.

### Understanding the Simple Program

Now I want to talk about this simple program that we just wrote, because I want to explain a couple things.

First of all, every program has to have a `main` function, and that tells Go where the program starts. It always starts in the `main` function.

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

Go is a modular language — we can put the program in different files and compile it together, which is different from when I was a kid when the program had to be in one big file (or in my case, one big stack of punch cards). In Go, we can put different parts of the program into packages, but the `main` function has to be in a `package main`. So we need this declaration at the top that says, "Hey, this file is going to be part of package main."

The other thing we need to do is import any package we use. We looked at the `fmt` package and `Println` — in order to use it, we need an import. We import the `fmt` package, and then when we call it, we call `fmt.Println` — we put `fmt` in front of it, so we're calling the package dot the function name.

There's a connection between importing `fmt` and using `fmt`. There's a connection between declaring a `main` function and putting it in `package main`. Those all go together. And the only other thing to point out is the `func` keyword that we put in front of a function declaration.

### Other Environments

There's another online environment that's very convenient called Replit, and it has one advantage: you can actually write a program that does I/O. You can read or write files, open a socket, or read from the console. So it's a little more sophisticated than the Playground environment.

### Installing Go

I want to briefly mention how to install Go. I'm not going to go into details — you go to the Go downloads page and there's instructions there. I typically use Homebrew on a Mac, so I just do `brew install go`. For Linux, you can download a gzip tar file and install that with `sudo`, and it puts things in the right place, but then you still have to remember to modify your `PATH`.

Once we've installed Go on our laptop, we can run from the command line. I can create an arbitrary directory, copy my little `main.go` program with Hello World in it, and then just do:

```bash
go run .
```

Which says "run what's in this directory." This is enough for a simple program that uses the standard library. If we want to use third-party software, we're going to have to do a bit more work, and I'm not ready to talk about that yet.

The other thing about `go run` is that it both compiles and runs your program — it compiles it, sticks it in some temp directory, runs it, and then gets rid of what's left over. Later on I'll talk about how to actually build a program that we want to deploy as a binary, either by itself or put it into a container.

---

## Chapter 2: A Simple Example

> 📊 **Slide Reference:** `slides/go-02-example1-slides.pdf`

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
