## Chapter 37: Static Analysis & Linting

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-37-static-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-37-static-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="GyoMEerSd0I" chapter="37" />

Static Analysis (or linting) is the inspection of code without executing it. It provides automatic guardrails to verify code correctness and style consistency before checking it into source control.

### 1. Key Linting Tools in Go

| Tool | Focus | Description |
| :--- | :--- | :--- |
| `gofmt` / `goimports` | Formatting | Standardizes whitespace, syntax brackets, and handles auto-formatting imports. |
| `go vet` | Correctness | Checks for common compiler-legal bugs (e.g. format verb mismatches in printf, copying mutexes, unkeyed struct initializers). |
| `ineffassign` | Correctness | Detects variables that are written to but never read before being overwritten. |
| `gosimple` | Style | Suggests simplifications (e.g. replacing `if x == true` with `if x`). |
| `gocyclo` | Complexity | Measures cyclomatic complexity of functions based on logic branches. |

---

### 2. Multi-Linter runner: `golangci-lint`

Instead of running separate tools, the Go community uses `golangci-lint`, a unified runner that coordinates dozens of linters concurrently.

#### Example Config (`.golangci.yml`)
Create a configuration file in the project root to manage active linters:

```yaml
linters:
  enable:
    - errcheck      # Checks that returned errors are handled
    - govetted      # Runs go vet
    - ineffassign   # Detects unused assignments
    - staticcheck   # Applies advanced static analysis checks
    - gocyclo       # Warns about high-complexity methods
    - unused        # Finds unused variables/constants/functions
linters-settings:
  gocyclo:
    min-complexity: 15 # Flag functions with complexity score > 15
```

#### Running golangci-lint
```powershell
golangci-lint run
```

---

### 3. Common Static Errors Detected

#### Ineffectual Assignment (Shadowing / Overwriting)
```go
func parseData(r io.Reader) error {
    data, err := ioutil.ReadAll(r)
    // err is assigned but never checked before overwriting below
    
    data, err = decrypt(data) 
    if err != nil {
        return err
    }
    return nil
}
```
*Linter output:* `[ineffassign] ineffectual assignment to err`

#### Printf Verb Mismatches
```go
package main

import "fmt"

func main() {
    count := 42
    fmt.Printf("Count is: %s\n", count) // %s expects string, got int
}
```
*Linter output:* `[govet] printf: Printf format %s has arg count of wrong type int`
