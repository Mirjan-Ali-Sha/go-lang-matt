import os

intros = {
    "part-1": {
        "title": "Part I — Getting Started",
        "description": "Welcome to the first part of Programming in Go. Here, we explore the design goals behind the Go programming language, get familiar with the Go Playground, set up a local development environment, write our first programs, and introduce Go's testing framework."
    },
    "part-2": {
        "title": "Part II — Language Fundamentals",
        "description": "In this part, we lay the foundations of Go syntax and semantics. We cover basic types, strings, arrays, slices, maps, control flow statements, formatted/file I/O, functions, defer, and closures. We also dive deep into slice headers and build a practical HTML word and image counter."
    },
    "part-3": {
        "title": "Part III — Structured Data & Networking",
        "description": "This part focuses on structuring data and communicating over the network. We cover custom structs, struct tags, JSON serialization, regular expressions, reference and value semantics (pointers), and networking with Go's powerful standard `net/http` package. We conclude by building a command-line XKCD search tool."
    },
    "part-4": {
        "title": "Part IV — Object-Oriented Go",
        "description": "Explore how Go supports object-oriented design without traditional inheritance. We learn about struct methods, receiver semantics (value vs pointer), interface types, composition, embedding, and standard interface paradigms. Finally, we implement an OOP-based storefront web server."
    },
    "part-5": {
        "title": "Part V — Concurrency",
        "description": "Concurrency is a core pillar of Go's design. We study the Communicating Sequential Processes (CSP) model, goroutines, channels, select, context, and conventional sync primitives (Mutex, RWMutex, Once, Pool). We also examine common concurrency bugs like deadlocks, goroutine leaks, and loop closures, and refactor a sequential directory walker into a high-performance concurrent duplicate file finder."
    },
    "part-6": {
        "title": "Part VI — Tools & Advanced Topics",
        "description": "Professional Go development relies on strong tooling and advanced practices. We cover custom error wrapping and inspection (`errors.Is`/`As`), runtime reflection, mechanical sympathy (CPU cache lines and false sharing), benchmarking (`testing.B`), profiling (`pprof`), static analysis, database mocking, module management, and building production-ready Docker containers."
    },
    "part-7": {
        "title": "Part VII — The Future of Go",
        "description": "Explore modern Go capabilities and software philosophy. We cover Parametric Polymorphism (Generics), type parameter constraints, mapping functions, and compiler type inference. We conclude with parting software engineering wisdom from Matt Holiday."
    },
    "appendices": {
        "title": "Appendices",
        "description": "Reference materials to accompany your Go journey. Includes a detailed explanation of the 19 Go Proverbs and a curated bibliography of books, papers, articles, and talks recommended throughout this course."
    }
}

for folder, data in intros.items():
    intro_file = os.path.join("docs", folder, "intro.md")
    content = f"# {data['title']}\n\n{data['description']}\n"
    with open(intro_file, "w", encoding="utf-8") as f:
        f.write(content)

print("Intros updated successfully!")
