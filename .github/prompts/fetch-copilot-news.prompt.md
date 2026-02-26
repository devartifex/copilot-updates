---
mode: 'agent'
tools: ['web/fetch', 'edit', 'read', 'search']
description: 'Fetch GitHub Copilot changelog articles and create structured markdown files for PowerPoint conversion'
---

# GitHub Copilot Changelog Fetcher

Fetch GitHub Copilot changelog articles from the GitHub Blog and produce structured markdown files ready for PowerPoint conversion via `create_pptx.py`.

## Inputs

- **Start date**: ${input:startDate} (YYYY-MM-DD)
- **End date**: ${input:endDate} (YYYY-MM-DD)
- **Language**: ${input:language} (default: english)

## Rules (apply throughout all steps)

- Process **ALL** articles in the date range — never stop early or skip items.
- **Locale folder**: Derive a short locale code from `${input:language}` (e.g. `english` → `en`, `italian` → `it`, `spanish` → `es`, `french` → `fr`, `german` → `de`, `portuguese` → `pt`, `japanese` → `ja`, `chinese` → `zh`, `korean` → `ko`). All output files go under `output/{locale}/` (e.g. `output/en/`, `output/it/`). The `raw/` folder stays shared at `output/raw/` (language-independent).
- **Skip existing articles**: Before fetching or processing an article, check if the final output file already exists in `output/{locale}/{new-releases,improvements,deprecations}/YYYY-MM-DD-slug.md`. If it does, skip that article entirely (do not re-fetch, re-process, or overwrite it). Only process **new** articles not already present.
- Follow **all pagination links** on listing pages; do not stop at the first page.
- **Language handling**: When `${input:language}` is `english` (default), write everything in English. When a different language is specified, translate **summaries** and **speaker notes** into that language. **Do NOT translate**: article titles (keep the original English title in YAML `title`, `# Heading`, and slide references), product/feature names (e.g. "Copilot", "GitHub Actions", "Gemini 3.1 Pro"), proper nouns, technical terms, or any text that originates from the source article and would lose meaning if translated.
- YAML values must be **double-quoted**. Filenames must match the URL slug.
- The Python script parses this exact structure — do not alter the front matter format, `---` separator, or `<!-- speaker_notes: -->` comment format. The `##` heading after the separator must match the article type (`## What's new`, `## What changed`, or `## What's deprecated`).

---

## Step 1 — Fetch article listings

Use `#fetch` to retrieve listing pages (no `&type=` filter):

| Scope | URL |
|---|---|
| Current/latest year | `https://github.blog/changelog/?label=copilot` |
| Specific year | `https://github.blog/changelog/{year}/?label=copilot` |

Fetch every year page that overlaps the date range. Follow all pagination links.

Extract per entry:

| Field | Source |
|---|---|
| **Title** | Entry heading |
| **URL** | `https://github.blog/changelog/YYYY-MM-DD-slug` |
| **Date** | From the URL slug |
| **Type** | Badge label → `new-release` (New release / New), `improvement`, `deprecation` (Retired / Deprecation) |

Keep only articles whose date falls within [startDate, endDate] inclusive.

## Step 2 — Fetch each article & save raw content

Use `#fetch` on each article URL (returns markdown-converted content). Extract:

- **Title**: first `# Heading`
- **Hero image**: first `![...](URL)` — skip placeholders like `[Image: Image]`; empty string if none
- **Body text**: remaining paragraph text

Save to `output/raw/YYYY-MM-DD-slug.md`:

```markdown
---
title: "Article Title"
date: "YYYY-MM-DD"
type: "new-release|improvement|deprecation"
image_url: "https://..."
article_url: "https://github.blog/changelog/YYYY-MM-DD-slug"
---

# Article Title

## Raw Content

Plain text body here.
```

## Step 3 — Generate summaries, classify & save

For each raw file, generate:

1. **Structured slide content** — NOT a descriptive paragraph. Use headings, bullet points, bold keywords, and tables to make the content scannable on a slide. The structure depends on the article type (see examples below).
2. **Speaker notes** (5–8 sentences): conversational tone — practical impact, rollout dates, demo ideas.

Both must be written in `${input:language}`. Keep article titles, product names, feature names, and technical terms in their original English form — translate only the explanatory prose around them.

If the type could not be determined from the listing badges, infer it from the article content (e.g. mentions of retirement → `deprecation`).

Save final files organized by locale and type:

```
output/{locale}/new-releases/YYYY-MM-DD-slug.md
output/{locale}/improvements/YYYY-MM-DD-slug.md
output/{locale}/deprecations/YYYY-MM-DD-slug.md
```

### Slide content structure by type

Use these structures depending on the article type. Each `###` sub-heading becomes a colored section label on the slide. Bullet points use `- ` prefix. Use `**bold**` for key terms.

#### New Release (`new-release`)

```markdown
## What's new

One-liner with **key product/feature** and **status** (e.g. public preview, GA).

### Why it matters

- **Key benefit 1** — short explanation
- **Key benefit 2** — short explanation

### Where you can use it

- **Platform 1** — details
- **Platform 2** — details

### Who gets it

- Plans, rollout info, admin requirements
```

#### Improvement (`improvement`)

```markdown
## What changed

One-liner explaining the change with **key terms** bolded.

### Why it matters

- **Benefit 1** — short explanation
- **Benefit 2** — short explanation

### How to get started (or Details)

1. Step 1
2. Step 2
3. Step 3

### Who gets it

- Plans and availability
```

#### Deprecation (`deprecation`)

```markdown
## What's deprecated

One-liner with **effective date** and scope.

| Deprecated model | Replacement |
|---|---|
| Old thing 1 | **New thing 1** |
| Old thing 2 | **New thing 2** |

### Action required

- **Who** needs to do what → specific action
- **Admins** → specific action
- What happens automatically (no action needed)
```

### Output file format

```markdown
---
title: "Article Title"
date: "YYYY-MM-DD"
type: "new-release|improvement|deprecation"
image_url: "https://..."
article_url: "https://github.blog/changelog/YYYY-MM-DD-slug"
---

# Article Title

![hero](image_url_here)

---

## What's new / What changed / What's deprecated

Structured content here (see type-specific templates above).

<!--
speaker_notes:
Speaker notes in ${input:language} here (5–8 sentences).
-->
```

> Omit `![hero]()` line entirely when no image is available.

## Step 4 — Update index file

After all articles are processed, **update** (do not overwrite) `output/{locale}/index.md`:

1. If `output/{locale}/index.md` already exists, **read it** and parse the existing entries.
2. **Merge** newly processed articles into the existing list (avoid duplicates — match by filename).
3. **Update the date range** in the title heading to span the full range of all articles present (min date → max date).
4. **Sort** entries within each section by date (ascending).
5. Write the updated file.

If the file does not exist, create it from scratch:

```markdown
# GitHub Copilot Updates: {minDate} - {maxDate}

## 🚀 New Releases
- [Article Title](new-releases/YYYY-MM-DD-slug.md) - YYYY-MM-DD

## ✨ Improvements
- [Article Title](improvements/YYYY-MM-DD-slug.md) - YYYY-MM-DD

## ⚠️ Deprecations
- [Article Title](deprecations/YYYY-MM-DD-slug.md) - YYYY-MM-DD
```
- [Article Title](deprecations/YYYY-MM-DD-slug.md) - YYYY-MM-DD
```
