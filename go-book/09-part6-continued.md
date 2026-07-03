# Part VI — Continued: Testing & Distribution

---

## Chapter 38: Testing & Mocking

> 📊 **Slide Reference:** `slides/go-38-testing-slides.pdf`

Go features a built-in testing framework that emphasizes clarity and simplicity. Tests reside alongside production code in files ending with `_test.go`. When building binaries for deployment, the compiler excludes these test files.

### 1. Basic Unit Tests

A test function must start with the prefix `Test`, accept a single pointer parameter of type `*testing.T`, and return no values.

```go
package crypto

import (
    "bytes"
    "testing"
)

func TestEncryptDecrypt(t *testing.T) {
    key1 := []byte("secret-key-16-bytes")
    key2 := []byte("wrong-key-16-bytes")
    plaintext := []byte("hello world")

    ciphertext, err := Encrypt(plaintext, key1)
    if err != nil {
        t.Fatalf("encryption failed: %v", err)
    }

    // Try decrypting with wrong key - should fail
    _, err = Decrypt(ciphertext, key2)
    if err == nil {
        t.Error("expected decryption to fail with incorrect key, but it succeeded")
    }

    // Decrypt with correct key
    decrypted, err := Decrypt(ciphertext, key1)
    if err != nil {
        t.Fatalf("decryption failed: %v", err)
    }

    if !bytes.Equal(decrypted, plaintext) {
        t.Errorf("decrypted plaintext mismatch: got %q, want %q", decrypted, plaintext)
    }
}
```

#### Error Reporting: `t.Error` vs. `t.Fatal`
- `t.Error` / `t.Errorf`: Logs an error message but continues executing the remaining lines of the test.
- `t.Fatal` / `t.Fatalf`: Logs an error message and stops executing the current test immediately.

---

### 2. Table-Driven Tests & Subtests

A **Table-Driven Test** defines a table of inputs and expected outputs as a slice of structs, then loops over them. Combining this with **Subtests** (`t.Run`) allows each case to run as a separate, named test with independent reporting.

```go
package calc

import (
    "testing"
)

func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -1, -2},
        {"identity property", 0, 5, 5},
    }

    for _, tc := range tests {
        // Run as an independent subtest
        t.Run(tc.name, func(t *testing.T) {
            result := Add(tc.a, tc.b)
            if result != tc.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tc.a, tc.b, result, tc.expected)
            }
        })
    }
}
```

---

### 3. Refactoring Large Tests Using Method Values

When test tables and logic loops grow excessively large, they obscure the test's intent. We can refactor them by defining a named struct for the test cases and writing the test logic as a method on that struct.

```go
package parser

import (
    "reflect"
    "testing"
)

// ScanTestCase defines the structure of a parser test case
type ScanTestCase struct {
    Name           string
    Input          string
    ExpectedTokens []string
}

// Run acts as the test execution template
func (tc ScanTestCase) Run(t *testing.T) {
    tokens, err := Scan(tc.Input)
    if err != nil {
        t.Fatalf("scan failed: %v", err)
    }
    if !reflect.DeepEqual(tokens, tc.ExpectedTokens) {
        t.Errorf("mismatched tokens:\n got: %v\nwant: %v", tokens, tc.ExpectedTokens)
    }
}

func TestScanner(t *testing.T) {
    cases := []ScanTestCase{
        {
            Name:           "simple addition",
            Input:          "1 + 2",
            ExpectedTokens: []string{"INT", "PLUS", "INT"},
        },
        {
            Name:           "parentheses priority",
            Input:          "(3 * 4)",
            ExpectedTokens: []string{"LPAREN", "INT", "MULT", "INT", "RPAREN"},
        },
    }

    for _, tc := range cases {
        // tc.Run is a Method Value bound to the specific case instance
        t.Run(tc.Name, tc.Run)
    }
}
```

---

### 4. Mocking External Interfaces (e.g. Database)

Unit tests must be self-contained and run quickly. They should avoid hitting actual external resources (like cloud databases or message queues). Instead, we declare interfaces at our boundary and inject mock implementations.

```go
package store

import "errors"

// DB is the data access layer interface
type DB interface {
    GetItem(id string) (string, error)
}

// Service uses the database
type Service struct {
    db DB
}

func (s *Service) FetchProduct(id string) (string, error) {
    if id == "" {
        return "", errors.New("empty id")
    }
    return s.db.GetItem(id)
}
```

To test the `Service` layer without a real database, we create a `MockDB`:

```go
package store

import "testing"

type MockDB struct {
    ShouldFail bool
    MockData   map[string]string
}

func (m *MockDB) GetItem(id string) (string, error) {
    if m.ShouldFail {
        return "", errors.New("database connection failed")
    }
    val, ok := m.MockData[id]
    if !ok {
        return "", errors.New("item not found")
    }
    return val, nil
}

func TestFetchProduct(t *testing.T) {
    mock := &MockDB{
        MockData: map[string]string{"p1": "Book"},
    }
    svc := Service{db: mock}

    // Test Happy Path
    val, err := svc.FetchProduct("p1")
    if err != nil || val != "Book" {
        t.Errorf("expected Book, got %q (%v)", val, err)
    }

    // Test Database Failure case
    mock.ShouldFail = true
    _, err = svc.FetchProduct("p1")
    if err == nil {
        t.Error("expected database failure error, but got nil")
    }
}
```

