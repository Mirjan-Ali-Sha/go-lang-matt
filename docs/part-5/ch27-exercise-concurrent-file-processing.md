## Chapter 27: Exercise — Concurrent File Processing

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-27-walk-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-27-walk-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="SPD7TykYy5w" chapter="27" />

In this chapter, we take a sequential program and refactor it into a high-performance concurrent application using the CSP (Communicating Sequential Processes) model.

### The Problem: Finding Duplicate Files

Suppose we have a large directory structure (e.g., a Dropbox folder with 50,000+ files) containing duplicate files with different names or timestamps. To find duplicates by their actual byte content, we must compute a secure cryptographic hash (such as MD5) of every file.

We represent the hash as a `string` (so it can be used as a map key) and group files by their hash in a `map[string][]string`.

#### 1. The Sequential Implementation

The standard library `path/filepath` package provides `filepath.Walk`, which recursively visits every file and directory under a starting path using a visitor closure.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
)

type FilePair struct {
    Path string
    Hash string
}

func hashFile(path string) (FilePair, error) {
    f, err := os.Open(path)
    if err != nil {
        return FilePair{}, err
    }
    // Defer close immediately after successful open to avoid leaking file descriptors
    defer f.Close()

    h := md5.New()
    if _, err := io.Copy(h, f); err != nil {
        return FilePair{}, err
    }

    hashStr := fmt.Sprintf("%x", h.Sum(nil))
    return FilePair{Path: path, Hash: hashStr}, nil
}

func searchTree(dir string) (map[string][]string, error) {
    results := make(map[string][]string)

    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        // Process regular non-empty files only
        if info.Mode().IsRegular() && info.Size() > 0 {
            pair, err := hashFile(path)
            if err != nil {
                return err
            }
            results[pair.Hash] = append(results[pair.Hash], pair.Path)
        }
        return nil
    }

    err := filepath.Walk(dir, visit)
    return results, err
}
```

Running this sequentially on a large drive is slow because it is bound by disk read latency and sequential hashing CPU usage.

---

###Refactoring 1: The Worker Pool Model

The worker pool model splits the work into three parts:
1. **The Generator (Main Thread):** Walks the directory tree and sends file paths down a channel.
2. **The Worker Pool (Goroutines):** A fixed number of goroutines read paths, read/hash the files, and send `FilePair` results down a pairs channel.
3. **The Collector (Goroutine):** Rages over the pairs channel and inserts them into the final map.

```
                  [Paths Channel]
                        |
            +-----------+-----------+
            |           |           |
        [Worker 1]  [Worker 2]  [Worker 3]  (Fixed Pool)
            |           |           |
            +-----------+-----------+
                        |
                  [Pairs Channel]
                        |
                  [Collector] ---> [Results Channel]
```

#### Synchronization Rules for the Worker Pool
- The main thread closes the `paths` channel when the directory walk is finished.
- When the `paths` channel closes, the workers finish their remaining work and signal completion on a shared `done` channel.
- The main thread reads from the `done` channel exactly $N$ times (where $N$ is the number of workers) to know all workers have exited.
- Once all workers are finished, the main thread safely closes the `pairs` channel.
- The `collector` finishes ranging over `pairs`, sends the final map down the `results` channel, and exits.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "runtime"
)

type FilePair struct {
    Path string
    Hash string
}

func hashWorker(paths <-chan string, pairs chan<- FilePair, done chan<- bool) {
    for path := range paths {
        f, err := os.Open(path)
        if err != nil {
            continue
        }
        h := md5.New()
        _, err = io.Copy(h, f)
        f.Close()
        if err != nil {
            continue
        }
        pairs <- FilePair{Path: path, Hash: fmt.Sprintf("%x", h.Sum(nil))}
    }
    done <- true
}

func collectHashes(pairs <-chan FilePair, results chan<- map[string][]string) {
    hashes := make(map[string][]string)
    for pair := range pairs {
        hashes[pair.Hash] = append(hashes[pair.Hash], pair.Path)
    }
    results <- hashes
}

func searchConcurrent(dir string) map[string][]string {
    // Determine pool size based on logical CPU cores
    numWorkers := runtime.NumCPU() * 2
    
    paths := make(chan string)
    pairs := make(chan FilePair, 100) // Buffered to remove friction
    done := make(chan bool)
    results := make(chan map[string][]string)

    // Start collector
    go collectHashes(pairs, results)

    // Start workers
    for i := 0; i < numWorkers; i++ {
        go hashWorker(paths, pairs, done)
    }

    // Walk directory and feed paths
    filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
        if err == nil && info.Mode().IsRegular() && info.Size() > 0 {
            paths <- path
        }
        return nil
    })
    close(paths) // Signal workers to stop

    // Wait for all workers to finish
    for i := 0; i < numWorkers; i++ {
        <-done
    }
    close(pairs) // Signal collector we are done

    return <-results
}
```

