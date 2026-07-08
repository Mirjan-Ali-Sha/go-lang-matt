## Chapter 41: Building & Deploying Go Programs

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-41-build-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-41-build-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="rXgUP_BNyaI" chapter="41" />

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
