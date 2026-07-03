import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Programming in Go",
  description: "A Complete Class by Matt Holiday",
  base: "/go-lang-matt/", // Base URL for GitHub Pages repository (assuming repository name is 'go-lang-matt')
  
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Preface', link: '/preface' },
      { text: 'Printable Book (PDF)', link: '/full-book' },
      { text: 'Appendices', link: '/appendices/intro' }
    ],

    search: {
      provider: 'local'
    },

    sidebar: [
      {
        text: 'Front Matter',
        items: [
          { text: 'Preface', link: '/preface' }
        ]
      },
      {
        text: 'Part I — Getting Started',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/part-1/intro' },
          { text: 'Chapter 0: Why Use Go', link: '/part-1/ch00-introduction-why-use-go' },
          { text: 'Chapter 1: Hello World', link: '/part-1/ch01-hello-world' },
          { text: 'Chapter 2: A Simple Example', link: '/part-1/ch02-a-simple-example' }
        ]
      },
      {
        text: 'Part II — Language Fundamentals',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/part-2/intro' },
          { text: 'Chapter 3: Basic Types', link: '/part-2/ch03-basic-types' },
          { text: 'Chapter 4: Strings', link: '/part-2/ch04-strings' },
          { text: 'Chapter 5: Slices & Maps', link: '/part-2/ch05-arrays-slices-and-maps' },
          { text: 'Chapter 6: Control Flow & Types', link: '/part-2/ch06-control-statements-declarations-types' },
          { text: 'Chapter 7: Formatted & File I/O', link: '/part-2/ch07-formatted-file-io' },
          { text: 'Chapter 8: Functions & Defer', link: '/part-2/ch08-functions-parameters-defer' },
          { text: 'Chapter 9: Closures', link: '/part-2/ch09-closures' },
          { text: 'Chapter 10: Slices in Detail', link: '/part-2/ch10-slices-in-detail' },
          { text: 'Chapter 11: Exercise: Word Counter', link: '/part-2/ch11-exercise-html-word-image-counter' }
        ]
      },
      {
        text: 'Part III — Structured Data & Networking',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/part-3/intro' },
          { text: 'Chapter 12: Structs & JSON', link: '/part-3/ch12-structs-struct-tags-json' },
          { text: 'Chapter 13: Regex & Search', link: '/part-3/ch13-regular-expressions-search' },
          { text: 'Chapter 14: Value/Ref Semantics', link: '/part-3/ch14-reference-value-semantics' },
          { text: 'Chapter 15: Networking with HTTP', link: '/part-3/ch15-networking-with-http' },
          { text: 'Chapter 16: Exercise: XKCD Searcher', link: '/part-3/ch16-homework-xkcd-comic-indexer-searcher' }
        ]
      },
      {
        text: 'Part IV — Object-Oriented Go',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/part-4/intro' },
          { text: 'Chapter 17: Go does OOP', link: '/part-4/ch17-go-does-oop' },
          { text: 'Chapter 18: Methods & Receivers', link: '/part-4/ch18-methods-receivers' },
          { text: 'Chapter 19: Struct Composition', link: '/part-4/ch19-struct-composition' },
          { text: 'Chapter 20: Interfaces in Detail', link: '/part-4/ch20-reader-writer-interface-details' },
          { text: 'Chapter 21: Exercise: OOP Storefront', link: '/part-4/ch21-homework-e-commerce-web-server' }
        ]
      },
      {
        text: 'Part V — Concurrency',
        collapsed: true,
        items: [
          { text: 'Overview', link: '/part-5/intro' },
          { text: 'Chapter 22: What is Concurrency', link: '/part-5/ch22-what-is-concurrency' },
          { text: 'Chapter 23: CSP & Goroutines', link: '/part-5/ch23-csp-goroutines-and-channels' },
          { text: 'Chapter 24: Select Statement', link: '/part-5/ch24-the-select-statement' },
          { text: 'Chapter 25: Context', link: '/part-5/ch25-context' },
          { text: 'Chapter 26: Channels in Detail', link: '/part-5/ch26-channels-in-detail' },
          { text: 'Chapter 27: Exercise: Concurrent Walker', link: '/part-5/ch27-exercise-concurrent-file-processing' },
          { text: 'Chapter 28: Traditional Sync', link: '/part-5/ch28-conventional-synchronization' },
          { text: 'Chapter 29: Exercise: Safe Store Server', link: '/part-5/ch29-exercise-thread-safe-web-server' },
          { text: 'Chapter 30: Concurrency Gotchas', link: '/part-5/ch30-concurrency-gotchas' },
          { text: 'Chapter 31: Odds & Ends', link: '/part-5/ch31-odds-ends' }
        ]
      },
      {
        text: 'Part VI — Tools & Advanced Topics',
        collapsed: true,
        items: [
          { text: 'Overview', link: '/part-6/intro' },
          { text: 'Chapter 32: Error Handling', link: '/part-6/ch32-custom-wrapped-errors' },
          { text: 'Chapter 33: Reflection', link: '/part-6/ch33-reflection' },
          { text: 'Chapter 34: Mechanical Sympathy', link: '/part-6/ch34-mechanical-sympathy' },
          { text: 'Chapter 35: Benchmarking', link: '/part-6/ch35-benchmarking' },
          { text: 'Chapter 36: Profiling', link: '/part-6/ch36-profiling' },
          { text: 'Chapter 37: Static Analysis', link: '/part-6/ch37-static-analysis-linting' },
          { text: 'Chapter 38: Testing & Mocking', link: '/part-6/ch38-testing-mocking' },
          { text: 'Chapter 39: Code Coverage', link: '/part-6/ch39-code-coverage' },
          { text: 'Chapter 40: Go Modules', link: '/part-6/ch40-dependency-management-go-modules' },
          { text: 'Chapter 41: Building & Deploying', link: '/part-6/ch41-building-deploying-go-programs' }
        ]
      },
      {
        text: 'Part VII — The Future & Wisdom',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/part-7/intro' },
          { text: 'Chapter 42: Generics', link: '/part-7/ch42-parametric-polymorphism-generics' },
          { text: 'Chapter 43: Parting Thoughts', link: '/part-7/ch43-parting-thoughts-software-philosophy' }
        ]
      },
      {
        text: 'Appendices',
        collapsed: false,
        items: [
          { text: 'Overview', link: '/appendices/intro' },
          { text: 'Appendix A: The Go Proverbs', link: '/appendices/appendix-a-the-go-proverbs' },
          { text: 'Appendix B: Recommended Resources', link: '/appendices/appendix-b-recommended-resources-readings' }
        ]
      }
    ],

    footer: {
      message: 'Faithfully compiled from Matt Holiday\'s lecture transcriptions.',
      copyright: 'Copyright © 2026-present'
    }
  }
})
