"""
Fetch a unique image for an article from one of several free sources.

Priority:
  1. Unsplash (UNSPLASH_ACCESS_KEY env var)
  2. Pexels (PEXELS_API_KEY env var)
  3. Wikimedia Commons (no key required)

Usage (from project root):
  python -m bkend.scripts.fetch_image "query term" output_filename.webp

  # Example:
  python -m bkend.scripts.fetch_image "us congress capitol" congress-session.webp
  python -m bkend.scripts.fetch_image "iran nuclear protest" iran-deal.webp

The file is saved to ./media/<output_filename>.
If the extension is .webp and the source returns a different format, the file
is saved with the original extension from the source URL.

Environment variables (all optional):
  UNSPLASH_ACCESS_KEY   Unsplash API access key
  PEXELS_API_KEY        Pexels API key
  MEDIA_DIR             Override the output directory (default: ./media)
"""

from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import json
from pathlib import Path


MEDIA_DIR = Path(os.environ.get("MEDIA_DIR", "./media"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _headers(extra: dict | None = None) -> dict:
    h = {"User-Agent": "AMA-site/1.0 (image-pipeline; +https://github.com/placeholder)"}
    if extra:
        h.update(extra)
    return h


def _get_json(url: str, extra_headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers=_headers(extra_headers))
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())


def _ext_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"} else ".jpg"


# ---------------------------------------------------------------------------
# Source adapters
# ---------------------------------------------------------------------------


def _fetch_unsplash(query: str, dest_stem: str) -> Path | None:
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return None
    print(f"[fetch_image] Trying Unsplash for '{query}' …")
    params = urllib.parse.urlencode({"query": query, "per_page": 1, "orientation": "landscape"})
    data = _get_json(
        f"https://api.unsplash.com/photos/random?{params}",
        extra_headers={"Authorization": f"Client-ID {key}"},
    )
    url = data["urls"]["regular"]
    ext = _ext_from_url(url) or ".jpg"
    dest = MEDIA_DIR / f"{dest_stem}{ext}"
    _download(url, dest)
    print(f"[fetch_image] Saved Unsplash image → {dest}")
    return dest


def _fetch_pexels(query: str, dest_stem: str) -> Path | None:
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        return None
    print(f"[fetch_image] Trying Pexels for '{query}' …")
    params = urllib.parse.urlencode({"query": query, "per_page": 1, "orientation": "landscape"})
    data = _get_json(
        f"https://api.pexels.com/v1/search?{params}",
        extra_headers={"Authorization": key},
    )
    photos = data.get("photos", [])
    if not photos:
        print("[fetch_image] Pexels returned no results.")
        return None
    url = photos[0]["src"]["large"]
    ext = _ext_from_url(url) or ".jpg"
    dest = MEDIA_DIR / f"{dest_stem}{ext}"
    _download(url, dest)
    print(f"[fetch_image] Saved Pexels image → {dest}")
    return dest


_WIKIMEDIA_THUMB_WIDTH = 960


def _wikimedia_thumb_url(filename: str) -> str:
    """Return the Special:FilePath thumbnail URL for a Commons filename."""
    encoded = urllib.parse.quote(filename.replace("File:", "").replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width={_WIKIMEDIA_THUMB_WIDTH}"


def _fetch_wikimedia(query: str, dest_stem: str) -> Path | None:
    """Search Wikimedia Commons and download the first suitable image."""
    print(f"[fetch_image] Trying Wikimedia Commons for '{query}' …")
    search_params = urllib.parse.urlencode({
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,  # File namespace
        "srlimit": 10,
        "format": "json",
    })
    search_url = f"https://commons.wikimedia.org/w/api.php?{search_params}"
    data = _get_json(search_url)
    results = data.get("query", {}).get("search", [])
    if not results:
        print("[fetch_image] Wikimedia Commons returned no results.")
        return None

    for result in results:
        title = result["title"]  # e.g. "File:US_Capitol.jpg"
        if not re.match(r"File:.+\.(jpe?g|png|webp)$", title, re.IGNORECASE):
            continue
        # Get metadata to filter out tiny images
        info_params = urllib.parse.urlencode({
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size",
            "format": "json",
        })
        info_url = f"https://commons.wikimedia.org/w/api.php?{info_params}"
        info_data = _get_json(info_url)
        pages = info_data.get("query", {}).get("pages", {})
        for page in pages.values():
            imageinfo = page.get("imageinfo", [])
            if not imageinfo:
                continue
            width = imageinfo[0].get("width", 0)
            if width and width < 400:
                continue
            # Use the thumbnail URL so downloaded files are web-friendly size
            thumb_url = _wikimedia_thumb_url(title)
            # Determine actual extension by following the redirect
            req = urllib.request.Request(thumb_url, headers=_headers())
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    final_url = resp.url
                    raw = resp.read()
            except urllib.error.HTTPError as exc:
                print(f"[fetch_image] Thumbnail fetch failed ({exc}), trying next …")
                continue
            ext = _ext_from_url(final_url) or ".jpg"
            dest = MEDIA_DIR / f"{dest_stem}{ext}"
            dest.write_bytes(raw)
            print(f"[fetch_image] Saved Wikimedia thumbnail '{title}' → {dest}")
            return dest

    print("[fetch_image] No usable Wikimedia images found.")
    return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def fetch_image(query: str, output_name: str) -> Path:
    """
    Fetch an image matching *query* and save it to MEDIA_DIR/<output_name>.

    The actual file extension may differ from *output_name* if the source
    returns a different format; the returned Path reflects the real path.

    Raises RuntimeError if no source could provide an image.
    """
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    dest_stem = Path(output_name).stem

    for fetcher in (_fetch_unsplash, _fetch_pexels, _fetch_wikimedia):
        try:
            result = fetcher(query, dest_stem)
            if result is not None:
                return result
        except Exception as exc:  # noqa: BLE001
            print(f"[fetch_image] Source failed: {exc}")

    raise RuntimeError(
        f"All image sources exhausted for query '{query}'. "
        "Set UNSPLASH_ACCESS_KEY or PEXELS_API_KEY for better results."
    )


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    query = sys.argv[1]
    output_name = sys.argv[2]
    try:
        path = fetch_image(query, output_name)
        print(f"Done: {path}")
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
