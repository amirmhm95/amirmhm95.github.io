#!/usr/bin/env python3
"""Import an author-supplied PDF unchanged; never regenerate or restyle it.

Usage: python3 scripts/build_cv.py /path/to/Amir_CV_2026.pdf
Only the website copy and its HTML page-count label are updated.
"""
from pathlib import Path
import argparse
import hashlib
import re
import shutil
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path, help="The PDF to copy without modification")
args = parser.parse_args()
source = args.source.resolve(strict=True)
if source.suffix.lower() != ".pdf":
    parser.error("The source must be a PDF file.")
original = source.read_bytes()
reader = PdfReader(str(source))
page_count = len(reader.pages)
if not page_count:
    parser.error("The supplied PDF has no pages.")
destination = ROOT / "documents/Amir_CV_2026.pdf"
if source != destination.resolve():
    shutil.copy2(source, destination)
assert source.read_bytes() == original, "The source must remain unchanged."
assert destination.read_bytes() == original, "The website copy must be byte-identical."
legacy_destination = ROOT / "amirmmohammadi/documents/Amir_CV_2026.pdf"
if legacy_destination.parent.exists():
    shutil.copy2(destination, legacy_destination)
    assert legacy_destination.read_bytes() == original
cv_page = ROOT / "_pages/cv.html"
content = re.sub(r'<span id="cv-pages">\d+ pages?</span>',
                 f'<span id="cv-pages">{page_count} {"page" if page_count == 1 else "pages"}</span>',
                 cv_page.read_text())
if content != cv_page.read_text():
    cv_page.write_text(content)
print(f"Imported unchanged: {destination.relative_to(ROOT)}, {page_count} pages")
print("SHA256: " + hashlib.sha256(original).hexdigest())
