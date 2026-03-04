"""
🌐 GENESIS WEB SEARCH — Advanced Scraper & Markdown Parser
Searches DuckDuckGo, then deep-fetches top URLs with robust headers.
Extracts site-specific content (StackOverflow, GitHub, or Fallbacks)
and converts it directly to clean, LLM-friendly Markdown.

Usage:
    from tools.web_search import search_web
    context = search_web("aws eks iam role attach terraform")
"""

import time
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from ddgs import DDGS
from typing import List, Dict, Optional

# ── Configuration ──────────────────────────────────────────
DEEP_FETCH_COUNT = 3
MAX_CHARS_PER_RESULT = 1500
FETCH_TIMEOUT = 5
MAX_RETRIES = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


# ── Internal helpers ───────────────────────────────────────

def _extract_page_content(html: str, url: str) -> str:
    """
    Extract site-specific content and convert to Markdown.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove noise across all sites
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg"]):
        tag.decompose()

    target_node = None

    # StackOverflow specialized extraction
    if "stackoverflow.com" in url:
        target_node = soup.select_one('.accepted-answer .s-prose')
        if not target_node:
            target_node = soup.select_one('.answer .s-prose')
            
    # GitHub specialized extraction
    elif "github.com" in url:
        comments = soup.select('.comment-body')
        if comments:
            # Combine the first issue body and the top comment
            combined_html = "<div>"
            for comment in comments[:2]:
                combined_html += str(comment) + "<hr>"
            combined_html += "</div>"
            target_node = BeautifulSoup(combined_html, "html.parser")

    # Fallback for generic sites
    if not target_node:
        target_node = soup.find('main') or soup.find('article') or soup.find('body')

    if not target_node:
        return ""

    # Convert the targeted HTML directly to Markdown
    markdown_content = md(str(target_node), heading_style="ATX").strip()
    return markdown_content


def _smart_truncate(text: str, max_chars: int = MAX_CHARS_PER_RESULT) -> str:
    """
    Truncate to max_chars while ensuring we don't leave
    unclosed markdown code blocks (```).
    """
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    
    # Check for unclosed code blocks
    # Count the number of '```' occurrences
    # Note: this is a simple heuristic. It might fail on edge cases like inline ``` 
    # but works 95% of the time for standard markdown.
    code_block_count = truncated.count('```')
    if code_block_count % 2 != 0:
        # We have an unclosed code block, let's close it
        truncated += "\n```\n...[truncated]"
    else:
        truncated += "\n...[truncated]"

    return truncated


def _deep_fetch(url: str) -> Optional[str]:
    """
    Download a URL and extract markdown content with retries.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url,
                timeout=FETCH_TIMEOUT,
                headers=HEADERS,
                allow_redirects=True,
            )
            
            # If rate limited or forbidden, wait and retry
            if resp.status_code in [403, 429] and attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                continue
                
            resp.raise_for_status()

            if "text/html" not in resp.headers.get("Content-Type", ""):
                return None

            raw_markdown = _extract_page_content(resp.text, url)
            if not raw_markdown:
                return None
                
            return _smart_truncate(raw_markdown)

        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


# ── Public API ─────────────────────────────────────────────

def search_web(query: str, max_results: int = 5, deep_fetch: bool = True) -> str:
    """
    Search DuckDuckGo and optionally deep-scrape the top results.
    """
    try:
        with DDGS() as ddgs:
            results: List[Dict] = list(ddgs.text(query, max_results=max_results))

        if not results:
            return f"[No web results found for: '{query}']"

        output_lines = [f"🌐 Web Search Results for: '{query}'\n{'━' * 60}"]

        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            snippet = r.get("body", "")
            url = r.get("href", "")

            # Deep-fetch for the top N results
            scraped_md = None
            if deep_fetch and i <= DEEP_FETCH_COUNT and url:
                scraped_md = _deep_fetch(url)

            content = scraped_md if scraped_md else snippet
            label = "SCRAPED MARKDOWN" if scraped_md else "snippet fallback"

            output_lines.append(
                f"\n[{i}] {title}\n"
                f"    URL: {url}\n"
                f"    ({label}):\n"
                f"{content}"
            )

        output_lines.append(f"\n{'━' * 60}")
        return "\n".join(output_lines)

    except Exception as e:
        return f"[Web search failed: {e}. Query was: '{query}']"


def search_web_raw(query: str, max_results: int = 5) -> List[Dict]:
    """Return raw DDG results as a list of dicts."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return [{"title": "Error", "body": str(e), "href": ""}]


# ── Self-test ──────────────────────────────────────────────
if __name__ == "__main__":
    print(search_web("pytest fixture scope example site:stackoverflow.com", max_results=2))
