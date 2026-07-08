---
layout: home

hero:
  name: Programming in Go
  text: Matt Holiday & Nic Jackson Lectures
  tagline: A comprehensive Go programming book compiled from Matt Holiday's Go Class and Nic Jackson's Building Microservices series.
  actions:
    - theme: brand
      text: Start Reading
      link: /preface
    - theme: alt
      text: Print / Download PDF
      link: /full-book
    - theme: alt
      text: Appendices
      link: /appendices/intro

features:
  - icon: ⚡
    title: Core Language Fundamentals
    details: From basic types and slices in detail to Closures and Struct Tags.
  - icon: 🗺️
    title: Concurrency Deep Dive
    details: Covers CSP, channels, select, context, and conventional sync packages.
  - icon: ⚙️
    title: Tooling & Optimization
    details: Benchmarking, profiling, dependency management, and packaging.
  - icon: 🌐
    title: Building Microservices
    details: RESTful APIs, Gorilla Toolkit, Swagger, gRPC, and bidirectional streaming.
---

## Table of Contents {#table-of-contents}

<div class="toc-container">

<div class="toc-column">

### [Part I — Getting Started](/part-1/intro)
- [Chapter 0: Why Use Go](/part-1/ch00-introduction-why-use-go)
- [Chapter 1: Hello World](/part-1/ch01-hello-world)
- [Chapter 2: A Simple Example](/part-1/ch02-a-simple-example)

</div>

<div class="toc-column">

### [Part II — Language Fundamentals](/part-2/intro)
- [Chapter 3: Basic Types](/part-2/ch03-basic-types)
- [Chapter 4: Strings](/part-2/ch04-strings)
- [Chapter 5: Slices & Maps](/part-2/ch05-arrays-slices-and-maps)
- [Chapter 6: Control Flow & Types](/part-2/ch06-control-statements-declarations-types)
- [Chapter 7: Formatted & File I/O](/part-2/ch07-formatted-file-io)
- [Chapter 8: Functions & Defer](/part-2/ch08-functions-parameters-defer)
- [Chapter 9: Closures](/part-2/ch09-closures)
- [Chapter 10: Slices in Detail](/part-2/ch10-slices-in-detail)
- [Chapter 11: Exercise: Word Counter](/part-2/ch11-exercise-html-word-image-counter)

</div>

<div class="toc-column">

### [Part III — Structured Data & Networking](/part-3/intro)
- [Chapter 12: Structs & JSON](/part-3/ch12-structs-struct-tags-json)
- [Chapter 13: Regex & Search](/part-3/ch13-regular-expressions-search)
- [Chapter 14: Value/Ref Semantics](/part-3/ch14-reference-value-semantics)
- [Chapter 15: Networking with HTTP](/part-3/ch15-networking-with-http)
- [Chapter 16: Exercise: XKCD Searcher](/part-3/ch16-homework-xkcd-comic-indexer-searcher)

</div>

<div class="toc-column">

### [Part IV — Object-Oriented Go](/part-4/intro)
- [Chapter 17: Go does OOP](/part-4/ch17-go-does-oop)
- [Chapter 18: Methods & Receivers](/part-4/ch18-methods-receivers)
- [Chapter 19: Struct Composition](/part-4/ch19-struct-composition)
- [Chapter 20: Interfaces in Detail](/part-4/ch20-reader-writer-interface-details)
- [Chapter 21: Exercise: OOP Storefront](/part-4/ch21-homework-e-commerce-web-server)

</div>

<div class="toc-column">

### [Part V — Concurrency](/part-5/intro)
- [Chapter 22: What is Concurrency](/part-5/ch22-what-is-concurrency)
- [Chapter 23: CSP & Goroutines](/part-5/ch23-csp-goroutines-and-channels)
- [Chapter 24: Select Statement](/part-5/ch24-the-select-statement)
- [Chapter 25: Context](/part-5/ch25-context)
- [Chapter 26: Channels in Detail](/part-5/ch26-channels-in-detail)
- [Chapter 27: Exercise: Concurrent Walker](/part-5/ch27-exercise-concurrent-file-processing)
- [Chapter 28: Traditional Sync](/part-5/ch28-conventional-synchronization)
- [Chapter 29: Exercise: Safe Store Server](/part-5/ch29-exercise-thread-safe-web-server)
- [Chapter 30: Concurrency Gotchas](/part-5/ch30-concurrency-gotchas)
- [Chapter 31: Odds & Ends](/part-5/ch31-odds-ends)

