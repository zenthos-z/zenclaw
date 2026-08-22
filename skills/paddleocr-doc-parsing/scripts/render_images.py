"""High-resolution local rendering of figures referenced by a PaddleOCR result.

The API's markdown images are rasterized at page-scale 2x, which is soft for
vector figures (tikz/matplotlib diagrams common in arXiv papers). This script
re-renders each image region directly from the source PDF at higher scale and
overwrites the low-res copies, keeping the markdown `<img>` refs unchanged.

Coordinate math: API bboxes live in the API's rendered page space
(result.dataInfo.pages[i].width/height); the PDF page may differ in size.
scale = pdf_page_size / api_page_size, applied to both axes.

Usage:
    uv run scripts/render_images.py result.json "source.pdf" [--scale 4] [--output-dir DIR]

    - result.json: raw API envelope (needed for page count + sizes)
    - source.pdf:  the original PDF that was parsed
    - --scale:     render scale relative to the API's 2x space (default 4)
    - --output-dir: default = alongside result.json (images into <dir>/imgs/)

Exit codes:
    0   all referenced images rendered
    1   some failed (see stderr)
"""

# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pymupdf>=1.24",
# ]
# ///

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

IMG_RE = re.compile(r"img_in_(image|chart)_box_(\d+)_(\d+)_(\d+)_(\d+)\.jpg$")


def parse_bbox_from_name(name: str) -> tuple[int, int, int, int] | None:
    m = IMG_RE.search(name)
    if not m:
        return None
    return int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))


def render_all(
    result_path: Path, pdf_path: Path, output_dir: Path, scale: float = 4.0
) -> tuple[int, list[tuple[str, str]]]:
    """Render all images referenced in result JSON from the source PDF.

    Returns (rendered_count, [(relative_path, error), ...]).
    """
    data = json.loads(result_path.read_text(encoding="utf-8"))
    if not data.get("ok"):
        print(f"result JSON reports ok=false: {data.get('error')}", file=sys.stderr)
        sys.exit(1)

    pages = data.get("result", {}).get("result", {}).get("layoutParsingResults", [])
    doc = pymupdf.open(str(pdf_path))
    if len(doc) < len(pages):
        print(
            f"PDF has {len(doc)} pages but result has {len(pages)}; page mapping unreliable",
            file=sys.stderr,
        )
        sys.exit(1)

    info_pages = (
        data.get("result", {}).get("result", {}).get("dataInfo", {}).get("pages", [])
    )
    failed: list[tuple[str, str]] = []
    rendered = 0
    for i, page in enumerate(pages):
        pdf_page = doc[i]
        api_w = pdf_page.rect.width * 2  # API default renders at 2x
        if i < len(info_pages):
            api_w = info_pages[i].get("width", api_w)
        factor = pdf_page.rect.width / api_w

        images = (page.get("markdown", {}) or {}).get("images", {}) or {}
        for rel, _url in images.items():
            bbox = parse_bbox_from_name(rel)
            if not bbox:
                print(f"SKIP {rel}: bbox not parseable from name", file=sys.stderr)
                continue
            x1, y1, x2, y2 = bbox
            clip = pymupdf.Rect(x1 * factor, y1 * factor, x2 * factor, y2 * factor)
            dest = (output_dir / rel).resolve()
            if not str(dest).startswith(str(output_dir.resolve())):
                failed.append((rel, "unsafe relative path"))
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                pm = pdf_page.get_pixmap(
                    matrix=pymupdf.Matrix(scale, scale), clip=clip
                )
                pm.save(str(dest), jpg_quality=95)
                rendered += 1
                print(f"OK  {rel}  {pm.width}x{pm.height}")
            except Exception as e:
                failed.append((rel, str(e)))
                print(f"FAIL {rel}: {e}", file=sys.stderr)

    print(f"\n{rendered} images rendered at {scale}x into {output_dir}")
    return rendered, failed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_json", help="result JSON from layout_caller.py")
    parser.add_argument("source_pdf", help="original PDF that was parsed")
    parser.add_argument("--scale", type=float, default=4.0, help="render scale (default 4)")
    parser.add_argument("--output-dir", default=None, help="output dir (default: alongside result JSON)")
    args = parser.parse_args()

    result_path = Path(args.result_json).expanduser().resolve()
    pdf_path = Path(args.source_pdf).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else result_path.parent

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    rendered, failed = render_all(result_path, pdf_path, output_dir, scale=args.scale)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