---

### 5. Setup & Teardown with `TestMain`

If a package needs global setup (like starting local emulators, populating test databases, or clearing cache dirs) before any tests run, define a `TestMain` function:

```go
package integration

import (
    "fmt"
    "os"
    "testing"
)

func TestMain(m *testing.M) {
    // 1. Setup phase (e.g. start local Redis emulator)
    fmt.Println("Starting test environment/emulators...")
    err := startDatabaseEmulator()
    if err != nil {
        fmt.Printf("Setup failed: %v\n", err)
        os.Exit(1)
    }

    // 2. Run all tests in the package
    exitCode := m.Run()

    // 3. Teardown phase
    fmt.Println("Cleaning up emulators...")
    stopDatabaseEmulator()

    // 4. Terminate process with appropriate exit code
    os.Exit(exitCode)
}

func startDatabaseEmulator() error {
    // Emulator startup logic
    return nil
}

func stopDatabaseEmulator() {
    // Clean-up logic
}
```

---

### 6. External Tests (`package_test`)

By default, tests are in the same package as the source code (e.g., `package calc`), granting them access to private fields and functions. 

However, to prevent import cycle loops or to test a package purely through its public API, we suffix the package name with `_test` in the test file (e.g., `package calc_test` inside `calc_test.go`). This treats the test file as a consumer, allowing it to import only the public interface.

---

## Chapter 39: Code Coverage

> 📊 **Slide Reference:** `slides/go-39-coverage-slides.pdf`

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

## Chapter 40: Dependency Management & Go Modules

> 📊 **Slide Reference:** `slides/go-40-modules-slides.pdf`

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

## Chapter 41: Building & Deploying Go Programs

> 📊 **Slide Reference:** `slides/go-41-build-slides.pdf`

Go compiles code into self-contained binaries. Understanding compilation options and containment strategies simplifies deployments.

### 1. Building Statically Linked Executables

By default, Go binaries may dynamically link to C library dependencies (like `libc`). To generate a statically linked binary with no external runtime dependencies:

```powershell
go build -tags netgo -ldflags '-extldflags "-static"' -o app.exe main.go
```
- `-tags netgo`: Uses Go's native DNS resolver instead of C libraries.
- `-ldflags '-extldflags "-static"'`: Forces static linking on external links.

---

### 2. Cross-Compilation

Go's compiler natively supports cross-compilation. By setting `GOOS` (target OS) and `GOARCH` (target CPU architecture), we can compile binaries for other platforms:

```powershell
# Compile a Linux binary from a Windows machine
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o app-linux main.go

# Compile for a 32-bit Raspberry Pi
$env:GOOS="linux"
$env:GOARCH="arm"
$env:GOARM="7"
go build -o app-rpi main.go
```

---

### 3. Versioning Binaries Using Linker Flags (`-X`)

Baking version tags or git commit hashes into the compiled binary helps identify what code is running in production.

#### Production Code (`main.go`)
```go
package main

import "fmt"

// Declared but uninitialized package-level variable
var Version = "unknown"

func main() {
    fmt.Printf("App version: %s\n", Version)
}
```

#### Injecting Values at Build Time
Using the `-ldflags "-X ..."` flag, we write a string value directly into the target package variable:

```powershell
# 1. Fetch current git description version string
$GIT_VER = git describe --tags --always --dirty

# 2. Link version variable directly into the executable
go build -ldflags "-X main.Version=$GIT_VER" -o app.exe main.go
```

---

### 4. standard Project Layout

Go projects organize packages logically to keep directories clean.

```
project-root/
│
├── cmd/                          # Entrypoints / main packages
│   ├── app/
│   │   └── main.go
│   └── cron/
│       └── main.go
│
├── pkg/                          # Shared library code
│   ├── calc/
│   │   ├── calc.go
│   │   └── calc_test.go
│   └── store/
│       └── store.go
│
├── build/                        # Dockerfiles and configurations
│   └── Dockerfile
│
├── go.mod
├── go.sum
└── Makefile
```

---

### 5. Multi-Stage Docker Builds

A multi-stage Dockerfile uses one heavy container (with the compiler and dependencies) to build the program, then copies the compiled binary into a lightweight container (like `busybox` or `scratch`).

This keeps target deployment images tiny (e.g. 15–30 MB) and secure, as they exclude development utilities.

```dockerfile
# --- Stage 1: Build Environment ---
FROM golang:1.16-alpine AS builder

# Add certificates and timezone database
RUN apk update && apk add --no-cache ca-certificates tzdata

# Create build user
ENV USER=appuser
ENV UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    "${USER}"

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

# Copy source code files
COPY . .

# Argument to pass git version
ARG APP_VERSION=unknown

# Build statically-linked binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags "-w -s -X main.Version=${APP_VERSION}" \
    -o /app/bin/server ./cmd/app/main.go

# --- Stage 2: Final Runtime ---
FROM busybox:stable-musl

WORKDIR /

# Import system users, SSL certificates, and timezones from builder stage
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Copy compiled executable
COPY --from=builder /app/bin/server /server

# Run as non-root user
USER appuser:appgroup

EXPOSE 8080

ENTRYPOINT ["/server"]
```