</div>

<div class="toc-column">

### [Part VI — Tools & Advanced Topics](/part-6/intro)
- [Chapter 32: Error Handling](/part-6/ch32-custom-wrapped-errors)
- [Chapter 33: Reflection](/part-6/ch33-reflection)
- [Chapter 34: Mechanical Sympathy](/part-6/ch34-mechanical-sympathy)
- [Chapter 35: Benchmarking](/part-6/ch35-benchmarking)
- [Chapter 36: Profiling](/part-6/ch36-profiling)
- [Chapter 37: Static Analysis](/part-6/ch37-static-analysis-linting)
- [Chapter 38: Testing & Mocking](/part-6/ch38-testing-mocking)
- [Chapter 39: Code Coverage](/part-6/ch39-code-coverage)
- [Chapter 40: Go Modules](/part-6/ch40-dependency-management-go-modules)
- [Chapter 41: Building & Deploying](/part-6/ch41-building-deploying-go-programs)

</div>

<div class="toc-column">

### [Part VII — The Future & Wisdom](/part-7/intro)
- [Chapter 42: Generics](/part-7/ch42-parametric-polymorphism-generics)
- [Chapter 43: Parting Thoughts](/part-7/ch43-parting-thoughts-software-philosophy)

</div>

<div class="toc-column">

### [Part VIII — Building Microservices](/part-8/intro)
- [Chapter 44: Intro to Microservices](/part-8/ch44-introduction-to-microservices)
- [Chapter 45: Structuring Code](/part-8/ch45-structuring-microservice-code)
- [Chapter 46: RESTful Services](/part-8/ch46-restful-services)
- [Chapter 47: Reading & Writing JSON](/part-8/ch47-restful-services-reading-and-writing-json)
- [Chapter 48: The Gorilla Framework](/part-8/ch48-the-gorilla-framework)
- [Chapter 49: JSON Validation](/part-8/ch49-json-validation)
- [Chapter 50: Swagger Documentation](/part-8/ch50-documenting-restful-apis-with-swagger)
- [Chapter 51: Auto-Generating Clients](/part-8/ch51-auto-generating-http-clients-from-swagger)
- [Chapter 52: CORS](/part-8/ch52-cors-cross-origin-resource-sharing)
- [Chapter 53: Standard Lib Files](/part-8/ch53-handling-files-with-the-go-standard-library)
- [Chapter 54: HTTP Multi-Part Requests](/part-8/ch54-http-multi-part-requests)
- [Chapter 55: Gzip Compression](/part-8/ch55-gzip-compression-for-http-responses)
- [Chapter 56: gRPC & Protocol Buffers](/part-8/ch56-introduction-to-grpc-and-protocol-buffers)
- [Chapter 57: gRPC Client Connections](/part-8/ch57-grpc-client-connections)
- [Chapter 58: Refactoring Codebase](/part-8/ch58-refactoring-the-codebase)
- [Chapter 59: gRPC Streaming (Part 1)](/part-8/ch59-grpc-bi-directional-streaming-part-1)
- [Chapter 60: gRPC Streaming (Part 2)](/part-8/ch60-grpc-bi-directional-streaming-part-2)
- [Chapter 61: gRPC Error Messages](/part-8/ch61-grpc-error-messages-in-unary-rpcs)
- [Chapter 62: gRPC Stream Error Handling](/part-8/ch62-grpc-error-handling-in-bidirectional-streams)

</div>

<div class="toc-column">

### [Part IX — Go Build & Tooling](/part-9/intro)
- [Chapter 63: Go Build, Compile & Package](/part-9/ch63-go-build-compilation-and-packaging)

</div>

<div class="toc-column">

### [Appendices](/appendices/intro)
- [Appendix A: The Go Proverbs](/appendices/appendix-a-the-go-proverbs)
- [Appendix B: Recommended Resources](/appendices/appendix-b-recommended-resources-readings)

</div>

</div>

<style>
.toc-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}
.toc-container h3 {
  margin-top: 0 !important;
  border-bottom: 2px solid var(--vp-c-divider);
  padding-bottom: 0.5rem;
}
.toc-container ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.toc-container li {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}
.toc-container a {
  text-decoration: none;
  font-weight: 500;
  color: var(--vp-c-brand-1);
}
.toc-container a:hover {
  color: var(--vp-c-brand-2);
}
</style>
