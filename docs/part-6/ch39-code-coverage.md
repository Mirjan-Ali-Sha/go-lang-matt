## Chapter 39: Code Coverage

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-39-coverage-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-39-coverage-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="HfCsfuVqpcM" chapter="39" />

Code coverage measures the percentage of statements executed by your test suite. Go provides native statement-level coverage tools.

### 1. Generating & Viewing Coverage Reports

To calculate coverage directly:
```powershell
go test -cover
```

To export statement profiling data and generate an interactive HTML report:
```powershell
# 1. Output coverage records to a file
go test -coverprofile=c.out

# 2. Convert coverage record to HTML and launch it in the web browser
go tool cover -html=c.out
```

---

### 2. Statement Heat Maps

Go can track execution frequency to build a statement heat map.

Run coverage with a count mode:
```powershell
go test -covermode=count -coverprofile=c.out
```

When opened in `go tool cover -html`, statements are color-coded:
- **Red:** Uncovered code.
- **Gray:** Non-statement code (declarations, brackets).
- **Light Green:** Low-frequency execution paths.
- **Bright Green:** High-frequency/hotspot execution paths.

This visualization identifies untested branches and error-handling fallback blocks. However, **100% coverage does not mean your code works**. Writing bad assertions can yield high coverage without verifying correctness.

---
