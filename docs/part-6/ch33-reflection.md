## Chapter 33: Reflection

<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>/slides/go-33-reflect-slides.pdf</code></summary>
    <div class="slide-iframe-container">
      <iframe src="/GO-Lang-Matt/slides/go-33-reflect-slides.pdf" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>

<VideoPlayer videoId="T2fqLam1iuk" chapter="33" />

Reflection is the ability of a program to inspect and manipulate its own types, variables, and structure at runtime. Go is a statically typed language, but it embeds type descriptors in the compiled binary, allowing the `reflect` package to decode interface values.

### 1. The Empty Interface (`interface{}`) and Type Assertions

An empty interface (`interface{}`) holds values of any concrete type since it declares zero methods. To convert it back to a concrete type, we perform a **Type Assertion**:

```go
var x interface{} = "hello"

// Single-value type assertion (panics if assertion fails)
s := x.(string)

// Two-value type assertion (fails safely without panicking)
s, ok := x.(string)
if !ok {
    // Handle failure
}
```

---

### 2. The Type Switch

A type switch permits multiple type assertions to be evaluated in a top-down switch block. We use the syntax `value.(type)` within the switch guard:

```go
func printValue(x interface{}) {
    switch v := x.(type) {
    case int:
        fmt.Printf("Integer: %d\n", v) // v is treated as type int
    case string:
        fmt.Printf("String: %q\n", v)  // v is treated as type string
    case fmt.Stringer:
        fmt.Printf("Stringer: %s\n", v.String()) // v is stringer interface
    default:
        fmt.Printf("Unknown type: %T\n", v)
    }
}
```

---

### 3. Custom JSON Unmarshalling with Reflection

Standard library JSON parsing uses reflection to map properties to struct tags. If we have a nested JSON format with dynamic keys, we can write a custom unmarshaller combining maps of empty interfaces and reflection.

#### dynamic Schema:
```json
{
  "item": "album",
  "album": {
    "title": "A Night at the Opera",
    "artist": "Queen"
  }
}
```

#### Custom Unmarshal Implementation
```go
package main

import (
    "encoding/json"
    "fmt"
)

type Response struct {
    Item   string
    Title  string
    Artist string
}

// ResponseWrapper prevents recursive unmarshal loops
type ResponseWrapper struct {
    Response
}

func (r *ResponseWrapper) UnmarshalJSON(data []byte) error {
    // 1. Decode first-level properties (extract 'item' tag)
    type Alias ResponseWrapper
    var aux Alias
    if err := json.Unmarshal(data, &aux); err != nil {
        return err
    }
    r.Item = aux.Item

    // 2. Decode raw data into a map of empty interfaces
    var raw map[string]interface{}
    if err := json.Unmarshal(data, &raw); err != nil {
        return err
    }

    // 3. Extract properties by probing maps with type assertions
    switch r.Item {
    case "album":
        if albumVal, ok := raw["album"]; ok {
            if albumObj, ok := albumVal.(map[string]interface{}); ok {
                if title, ok := albumObj["title"].(string); ok {
                    r.Title = title
                }
                if artist, ok := albumObj["artist"].(string); ok {
                    r.Artist = artist
                }
            }
        }
    case "song":
        if songVal, ok := raw["song"]; ok {
            if songObj, ok := songVal.(map[string]interface{}); ok {
                if title, ok := songObj["title"].(string); ok {
                    r.Title = title
                }
            }
        }
    }
    return nil
}
```

---

### 4. Recursive Value Probe: `contains` function

In unit tests, we often want to verify if a JSON payload matches a specific subset of expected fields, without comparing the entire payload (which contains dynamic timestamps or IDs).

We write a recursive `contains` utility that validates if `expected` exists as a subset inside `got`:

```go
package main

import (
    "errors"
    "strings"
)

// Match numerical values (JSON decodes numbers to float64 by default)
func matchNum(key string, expected float64, data map[string]interface{}) bool {
    val, ok := data[key]
    if !ok {
        return false
    }
    actual, ok := val.(float64)
    return ok && actual == expected
}

// Match string values case-insensitively
func matchString(key string, expected string, data map[string]interface{}) bool {
    val, ok := data[key]
    if !ok {
        return false
    }
    actual, ok := val.(string)
    return ok && strings.EqualFold(actual, expected)
}

func contains(expected, got map[string]interface{}) error {
    for k, ev := range expected {
        switch evTyped := ev.(type) {
        case float64:
            if !matchNum(k, evTyped, got) {
                return errors.New("mismatched number field: " + k)
            }
        case string:
            if !matchString(k, evTyped, got) {
                return errors.New("mismatched string field: " + k)
            }
        case map[string]interface{}:
            // Recursive check for nested objects
            gv, ok := got[k]
            if !ok {
                return errors.New("missing expected object key: " + k)
            }
            gotSubMap, ok := gv.(map[string]interface{})
            if !ok {
                return errors.New("type mismatch on nested object: " + k)
            }
            if err := contains(evTyped, gotSubMap); err != nil {
                return err
            }
        default:
            return errors.New("unsupported type in expected comparison: " + k)
        }
    }
    return nil
}
```

---
