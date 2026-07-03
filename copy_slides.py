import os
import shutil

src = "slides"
dst = os.path.join("docs", "public", "slides")

os.makedirs(dst, exist_ok=True)

for item in os.listdir(src):
    if item.endswith(".pdf"):
        shutil.copy2(os.path.join(src, item), os.path.join(dst, item))

print("Slides copied successfully!")
