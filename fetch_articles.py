#!/usr/bin/env python3
"""
Fetch GitHub changelog articles and save raw markdown files.

This script scrapes the GitHub Blog changelog listing pages for one or more
labels, deduplicates multi-label articles, fetches each individual article
page, and writes structured raw markdown files to output/raw/.

Usage:
    python fetch_articles.py --labels copilot,actions --from-date 2026-02-01 --to-date 2026-02-25
    python fetch_articles.py --labels all --from-date 2026-01-01 --to-date 2026-02-25
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup


# ── Load config ──────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"


def load_config() -> dict:
    """Load and return the config.yaml file."""
    if not CONFIG_PATH.exists():
        print(f"❌ Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Data model ───────────────────────────────────────────────────────────────

@dataclass
class ChangelogEntry:
    """A single changelog article discovered from listing pages."""
    title: str
    url: str
    slug: str             # YYYY-MM-DD-rest-of-slug
    date: str             # YYYY-MM-DD
    type: str             # canonical: new-release | improvement | deprecation
    labels: list[str] = field(default_factory=list)

    def merge_labels(self, other_labels: list[str]) -> None:
        """Merge labels from a duplicate entry (same article, different label query)."""
        for lbl in other_labels:
            if lbl not in self.labels:
                self.labels.append(lbl)


# ── HTTP session ─────────────────────────────────────────────────────────────

def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) github-changelog-fetcher/1.0",
        "Accept": "text/html,application/xhtml+xml",
    })
    return s


# ── Listing page parser ─────────────────────────────────────────────────────

# Regex to extract date from changelog URL path: /changelog/YYYY-MM-DD-slug
_DATE_FROM_URL = re.compile(r"/changelog/(\d{4}-\d{2}-\d{2})-([\w-]+)")

# Match the type badge text in headings like "### FEB.19RELEASE" or "### FEB.19IMPROVEMENT"
_BADGE_RE = re.compile(r"[A-Z]{3}\.\d{1,2}(RELEASE|IMPROVEMENT|RETIRED|NEW|DEPRECATION)")


def _parse_listing_page(html: str, label_slug: str | None, config: dict) -> list[ChangelogEntry]:
    """Parse a changelog listing page and return ChangelogEntry objects.

    When *label_slug* is ``None`` (unfiltered fetch), the initial label list
    is built entirely from the label links found in the page HTML.
    """
    soup = BeautifulSoup(html, "lxml")
    entries: list[ChangelogEntry] = []

    badge_map = config.get("badge_type_map", {})
    display_to_slug = config.get("display_to_label_slug", {})

    # Find all changelog entry links — they are <a> tags whose href matches
    # the changelog article URL pattern
    for link in soup.find_all("a", href=_DATE_FROM_URL):
        href = link.get("href", "")
        m = _DATE_FROM_URL.search(href)
        if not m:
            continue

        date_str = m.group(1)
        slug_rest = m.group(2)
        full_slug = f"{date_str}-{slug_rest}"
        title = link.get_text(strip=True)

        if not title:
            continue

        # Determine article type from surrounding context
        # Look for badge text in parent/sibling elements
        article_type = "improvement"  # default fallback
        parent = link.parent
        # Walk up to find the heading that contains the type badge
        for _ in range(5):
            if parent is None:
                break
            text = parent.get_text(" ", strip=True)
            bm = _BADGE_RE.search(text)
            if bm:
                badge_text = bm.group(1)
                article_type = badge_map.get(badge_text, "improvement")
                break
            parent = parent.parent

        # Collect all label tags associated with this entry
        article_labels = [label_slug] if label_slug else []

        # Look for label links near the article link
        entry_container = link.parent
        for _ in range(5):
            if entry_container is None:
                break
            label_links = entry_container.find_all(
                "a", href=re.compile(r"\?label=")
            )
            if label_links:
                for ll in label_links:
                    label_text = ll.get_text(strip=True).upper()
                    if label_text in display_to_slug:
                        article_labels.append(display_to_slug[label_text])
                break
            entry_container = entry_container.parent

        # Deduplicate labels
        article_labels = list(dict.fromkeys(article_labels))

        entries.append(ChangelogEntry(
            title=title,
            url=href if href.startswith("http") else f"https://github.blog{href}",
            slug=full_slug,
            date=date_str,
            type=article_type,
            labels=article_labels,
        ))

    return entries


def _find_next_page(html: str, current_url: str) -> str | None:
    """Find the 'next page' pagination link, if any."""
    soup = BeautifulSoup(html, "lxml")
    # Look for pagination links — GitHub blog uses different patterns
    for a in soup.find_all("a"):
        text = a.get_text(strip=True).lower()
        if text in ("next", "older posts", "→", "›"):
            href = a.get("href", "")
            if href:
                return urljoin(current_url, href)
    # Also look for rel="next" link
    link = soup.find("a", rel="next")
    if link:
        href = link.get("href", "")
        if href:
            return urljoin(current_url, href)
    return None


# ── Article page parser ──────────────────────────────────────────────────────

def _fetch_article(session: requests.Session, url: str) -> dict:
    """Fetch an individual article page and extract content."""
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠ Failed to fetch {url}: {e}")
        return {"title": "", "image_url": "", "body": ""}

    soup = BeautifulSoup(resp.text, "lxml")

    # Extract title — look for the main heading
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    # Extract hero image
    image_url = ""
    # Look in the article/post content area
    content_area = (
        soup.find("article")
        or soup.find("div", class_=re.compile(r"post|entry|content|changelog", re.I))
        or soup.find("main")
    )
    if content_area:
        img = content_area.find("img")
        if img:
            src = img.get("src", "") or img.get("data-src", "")
            if src and "placeholder" not in src.lower() and not src.startswith("data:"):
                image_url = src

    # Extract body text
    body_parts: list[str] = []
    if content_area:
        # Get all paragraphs, lists, headings within the content area
        for elem in content_area.find_all(["p", "li", "h2", "h3", "h4", "pre", "blockquote"]):
            text = elem.get_text(strip=True)
            if text:
                tag = elem.name
                if tag in ("h2", "h3", "h4"):
                    body_parts.append(f"\n{'#' * int(tag[1])} {text}\n")
                elif tag == "li":
                    body_parts.append(f"- {text}")
                elif tag == "pre":
                    body_parts.append(f"```\n{text}\n```")
                elif tag == "blockquote":
                    body_parts.append(f"> {text}")
                else:
                    body_parts.append(text)

    body = "\n\n".join(body_parts) if body_parts else ""

    return {"title": title, "image_url": image_url, "body": body}


# ── Raw file writer ──────────────────────────────────────────────────────────

def _save_raw_article(entry: ChangelogEntry, article_data: dict, output_dir: Path) -> Path:
    """Save a raw article markdown file and return its path."""
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    filepath = raw_dir / f"{entry.slug}.md"

    title = article_data.get("title") or entry.title
    image_url = article_data.get("image_url", "")
    body = article_data.get("body", "")

    content = f"""---
