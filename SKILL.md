---
name: copilot-updates
description: 'Generate GitHub changelog digests and PowerPoint presentations from date ranges, labels, and languages. Use when asked to fetch GitHub changelog articles, summarize weekly product updates, translate release notes, build stakeholder update decks, or create presentations about Copilot, Actions, Security, client apps, or other GitHub changelog labels.'
license: MIT
---

# Copilot Updates

Use this skill to run the changelog-to-presentation workflow end to end. This skill should orchestrate the existing Python scripts for deterministic work and use AI only for structured summaries and speaker notes.

## When to Use This Skill

- The user wants a weekly or date-bounded GitHub changelog digest
- The user wants a PowerPoint deck covering GitHub product updates
- The user wants changelog summaries filtered by labels such as `copilot`, `actions`, or `client-apps`
- The user wants translated summaries or speaker notes for a specific language
- The user wants to rerun or update the existing changelog presentation pipeline

## Prerequisites

### Python dependencies

The skill's Python scripts require Python 3.11+ and several packages. Install them:

```bash
cd <skill-root>/scripts
pip install -e .
# or, if using uv:
uv sync
```

### Installation as a global user skill

Clone or symlink this repository to your Copilot skills directory so it's available from any project:

```bash
# Clone directly
git clone https://github.com/<owner>/copilot-updates ~/.copilot/skills/copilot-updates

# Or symlink an existing clone
ln -s /path/to/copilot-updates ~/.copilot/skills/copilot-updates
```

On Windows:
```powershell
# Symlink
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.copilot\skills\copilot-updates" -Target "C:\path\to\copilot-updates"
```

Once installed, Copilot will discover the skill automatically when you ask about GitHub changelog updates or presentations.

### Installation as a project-level skill

Clone into your repository's `.github/skills/` directory:

```bash
git clone https://github.com/<owner>/copilot-updates .github/skills/copilot-updates
```

## Script Resolution

All Python scripts live in the `scripts/` subdirectory of this skill. When running commands, resolve script paths relative to the skill's root directory.

If the skill is installed at `~/.copilot/skills/copilot-updates/`, the scripts are at `~/.copilot/skills/copilot-updates/scripts/`. The scripts use `SCRIPT_DIR = Path(__file__).resolve().parent` internally, so they find their own config and image assets regardless of the working directory.

Output (the `output/` directory and `.pptx` files) is always created in the **current working directory**, not in the skill folder.

## Core Principles

- Always use the skill's Python scripts in `scripts/` for deterministic tasks
- Never create raw files manually
- Never write `index.md` manually
- Never invent article metadata that should come from `output/batch.json`
- Process every article in the batch; do not stop after a sample
- Keep generated article front matter machine-parseable and consistent with repository conventions

## Inputs to Confirm

Confirm or infer these values before running the pipeline:

- `startDate` and `endDate` in `YYYY-MM-DD`
- `labels` as comma-separated slugs or `all`
- `language` as a natural language name such as `english`, `italian`, or `spanish`

When the user gives a relative range such as "last 3 days" or "past week", compute an inclusive calendar-day range where today counts as day 1, then confirm the computed dates before executing.

Map language names to locale codes using this table:

| Language | Locale |
|---|---|
| `english` | `en` |
| `italian` | `it` |
| `spanish` | `es` |
| `french` | `fr` |
| `german` | `de` |
| `portuguese` | `pt` |
| `japanese` | `ja` |
| `chinese` | `zh` |
| `korean` | `ko` |

## End-to-End Workflow

### 1. Fetch raw articles

Run the scraper first. If the label filter is `all`, omit the `--labels` flag.

```bash
python scripts/fetch_articles.py --from-date <startDate> --to-date <endDate>
python scripts/fetch_articles.py --labels <labels> --from-date <startDate> --to-date <endDate>
```

This writes raw markdown files to `output/raw/`.

### 2. Prepare the batch

Run the deterministic planning step to produce `output/batch.json`.

```bash
python scripts/process_articles.py --prepare --locale <locale> --from-date <startDate> --to-date <endDate>
```

Read `output/batch.json` and report the number of articles found. If the batch is empty, skip directly to PowerPoint generation.

### 3. Generate structured summaries

**IMPORTANT: Write each file yourself using the create or edit tool. Do not delegate this step to a background agent or sub-agent — they run in separate contexts, may fail silently, and cannot access the skill references.**

For each article in `output/batch.json`:

1. Read the `raw_file` content
2. Read the matching reference guide for the article's `type`:
   - `new-releases` → `references/summarize-new-releases.md`
   - `improvements` → `references/summarize-improvements.md`
   - `deprecations` → `references/summarize-deprecations.md`
3. Generate a structured summary body following the reference guide's exact format
4. If `language` is not English, also apply `references/translate-content.md` to the summary body
5. Assemble the complete file (front matter + title + hero + separator + summary body)
6. Write the file to the `target_file` path from the batch entry using the create tool
7. **After writing, verify the file exists on disk** before moving to the next article

Copy `title`, `date`, `type`, `labels`, `image_url`, and `article_url` from the batch entry exactly. Do not rewrite or normalize them manually.

Assemble each processed article with this exact structure:

```markdown
---
title: "Article Title"
date: "YYYY-MM-DD"
type: "new-releases"
labels: ["copilot", "actions"]
image_url: "https://..."
article_url: "https://github.blog/changelog/YYYY-MM-DD-slug"
---

# Article Title

![hero](image_url)

---

{generated summary body from reference guide}
```

If `image_url` is empty or points to an SVG, omit the `![hero](...)` line but keep the `---` separator.

Process **every** article in the batch — do not stop after a sample or subset.

## Required formatting rules

- YAML front-matter values must be double-quoted
- `labels` must remain a YAML list
- The main `##` heading must stay in English:
  - `## What's new`
  - `## What changed`
  - `## What's deprecated`
- Speaker notes must use the HTML comment format documented in the reference files
- Do not translate article titles, product names, model names, technical terms, plan names, or YAML keys

### 4. Verify all files were written

Before running validation, confirm that every `target_file` from `output/batch.json` exists on disk. List the target directory contents and compare against the batch manifest. If any files are missing, create them now.

### 5. Validate output

Run validation after writing the processed files.

```bash
python scripts/process_articles.py --validate --locale <locale>
```

If validation fails, inspect the reported files, fix them, and run validation again until it passes.

### 6. Generate the index

```bash
python scripts/process_articles.py --index --locale <locale>
```

Do not hand-author `output/<locale>/index.md`.

### 7. Generate the PowerPoint

If labels are filtered, include `--label`. If labels are `all`, omit it.

```bash
python scripts/create_pptx.py --locale <locale> --from-date <startDate> --to-date <endDate>
python scripts/create_pptx.py --locale <locale> --label <labels> --from-date <startDate> --to-date <endDate>
```

Report the output filename and slide count.

## Troubleshooting

- If no locale directory exists yet, make sure `--prepare` ran before validation or indexing
- If validation reports a missing heading, use the exact English heading required for that article type
- If validation reports missing speaker notes, restore the required HTML comment block
- If the PowerPoint step says no processed articles exist, check that the summarization step actually wrote the files — list the target directory to confirm
- **Do not delegate file writing to background agents** — they run in isolated contexts and may silently fail to create files. Always use the create or edit tool directly
- If the PowerPoint reports 0 articles despite files existing, verify front-matter `labels` uses the YAML list format `["copilot"]` not the bare format `[copilot]`

## References

- `references/summarize-new-releases.md`
- `references/summarize-improvements.md`
- `references/summarize-deprecations.md`
- `references/translate-content.md`
