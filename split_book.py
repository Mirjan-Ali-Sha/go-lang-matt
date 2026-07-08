import os
import re
import shutil

# Directories
src_dir = "go-book"
dest_dir = "docs"

# Create directories
os.makedirs(dest_dir, exist_ok=True)

# List of source files in chronological order
source_files = [
    ("00-front-matter.md", "preface"),
    ("01-part1-introduction.md", "part-1"),
    ("02-part2-fundamentals.md", "part-2"),
    ("03-part2-continued.md", "part-2"),
    ("04-part3-data-structures.md", "part-3"),
    ("05-part4-oop.md", "part-4"),
    ("06-part5-concurrency.md", "part-5"),
    ("07-part5-continued.md", "part-5"),
    ("08-part6-advanced.md", "part-6"),
    ("09-part6-continued.md", "part-6"),
    ("10-part7-future.md", "part-7"),
    ("11-appendices.md", "appendices")
]

# Video ID mapping for all 44 chapters (Go Class 00 to 43)
video_mapping = {
    "00": "iDQAZEJK8lI",
    "01": "A9HfEhvpOEY",
    "02": "-EYNVEv-snE",
    "03": "NNLpEPb2ddE",
    "04": "nxWqANttAdA",
    "05": "T0Xymg0_aSU",
    "06": "qpHLhmoV3BY",
    "07": "dqEtGT-dxoY",
    "08": "wj0hUjRHkPs",
    "09": "US3TGA-Dpqo",
    "10": "pHl9r3B2DFI",
    "11": "CR4OYGxaie8",
    "12": "0m6iFd9N_CY",
    "13": "XCE0psygwj8",
    "14": "904pyovPvXM",
    "15": "Q-uy0FS6RwU",
    "16": "mFB6_sOiggI",
    "17": "jexEpE7Yv2A",
    "18": "W3ZWbhQF6wg",
    "19": "0X6AcnwocbM",
    "20": "AXCIEiebVfI",
    "21": "YUaruvHkXio",
    "22": "A3R-4ZYBqvE",
    "23": "zJd7Dvg3XCk",
    "24": "tG7gII0Ax0Q",
    "25": "0x_oUlxzw5A",
    "26": "fCkxKGd6CVQ",
    "27": "SPD7TykYy5w",
    "28": "DtXNSE3Yejg",
    "29": "juBGb6rvoec",
    "30": "K1hwpNnCJgY",
    "31": "oTtYtrFv3gw",
    "32": "oIxXp0OgK_0",
    "33": "T2fqLam1iuk",
    "34": "7QLoOd9HinY",
    "35": "nk4rALKLQkc",
    "36": "MDB2x1Di5uM",
    "37": "GyoMEerSd0I",
    "38": "PIPfNIWVbc8",
    "39": "HfCsfuVqpcM",
    "40": "_N6BxmbLYBk",
    "41": "rXgUP_BNyaI",
    "42": "Si0rAE8yT9g",
    "43": "i7wbTq-beQo"
}

# Map to slugify titles for filenames
def slugify(title):
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s-]', '', title)
    title = re.sub(r'[\s-]+', '-', title).strip('-')
    return title

# Track full book markdown content for the PDF version
full_book_content = []

print("Starting to split files and generate slide + video boxes...")

# Use non-backtick pattern to greedily match the full file path inside backticks
slide_regex = r'> 📊 \*\*Slide Reference:\*\*\s+`?([^`\s]+)`?'

