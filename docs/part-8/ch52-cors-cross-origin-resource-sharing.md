## Chapter 52: CORS — Cross-Origin Resource Sharing

<VideoPlayer videoId="RlYoy_RiYPw" chapter="52" />  
> 🔗 **Source Code:** [GitHub - Episode 9 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_9)

Web browsers enforce CORS (Cross-Origin Resource Sharing) security policies to block client scripts on one origin from accessing resources on another. We configure CORS support in our service using standard Gorilla middleware.

### 1. Understanding CORS Headers
*   `Access-Control-Allow-Origin`: Defines which client domains are permitted to retrieve data.
*   `Access-Control-Allow-Methods`: Lists approved request verbs (`GET`, `POST`, `PUT`, etc.).
*   `Access-Control-Allow-Headers`: Approves custom headers (such as `Content-Type` or `Authorization`).

### 2. Implementing CORS Middleware
Using the `github.com/gorilla/handlers` package, we wrap our main server router to configure allowed origins, headers, and HTTP methods.

```go
package main

import (
    "net/http"
    "os"
    "github.com/gorilla/handlers"
    "github.com/gorilla/mux"
)

func main() {
    sm := mux.NewRouter()

    // Configure CORS origins and parameters
    ch := handlers.CORS(
        handlers.AllowedOrigins([]string{"http://localhost:3000"}),
        handlers.AllowedHeaders([]string{"X-Requested-With", "Content-Type", "Authorization"}),
        handlers.AllowedMethods([]string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}),
    )

    // Wrap the router with the CORS middleware
    server := &http.Server{
        Addr:    ":9090",
        Handler: ch(sm),
    }

    server.ListenAndServe()
}
```
