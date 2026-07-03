## Chapter 13: Regular Expressions & Search

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-13-regex-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-13-regex-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="XCE0psygwj8" chapter="13" />

We have already talked about basic string searches using the `strings` package (like `strings.Contains` or `strings.HasPrefix`). However, when your search patterns are more dynamic or complex, you need regular expressions.

As the famous quote by Jamie Zawinski goes:
> "Some people, when confronted with a problem, think 'I know, I'll use regular expressions.' Now they have two problems."

Regular expressions are incredibly concise and powerful, but that means they can easily become unreadable and difficult to test. Additionally, poorly written regular expressions can cause serious performance issues due to **backtracking**.

### RE2 Engine and Performance Safety

To prevent catastrophic backtracking and Denial of Service (DoS) attacks, Go’s regular expression engine (the `regexp` package) is built on **RE2**. 

Unlike standard PCRE (Perl-Compatible Regular Expressions) engines, RE2 runs in time linear to the size of the input string. To guarantee this linear performance, RE2 does not support certain features like backreferences or look-arounds (look-ahead/look-behind), which require exponential backtracking in the worst-case.

### Standard String Searching vs. Regexp

Whenever possible, prefer the `strings` package because it is significantly faster and easier to understand.

**Example: Finding a path suffix**
```go
// Fast, simple strings approach
index := strings.LastIndexByte(filename, '/')
if index != -1 {
    basename := filename[index+1:]
}
```

Only reach for the `regexp` package when you need to match pattern classes (like "one or more digits") rather than exact substrings.

### Compilation and Matching

To use a regular expression, you compile the pattern string into a `regexp.Regexp` object.

```go
// Compile returns an error if the pattern is invalid
re, err := regexp.Compile(`[a-z]+`)

// MustCompile panics if the pattern is invalid.
// Use this for package-level global constants where a syntax error is a programmer bug.
var emailRE = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
```

### Common Regexp Methods

- **`MatchString`**: Returns a boolean indicating if the string matches the pattern.
- **`FindString`**: Returns the first matching substring.
- **`FindAllString`**: Returns a slice of all matching substrings.
- **`FindAllStringIndex`**: Returns a slice of pairs indicating the start and end indexes of matches in the original string.

```go
re := regexp.MustCompile(`b+`)
matches := re.FindAllString("ab bbb abbb", -1)
fmt.Println(matches) // [b bbb bbb]
```

### Capture Groups and Submatches

Parentheses `()` in a regular expression pattern define **capture groups**. When you perform a match, you can extract the exact sub-portions of the match:

```go
// Matching phone number: (123) 456-7890
phoneRE := regexp.MustCompile(`\((\d{3})\)\s*(\d{3})-(\d{4})`)

matches := phoneRE.FindStringSubmatch("My number is (800) 555-1212 today.")
// matches[0] = "(800) 555-1212" (full match)
// matches[1] = "800" (first capture group)
// matches[2] = "555" (second capture group)
// matches[3] = "1212" (third capture group)
```

We can use capture groups to easily reformat text using `ReplaceAllString`:

```go
// Reformat to international layout: +1 800-555-1212
result := phoneRE.ReplaceAllString("Call (800) 555-1212", "+1 $1-$2-$3")
fmt.Println(result) // "Call +1 800-555-1212"
```

---
