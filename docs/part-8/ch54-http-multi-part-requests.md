## Chapter 54: HTTP Multi-Part Requests

<VideoPlayer videoId="_7-IhHMptNo" chapter="54" />  
> 🔗 **Source Code:** [GitHub - Episode 11 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_11)

Raw PUT streams only upload one file at a time. To support complex form submissions (like metadata alongside files), we implement multi-part form handling.

### 1. Reading Multi-Part Payloads
Instead of caching the entire payload in RAM, we stream parts sequentially using Go's `mime/multipart` package.

```go
package handlers

import (
    "io"
    "net/http"
    "files"
)

type Multipart struct {
    store files.Storage
}

func (mp *Multipart) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // Parse the multipart form, allocating max 2MB in memory buffer
    err := r.ParseMultipartForm(128 * 1024 * 1024) // 128MB max payload
    if err != nil {
        http.Error(w, "Expected multipart form data", http.StatusBadRequest)
        return
    }

    // Retrieve form text field
    idStr := r.FormValue("id")
    
    // Retrieve the file header
    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "Missing file payload", http.StatusBadRequest)
        return
    }
    defer file.Close()

    // Save the file using our storage utility
    err = mp.store.Save(header.Filename, file)
    if err != nil {
        http.Error(w, "Failed to save file", http.StatusInternalServerError)
        return
    }

    w.Write([]byte("Successfully saved part: " + header.Filename))
}
```
