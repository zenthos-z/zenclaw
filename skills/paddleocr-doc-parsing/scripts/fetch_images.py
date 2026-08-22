"""Fetch markdown images referenced by a PaddleOCR doc-parsing result JSON.

The API returns, per page, `markdown.images` mapping relative paths
(e.g. `imgs/img_in_image_box_225_901_996_1178.jpg`) to signed URLs on
Baidu BOS. This script downloads them so the rendered markdown shows
figures/charts instead of broken references.

Usage:
    uv run scripts/fetch_images.py result.json [output_dir]

    - result.json: raw API envelope saved by layout_caller.py
    - output_dir:  default = directory of result.json (images land in
                   <output_dir>/imgs/), matching the markdown's relative
                   paths.

Exit codes:
    0   all referenced images fetched (or none referenced)
    1   some/all downloads failed (see stderr)
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "httpx>=0.24.0",
# ]
# ///

import argparse
import json
import sys
from pathlib import Path

import httpx


def collect_image_refs(result_path: Path) -> list[tuple[str, str, int]]:
    """Return [(relative_path, signed_url, page_no), ...] for every page."""
    data = json.loads(result_path.read_text(encoding="utf-8"))
    if not data.get("ok"):
        print(f"result JSON reports ok=false: {data.get('error')}", file=sys.stderr)
        sys.exit(1)

    pages = data.get("result", {}).get("result", {}).get("layoutParsingResults", [])
    refs: list[tuple[str, str, int]] = []
    for i, page in enumerate(pages, start=1):
        images = page.get("markdown", {}).get("images") or {}
        for rel, url in images.items():
            refs.append((rel, url, i))
    return refs


def fetch_all(result_path: Path, output_dir: Path) -> tuple[int, list[tuple[str, str]]]:
    """Download all images referenced in result JSON.

    Returns (fetched_count, [(relative_path, error), ...]).
    """
    refs = collect_image_refs(result_path)
    if not refs:
        return 0, []

    seen: dict[str, str] = {}
    for rel, url, page in refs:
        if rel not in seen:  # keep first occurrence
            seen[rel] = url

    failed: list[tuple[str, str]] = []
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        for rel, url in seen.items():
            dest = (output_dir / rel).resolve()
            # guard against path traversal in relative names
            if not str(dest).startswith(str(output_dir.resolve())):
                failed.append((rel, "unsafe relative path"))
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                resp = client.get(url)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                print(f"OK  {rel}  ({len(resp.content)} bytes)")
            except Exception as e:
                failed.append((rel, str(e)))
                print(f"FAIL {rel}: {e}", file=sys.stderr)

    print(f"\n{len(seen) - len(failed)}/{len(seen)} images fetched into {output_dir}")
    return len(seen) - len(failed), failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_json", help="result JSON from layout_caller.py")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="output directory (default: alongside the result JSON)",
    )
    args = parser.parse_args()

    result_path = Path(args.result_json).expanduser().resolve()
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else result_path.parent
    )

    fetched, failed = fetch_all(result_path, output_dir)
    if not fetched and not failed:
        print("No images referenced in this result.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
