#!/usr/bin/env python3
"""
Deterministic processing pipeline for GitHub changelog articles.

This script handles all mechanical (non-AI) tasks in the changelog pipeline:
  --prepare   : Scan raw files, diff against existing output, produce batch.json
                 with articles that need AI summarization.
  --validate  : Check processed articles for correct format, front matter, structure.
  --index     : Generate / update output/{locale}/index.md deterministically.

Usage:
    python process_articles.py --prepare  --locale en --from-date 2026-02-01 --to-date 2026-02-25
    python process_articles.py --validate --locale en
    python process_articles.py --index    --locale en
    python process_articles.py --prepare --validate --index --locale en --from-date 2026-02-01 --to-date 2026-02-25
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


# ── Config ───────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"❌ Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_CONFIG = _load_config()

_TYPE_ALIASES: dict[str, str] = {
    k.lower(): v for k, v in _CONFIG.get("type_aliases", {}).items()
}

_CATEGORIES: dict[str, dict] = _CONFIG.get("categories", {})
_CATEGORY_ORDER: list[str] = _CONFIG.get("category_order", list(_CATEGORIES.keys()))


def _canonical_type(raw_type: str) -> str:
    return _TYPE_ALIASES.get(raw_type.lower(), raw_type.lower())


def _dir_for_type(canonical: str) -> str:
    return _CATEGORIES.get(canonical, {}).get("dir", canonical)


# ── Front-matter parser ─────────────────────────────────────────────────────

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)", re.DOTALL)


def _parse_front_matter(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


# ── PREPARE ──────────────────────────────────────────────────────────────────

def cmd_prepare(output_dir: Path, locale: str,
                from_date: str | None, to_date: str | None,
                labels_filter: list[str] | None) -> list[dict]:
    """Scan output/raw/, diff against output/{locale}/, write batch.json."""
    raw_dir = output_dir / "raw"
    locale_dir = output_dir / locale

    if not raw_dir.exists():
        print("❌ No raw/ directory found. Run fetch_articles.py first.")
        sys.exit(1)

    raw_files = sorted(raw_dir.glob("*.md"))
    if not raw_files:
        print("ℹ️  No raw files found.")
        return []

    batch: list[dict] = []

    for raw_path in raw_files:
        text = raw_path.read_text(encoding="utf-8")
        fm, body = _parse_front_matter(text)
        if not fm:
            print(f"  ⚠ Skipping {raw_path.name}: no front matter")
            continue

        date = fm.get("date", "")
        article_type = _canonical_type(fm.get("type", "improvements"))
        article_labels = fm.get("labels", [])
        if isinstance(article_labels, str):
            article_labels = [article_labels]
        slug = raw_path.stem  # e.g. 2026-02-24-some-slug

        # Date filter
        if from_date and date < from_date:
            continue
        if to_date and date > to_date:
            continue

        # Label filter
        if labels_filter:
            if not any(lbl in article_labels for lbl in labels_filter):
                continue

        # Check if already processed
        type_dir = _dir_for_type(article_type)
        target_path = locale_dir / type_dir / f"{slug}.md"
        if target_path.exists():
            print(f"  ⏭ Already processed: {slug}")
            continue

        batch.append({
            "slug": slug,
            "date": date,
            "type": article_type,
            "type_dir": type_dir,
            "labels": article_labels,
            "title": fm.get("title", ""),
            "image_url": fm.get("image_url", ""),
            "article_url": fm.get("article_url", ""),
            "raw_file": str(raw_path.resolve()),
            "target_file": str(target_path.resolve()),
        })

    # Group by type for efficient batch processing
    batch.sort(key=lambda a: (_CATEGORY_ORDER.index(a["type"])
                               if a["type"] in _CATEGORY_ORDER else 99,
                               a["date"], a["slug"]))

    # Ensure target directories exist
    for cat in _CATEGORIES.values():
        (locale_dir / cat["dir"]).mkdir(parents=True, exist_ok=True)

    # Write batch manifest
    batch_path = output_dir / "batch.json"
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump({"locale": locale, "articles": batch}, f, indent=2, ensure_ascii=False)

    # Summary by type
    type_counts: dict[str, int] = {}
    for a in batch:
        type_counts[a["type"]] = type_counts.get(a["type"], 0) + 1

    print(f"\n📋 Batch manifest: {batch_path}")
    print(f"   Total articles to process: {len(batch)}")
    for t, c in type_counts.items():
        emoji = _CATEGORIES.get(t, {}).get("emoji", "")
        title = _CATEGORIES.get(t, {}).get("title", t)
        print(f"   {emoji} {title}: {c}")

    return batch


# ── VALIDATE ─────────────────────────────────────────────────────────────────

_SPEAKER_NOTES_RE = re.compile(r"<!--\s*\n?\s*speaker_notes:\s*\n(.*?)\s*-->", re.DOTALL)

# Expected heading by type
_TYPE_HEADING = {
    "new-releases": "What's new",
    "improvements": "What changed",
    "deprecations": "What's deprecated",
}

_REQUIRED_FM_KEYS = {"title", "date", "type", "labels", "article_url"}


def _load_expected_batch_targets(output_dir: Path, locale: str) -> tuple[list[Path], list[str]]:
    """Return expected target files from batch.json for the given locale.

    If batch.json is missing, malformed, or for a different locale, return an
    empty target list and any parsing errors encountered.
    """
    batch_path = output_dir / "batch.json"
    if not batch_path.exists():
        return [], []

    try:
        data = json.loads(batch_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"{batch_path.name}: unreadable batch manifest ({exc})"]

    if data.get("locale") != locale:
        return [], []

    expected_targets: list[Path] = []
    errors: list[str] = []
    for article in data.get("articles", []):
        target = article.get("target_file")
        if not isinstance(target, str) or not target.strip():
            slug = article.get("slug", "<unknown>")
            errors.append(f"{batch_path.name}: article '{slug}' is missing a valid target_file")
            continue
        expected_targets.append(Path(target))

    return expected_targets, errors


def cmd_validate(output_dir: Path, locale: str) -> bool:
    """Validate all processed article files. Returns True if all pass."""
    locale_dir = output_dir / locale
    if not locale_dir.exists():
        print(f"❌ Locale directory not found: {locale_dir}")
        return False

    errors: list[str] = []
    checked = 0

    expected_targets, batch_errors = _load_expected_batch_targets(output_dir, locale)
    errors.extend(batch_errors)
    for target in expected_targets:
        if not target.exists():
            try:
                rel = target.relative_to(output_dir)
            except ValueError:
                rel = target
            errors.append(f"{rel}: expected from batch.json but file is missing")

    for cat_key, cat_meta in _CATEGORIES.items():
        cat_dir = locale_dir / cat_meta["dir"]
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            checked += 1
            text = md_file.read_text(encoding="utf-8")
            fm, body = _parse_front_matter(text)
            rel = md_file.relative_to(output_dir)

            # Check required front-matter keys
            missing = _REQUIRED_FM_KEYS - set(fm.keys())
            if missing:
                errors.append(f"{rel}: missing front-matter keys: {missing}")

            # Check type consistency
            file_type = _canonical_type(fm.get("type", ""))
            if file_type != cat_key:
                errors.append(f"{rel}: type '{fm.get('type')}' doesn't match directory '{cat_meta['dir']}'")

            # Check labels is a list
            labels_val = fm.get("labels")
            if not isinstance(labels_val, list):
                errors.append(f"{rel}: 'labels' should be a list, got {type(labels_val).__name__}")

            # Check expected ## heading
            expected_heading = _TYPE_HEADING.get(cat_key, "")
            if expected_heading and f"## {expected_heading}" not in body:
                errors.append(f"{rel}: missing '## {expected_heading}' heading")

            # Check speaker notes
            if not _SPEAKER_NOTES_RE.search(body):
                errors.append(f"{rel}: missing speaker_notes comment block")

            # Check date in filename matches front matter
            slug = md_file.stem
            if slug[:10] != fm.get("date", ""):
                errors.append(f"{rel}: filename date '{slug[:10]}' ≠ front-matter date '{fm.get('date')}'")

    if errors:
        print(f"\n❌ Validation failed — {len(errors)} issue(s) in {checked} file(s):\n")
        for e in errors:
            print(f"  • {e}")
        return False

    print(f"\n✅ Validation passed — {checked} file(s) checked, no issues.")
    return True


# ── INDEX ────────────────────────────────────────────────────────────────────

def cmd_index(output_dir: Path, locale: str) -> None:
    """Generate / update output/{locale}/index.md deterministically."""
    locale_dir = output_dir / locale

    # Collect all articles from category directories
    sections: dict[str, list[dict]] = {key: [] for key in _CATEGORY_ORDER}

    for cat_key in _CATEGORY_ORDER:
        cat_meta = _CATEGORIES.get(cat_key, {})
        cat_dir = locale_dir / cat_meta.get("dir", cat_key)
        if not cat_dir.exists():
            continue
        for md_file in sorted(cat_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            fm, _ = _parse_front_matter(text)
            rel_path = md_file.relative_to(locale_dir).as_posix()
            sections[cat_key].append({
                "title": fm.get("title", md_file.stem),
                "date": fm.get("date", md_file.stem[:10]),
                "path": rel_path,
            })

    # Sort each section by date ascending
    for key in sections:
        sections[key].sort(key=lambda a: (a["date"], a["title"]))

    # Determine date range
    all_dates = [a["date"] for articles in sections.values() for a in articles]
    if not all_dates:
        print("ℹ️  No processed articles found — nothing to index.")
        return

    min_date = min(all_dates)
    max_date = max(all_dates)

    # Build index content
    lines: list[str] = [f"# GitHub Changelog Updates: {min_date} - {max_date}", ""]

    section_labels = {
        "new-releases": "🚀 New Releases",
        "improvements": "✨ Improvements",
        "deprecations": "⚠️ Deprecations",
    }

    for cat_key in _CATEGORY_ORDER:
        label = section_labels.get(cat_key, cat_key)
        lines.append(f"## {label}")
        articles = sections[cat_key]
        if articles:
            for a in articles:
                lines.append(f"- [{a['title']}]({a['path']}) - {a['date']}")
        lines.append("")

    index_path = locale_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    total = sum(len(v) for v in sections.values())
    print(f"\n📄 Index updated: {index_path} ({total} article(s))")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic processing pipeline for GitHub changelog articles",
    )
    parser.add_argument("--prepare", action="store_true",
                        help="Scan raw files and produce batch.json")
    parser.add_argument("--validate", action="store_true",
                        help="Validate processed article files")
    parser.add_argument("--index", action="store_true",
                        help="Generate/update index.md")
    parser.add_argument("--locale", "-l", default="en",
                        help="Locale code (default: en)")
    parser.add_argument("--from-date", default=None,
                        help="Start date filter (YYYY-MM-DD)")
    parser.add_argument("--to-date", default=None,
                        help="End date filter (YYYY-MM-DD)")
    parser.add_argument("--labels", "-L", default=None,
                        help="Comma-separated label slugs to filter")
    parser.add_argument("-d", "--output-dir",
                        default=_CONFIG.get("defaults", {}).get("output_dir", "output"),
                        help="Output directory (default: output/)")
    args = parser.parse_args()

    if not any([args.prepare, args.validate, args.index]):
        parser.error("Specify at least one of: --prepare, --validate, --index")

    output_dir = Path(args.output_dir)
    labels_filter = (
        [l.strip() for l in args.labels.split(",") if l.strip()]
        if args.labels else None
    )

    if args.prepare:
        print(f"{'='*60}")
        print("PREPARE: Scanning raw files and building batch manifest")
        print(f"{'='*60}")
        cmd_prepare(output_dir, args.locale, args.from_date, args.to_date, labels_filter)

    if args.validate:
        print(f"\n{'='*60}")
        print("VALIDATE: Checking processed article files")
        print(f"{'='*60}")
        ok = cmd_validate(output_dir, args.locale)
        if not ok:
            sys.exit(1)

    if args.index:
        print(f"\n{'='*60}")
        print("INDEX: Generating index.md")
        print(f"{'='*60}")
        cmd_index(output_dir, args.locale)


if __name__ == "__main__":
    main()
