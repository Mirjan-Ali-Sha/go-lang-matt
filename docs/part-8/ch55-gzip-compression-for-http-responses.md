## Chapter 55: Gzip Compression for HTTP Responses

<VideoPlayer videoId="GtSg1H7SU5Y" chapter="55" />  
> 🔗 **Source Code:** [GitHub - Episode 12 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_12)

Compressing text payloads (like JSON) reduces bandwidth usage and improves transfer speeds. We implement a Gzip middleware using Go's `compress/gzip` package.

### 1. Creating a Gzip response writer wrapper
To support compression, we wrap `http.ResponseWriter` in a custom struct that intercepts writes and redirects them through a `gzip.Writer`.

```go
package middleware

import (
    "compress/gzip"
    "io"
    "net/http"
)

type GzipResponseWriter struct {
    gw  *gzip.Writer
    w   http.ResponseWriter
}

func NewGzipResponseWriter(w http.ResponseWriter) *GzipResponseWriter {
    gw := gzip.NewWriter(w)
    return &GzipResponseWriter{gw: gw, w: w}
}

func (grw *GzipResponseWriter) Header() http.Header {
    return grw.w.Header()
}

func (grw *GzipResponseWriter) WriteHeader(statusCode int) {
    grw.w.WriteHeader(statusCode)
}

func (grw *GzipResponseWriter) Write(b []byte) (int, error) {
    return grw.gw.Write(b)
}

func (grw *GzipResponseWriter) Flush() {
    grw.gw.Close()
}
```

### 2. The Gzip Middleware
The middleware intercepts requests, checks the client's `Accept-Encoding` header for Gzip support, and wraps the response writer accordingly.

```go
func GzipMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // Check client support for gzip
        if !strings.Contains(r.Header.Get("Accept-Encoding"), "gzip") {
            next.ServeHTTP(w, r)
            return
        }

        // Prepare compression headers
        w.Header().Set("Content-Encoding", "gzip")
        
        gWriter := NewGzipResponseWriter(w)
        defer gWriter.Flush()

        // Execute handler chain using our compressed writer
        next.ServeHTTP(gWriter, r)
    })
}
```
