## Chapter 40: Dependency Management & Go Modules

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-40-modules-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-40-modules-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="_N6BxmbLYBk" chapter="40" />

Go Modules manage dependencies, version selection, and reproducibility.

### 1. The Module Files: `go.mod` and `go.sum`

- **`go.mod`:** Defines the module path (identity) and lists direct/indirect dependency packages with their versions.
- **`go.sum`:** Contains cryptographic checksums of each downloaded dependency version. This verifies that future builds fetch the exact same source bytes.

```go
// Example go.mod file
module github.com/user/myproject

go 1.16

require (
    github.com/google/uuid v1.3.0
    github.com/sirupsen/logrus v1.8.1 // indirect
)
```

---

### 2. Dependency Philosophy: Copying vs. Importing

Go values simple dependencies:
> "A little copying is better than a little dependency." — Go Proverb

Adding a dependency introduces security risks, build chain delays, and maintenance debt. Consider copying simple utility routines instead of importing large external packages.

---

### 3. Modifying Module Versions

Common module commands:
```powershell
# Initialize a new module in the current directory
go mod init github.com/username/projectname

# Resolve, download missing dependencies, and prune unused ones
go mod tidy

# Upgrade all dependencies to their latest patch versions
go get -u ./...

# Force a dependency to a specific version or commit
go get github.com/google/uuid@v1.2.0
```

#### Vendoring
To copy all dependencies locally into the project root (e.g. for offline builds or air-gapped CI environments), run:
```powershell
go mod vendor
```

---

### 4. Handling Private Modules

If dependencies reside in private repositories (like corporate servers), Go must bypass public proxy servers and checksum databases.

Configure environment variables:
```powershell
# Bypass the default proxy for these domains
go env -w GOPRIVATE="github.com/mycompany/*,gitlab.com/myteam/*"
```
This automatically configures `GONOPROXY` and `GONOSUMDB` for these private paths.

---
