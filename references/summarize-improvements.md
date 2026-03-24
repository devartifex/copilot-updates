# Summarize: Improvement

Use these instructions when summarizing a GitHub changelog article classified as an `improvements` article.

## Input

You will receive the raw article content from `output/raw/{slug}.md`.

## Output format

Generate only the body content that comes after the front matter, title, optional hero image, and `---` separator. The caller assembles the final file.

Your output must follow this exact structure:

```markdown
## What changed

One-liner explaining the change with **key terms** bolded.

### Why it matters

- **Benefit 1** — short explanation
- **Benefit 2** — short explanation

### How to get started

1. Step 1
2. Step 2
3. Step 3

### Who gets it

- Plans and availability
```

If the article does not have clear steps, replace `### How to get started` with `### Details` and use a bullet list or table instead.

Then, on a new line, add speaker notes inside an HTML comment:

```markdown
<!--
speaker_notes:
5-8 sentences in conversational tone. Cover practical impact, rollout dates, and demo ideas.
-->
```

## Rules

- Use `## What changed` as the main heading
- Use `###` headings for each section
- Use `- **Bold keyword** — explanation` for bullet points
- Use numbered lists for actionable steps
- Use a table when comparing items or multiple changes
- Keep each bullet concise
- Speaker notes should mention rollout timing, workflow impact, and good demo angles
- Do not repeat the article title or front matter

## Example output

```markdown
## What changed

**Dependabot** can now **group updates by dependency name** across multiple directories in a monorepo.

### Why it matters

- **Fewer PRs** — related dependency updates across packages are combined into a single pull request
- **Consistent versions** — ensures the same dependency version is used across all directories

### How to get started

1. Open `.github/dependabot.yml`
2. Add `groups:` with a `patterns:` list matching dependency names
3. Set `directories:` to `["/*"]` or list specific paths
4. Dependabot will batch matching updates into grouped PRs on next scheduled run

### Who gets it

- **All GitHub.com users** — available now
- **GHES 3.18+** — included in next patch release

<!--
speaker_notes:
Dependabot now lets you group dependency updates by name across multiple directories. This is huge for monorepos: if you have the same library in five packages, instead of getting five separate PRs you'll get one grouped PR. Configuration is straightforward — you add a groups block to your dependabot.yml with patterns matching the dependency names. The directories field controls which paths are included. This feature is live on github.com right now and will be in GHES 3.18. A good demo would be showing a before/after of the PR list for a monorepo with shared dependencies. No admin action is needed — any developer with write access to the repo can update the Dependabot config.
-->
```
