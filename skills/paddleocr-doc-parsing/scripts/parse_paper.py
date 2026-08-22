"""One-shot pipeline: PDF -> markdown + images (PaddleOCR doc parsing).

Wraps layout_caller.py + fetch_images.py + markdown export so a paper can
be parsed in a single command, following the 论文/解析/ output convention.

Usage:
    uv run scripts/parse_paper.py "paper.pdf" [output_dir]

    - paper.pdf:   local PDF (or --file-url <url>)
    - output_dir:  default = <paper dir>/解析

Output (in output_dir):
    <name>.md             full markdown with <img> refs into imgs/
    <name>.result.json    raw API envelope
    imgs/                 fetched figure/chart images

Naming: derived from the input filename (keeps the leading sequence number
and arXiv id, e.g. "011 LeWM 2603.19312v1" -> "011-LeWM-2603.19312v1").
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "httpx>=0.24.0",
#   "pymupdf>=1.24",
# ]
# ///

import argparse
import json
import re
import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from lib import parse_document  # noqa: E402


def slugify(name: str) -> str:
    """Turn '011 LeWM 2603.19312v1.pdf' into '011-LeWM-2603.19312v1'."""
    stem = Path(name).stem
    # collapse whitespace runs to single spaces, then spaces -> '-'
    return re.sub(r"\s+", "-", stem.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="local PDF path")
    parser.add_argument("output_dir", nargs="?", default=None)
    parser.add_argument("--pretty", action="store_true", help="pretty-print result JSON")
    args = parser.parse_args()

    pdf = Path(args.input).expanduser().resolve()
    if not pdf.exists():
        print(f"File not found: {pdf}", file=sys.stderr)
        sys.exit(1)

    output_dir = (
        Path(args.output_dir).expanduser().resolve() if args.output_dir else pdf.parent / "解析"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    base = slugify(pdf.name)
    json_path = output_dir / f"{base}.result.json"
    md_path = output_dir / f"{base}.md"

    print(f"[1/3] Parsing {pdf.name} ...")
    result = parse_document(file_path=str(pdf), file_type=0)
    if not result.get("ok"):
        print(f"Parse failed: {result.get('error')}", file=sys.stderr)
        sys.exit(1)

    indent = 2 if args.pretty else None
    json_path.write_text(
        json.dumps(result, indent=indent, ensure_ascii=False), encoding="utf-8"
    )
    print(f"      result JSON -> {json_path}")

    md_path.write_text(result.get("text", ""), encoding="utf-8")
    print(f"[2/3] Markdown ({len(result.get('text',''))} chars) -> {md_path}")

    print(f"[3/3] Rendering hi-res images from PDF (default 4x) ...")
    sys.path.insert(0, str(Path(__file__).parent))
    from render_images import render_all  # noqa: E402

    rendered, failed = render_all(json_path, pdf, output_dir)
    print(f"      {rendered} images rendered; {len(failed)} failed")
    if failed:
        for rel, err in failed:
            print(f"  FAIL {rel}: {err}", file=sys.stderr)
        # fallback: fetch API copy for images that failed to render locally,
        # so the markdown <img> refs never dangle
        n = _download_fallback(json_path, output_dir, [rel for rel, _ in failed])
        print(f"      fallback: {n}/{len(failed)} fetched from API")

    missing = _verify_md_images(md_path, output_dir)
    if missing:
        print(f"  WARN: {len(missing)} md-referenced images missing: {missing[:5]}", file=sys.stderr)

    print(f"\nDone. Output in {output_dir}")


def _download_fallback(json_path: Path, output_dir: Path, rels: list[str]) -> int:
    """Download API copies (markdown.images URLs) for the given relative paths."""
    import httpx

    data = json.loads(json_path.read_text(encoding="utf-8"))
    urls: dict[str, str] = {}
    for page in data.get("result", {}).get("result", {}).get("layoutParsingResults", []):
        urls.update((page.get("markdown", {}) or {}).get("images", {}) or {})

    ok = 0
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        for rel in rels:
            url = urls.get(rel)
            if not url:
                continue
            dest = (output_dir / rel).resolve()
            if not str(dest).startswith(str(output_dir.resolve())):
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                resp = client.get(url)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                ok += 1
            except Exception as e:
                print(f"  fallback FAIL {rel}: {e}", file=sys.stderr)
    return ok


def _verify_md_images(md_path: Path, output_dir: Path) -> list[str]:
    """Return md <img src> references whose files do not exist on disk."""
    md = md_path.read_text(encoding="utf-8")
    refs = re.findall(r'<img src="([^"]+)"', md)
    return [r for r in refs if not (output_dir / r).resolve().exists()]


if __name__ == "__main__":
    main()
