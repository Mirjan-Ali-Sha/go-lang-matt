## Chapter 38: Testing & Mocking

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-38-testing-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-38-testing-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="PIPfNIWVbc8" chapter="38" />

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
