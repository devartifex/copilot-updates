<div align="center">

# GitHub Changelog → PowerPoint

**Turn GitHub changelog articles into polished, presentation-ready slides — automatically.**

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

## 📸 Example Output

Every generated presentation uses a **dark GitHub-themed design** (16:9 widescreen) with four slide types:

| Title slide | Section divider |
|:---:|:---:|
| ![Title slide](imgs/slides/example-title.png) | ![Section divider](imgs/slides/example-section-divider.png) |
| Date range, active label filters, and source | Category header with article count |

| Article hero | Summary |
|:---:|:---:|
| ![Article hero](imgs/slides/example-article-hero.png) | ![Summary slide](imgs/slides/example-summary.png) |
| Article title with hero image and date | Structured content with clickable source link and speaker notes |

> Summaries and speaker notes can be generated in **any language** — the example above shows Italian. Article titles and technical terms always stay in English.

---

## 🚀 Getting Started

### Prerequisites

- [Python 3.11+](https://www.python.org)
- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://github.com/features/copilot) *(for agent mode — optional for CLI usage)*

### Installation

```bash
uv sync
```

<details>
<summary><strong>Alternative: plain venv / pip</strong></summary>

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate    # macOS / Linux
pip install .
```

</details>

---

## 📖 Usage

### Option A — Copilot Agent ✨ (recommended)

Open VS Code Copilot Chat in **Agent mode** and invoke:

```
@copilot-updates
```

You'll be prompted for:

| Input | Example |
|---|---|
| `startDate` | `2026-02-01` |
| `endDate` | `2026-02-25` |
| `labels` | `copilot,actions` or `all` |
| `language` | `italian`, `english`, `spanish`, ... |

The agent orchestrates the full pipeline end-to-end:

```
Fetch → Prepare → Summarize → Validate → Index → PowerPoint
```

> [!TIP]
> Re-running for the same date range is safe — both the scraper and the agent skip articles that already have output files.

---

### Option B — Manual CLI

#### 1. Fetch raw articles

```bash
python fetch_articles.py --labels copilot --from-date 2026-02-01 --to-date 2026-02-25
```

<details>
<summary><strong>More examples & flags</strong></summary>

```bash
# Multiple labels
python fetch_articles.py --labels copilot,actions,client-apps --from-date 2026-02-01 --to-date 2026-02-25

# All labels
python fetch_articles.py --labels all --from-date 2026-02-01 --to-date 2026-02-25
```

| Flag | Default | Description |
|---|---|---|
| `--labels`, `-L` | `copilot` | Comma-separated label slugs, or `all` |
| `--from-date` | *required* | Start date (YYYY-MM-DD) |
| `--to-date` | *required* | End date (YYYY-MM-DD) |
| `--output-dir`, `-d` | `output/` | Output directory |

</details>

#### 2. Process articles

```bash
python process_articles.py --prepare --validate --index --locale en \
  --from-date 2026-02-01 --to-date 2026-02-25
```

> Between `--prepare` and `--validate`, run the Copilot agent (or write summaries manually) to generate the structured article files.

<details>
<summary><strong>Flags</strong></summary>

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

</details>

#### 3. Generate the PowerPoint

```bash
python create_pptx.py --locale it --from-date 2026-02-01 --to-date 2026-02-25
```

<details>
<summary><strong>More examples & flags</strong></summary>

```bash
python create_pptx.py --label copilot
python create_pptx.py --label copilot,actions --categories new-release,improvement
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

</details>

---

## ⚙️ Configuration

All labels, categories, colors, and defaults live in [`config.yaml`](config.yaml). Supports all 13 GitHub changelog labels including `copilot`, `actions`, `application-security`, `client-apps`, and more.

<details>
<summary><strong>Supported labels</strong></summary>

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

</details>

<details>
<summary><strong>Article format</strong></summary>

Each processed article follows this markdown structure:

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

<!-- speaker_notes: Speaker notes in the target language (5–8 sentences). -->
```

The `##` heading varies by type: `What's new` (new-releases), `What changed` (improvements), `What's deprecated` (deprecations).

</details>

---

## 📂 Project Structure

```
copilot-updates/
├── .github/
│   ├── agents/
│   │   └── copilot-updates.agent.md       # Copilot agent — 6-step orchestration
│   └── prompts/                           # AI summarization prompt templates
├── imgs/                                  # Fallback hero images + slide examples
├── output/                                # Generated artifacts (git-ignored)
│   ├── raw/                               # Scraped raw articles (language-independent)
│   └── {locale}/                          # Processed articles per language
│       ├── index.md
│       ├── new-releases/
│       ├── improvements/
│       └── deprecations/
├── config.yaml                            # Centralized configuration
├── fetch_articles.py                      # Stage 1 — Web scraper
├── process_articles.py                    # Stage 2 — Batch planning, validation, indexing
├── create_pptx.py                         # Stage 3 — PowerPoint generator
└── pyproject.toml                         # Project metadata & dependencies
```

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes
4. **Open** a Pull Request

> When adding new categories or labels, update `config.yaml` — all scripts read it at startup.

---

## 🙏 Credits

Special thanks to [@congiuluc](https://github.com/congiuluc) for conceiving and inspiring this solution.

Built entirely with [GitHub Copilot](https://github.com/features/copilot).

---

## 📄 License

[MIT License](LICENSE)
