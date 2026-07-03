## Chapter 1: Hello World

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-01-hello-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-01-hello-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="A9HfEhvpOEY" chapter="01" />

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
