## Chapter 17: Go does OOP

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-17-go-oop-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="../slides/go-17-go-oop-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="jexEpE7Yv2A" chapter="17" />

Object-oriented programming (OOP) is often defined in textbooks as the combination of four core features:
1. **Abstraction**
2. **Encapsulation**
3. **Polymorphism**
4. **Inheritance**

While Go supports the first three features, it completely lacks the fourth: **inheritance**. In this chapter, we explore how Go manages to be a powerful object-oriented language without classes or type hierarchies.

### Abstraction & Encapsulation

**Abstraction** is the logical simplification of a system. A classic example is the file system API: we want to open, read, and write files without worrying about OS buffers, page boundaries, or magnetic sector layouts.

**Encapsulation** is the physical enforcement of abstraction by hiding internal details. In Go, encapsulation is package-level and controlled by capitalization:
- Identifiers starting with an **uppercase letter** (e.g., `ExportedType`, `Field`) are visible to other packages.
- Identifiers starting with a **lowercase letter** (e.g., `internalField`, `privateStruct`) are hidden, protecting the package’s internal state from external tampering.

### Polymorphism

Polymorphism ("many shapes") allows a single interface to represent multiple underlying concrete types. There are several forms of polymorphism:
1. **Ad-hoc Polymorphism:** Function overloading or operator overloading (not supported in Go).
2. **Parametric Polymorphism:** Generics (type parameters, supported in Go 1.18+).
3. **Subtype Polymorphism:** Class inheritance hierarchies where a subclass replaces a superclass (not supported in Go).
4. **Interface Polymorphism:** Also called *protocol-oriented programming*, where types are grouped based on what they can *do* (behavior) rather than what they *are* (lineage). This is Go's primary mechanism for polymorphism.

### The Inheritance Tax

Many mainstream languages tie polymorphism directly to class inheritance. However, inheritance can lead to fragile, bloated systems:
- **Tight Coupling:** Subclasses often depend on the internal details of their superclasses. Changing a superclass can break subclasses unexpectedly.
- **Deep Hierarchies:** Deep, parallel inheritance hierarchies are notoriously hard to reason about.
- **Leaky Abstractions:** Subtyping can force child types to inherit behaviors that do not make sense for them (e.g., a `Line` class inheriting from `Shape` but having to panic or return zero for a `.Area()` method).

Because of these pitfalls, the software engineering industry has moved toward the mantra: **"Prefer composition over inheritance."**

### Alan Kay's Vision of OOP

Alan Kay, who coined the term "object-oriented programming" and developed Smalltalk, wrote in the late 1990s about his original vision:

> "I'm sorry that I long ago coined the term 'objects' for this topic because it gets many people to focus on the lesser idea. The big idea is 'messaging'..."
>
> Kay’s core pillars:
> 1. Message passing (dynamic dispatch).
> 2. Local retention and protection of state (encapsulation).
> 3. Extreme late-binding of all things.

Notice that classes and inheritance are completely absent from this list. Go adheres closely to this philosophy: objects have protected state, communicate via methods, and establish relationships dynamically through interfaces.

In Go:
- **There are no classes.** There are only types.
- **There is no inheritance.** There is only composition.
- **Methods can be defined on any user-declared type**—not just structs. You can add methods to strings, integers, slices, and even functions.

---