title: "{title}"
date: "{entry.date}"
type: "{entry.type}"
labels: {yaml.dump(sorted(entry.labels), default_flow_style=True).strip()}
image_url: "{image_url}"
article_url: "{entry.url}"
---

# {title}

## Raw Content

{body}
"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ── Main pipeline ────────────────────────────────────────────────────────────

def fetch_listings(session: requests.Session, labels: list[str] | None,
                   from_date: str, to_date: str,
                   config: dict) -> dict[str, ChangelogEntry]:
    """Fetch unfiltered listing pages and optionally filter by labels locally.

    Always fetches the unfiltered changelog pages (no ``?label=`` query
    parameter) — this is faster than making separate requests per label.
    When *labels* is not ``None``, results are filtered locally to keep
    only articles that carry at least one of the requested labels.

    Returns a dict mapping slug → ChangelogEntry (deduplicated).
    """
    base_url = config.get("changelog_base_url", "https://github.blog/changelog")
    entries: dict[str, ChangelogEntry] = {}

    # Determine which years to fetch
    start_year = int(from_date[:4])
    end_year = int(to_date[:4])
    years = list(range(start_year, end_year + 1))

    print("\n📋 Fetching changelog listings (unfiltered)")
    for year in years:
        url = f"{base_url}/{year}/"
        page_num = 1
        while url:
            print(f"   Page {page_num} ({year}): {url}")
            try:
                resp = session.get(url, timeout=30)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"   ⚠ Failed to fetch listing page: {e}")
                break

            page_entries = _parse_listing_page(resp.text, None, config)
            if not page_entries:
                break

            # Filter by date range and deduplicate
            in_range = 0
            for entry in page_entries:
                if entry.date < from_date or entry.date > to_date:
                    continue
                in_range += 1
                if entry.slug in entries:
                    entries[entry.slug].merge_labels(entry.labels)
                else:
                    entries[entry.slug] = entry

            print(f"   Found {len(page_entries)} entries, {in_range} in date range")

            # Check for next page
            next_url = _find_next_page(resp.text, url)
            if next_url and next_url != url:
                url = next_url
                page_num += 1
                time.sleep(0.5)  # be polite
            else:
                break

        time.sleep(0.3)  # be polite between years

    # Apply local label filter if specific labels were requested
    if labels is not None:
        label_set = set(labels)
        before = len(entries)
        entries = {
            slug: entry for slug, entry in entries.items()
            if label_set.intersection(entry.labels)
        }
        print(f"\n🏷  Label filter ({', '.join(labels)}): {before} → {len(entries)} articles")

    return entries


