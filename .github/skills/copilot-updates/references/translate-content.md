# Translation Rules for Changelog Content

Apply these rules when translating changelog summaries and speaker notes into a non-English language.

## Translate

- Explanatory prose
- Speaker notes
- `###` section headings such as `Why it matters` or `How to get started`

## Never translate

- Article titles
- Product and feature names such as GitHub Copilot, Dependabot, GitHub Actions, CodeQL, and Codespaces
- Model names
- Technical terms such as API, SDK, CLI, OAuth, SSO, SAML, REST, GraphQL, webhook, token, PAT, and RBAC
- Plan names
- YAML keys and values
- File paths, URLs, and code snippets

## Main heading rule

The main `##` heading must stay in English because `create_pptx.py` parses it:

- `## What's new`
- `## What changed`
- `## What's deprecated`

## Quality rules

- Preserve the original markdown structure
- Preserve bold markers on the same concepts
- Keep bullet structure and numbering intact
- Translate naturally rather than word-for-word
