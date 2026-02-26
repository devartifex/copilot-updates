---
agent: agent
description: "Translation rules for GitHub changelog content. Apply when language ≠ english."
---

# Translation Rules for Changelog Content

Apply these rules when translating changelog summaries and speaker notes into a non-English language.

## What to translate

- Explanatory prose (bullet descriptions, one-liners, section content)
- Speaker notes (full translation — keep conversational tone)
- Section sub-headings (`### Why it matters`, `### How to get started`, etc.)

## What to NEVER translate (keep original English)

- **Article titles** — the `title` field in YAML front matter, the `# Heading`, and slide references must stay in English
- **Product and feature names** — "GitHub Copilot", "Dependabot", "GitHub Actions", "CodeQL", "Codespaces", "GitHub Mobile", "Pull Requests", "Issues", etc.
- **Model names** — "GPT-4o", "Claude 3.7 Sonnet", "Gemini 2.5 Pro", etc.
- **Technical terms** — "API", "SDK", "CLI", "OAuth", "SSO", "SAML", "REST", "GraphQL", "webhook", "token", "PAT", "RBAC", etc.
- **Plan names** — "Copilot Individual", "Copilot Business", "Copilot Enterprise", "GitHub Free", "GitHub Team", "GitHub Enterprise"
- **Status labels** — "GA" (Generally Available), "public preview", "private preview", "beta"
- **YAML keys and values** — front matter must remain in English
- **Markdown formatting** — `## What's new`, `## What changed`, `## What's deprecated` headings stay in English (they are parsed by the PowerPoint script)
- **File paths, URLs, code snippets**

## The `##` type heading rule

The main `## heading` MUST stay in English because `create_pptx.py` parses it:
- `## What's new` — NOT "## Cosa c'è di nuovo"
- `## What changed` — NOT "## Cosa è cambiato"
- `## What's deprecated` — NOT "## Cosa è deprecato"

## Translation quality

- Match the tone: summaries are professional-concise; speaker notes are conversational
- Preserve bold markers (`**word**`) on the same keywords
- Keep bullet structure and numbering intact
- Use the natural grammatical structure of the target language — don't translate word-for-word
