## Chapter 11: Exercise — HTML Word & Image Counter

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-11-hw2-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-11-hw2-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="CR4OYGxaie8" chapter="11" />

In this segment I'm not going to introduce any new material. Instead, I want to take one of the exercises out of *The Go Programming Language* book — Exercise 5.5 — and we're going to work through it with a small modification.

The exercise is to get some HTML, parse it, and count the words and images. Instead of going out on the network (we haven't done that yet), I'm going to copy a snippet of HTML into the program as a raw string.

### The Program

```go
package main

import (
    "bytes"
    "fmt"
    "os"
    "strings"

    "golang.org/x/net/html"
)

const rawHTML = `<html><body>
<h1>My Page</h1>
<p>My first paragraph</p>
<p>My second paragraph has <b>bold</b> text</p>
<img src="photo.jpg">
</body></html>`

func main() {
    r := bytes.NewReader([]byte(rawHTML))
    doc, err := html.Parse(r)
    if err != nil {
        fmt.Fprintf(os.Stderr, "parse failed: %s\n", err)
        os.Exit(1)
    }
    words, pics := countWordsAndImages(doc)
    fmt.Printf("%d words, %d images\n", words, pics)
}
```

We take the raw string, convert it to a byte slice, create a reader around it so the HTML parser can treat it the same way it would treat a network socket. The `golang.org/x/net/html` package is from the extended standard library.

### The Counting Functions

The strategy is recursive: visit every node in the HTML tree, count text nodes as words and element nodes with tag `img` as images.

```go
func countWordsAndImages(doc *html.Node) (int, int) {
    var words, pics int
    visit(doc, &words, &pics)
    return words, pics
}

func visit(n *html.Node, pWords, pPics *int) {
    if n.Type == html.TextNode {
        *pWords += len(strings.Fields(n.Data))
    } else if n.Type == html.ElementNode && n.Data == "img" {
        *pPics++
    }

    for c := n.FirstChild; c != nil; c = c.NextSibling {
        visit(c, pWords, pPics)
    }
}
```

The `countWordsAndImages` function is a "landing spot" — it creates the two accumulator variables and passes their pointers into the recursive `visit` function. This way, every call to `visit` modifies the same `words` and `pics`.

The tree traversal is **depth-first**: we go to the first child, and if it has a first child, we go there too — going as deep as we can, then up and over.

The `strings.Fields(n.Data)` call breaks text into words (splitting on whitespace), and `len()` gives us the word count.

> 💡 **Exercise Extension:** If you pull a real web page, you'll discover text nodes that contain JavaScript. You'll need to add logic to skip those subtrees, or you'll get an enormous word count from embedded scripts.
