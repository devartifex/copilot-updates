# GitHub Changelog → PowerPoint

> Fetch GitHub changelog articles for **any label** (Copilot, Actions, Security, and more) and turn them into a polished presentation — powered by a Python scraper, a VS Code Copilot agent, and a Python PowerPoint generator.

[![Built with GitHub Copilot](https://img.shields.io/badge/Built%20with-GitHub%20Copilot-8957e5?logo=githubcopilot)](https://github.com/features/copilot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?logo=python&logoColor=white)](https://www.python.org)

---

## 🙏 Credits

Special thanks to [@congiuluc](https://github.com/congiuluc) for conceiving and inspiring this solution.

---

## ✨ Features

- 🏷️ **Multi-label support** — fetch articles for any of the 13 GitHub changelog labels (see table below)
- 🤖 **One-click workflow** — Copilot agent orchestrates Python scraping → AI summarization → PowerPoint generation
- 📊 **Dark GitHub-themed slides** — widescreen 16:9 `.pptx` with section dividers, hero images, and speaker notes
- 🌍 **Multi-language support** — summaries and notes translated into any language; titles and technical terms stay in English
- ⏩ **Incremental processing** — already-processed articles are skipped on re-runs
- 🚀 New Releases · ✨ Improvements · ⚠️ Deprecations — articles sorted by type
- 🔍 **Label & category filtering** — generate presentations filtered by label and/or category
- 🖼️ **Fallback images** — built-in placeholder images when article hero images are unavailable
- 🔗 **Clickable links** — each summary slide includes a hyperlink back to the original article
- ⚙️ **Centralized configuration** — all labels, categories, and settings in `config.yaml`

### Available labels

| Slug | Display Name |
|---|---|
| `account-management` | Account Management |
| `actions` | Actions |
| `application-security` | Application Security |
| `client-apps` | Client Apps |
| `collaboration-tools` | Collaboration Tools |
| `community-engagement` | Community Engagement |
| `copilot` | Copilot |
| `ecosystem-and-accessibility` | Ecosystem & Accessibility |
| `enterprise-management-tools` | Enterprise Management Tools |
| `platform-governance` | Platform Governance |
| `projects-and-issues` | Projects & Issues |
| `supply-chain-security` | Supply Chain Security |
| `universe25` | Universe '25 |

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

### Option A — One-click with the Copilot agent (recommended)

Open VS Code Copilot Chat in **Agent mode** and invoke the custom agent:

```
@copilot-updates
```

You'll be asked for:

| Input | Description | Example |
|---|---|---|
| `startDate` | Start of date range (YYYY-MM-DD) | `2026-02-01` |
| `endDate` | End of date range (YYYY-MM-DD) | `2026-02-25` |
| `labels` | Label slugs (comma-separated, or `all`) | `copilot,actions` |
| `language` | Language for summaries and speaker notes | `english` (default) |

The agent will:

1. **Run `fetch_articles.py`** — scrapes changelog listing pages and individual articles, saves raw `.md` files to `output/raw/`
2. **Generate summaries** — classifies each article, creates structured slide content + speaker notes in your chosen language
3. **Save** final markdown files under `output/{locale}/` organized by type
4. **Update** `output/{locale}/index.md` — a table of contents
5. **Run `create_pptx.py`** — generates the PowerPoint presentation

> [!TIP]
> Re-running the agent for the same date range is safe — both the scraper and the agent skip articles that already have output files.

### Option B — Manual two-step workflow

#### Step 1 — Fetch raw articles

```bash
# Fetch Copilot articles for February 2026
python fetch_articles.py --labels copilot --from-date 2026-02-01 --to-date 2026-02-25

# Fetch multiple labels
python fetch_articles.py --labels copilot,actions,client-apps --from-date 2026-02-01 --to-date 2026-02-25

# Fetch ALL labels
python fetch_articles.py --labels all --from-date 2026-02-01 --to-date 2026-02-25
```

| Flag | Default | Description |
|---|---|---|
| `--labels`, `-L` | `copilot` | Comma-separated label slugs, or `all` |
| `--from-date` | *required* | Start date (YYYY-MM-DD) |
| `--to-date` | *required* | End date (YYYY-MM-DD) |
| `--output-dir`, `-d` | `output/` | Output directory |

> After fetching, run the Copilot agent (`/fetch-github-changelog`) to generate summaries from the raw files, or write your own summaries manually.

#### Step 2 — Generate the PowerPoint

```bash
# Default: all articles in output/en/
python create_pptx.py

# Filter by label
python create_pptx.py --label copilot

# Filter by multiple labels and categories
python create_pptx.py --label copilot,actions --categories new-release,improvement

# Date range + locale
python create_pptx.py --locale it --from-date 2026-02-01 --to-date 2026-02-25
```

| Flag | Default | Description |
|---|---|---|
| `--output-dir`, `-d` | `output/` | Root directory containing locale subfolders |
| `--locale`, `-l` | `en` | Locale subfolder to read from |
| `--output`, `-o` | auto-generated | Output `.pptx` filename |
| `--from-date` | auto-detected | Start date filter |
| `--to-date` | auto-detected | End date filter |
| `--label`, `-L` | *(all)* | Comma-separated label slugs to filter by |
| `--categories`, `-c` | *(all)* | Comma-separated categories: `new-releases`, `improvements`, `deprecations` |

The script reads markdown files from `output/{locale}/{new-releases,improvements,deprecations}/` and produces a widescreen (16:9) `.pptx` with dark GitHub-themed slides:

- **Title slide** with the date range and active filters
- **Section dividers** for New Releases 🚀, Improvements ✨, Deprecations ⚠️
- **Article title slide** with hero image (or fallback placeholder)
- **Summary slide** with structured content, clickable article link, and speaker notes in the Notes pane

> [!NOTE]
> When a non-English language is specified, summaries and speaker notes are translated into that language. Article titles, product names, and technical terms always stay in English.

---

## 🗂️ Markdown file format

<details>
<summary>Each article markdown file follows this structure (produced by the Copilot agent)</summary>

```markdown
---
title: "Article Title"
date: "2026-02-15"
type: "new-releases"
labels: ["copilot", "client-apps"]
image_url: "https://github.blog/wp-content/uploads/..."
article_url: "https://github.blog/changelog/2026-02-15-slug"
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

## ⚙️ Configuration

All labels, categories, colors, and defaults are defined in [`config.yaml`](config.yaml). Edit this file to:
- Add or remove changelog labels
- Change category colors/emojis
- Update default label selections
- Add new type aliases

---

## 📂 Project structure

```
copilot-updates/
├── .github/
│   └── copilot/
│       └── agents/
│           └── copilot-updates.agent.md  # Custom Copilot agent
├── imgs/                                      # Fallback hero images
│   ├── featured-v3-new-releases.png
│   ├── featured-v3-improvements.png
│   └── featured-v3-deprecations.png
├── config.yaml                                # Centralized configuration
├── fetch_articles.py                          # Python scraper (Step 1)
├── create_pptx.py                             # PowerPoint generator (Step 2)
├── pyproject.toml                             # Project metadata & dependencies
├── LICENSE
└── README.md
```

---

## 🤖 Built with GitHub Copilot

This repository was created entirely with [GitHub Copilot](https://github.com/features/copilot).


## 📄 License

This project is licensed under the [MIT License](LICENSE).
