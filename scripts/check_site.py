#!/usr/bin/env python3
"""Check generated navigation, resources, fragments, metadata, and PDF content."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import sys
import yaml
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
config = yaml.safe_load((ROOT / "_config.yml").read_text())
base = config["baseurl"]
origin = config["url"]
errors = []


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.canonicals = set(), [], []
        self.h1 = 0
        self.described = False
        self.refresh = []
        self.noindex = False
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            if attrs["id"] in self.ids:
                errors.append(f"Duplicate ID: {self.path}: {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.described = bool(attrs.get("content"))
        if tag == "meta" and attrs.get("http-equiv") == "refresh":
            self.refresh.append(attrs.get("content"))
        if tag == "meta" and attrs.get("name") == "robots":
            self.noindex = "noindex" in attrs.get("content", "")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))
        if tag in ("a", "link", "img", "script", "source"):
            value = attrs.get("href") or attrs.get("src") or attrs.get("srcset")
            if value:
                self.links.append(value)
        if tag == "img" and "alt" not in attrs:
            errors.append(f"Missing image alternative text: {self.path}")


pages = {path: Page(path) for path in SITE.rglob("*.html")}
assert pages, "Build the website before checking it."
external = set()
for path, page in pages.items():
    if page.h1 != 1:
        errors.append(f"Expected one h1: {path} (found {page.h1})")
    if not page.described:
        errors.append(f"Missing description: {path}")
    if len(page.canonicals) != 1 or not page.canonicals[0].startswith(origin + base + "/"):
        errors.append(f"Invalid canonical: {path}: {page.canonicals}")
    raw = path.read_text()
    if "amirmmohammadi.github.io" in raw:
        errors.append(f"Obsolete hostname: {path}")
    for href in page.links:
        url = urlsplit(href)
        if url.scheme in ("mailto", "tel", "data"):
            continue
        if url.netloc and url.netloc != urlsplit(origin).netloc:
            external.add(href)
            continue
        route = unquote(url.path)
        if route.startswith(base + "/"):
            target = SITE / route[len(base) + 1:]
        elif route.startswith("/"):
            errors.append(f"Link misses project base path: {path}: {href}")
            continue
        elif route:
            target = path.parent / route
        else:
            target = path
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"Missing local resource: {path}: {href}")
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f"Missing fragment: {path}: {href}")

pdf = PdfReader(str(ROOT / "documents/Amir_CV_2026.pdf"))
pdf_text = " ".join(page.extract_text() for page in pdf.pages)
normalize = lambda text: re.sub(r"\s+", " ", text).strip()
pdf_text = normalize(pdf_text)
publications = yaml.safe_load((ROOT / "_data/publications.yml").read_text())
publication_page = pages[SITE / "publications/index.html"]
for pub in publications:
    assert pub["id"] in publication_page.ids, f"Publication missing from website: {pub['id']}"
assert len(pdf.pages) > 0, "The CV PDF must contain at least one page."
assert all(page.extract_text().strip() for page in pdf.pages), "PDF contains an empty/image-only page."
assert "amir.mhm.ee@gmail.com" in pdf_text
assert pdf.pages[0].extract_text().lstrip().startswith("Amirmohammad (Amir) Mohammadi"), "PDF reading order should start with the name."
assert "U.S. Permanent Resident" in pdf_text
assert not (SITE / "blog").exists(), "Empty blog must not be published."
assert not (SITE / "scripts").exists(), "Build tools must not be published."
assert (SITE / "documents/Amir_CV_2026.pdf").read_bytes() == (ROOT / "documents/Amir_CV_2026.pdf").read_bytes()
legacy_cv = Path("amirmmohammadi/documents/Amir_CV_2026.pdf")
assert not (ROOT / legacy_cv).exists(), "Keep only the current CV; do not recreate a legacy copy."
assert not (SITE / legacy_cv).exists(), "The old CV must not be published."
sitemap = (SITE / "sitemap.xml").read_text()
assert "amirmmohammadi.github.io" not in sitemap
assert "/blog/" not in sitemap
if base == "":
    for route in ("", "aboutme/", "research/", "publications/", "cv/"):
        legacy = pages[SITE / "amirmmohammadi" / route / "index.html"]
        expected = origin + "/" + route
        assert legacy.canonicals == [expected]
        assert legacy.refresh == ["0;url=" + expected]
        assert legacy.noindex
    assert origin + "/amirmmohammadi/" not in sitemap
print(f"Checked {len(pages)} HTML pages, all local links/resources/fragments, metadata, sitemap, and {len(pdf.pages)} PDF pages.")
annotation_count = sum(len(p["/Annots"]) if "/Annots" in p else 0 for p in pdf.pages)
print(f"Website includes all {len(publications)} publications/manuscripts; the author-supplied PDF has {annotation_count} link annotations.")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("PASS")