---

### Refactoring 2: Parallel Directory Traversals

To speed up path discovery, we can walk directories in parallel. Since the number of subdirectories is unknown, we cannot use a fixed-size loop. Instead, we use `sync.WaitGroup` to coordinate completion.

We start a goroutine for each directory. In the visitor function:
- If a visitor encounters a subdirectory, it increments the WaitGroup (`wg.Add(1)`), spawns a new goroutine to walk that subdirectory, and returns `filepath.SkipDir` to prevent the current walker from descending into it.

```go
package main

import (
    "os"
    "path/filepath"
    "sync"
)

func walkDir(dir string, wg *sync.WaitGroup, paths chan<- string) {
    defer wg.Done()

    // visit closure captures the WaitGroup and paths channel
    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return nil
        }
        if info.IsDir() && path != dir {
            // Found a subdirectory: spawn a new walk routine
            wg.Add(1)
            go walkDir(path, wg, paths)
            return filepath.SkipDir // Do not descend on this routine
        }
        if info.Mode().IsRegular() && info.Size() > 0 {
            paths <- path
        }
        return nil
    }

    filepath.Walk(dir, visit)
}
```

---

### Refactoring 3: A Goroutine per File (Counting Semaphore)

What if we spawn a goroutine for *every* file? If we do this naively on a directory tree with 50,000 files, the operating system will crash because it will exceed the limit of open file descriptors or active OS threads (typically 1,000 per process).

To prevent this, we use a **Counting Semaphore** (implemented via a buffered channel) to limit active disk I/O operations, while still spawning goroutines freely.

```go
package main

import (
    "crypto/md5"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "sync"
)

type FilePair struct {
    Path string
    Hash string
}

func processFile(path string, wg *sync.WaitGroup, limits chan bool, pairs chan<- FilePair) {
    defer wg.Done()

    limits <- true // Acquire token (blocks if buffer is full)
    defer func() { <-limits }() // Release token when function exits

    f, err := os.Open(path)
    if err != nil {
        return
    }
    defer f.Close()

    h := md5.New()
    if _, err := io.Copy(h, f); err != nil {
        return
    }
    pairs <- FilePair{Path: path, Hash: fmt.Sprintf("%x", h.Sum(nil))}
}

func walkDir(dir string, wg *sync.WaitGroup, limits chan bool, pairs chan<- FilePair) {
    defer wg.Done()

    limits <- true // Walk directories within resource limits too
    defer func() { <-limits }()

    visit := func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return nil
        }
        if info.IsDir() && path != dir {
            wg.Add(1)
            go walkDir(path, wg, limits, pairs)
            return filepath.SkipDir
        }
        if info.Mode().IsRegular() && info.Size() > 0 {
            wg.Add(1)
            go processFile(path, wg, limits, pairs)
        }
        return nil
    }
    filepath.Walk(dir, visit)
}

func search(dir string) map[string][]string {
    var wg sync.WaitGroup
    limits := make(chan bool, 32) // Allow maximum 32 active disk operations
    pairs := make(chan FilePair, 100)
    results := make(chan map[string][]string)

    // Start collector
    go func() {
        hashes := make(map[string][]string)
        for pair := range pairs {
            hashes[pair.Hash] = append(hashes[pair.Hash], pair.Path)
        }
        results <- hashes
    }()

    wg.Add(1)
    go walkDir(dir, &wg, limits, pairs)

    wg.Wait() // Wait for all directories and files to finish
    close(pairs)

    return <-results
}
```

### Amdahl's Law

Refactoring a program to run concurrently does not yield linear performance speedups forever. **Amdahl's Law** states that the maximum speedup $S$ of a program is limited by the sequential fraction of that program ($1 - P$):

$$S = \frac{1}{(1 - P) + \frac{P}{s}}$$

Where:
- $P$ is the parallelizable fraction of the program.
- $s$ is the speedup factor of the parallel part (typically the number of CPU cores).

If $5\%$ of a program must run sequentially (such as final collection into a map, file path generation, or filesystem lookup), the maximum theoretical speedup is $20\text{x}$, even with an infinite number of processors. In practice, I/O bottlenecks (SATA/NVMe drive read limit) will cap the performance benefits much earlier.

---
