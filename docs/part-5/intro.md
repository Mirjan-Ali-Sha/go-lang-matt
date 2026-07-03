# Part V — Concurrency

Concurrency is a core pillar of Go's design. We study the Communicating Sequential Processes (CSP) model, goroutines, channels, select, context, and conventional sync primitives (Mutex, RWMutex, Once, Pool). We also examine common concurrency bugs like deadlocks, goroutine leaks, and loop closures, and refactor a sequential directory walker into a high-performance concurrent duplicate file finder.
