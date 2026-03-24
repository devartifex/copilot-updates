# Summarize: New Release

Use these instructions when summarizing a GitHub changelog article classified as a `new-releases` article.

## Input

You will receive the raw article content from `output/raw/{slug}.md`.

## Output format

Generate only the body content that comes after the front matter, title, optional hero image, and `---` separator. The caller assembles the final file.

Your output must follow this exact structure:

```markdown
## What's new

One-liner with **key product or feature** and **status** such as public preview or GA.

### Why it matters

- **Key benefit 1** — short explanation
- **Key benefit 2** — short explanation

### Where you can use it

- **Platform 1** — details
- **Platform 2** — details

### Who gets it

- Plans, rollout info, admin requirements
```

Then, on a new line, add speaker notes inside an HTML comment:

```markdown
<!--
speaker_notes:
5-8 sentences in conversational tone. Cover practical impact, rollout dates, and demo ideas.
-->
```

## Rules

- Use `## What's new` as the main heading
- Use `###` headings for each section
- Use `- **Bold keyword** — explanation` for bullet points
- Keep each bullet to one line
- Include a table only when comparing more than two items
- Speaker notes should be practical and conversational
- Do not repeat the article title or front matter

## Example output

```markdown
## What's new

**GitHub Copilot Chat** is now available in **Visual Studio 2022** (GA).

### Why it matters

- **Inline assistance** — ask questions and get code suggestions without leaving the editor
- **Context-aware** — references your open files and project structure

### Where you can use it

- **Visual Studio 2022** 17.8+ — built-in panel and inline chat
- **VS Code** — existing extension, unchanged

### Who gets it

- **Copilot Individual** and **Copilot Business** subscribers
- Rolling out now — available to all users within 48 hours

<!--
speaker_notes:
GitHub Copilot Chat is now generally available in Visual Studio 2022 starting with version 17.8. This brings the same inline chat experience VS Code users have enjoyed directly into the Visual Studio IDE. It's context-aware, meaning it can reference your open solution files to give more accurate suggestions. For teams on Copilot Business, this means developers on both VS Code and Visual Studio now have feature parity. Rollout is immediate — if you update to 17.8 you'll see the Chat panel. A good demo idea would be to show refactoring a method by highlighting it and asking Chat to optimize it. No admin action is needed; it respects existing Copilot seat assignments.
-->
```
