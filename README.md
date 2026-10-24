# Amir Mohammadi — research portfolio

Personal academic website: **https://amirmhm95.github.io/amirmmohammadi/**

A static Jekyll site with a custom, accessible portfolio layout. The active pages use native CSS and semantic HTML; they require no JavaScript, remote fonts, or icon CDN. The earlier Minimal Mistakes theme files remain available, with their license preserved, but are not used by the portfolio layout.

## Edit content

| Content | Source |
| --- | --- |
| Name, contact links, research summary, PDF URL, featured publications | `_data/profile.yml` |
| Education, experience, skills, service, awards | `_data/cv.yml` |
| Publications, author order, status, resource links | `_data/publications.yml` |
| Homepage | `index.html` |
| Research summaries | `_pages/research.html` |
| About, HTML CV, publication list | `_pages/` |
| Navigation | `_data/navigation.yml` |
| Active template and components | `_layouts/portfolio.html`, `_includes/portfolio/` |
| Active styles | `assets/css/portfolio.css` |
| Site address, update date, indexing | `_config.yml` |
| Public PDF | `documents/Amir_CV_2026.pdf` |

Use `relative_url` for internal links and `absolute_url` for canonical/social URLs. Keep `url: https://amirmhm95.github.io` and `baseurl: /amirmmohammadi` together unless the hosting address changes. Existing `/aboutme/` and PDF addresses are preserved. The CV navigation item opens the PDF directly; `/cv/` remains an accessible HTML overview. PDF links do not use a download attribute. The unused blog is excluded from the build and sitemap.

Publication author order and review status must be checked before updates. `_data/publications.yml` also feeds the PDF generator. If research or career data changes, regenerate the PDF and update the prose where relevant. Keep `updated` and `last_modified_at` in `_config.yml` current. The website uses Gmail for all contact links. The final examination and expected graduation date are recorded separately; the degree is not presented as conferred.

## Preview and build

Use Ruby with Bundler. The lockfile pins the tested dependencies.

```sh
bundle install
bundle exec jekyll serve
```

Open **http://127.0.0.1:4000/amirmmohammadi/**. Configuration changes require restarting the server.

For this working copy, project-local build tools have already been installed in the ignored `.tools/` directory. The helper uses them when present and falls back to ordinary Bundler on another computer:

```sh
bash scripts/site.sh serve
bash scripts/site.sh build
```

The generated `_site/` directory is ignored. Never commit `.tools/`, `.bundle/`, or generated review screenshots. npm is not required for the active portfolio. The old npm scripts and theme templates are retained only for the earlier theme.

## Regenerate the PDF CV

The comprehensive Pages CV is a read-only source document. It is **not** opened or modified by the generator. Website data is the editable source for the new public PDF.

With Python 3.9 or later, install `requirements-dev.txt` in a project-local environment, then run:

```sh
python3 scripts/build_cv.py
```

In this prepared working copy:

```sh
PYTHONPATH="$PWD/.tools/python" PYTHONDONTWRITEBYTECODE=1 python3 scripts/build_cv.py
```

This replaces `documents/Amir_CV_2026.pdf` and updates its page count in `_pages/cv.html`. It embeds fonts and selectable text, preserves author order, and adds clickable paper/profile links. It uses a single-column layout and standard section headings. Footers are drawn after the page body to preserve text-extraction order. Methods and task keywords appear in accomplishment bullets; the PDF skills section lists programming languages, libraries, and development tools. Review pagination after substantive changes; the current CV has two pages. Build the site again afterward.

## Verify changes

After a Jekyll build:

```sh
python3 scripts/check_site.py
python3 -m playwright install chromium
python3 scripts/check_browser.py
```

For the tools already prepared in this working copy:

```sh
PYTHONPATH="$PWD/.tools/python" PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_site.py
PYTHONPATH="$PWD/.tools/python" PYTHONDONTWRITEBYTECODE=1 PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers" TMPDIR="$PWD/.tools/tmp" python3 scripts/check_browser.py
```

The static check validates local links, images, fragments, canonical URLs, sitemap exclusions, PDF coverage, career milestones, and the PDF’s initial reading order. Browser checks cover six screen widths (320–1440px), 200% text enlargement, keyboard navigation, visible focus, reduced-motion configuration, print behavior, and image loading. The 320px layout also tests reflow equivalent to a 1280px browser viewport at 400% zoom. Screenshots and results are saved only in `.tools/review/`.

When `.tools/axe.min.js` exists, the browser script also runs axe WCAG A/AA checks. These automated checks complement manual review; they do not replace assistive-technology testing. External publishers may block automated requests even when a link works in a regular browser.

## Publishing

**No deployment is initiated by these scripts.** Review and push the source changes yourself. Keep the repository's existing GitHub Pages settings; the source files do not change those settings. If Pages is configured to build from `master` at the repository root, pushing to that source branch will trigger GitHub's normal Pages build. Confirm the configured publishing source in GitHub → Settings → Pages before changing it.

The validation workflow runs on pull requests or manual dispatch and has read-only repository permissions. It does not publish the website. After your push, check the Pages build, then open the homepage, Research, Publications, About, CV, and PDF links on the public address.

Preserve `LICENSE` and attribution for retained third-party theme code and research figures.
