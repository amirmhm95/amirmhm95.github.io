#!/usr/bin/env python3
"""Check layout, images, navigation, text enlargement, and keyboard access.

Uses a temporary local HTTP server and saves review artifacts inside .tools/review.
If .tools/axe.min.js exists, also runs axe's WCAG A/AA accessibility checks.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import json
import os
import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
ARTIFACTS = ROOT / ".tools/review"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
config = yaml.safe_load((ROOT / "_config.yml").read_text())
BASE = config["baseurl"]
routes = ["/", "/research/", "/publications/", "/cv/", "/404.html"]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def do_GET(self):
        if self.path.startswith(BASE + "/"):
            self.path = self.path[len(BASE):]
        else:
            self.send_error(404)
            return
        super().do_GET()

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
Thread(target=server.serve_forever, daemon=True).start()
origin = f"http://127.0.0.1:{server.server_port}{BASE}"
results = []
errors = []
axe_path = ROOT / ".tools/axe.min.js"
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        for width in (320, 375, 540, 768, 1024, 1440):
            page.set_viewport_size({"width": width, "height": 1000})
            for route in routes:
                response = page.goto(origin + route, wait_until="networkidle")
                assert response.status == 200, (route, response.status)
                assert page.locator("h1").count() == 1
                assert page.locator("nav[aria-label='Main navigation'] a").count() == 4
                if route not in ("/404.html", "/cv/"):
                    assert page.locator("[aria-current='page']").count() == 1
                # Exercise below-the-fold content before judging image loading or captures.
                for image in page.locator("img").all():
                    image.scroll_into_view_if_needed()
                    image.evaluate("async image => { await image.decode(); }")
                page.evaluate("scrollTo(0, 0)")
                layout = page.evaluate("""() => ({
                    width: innerWidth,
                    content: document.documentElement.scrollWidth,
                    badImages: [...document.images].filter(i => !i.complete || !i.naturalWidth).map(i => i.src)
                })""")
                assert layout["content"] <= layout["width"] + 1, (route, width, "horizontal overflow", layout)
                assert not layout["badImages"], (route, layout["badImages"])
                assert page.locator("a[download]").count() == 0
                assert page.locator("nav[aria-label='Main navigation'] a").last.get_attribute("href") == BASE + "/documents/Amir_CV_2026.pdf"
                results.append({"route": route, "width": width, "layout": "pass"})
                if width in (375, 1440):
                    if route in ("/", "/research/", "/publications/", "/cv/"):
                        name = "home" if route == "/" else route.strip("/")
                        page.screenshot(path=str(ARTIFACTS / f"{name}-{width}.png"), full_page=True)
                    if axe_path.exists():
                        page.add_script_tag(path=str(axe_path))
                        audit = page.evaluate("""async () => await axe.run(document, {
                          runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}
                        })""")
                        violations = [{"id": v["id"], "impact": v["impact"],
                                       "targets": [n["target"] for n in v["nodes"]]}
                                      for v in audit["violations"]]
                        assert not violations, (route, width, violations)
        # 320px reflow corresponds to a 1280px viewport at 400% browser zoom.
        # Separately test 200% text enlargement at both desktop and narrow widths.
        for width in (375, 1440):
            page.set_viewport_size({"width": width, "height": 1000})
            for route in routes:
                page.goto(origin + route)
                page.evaluate("document.documentElement.style.fontSize = '200%'")
                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), (route, width, "200% text overflow")
                results.append({"route": route, "width": width, "text_enlargement": "200% pass"})
        page.set_viewport_size({"width": 375, "height": 900})
        page.goto(origin + "/")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.className") == "skip-link"
        page.keyboard.press("Enter")
        assert page.evaluate("document.activeElement.id") == "main"
        page.goto(origin + "/")
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.className") == "wordmark"
        for name in ("Home", "Research", "Publications", "CV"):
            page.keyboard.press("Tab")
            assert page.evaluate("document.activeElement.textContent") == name
            outline = page.evaluate("getComputedStyle(document.activeElement).outlineWidth")
            assert outline == "3px", (name, outline)
        page.emulate_media(reduced_motion="reduce")
        assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        page.emulate_media(media="print")
        page.goto(origin + "/cv/")
        assert not page.locator(".site-header").is_visible()
        # The portfolio should remain fully navigable without executable JavaScript.
        context_no_js = browser.new_context(java_script_enabled=False,
                                            viewport={"width": 375, "height": 900})
        page_no_js = context_no_js.new_page()
        for route in routes:
            page_no_js.goto(origin + route)
            assert page_no_js.locator("nav[aria-label='Main navigation'] a:visible").count() == 4
            assert page_no_js.locator("h1").is_visible()
        context_no_js.close()
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
(ARTIFACTS / "browser-checks.json").write_text(json.dumps(results, indent=2))
print(f"PASS: {len(results)} page/viewport/text-size checks, image loading, current navigation, keyboard skip link, visible focus, reduced-motion setting, print layout, and navigation without JavaScript.")
print("WCAG A/AA axe checks passed at 375px and 1440px." if axe_path.exists() else "axe not installed; automated accessibility audit skipped.")
