#!/usr/bin/env python3
"""Build the public CV exclusively from the website's structured data.

This script never reads or writes the comprehensive Pages document.
Install requirements-dev.txt, then run: python3 scripts/build_cv.py
"""
from pathlib import Path
from datetime import date
from xml.sax.saxutils import escape
import re
import yaml
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, KeepTogether, PageBreak,
    HRFlowable, ListFlowable, ListItem,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data"
profile = yaml.safe_load((DATA / "profile.yml").read_text())
cv = yaml.safe_load((DATA / "cv.yml").read_text())
publications = yaml.safe_load((DATA / "publications.yml").read_text())
config = yaml.safe_load((ROOT / "_config.yml").read_text())
updated = date.fromisoformat(str(config["updated"])).strftime("%B %Y")
fonts = Path(reportlab.__file__).parent / "fonts"
for name, filename in [("Vera", "Vera.ttf"), ("Vera-Bold", "VeraBd.ttf"),
                       ("Vera-Italic", "VeraIt.ttf"), ("Vera-BoldItalic", "VeraBI.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
pdfmetrics.registerFontFamily("Vera", normal="Vera", bold="Vera-Bold",
                              italic="Vera-Italic", boldItalic="Vera-BoldItalic")
ACCENT = colors.HexColor("#7c293e")
INK = colors.HexColor("#202c36")
MUTED = colors.HexColor("#46545e")
styles = {
    "body": ParagraphStyle("Body", fontName="Vera", fontSize=10, leading=13.2,
                           textColor=INK, spaceAfter=3, alignment=TA_LEFT),
    "small": ParagraphStyle("Small", fontName="Vera", fontSize=9, leading=12,
                            textColor=MUTED, spaceAfter=4),
    "name": ParagraphStyle("Name", fontName="Vera-Bold", fontSize=20, leading=25,
                           textColor=INK, spaceAfter=6),
    "section": ParagraphStyle("Section", fontName="Vera-Bold", fontSize=11,
                              leading=14, textColor=ACCENT, spaceBefore=11,
                              spaceAfter=7, keepWithNext=True),
    "entry": ParagraphStyle("Entry", fontName="Vera-Bold", fontSize=9.5,
                            leading=12.6, textColor=INK, spaceAfter=2,
                            keepWithNext=True),
    "pub": ParagraphStyle("Publication", fontName="Vera", fontSize=10,
                          leading=13.2, textColor=INK, spaceAfter=8),
}


def text(value):
    return escape(str(value))


def para(value, style="body"):
    return Paragraph(value, styles[style])


def link(url, label):
    return f'<link href="{text(url)}" color="#7c293e"><u>{text(label)}</u></link>'


def bullets(items):
    return ListFlowable(
        [ListItem(para(text(item)), leftIndent=9) for item in items],
        bulletType="bullet", leftIndent=11, bulletFontName="Vera", bulletFontSize=5,
        spaceAfter=3,
    )


def section(title):
    return para(text(title), "section")


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#deded7"))
    canvas.line(43, 37, 569, 37)
    canvas.setFont("Vera", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(43, 24, profile["name"] + " · Updated " + updated)
    canvas.drawRightString(569, 24, str(doc.page))
    canvas.restoreState()


story = [para(text(profile["display_name"]), "name")]
story.append(para("Computer Engineering PhD candidate · Texas A&amp;M University"))
story.append(para("College Station, Texas · U.S. Permanent Resident", "small"))
story.append(para(" · ".join([
    link("mailto:" + profile["personal_email"], profile["personal_email"]),
    link(profile["website"], "Website"), link(profile["scholar"], "Google Scholar"),
    link(profile["linkedin"], "LinkedIn"),
]), "small"))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceBefore=4, spaceAfter=7))
story.append(para("<b>Research focus:</b> " + text(profile["focus"])))
story.append(section("Education"))
for item in cv["education"]:
    entry = [para(f'{text(item["degree"])} · {text(item["institution"])}', "entry")]
    dates = item["dates"] + (" · " + item["completion"] if item.get("completion") else "")
    entry.append(para(text(dates), "small"))
    if not item["degree"].startswith("BS"):
        entry.append(para(f'<i>Thesis:</i> {text(item["thesis"])}', "small"))
    story.append(KeepTogether(entry))

story.append(section("Research experience"))
for item in cv["experience"]:
    story.append(para(f'{text(item["role"])} · {text(item["institution"])}', "entry"))
    story.append(para(text(item["dates"]), "small"))
    # The full web CV retains every bullet; the PDF omits a generic dissemination line.
    accomplishments = [b for b in item["bullets"] if not b.startswith("Communicated research")]
    story.append(bullets(accomplishments))

story.append(section("Technical skills"))
for item in cv["skills"]:
    story.append(para(f'<b>{text(item["label"])}:</b> {text(item["items"])}', "small"))
story.append(para("<b>Research support:</b> " + text(cv["support"]), "small"))

story.append(PageBreak())
story.append(para("Publications & research contributions", "name"))
for group, title in [("peer_reviewed", "Peer-reviewed & accepted publications"),
                     ("preprint", "Manuscripts under review")]:
    story.append(section(title))
    for pub in publications:
        if pub["group"] != group:
            continue
        authors = ", ".join("<b>" + text(a) + "</b>" if a == "A. Mohammadi" else text(a)
                            for a in pub["authors"])
        venue = f'{text(pub["venue"])} ({pub["year"]})'
        if pub.get("details"):
            venue += ", " + text(pub["details"])
        if pub["status"] != "Published":
            venue += " · " + text(pub["status"])
        resources = " · ".join(link(r["url"], r["label"]) for r in pub.get("links", []))
        content = f'{authors}. <b>{text(pub["title"])}</b>. <i>{venue}</i>.'
        if resources:
            content += " " + resources
        story.append(para(content, "pub"))

story.append(section("Academic service, teaching & mentoring"))
story.append(para(" ".join(text(item) for item in cv["service"]), "small"))
story.append(para(" ".join(text(item) for item in cv["mentoring"]), "small"))
story.append(section("Awards"))
for award in cv["awards"]:
    story.append(para(text(award["title"] + " · " + award["date"]), "small"))
story.append(para("<b>Languages:</b> " + text(cv["languages"]), "small"))

output = ROOT / "documents" / "Amir_CV_2026.pdf"
doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=43, leftMargin=43,
                        topMargin=38, bottomMargin=49,
                        title=profile["display_name"] + " — Research CV",
                        author=profile["name"], subject=profile["focus"],
                        pageCompression=1)
doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
from pypdf import PdfReader
reader = PdfReader(str(output))
page_count = len(reader.pages)
cv_page = ROOT / "_pages" / "cv.html"
content = re.sub(r'<span id="cv-pages">\d+ pages</span>',
                 f'<span id="cv-pages">{page_count} pages</span>', cv_page.read_text())
cv_page.write_text(content)
assert all(page.extract_text().strip() for page in reader.pages), "PDF must contain selectable text"
print(f"Created {output.relative_to(ROOT)}: {page_count} pages, {output.stat().st_size:,} bytes")