def fetch_and_save_articles(session: requests.Session,
                            entries: dict[str, ChangelogEntry],
                            output_dir: Path) -> tuple[int, int]:
    """Fetch individual article pages and save raw files.

    Returns (fetched_count, skipped_count).
    """
    raw_dir = output_dir / "raw"
    total = len(entries)
    fetched = 0
    skipped = 0

    for i, (slug, entry) in enumerate(sorted(entries.items()), 1):
        raw_file = raw_dir / f"{slug}.md"
        if raw_file.exists():
            # Check if we need to update labels in existing file
            _update_labels_if_needed(raw_file, entry.labels)
            skipped += 1
            print(f"  [{i}/{total}] ⏭ Already exists: {slug}")
            continue

        print(f"  [{i}/{total}] 📥 Fetching: {entry.title[:60]}...")
        article_data = _fetch_article(session, entry.url)
        _save_raw_article(entry, article_data, output_dir)
        fetched += 1
        time.sleep(0.5)  # be polite

    return fetched, skipped


def _update_labels_if_needed(raw_file: Path, new_labels: list[str]) -> None:
    """Update the labels array in an existing raw file if new labels were discovered."""
    text = raw_file.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        return
    fm = yaml.safe_load(m.group(1)) or {}
    existing_labels = fm.get("labels", [])
    if not isinstance(existing_labels, list):
        existing_labels = [existing_labels] if existing_labels else []

    merged = list(dict.fromkeys(existing_labels + new_labels))
    if set(merged) == set(existing_labels):
        return  # no change

    fm["labels"] = sorted(merged)
    # Rewrite front matter
    body = m.group(2)
    new_fm = yaml.dump(fm, default_flow_style=False, allow_unicode=True).strip()
    raw_file.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    config = load_config()
    all_labels = list(config.get("labels", {}).keys())
    default_labels = config.get("defaults", {}).get("labels", ["copilot"])

    parser = argparse.ArgumentParser(
        description="Fetch GitHub changelog articles and save raw markdown files",
    )
    parser.add_argument(
        "--labels", "-L", default=",".join(default_labels),
        help=(
            f"Comma-separated label slugs to fetch, or 'all' for everything. "
            f"Available: {', '.join(all_labels)}. Default: {','.join(default_labels)}"
        ),
    )
    parser.add_argument("--from-date", required=True,
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to-date", required=True,
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("-d", "--output-dir", default=config.get("defaults", {}).get("output_dir", "output"),
                        help="Output directory (default: output/)")
    args = parser.parse_args()

    # Resolve labels
    if args.labels.lower() == "all":
        labels = None  # fetch unfiltered — faster than iterating every label
    else:
        labels = [l.strip() for l in args.labels.split(",") if l.strip()]
        unknown = [l for l in labels if l not in all_labels]
        if unknown:
            print(f"⚠ Unknown labels (ignored): {', '.join(unknown)}")
            labels = [l for l in labels if l in all_labels]
        if not labels:
            print(f"❌ No valid labels specified. Available: {', '.join(all_labels)}")
            sys.exit(1)

    # Validate dates
    try:
        datetime.strptime(args.from_date, "%Y-%m-%d")
        datetime.strptime(args.to_date, "%Y-%m-%d")
    except ValueError:
        print("❌ Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔧 GitHub Changelog Fetcher")
    print(f"   Labels: {', '.join(labels) if labels else 'all (unfiltered)'}")
    print(f"   Date range: {args.from_date} → {args.to_date}")
    print(f"   Output: {output_dir.resolve()}")

    session = _session()

    # Step 1: Fetch listings
    print(f"\n{'='*60}")
    print("Step 1: Fetching article listings...")
    print(f"{'='*60}")
    entries = fetch_listings(session, labels, args.from_date, args.to_date, config)
    print(f"\n📊 Found {len(entries)} unique articles" +
          (f" across {len(labels)} label(s)" if labels else " (unfiltered)"))

    if not entries:
        print("ℹ️  No articles found in the specified date range.")
        sys.exit(0)

    # Step 2: Fetch individual articles
    print(f"\n{'='*60}")
    print("Step 2: Fetching individual articles...")
    print(f"{'='*60}")
    fetched, skipped = fetch_and_save_articles(session, entries, output_dir)

    print(f"\n{'='*60}")
    print(f"✅ Done! Fetched: {fetched}, Skipped (existing): {skipped}")
    print(f"   Raw files saved to: {(output_dir / 'raw').resolve()}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
