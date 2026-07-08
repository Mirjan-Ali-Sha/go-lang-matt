## Chapter 53: Handling Files with the Go Standard Library

<VideoPlayer videoId="ctmhYJpGsgU" chapter="53" />  
> 🔗 **Source Code:** [GitHub - Episode 10 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_10)

Microservice architectures separate responsibilities. We construct a dedicated file storage service to handle, store, and serve image uploads independently of the primary database logic.

### 1. Writing the File Store Utility (`files/local.go`)
We implement a local file storage utility that creates path directories dynamically and writes file streams to disk safely.

```go
package files

import (
    "io"
    "os"
    "path/filepath"
)

type Local struct {
    maxFileSize int
    basePath    string
}

func NewLocal(basePath string, maxFileSize int) (*Local, error) {
    return &Local{basePath: basePath, maxFileSize: maxFileSize}, nil
}

func (l *Local) Save(path string, r io.Reader) error {
    // Construct target file path
    fp := filepath.Join(l.basePath, path)
    
    // Ensure parent directories exist
    err := os.MkdirAll(filepath.Dir(fp), os.ModePerm)
    if err != nil {
        return err
    }

    // If file exists, delete it first
    os.Remove(fp)

    // Create target file
    f, err := os.Create(fp)
    if err != nil {
        return err
    }
    defer f.Close()

    // Stream write from reader
    _, err = io.Copy(f, r)
    return err
}
```

### 2. Designing the File Upload Handler (`handlers/files.go`)
We define a handler to handle HTTP PUT requests containing raw file streams.

```go
package handlers

import (
    "net/http"
    "path/filepath"
    "files"
)

type Files struct {
    store files.Storage
}

func NewFiles(s files.Storage) *Files {
    return &Files{store: s}
}

func (f *Files) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Extract file name from URL path
    fn := filepath.Base(r.URL.Path)
    if fn == "." || fn == "/" {
        http.Error(w, "Invalid filename", http.StatusBadRequest)
        return
    }

    // Save the file stream directly from r.Body
    err := f.store.Save(fn, r.Body)
    if err != nil {
        http.Error(w, "Failed to save file", http.StatusInternalServerError)
        return
    }

    w.Write([]byte("File uploaded successfully"))
}
```
