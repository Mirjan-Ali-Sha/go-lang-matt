## Chapter 16: Homework — xkcd Comic Indexer & Searcher

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-16-hw3-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-16-hw3-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="mFB6_sOiggI" chapter="16" />

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
