## Chapter 58: Refactoring the Codebase

<VideoPlayer videoId="Vl88R9acq-Y" chapter="58" />  
> 🔗 **Source Code:** [GitHub - Episode 15 Branch](https://github.com/nicholasjackson/building-microservices-youtube/tree/episode_15)

To prepare our project for containerization and deployment, we refactor it into separate microservice modules.

### 1. Monorepo vs Multi-module Structure
*   **Monolith structure**: A single package where all services share imports and build configurations.
*   **Multi-module structure**: Separate root folders, each with its own `go.mod` file. This allows services to manage their dependencies and scale independently.

```text
building-microservices/
├── currency/
│   ├── go.mod
│   ├── main.go
│   └── server/
├── product-api/
│   ├── go.mod
│   ├── main.go
│   └── handlers/
└── sdk/
```

### 2. Managing Dependencies and Module Scopes
When working with multiple modules, you can use Go workspace config files (`go.work`) or local module replacements in your `go.mod` file to resolve local imports during development:

```text
// product-api/go.mod
module product-api

go 1.20

replace github.com/nicholasjackson/protos => ../protos
```
