# Summarize: Deprecation

Use these instructions when summarizing a GitHub changelog article classified as a `deprecations` article.

## Input

You will receive the raw article content from `output/raw/{slug}.md`.

## Output format

Generate only the body content that comes after the front matter, title, optional hero image, and `---` separator. The caller assembles the final file.

Preferred multi-item format:

```markdown
## What's deprecated

One-liner with **effective date** and scope.

| Deprecated item | Replacement |
|---|---|
| Old thing 1 | **New thing 1** |
| Old thing 2 | **New thing 2** |

### Action required

- **Who** needs to do what — specific action
- **Admins** — specific action
- What happens automatically with no action needed
```

Single-item alternative:

```markdown
## What's deprecated

**Feature X** will be retired on **YYYY-MM-DD**. It is replaced by **Feature Y**.

### Action required

- **Users** — migrate to Feature Y before the deadline
- **Admins** — update organization policies

### Timeline

- **YYYY-MM-DD** — deprecation announced
- **YYYY-MM-DD** — feature disabled for new users
- **YYYY-MM-DD** — feature fully removed
```

Then, on a new line, add speaker notes inside an HTML comment:

```markdown
<!--
speaker_notes:
5-8 sentences in conversational tone. Cover who is affected, what they need to do, deadlines, and migration path.
-->
```

## Rules

- Use `## What's deprecated` as the main heading
- Always include `### Action required`
- Use a table when multiple items are deprecated together
- Use `### Timeline` when several milestone dates matter
- Bold dates and action verbs for scanability
- Keep the summary concise and action-oriented
- Do not repeat the article title or front matter

## Example output

```markdown
## What's deprecated

**Legacy OAuth app tokens** will be fully removed on **2026-04-01**. Migrate to **fine-grained personal access tokens** or **GitHub App tokens**.

| Deprecated | Replacement |
|---|---|
| OAuth app tokens (classic) | **Fine-grained PATs** |
| OAuth app authorizations API | **GitHub App installations API** |

### Action required

- **Developers using OAuth tokens** → regenerate as fine-grained PATs with minimum required scopes
- **Admins** → audit organization token usage via Settings → Personal access tokens → Active tokens
- **CI/CD pipelines** → update stored secrets to use new token format

### Timeline

- **2026-01-15** — deprecation announced, warnings in API responses
- **2026-03-01** — creation of new OAuth app tokens disabled
- **2026-04-01** — all existing OAuth app tokens stop working

<!--
speaker_notes:
Legacy OAuth app tokens are being retired on April 1st, 2026. This has been telegraphed for a while but now there are firm dates. The biggest impact is on CI/CD pipelines and integrations that still use classic OAuth tokens. The migration path is straightforward: switch to fine-grained personal access tokens which offer better security through scoped permissions. Admins should audit their org's token usage now — there's a dashboard under Settings showing active tokens and their types. Note that the creation of new OAuth tokens will be blocked starting March 1st, a month before the full cutoff. Apps using the OAuth authorizations API need to migrate to the GitHub App installations API instead. Demo idea: show the token audit dashboard and the process of creating a fine-grained PAT with equivalent scopes.
-->
```