for filename, part_folder in source_files:
    filepath = os.path.join(src_dir, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (not found)")
        continue

    print(f"Processing {filename} -> docs/{part_folder}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by level-2 headers (## Chapter or ## Appendix)
    parts = re.split(r'^(## .*)$', content, flags=re.MULTILINE)
    
    # The first element is the introduction of this file (before any ## Chapter or ## Appendix)
    file_intro = parts[0].strip()
    
    # Handle the file introduction
    is_continued = "continued" in filename.lower()
    if file_intro and not is_continued:
        if part_folder == "preface":
            os.makedirs(dest_dir, exist_ok=True)
            with open(os.path.join(dest_dir, "preface.md"), "w", encoding="utf-8") as f_out:
                f_out.write(file_intro + "\n")
            full_book_content.append(re.sub(slide_regex, "", file_intro))
        else:
            part_path = os.path.join(dest_dir, part_folder)
            os.makedirs(part_path, exist_ok=True)
            
            intro_file = os.path.join(part_path, "intro.md")
            with open(intro_file, "w", encoding="utf-8") as f_out:
                f_out.write(file_intro + "\n")
            full_book_content.append(re.sub(slide_regex, "", file_intro))

    # Now process the chapter blocks
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i+1].strip() if i+1 < len(parts) else ""
        
        ch_padded = ""
        # Clean header text
        chapter_title_match = re.match(r'^##\s+(?:Chapter|Appendix)\s+(\w+)\s*[:—-]\s*(.*)$', header, re.IGNORECASE)
        if chapter_title_match:
            ch_num = chapter_title_match.group(1).lower()
            ch_title = chapter_title_match.group(2).strip()
            
            # Format filename
            if ch_num.isdigit():
                ch_padded = ch_num.zfill(2)
                filename_out = f"ch{ch_padded}-{slugify(ch_title)}.md"
            else:
                filename_out = f"appendix-{ch_num}-{slugify(ch_title)}.md"
        else:
            filename_out = slugify(header.replace("##", "")) + ".md"

        part_path = os.path.join(dest_dir, part_folder)
        os.makedirs(part_path, exist_ok=True)

        # 1. Generate content for individual chapter file (includes slide iframe box and VideoPlayer component)
        # Create a specific replacement function using a closure
        def make_replace_slide_ref(ch_num_str):
            def replace_slide_ref(match):
                path = match.group(1)
                # Ensure it starts with /slides/
                if path.startswith("slides/"):
                    clean_path = "/" + path
                elif path.startswith("/slides/"):
                    clean_path = path
                else:
                    clean_path = "/slides/" + path
                    
                iframe_src = ".." + clean_path
                
                box_html = f"""<div class="slide-visualization-box no-print">
  <details>
    <summary>📊 Slide Reference: <code>{clean_path}</code></summary>
    <div class="slide-iframe-container">
      <iframe src="{iframe_src}" width="100%" height="450px" style="border: none;"></iframe>
    </div>
  </details>
</div>"""
                
                # Append the VideoPlayer Vue component call if video ID exists
                video_id = video_mapping.get(ch_num_str)
                if video_id:
                    box_html += f"\n\n<VideoPlayer videoId=\"{video_id}\" chapter=\"{ch_num_str}\" />"
                    
                return box_html
            return replace_slide_ref

        body_for_chapter = re.sub(slide_regex, make_replace_slide_ref(ch_padded), body)
        full_chapter_content_for_chapter = f"{header}\n\n{body_for_chapter}"
        
        with open(os.path.join(part_path, filename_out), "w", encoding="utf-8") as f_out:
            f_out.write(full_chapter_content_for_chapter + "\n")
        
        # 2. Generate content for full book printable template (strips slide references completely)
        body_for_full_book = re.sub(slide_regex, "", body)
        body_for_full_book = body_for_full_book.strip()
        full_chapter_content_for_full_book = f"{header}\n\n{body_for_full_book}"
        
        full_book_content.append(full_chapter_content_for_full_book)

# Write the full book markdown for PDF printing (without slide or video boxes)
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

with open(os.path.join(dest_dir, "full-book.md"), "w", encoding="utf-8") as f_full:
    f_full.write(print_setup)
    f_full.write("# Programming in Go — A Complete Class by Matt Holiday\n\n")
    
    # Prepend Declaration if it exists
    decl_path = os.path.join(dest_dir, "declaration.md")
    if os.path.exists(decl_path):
        with open(decl_path, "r", encoding="utf-8") as f_decl:
            decl_content = f_decl.read().strip()
            if decl_content.startswith("---"):
                parts_decl = decl_content.split("---", 2)
                if len(parts_decl) >= 3:
                    decl_content = parts_decl[2].strip()
            f_full.write(decl_content + "\n\n---\n\n")
            
    f_full.write("\n\n---\n\n".join(full_book_content))

print("Restructuring completed successfully!")