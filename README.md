<div align="center">

# GitHub Changelog → PowerPoint

**Turn GitHub changelog articles into polished, presentation-ready slides — automatically.**

Fetch articles for any label (Copilot, Actions, Security, and more), generate structured summaries with AI, and produce dark-themed 16:9 PowerPoint presentations — all from a single command.

[![Built with GitHub Copilot](https://img.shields.io/badge/Built_with-GitHub_Copilot-8957e5?style=for-the-badge&logo=githubcopilot&logoColor=white)](https://github.com/features/copilot)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 🎯 The Opportunity

GitHub ships product updates **every single week** — across Copilot, Actions, Security, and more.

For any team that tracks these changes, the same recurring challenge surfaces: **how do you stay on top of everything, and share what matters with your audience in a meaningful way?**

Today, the answer is usually manual:

- Someone reads through dozens of changelog articles
- Picks what's relevant for their team or audience
- Writes summaries, formats slides, repeats this every week

**That's hours of low-leverage work — done by people who should be doing something harder.**

---

## ✨ The Solution

This repository is a **working AI pipeline** that takes GitHub changelog articles as input and produces a **polished, multilingual PowerPoint presentation** as output — automatically.

```
github.blog/changelog
        │
        ▼
  fetch_articles.py        ← scrapes raw changelog articles
        │
        ▼
  process_articles.py      ← prepares batches, validates output
        │
        ▼
  GitHub Copilot Agent     ← reads each article, writes structured summaries + speaker notes
        │
        ▼
  create_pptx.py           ← assembles the final .pptx, dark-themed, 16:9, ready to present
        │
        ▼
  presentation.pptx  🎉
```

One command. A few minutes. Done.

> The Copilot agent orchestrates the entire pipeline end-to-end — from fetch to finished slides.

---

## ⏱️ Time Saved

| Task | Without AI | With this pipeline |
|---|---|---|
| Reading & filtering changelog articles | ~60 min/week | ~0 min — automated |
| Writing summaries per article | ~5 min each | ~0 min — Copilot writes them |
| Translating for local teams | ~2 hrs/language | ~0 min — any language on demand |
| Formatting slides | ~30 min/session | ~0 min — generated automatically |
| **Total per weekly briefing** | **~3–4 hours** | **< 5 minutes** |

---

## Table of Contents

- [How It Works](#-how-it-works)
- [Features](#-features)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
  - [Option A — Copilot Agent (recommended)](#option-a--one-click-with-the-copilot-agent-recommended)
  - [Option B — Manual CLI Workflow](#option-b--manual-cli-workflow)
- [Supported Labels](#-supported-labels)
- [Article Format](#-article-format)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [Credits](#-credits)
- [License](#-license)

---

## 🔄 How It Works

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   github.blog/changelog ──► fetch_articles.py ──► output/raw/*.md               │
│                                                                                 │
│   output/raw/*.md ──► process_articles.py --prepare ──► batch.json              │
│                                                                                 │
│   batch.json ──► AI Summarization (Copilot Agent) ──► output/{locale}/**/*.md   │
│                                                                                 │
│   output/{locale}/ ──► process_articles.py --validate --index                   │
│                                                                                 │
│   output/{locale}/ ──► create_pptx.py ──► presentation.pptx                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

| Stage | Script | What it does |
|:---:|---|---|
| **1. Fetch** | `fetch_articles.py` | Scrapes `github.blog/changelog` and saves raw `.md` files to `output/raw/` |
| **2. Process** | `process_articles.py` | `--prepare` plans batches, `--validate` checks formatting, `--index` builds the index |
| **3. Summarize** | Copilot Agent / Manual | Generates structured summaries + speaker notes using AI prompt templates |
| **4. Present** | `create_pptx.py` | Produces a widescreen 16:9 `.pptx` with dark GitHub-themed slides |

---

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🏷️ | **Multi-label support** | Fetch articles for any of the 13 GitHub changelog labels |
| 🤖 | **One-click workflow** | Copilot agent orchestrates the entire pipeline end-to-end |
| 📊 | **Dark-themed slides** | Widescreen 16:9 `.pptx` with GitHub Primer colors, section dividers, and hero images |
| 🌍 | **Multi-language** | Summaries and speaker notes translated into any language; titles stay in English |
| ⏩ | **Incremental runs** | Already-processed articles are automatically skipped on re-runs |
| 🔍 | **Filtering** | Generate presentations filtered by label, category, or date range |
| 🖼️ | **Fallback images** | Built-in placeholders when article hero images are unavailable |
| 🔗 | **Clickable links** | Every summary slide links back to the original changelog article |
| ✅ | **Built-in validation** | Checks front matter, headings, and speaker notes before generating slides |
| ⚙️ | **Centralized config** | All labels, categories, colors, and defaults in a single `config.yaml` |

---

## 🚀 Getting Started

### Prerequisites

- [Python 3.11+](https://www.python.org)
- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://github.com/features/copilot) *(for agent mode — optional for CLI usage)*

### Installation

```bash
# Recommended: install with uv (fastest)
uv sync
```

<details>
<summary><strong>Alternative: plain venv / pip</strong></summary>

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install .
```

</details>

> **Don't have `uv`?** Install it with `pip install uv` or see the [uv docs](https://docs.astral.sh/uv/getting-started/installation/).

---

## 📖 Usage

### Option A — One-click with the Copilot agent (recommended)

Open VS Code Copilot Chat in **Agent mode** and invoke:

```
@copilot-updates
```

You'll be prompted for:

| Input | Description | Example |
|---|---|---|
| `startDate` | Start of date range (YYYY-MM-DD) | `2026-02-01` |
| `endDate` | End of date range (YYYY-MM-DD) | `2026-02-25` |
| `labels` | Label slugs (comma-separated, or `all`) | `copilot,actions` |
| `language` | Language for summaries and speaker notes | `english` (default) |

The agent runs a **six-step pipeline** automatically:

```
Fetch → Prepare → Summarize → Validate → Index → PowerPoint
```

1. **Fetch raw articles** — `fetch_articles.py` scrapes changelog pages into `output/raw/`
2. **Prepare batch manifest** — `process_articles.py --prepare` produces `output/batch.json`
3. **Generate summaries** — AI creates structured slide content + speaker notes
4. **Validate output** — `process_articles.py --validate` checks formatting
5. **Generate index** — `process_articles.py --index` creates `output/{locale}/index.md`
6. **Generate PowerPoint** — `create_pptx.py` produces the final `.pptx`

> [!TIP]
> Re-running the agent for the same date range is safe — both the scraper and the agent skip articles that already have output files.

---

### Option B — Manual CLI workflow

#### 1. Fetch raw articles

```bash
# Single label
python fetch_articles.py --labels copilot --from-date 2026-02-01 --to-date 2026-02-25

# Multiple labels
python fetch_articles.py --labels copilot,actions,client-apps --from-date 2026-02-01 --to-date 2026-02-25

# All labels
python fetch_articles.py --labels all --from-date 2026-02-01 --to-date 2026-02-25
```

<details>
<summary><strong>fetch_articles.py flags</strong></summary>

| Flag | Default | Description |
|---|---|---|
| `--labels`, `-L` | `copilot` | Comma-separated label slugs, or `all` |
| `--from-date` | *required* | Start date (YYYY-MM-DD) |
| `--to-date` | *required* | End date (YYYY-MM-DD) |
| `--output-dir`, `-d` | `output/` | Output directory |

</details>

#### 2. Process articles

```bash
# Prepare batch manifest
python process_articles.py --prepare --locale en --from-date 2026-02-01 --to-date 2026-02-25

# Validate processed files (after AI summarization or manual writing)
python process_articles.py --validate --locale en

# Generate index
python process_articles.py --index --locale en

# Or run all three stages at once
python process_articles.py --prepare --validate --index --locale en \
  --from-date 2026-02-01 --to-date 2026-02-25
```

<details>
<summary><strong>process_articles.py flags</strong></summary>

| Flag | Default | Description |
|---|---|---|
| `--prepare` | — | Scan raw files and produce `output/batch.json` |
| `--validate` | — | Validate processed article files |
| `--index` | — | Generate/update `index.md` |
| `--locale`, `-l` | `en` | Locale code |
| `--from-date` | *(none)* | Start date filter (YYYY-MM-DD) |
| `--to-date` | *(none)* | End date filter (YYYY-MM-DD) |
| `--labels`, `-L` | *(all)* | Comma-separated label slugs to filter |
| `--output-dir`, `-d` | `output/` | Output directory |

> At least one of `--prepare`, `--validate`, or `--index` must be specified.

</details>

#### 3. Generate the PowerPoint

```bash
# All articles for default locale
python create_pptx.py

# Filter by label
python create_pptx.py --label copilot

# Multiple labels + categories
python create_pptx.py --label copilot,actions --categories new-release,improvement

# Specific locale + date range
python create_pptx.py --locale it --from-date 2026-02-01 --to-date 2026-02-25
```

<details>
<summary><strong>create_pptx.py flags</strong></summary>

| Flag | Default | Description |
|---|---|---|
| `--output-dir`, `-d` | `output/` | Root directory containing locale subfolders |
| `--locale`, `-l` | `en` | Locale subfolder to read from |
| `--output`, `-o` | auto-generated | Output `.pptx` filename |
| `--from-date` | auto-detected | Start date filter |
| `--to-date` | auto-detected | End date filter |
| `--label`, `-L` | *(all)* | Comma-separated label slugs to filter by |
| `--categories`, `-c` | *(all)* | Comma-separated categories: `new-releases`, `improvements`, `deprecations` |

</details>

**Output slides include:**

| Slide Type | Description |
|---|---|
| **Title slide** | Date range and active filters |
| **Section dividers** | 🚀 New Releases · ✨ Improvements · ⚠️ Deprecations |
| **Article title** | Hero image (or fallback placeholder) |
| **Summary** | Structured content, clickable link, and speaker notes |

> [!NOTE]
> When a non-English language is specified, summaries and speaker notes are translated. Article titles, product names, and technical terms always stay in English.

---

## 🏷️ Supported Labels

All 13 labels available on `github.blog/changelog`:

| Slug | Display Name | | Slug | Display Name |
|---|---|---|---|---|
| `account-management` | Account Management | | `copilot` | Copilot |
| `actions` | Actions | | `ecosystem-and-accessibility` | Ecosystem & Accessibility |
| `application-security` | Application Security | | `enterprise-management-tools` | Enterprise Management Tools |
| `client-apps` | Client Apps | | `platform-governance` | Platform Governance |
| `collaboration-tools` | Collaboration Tools | | `projects-and-issues` | Projects & Issues |
| `community-engagement` | Community Engagement | | `supply-chain-security` | Supply Chain Security |
| | | | `universe25` | Universe '25 |

---

## 🗂️ Article Format

<details>
<summary><strong>Each processed article follows this markdown structure</strong></summary>

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

| Type | Heading |
|---|---|
| New Releases | `## What's new` |
| Improvements | `## What changed` |
| Deprecations | `## What's deprecated` |

</details>

---

## ⚙️ Configuration

All labels, categories, colors, and defaults are defined in [`config.yaml`](config.yaml):

| Setting | Description |
|---|---|
| `labels` | All available changelog labels (slug → display name) |
| `categories` | Article types with emoji, color, and directory mapping |
| `type_aliases` | Maps non-canonical type strings to canonical keys |
| `badge_type_map` | Maps badge text from changelog pages to article types |
| `colors` | GitHub Primer dark-theme color palette (RGB) |
| `defaults` | Default locale, labels, and output directory |

---

## 📂 Project Structure

```
copilot-updates/
│
├── .github/
│   ├── agents/
│   │   └── copilot-updates.agent.md       # Copilot agent — 6-step orchestration
│   ├── copilot-instructions.md            # Repo-level Copilot rules
│   └── prompts/                           # AI summarization prompt templates
│       ├── summarize-new-releases.prompt.md
│       ├── summarize-improvements.prompt.md
│       ├── summarize-deprecations.prompt.md
│       └── translate-content.prompt.md
│
├── imgs/                                  # Fallback hero images
│   ├── featured-v3-new-releases.png
│   ├── featured-v3-improvements.png
│   └── featured-v3-deprecations.png
│
├── output/                                # Generated artifacts (git-ignored)
│   ├── raw/                               # Scraped raw articles (language-independent)
│   └── {locale}/                          # Processed articles per language
│       ├── index.md
│       ├── new-releases/
│       ├── improvements/
│       └── deprecations/
│
├── config.yaml                            # Centralized configuration
├── fetch_articles.py                      # Stage 1 — Web scraper
├── process_articles.py                    # Stage 2 — Batch planning, validation, indexing
├── create_pptx.py                         # Stage 3 — PowerPoint generator
├── pyproject.toml                         # Project metadata & dependencies
├── LICENSE                                # MIT License
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

> When adding new categories or labels, update `config.yaml` — all scripts read it at startup.

---

## 🙏 Credits

Special thanks to [@congiuluc](https://github.com/congiuluc) for conceiving and inspiring this solution.

This repository was built entirely with [GitHub Copilot](https://github.com/features/copilot).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
