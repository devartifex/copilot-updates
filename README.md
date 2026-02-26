# Copilot Updates → PowerPoint

> A two-step workflow to fetch GitHub Copilot changelog articles and turn them into a polished presentation — powered by a VS Code Copilot agent and a Python script.

[![Built with GitHub Copilot](https://img.shields.io/badge/Built%20with-GitHub%20Copilot-8957e5?logo=githubcopilot)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&logoColor=white)](https://www.python.org)

---

## 🙏 Credits

Special thanks to [@congiuluc](https://github.com/congiuluc) for conceiving and inspiring this solution.

---

## ✨ Features

- 🤖 **Copilot agent prompt** fetches and classifies changelog articles automatically
- 📊 **Dark GitHub-themed slides** — widescreen 16:9 `.pptx` with section dividers, hero images, and speaker notes
- 🌍 **Multi-language support** — summaries and notes translated into any language; titles and technical terms stay in English
- ⏩ **Incremental processing** — already-processed articles are skipped on re-runs
- 🚀 New Releases · ✨ Improvements · ⚠️ Deprecations — articles sorted by type
- 🖼️ **Fallback images** — built-in placeholder images when article hero images are unavailable
- 🔗 **Clickable links** — each summary slide includes a hyperlink back to the original article

---

## 📋 Prerequisites

- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://github.com/features/copilot) (agent mode)
- [Python 3.11+](https://www.python.org)

## 🚀 Getting started

```bash
# Create a virtual environment and install dependencies in one step
uv sync
```

> **Don't have `uv`?** Install it with `pip install uv` or follow the [official docs](https://docs.astral.sh/uv/getting-started/installation/).

> **Prefer plain `venv`/`pip`?**
> ```bash
> python -m venv .venv
> # Windows (PowerShell)
> .venv\Scripts\Activate.ps1
> # macOS / Linux
> source .venv/bin/activate
> pip install .
> ```

---

## 📖 Workflow

### Step 1 — Generate markdown files with the Copilot agent

Open VS Code Copilot Chat in **Agent mode** and run:

```
/fetch-copilot-news
```

You'll be asked for:

| Input | Description | Example |
|---|---|---|
| `startDate` | Start of date range (YYYY-MM-DD) | `2025-01-01` |
| `endDate` | End of date range (YYYY-MM-DD) | `2025-12-31` |
| `language` | Language for summaries and speaker notes | `english` (default) |

The agent will:

1. Fetch **all** article listings from `github.blog/changelog` filtered by `copilot` label (following all pagination links)
2. Fetch each individual article page and **save raw content** under `output/raw/`
3. Classify each article by type (`new-release`, `improvement`, `deprecation`)
4. Generate **structured slide content** and **speaker notes** (in your chosen language)
5. Save final markdown files under `output/{locale}/` organized by type (e.g. `output/en/`, `output/it/`)
6. Update `output/{locale}/index.md` — a table of contents with links to all articles

> [!TIP]
> Re-running the prompt for the same date range is safe — the agent skips articles that already have output files, so only new articles are processed.

<details>
<summary>📁 Output file structure</summary>

```
output/
├── raw/                                  # Raw fetched content (shared, language-independent)
│   ├── 2025-03-15-some-feature.md
│   ├── 2025-04-01-some-improvement.md
│   └── ...
└── en/                                   # Locale folder (en, it, es, fr, …)
    ├── index.md                          # Table of contents
    ├── new-releases/                     # Classified final files
    │   ├── 2025-03-15-some-feature.md
    │   └── ...
    ├── improvements/
    │   ├── 2025-04-01-some-improvement.md
    │   └── ...
    └── deprecations/
        └── ...
```

</details>

### Step 2 — Generate the PowerPoint

```bash
python create_pptx.py
```

Options:

```bash
python create_pptx.py --locale it --output my-presentation.pptx
python create_pptx.py --from-date 2025-01-01 --to-date 2025-12-31
python create_pptx.py --output-dir output/ --locale en
```

| Flag | Default | Description |
|---|---|---|
| `--output-dir`, `-d` | `output/` | Root directory containing locale subfolders |
| `--locale`, `-l` | `en` | Locale subfolder to read from (e.g. `en`, `it`, `es`) |
| `--output`, `-o` | auto-generated | Output `.pptx` filename |
| `--from-date` | auto-detected | Start date filter and title-slide label |
| `--to-date` | auto-detected | End date filter and title-slide label |

The script reads markdown files from `output/{locale}/{new-releases,improvements,deprecations}/` and produces a widescreen (16:9) `.pptx` with dark GitHub-themed slides:

- **Title slide** with the date range
- **Section dividers** for New Releases 🚀, Improvements ✨, Deprecations ⚠️
- **Article title slide** with hero image (or fallback placeholder)
- **Summary slide** with structured content, clickable article link, and speaker notes in the Notes pane

> [!NOTE]
> When a non-English language is specified in Step 1, summaries and speaker notes are translated into that language. Article titles, product names, and technical terms always stay in English.

---

## 🗂️ Markdown file format

<details>
<summary>Each article markdown file follows this structure (produced by the Copilot agent)</summary>

```markdown
---
title: "Article Title"
date: "2025-03-15"
type: "new-release"
image_url: "https://github.blog/wp-content/uploads/..."
article_url: "https://github.blog/changelog/2025-03-15-slug"
---

# Article Title

![hero](https://github.blog/wp-content/uploads/...)

---

## What's new

One-liner with **key product/feature** and **status**.

### Why it matters

- **Key benefit 1** — short explanation
- **Key benefit 2** — short explanation

### Where you can use it

- **Platform 1** — details

### Who gets it

- Plans, rollout info

<!--
speaker_notes:
Speaker notes in the target language (5–8 sentences).
-->
```

The `##` heading varies by article type:
- **New Releases** → `## What's new`
- **Improvements** → `## What changed`
- **Deprecations** → `## What's deprecated`

</details>

---

## 📂 Project structure

```
copilot-updates/
├── .github/
│   └── prompts/
│       └── fetch-copilot-news.prompt.md   # Copilot agent prompt
├── imgs/                                   # Fallback hero images
│   ├── featured-v3-new-releases.png
│   ├── featured-v3-improvements.png
│   └── featured-v3-deprecations.png
├── create_pptx.py                          # PowerPoint generator
├── pyproject.toml                          # Project metadata & dependencies
├── LICENSE
└── README.md
```

---

## 🤖 Built with GitHub Copilot

This repository was created entirely with [GitHub Copilot](https://github.com/features/copilot).


## 📄 License

This project is licensed under the [MIT License](LICENSE).
