import os

filepath = os.path.join("docs", "full-book.md")

with open(filepath, "r", encoding="utf-8") as f:
    original_content = f.read()

# Custom styles and button
print_setup = """---
layout: doc
aside: false
---

<button onclick="window.print()" class="print-button">📄 Print / Save as PDF</button>

<style>
@media print {
  /* Hide standard VitePress navigation elements when printing */
  .VPNavbar,
  .VPSidebar,
  .VPFooter,
  .VPLocalNav,
  .print-button,
  .vp-doc-footer,
  .prev-next {
    display: none !important;
  }
  
  .VPContent {
    padding: 0 !important;
    margin: 0 !important;
    background: white !important;
    color: black !important;
  }
  
  /* Ensure page breaks before chapters */
  h1, h2 {
    page-break-before: always;
  }
}

.print-button {
  background-color: var(--vp-c-brand-1);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 2rem;
  font-size: 1.1rem;
  transition: background-color 0.2s;
  display: inline-block;
}

.print-button:hover {
  background-color: var(--vp-c-brand-2);
}
</style>

"""

# Prepend print setup
new_content = print_setup + original_content

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Print styles added successfully!")
