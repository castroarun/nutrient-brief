"""Headless Chromium rendering for The Nutrient Brief.

Two outputs we care about:
  1. share-card.html  →  share-card.pdf   (single tall page, mobile width 720px)
  2. carousel/slide_NN.html  →  assets/slide_NN.png  (1080×1350, IG 4:5)

Designed for both local dev and the GitHub Actions runner. Chromium installed via:
    python -m playwright install --with-deps chromium
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable

from playwright.async_api import async_playwright


# ---------- PDF: share card ----------
async def html_to_pdf(src_html: Path, out_pdf: Path) -> int:
    """Render share-card.html → tall single-page PDF. Returns bytes written."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 720, "height": 1200},
            device_scale_factor=2,
        )
        page = await ctx.new_page()
        await page.goto(f"file://{src_html.resolve()}")
        await page.wait_for_load_state("networkidle")
        # Measure actual rendered height so the card fits on one tall page.
        height = await page.evaluate("document.documentElement.scrollHeight")
        await page.pdf(
            path=str(out_pdf),
            width="720px",
            height=f"{height + 20}px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        await browser.close()
    return out_pdf.stat().st_size


# ---------- PNG: IG carousel slides ----------
async def html_to_png(src_html: Path, out_png: Path,
                      width: int = 1080, height: int = 1350) -> int:
    """Render one slide HTML → exact 1080×1350 PNG (IG 4:5 portrait)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=1,  # IG expects 1080x1350; higher DSR balloons size
        )
        page = await ctx.new_page()
        await page.goto(f"file://{src_html.resolve()}")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(
            path=str(out_png),
            clip={"x": 0, "y": 0, "width": width, "height": height},
            type="png",
        )
        await browser.close()
    return out_png.stat().st_size


async def render_slides(slide_paths: Iterable[Path], out_dir: Path) -> list[int]:
    """Render multiple slides in one browser session (faster than per-slide launch)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sizes: list[int] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for src in slide_paths:
            ctx = await browser.new_context(
                viewport={"width": 1080, "height": 1350},
                device_scale_factor=1,
            )
            page = await ctx.new_page()
            await page.goto(f"file://{src.resolve()}")
            await page.wait_for_load_state("networkidle")
            out = out_dir / src.name.replace(".html", ".png")
            await page.screenshot(
                path=str(out),
                clip={"x": 0, "y": 0, "width": 1080, "height": 1350},
                type="png",
            )
            sizes.append(out.stat().st_size)
            await ctx.close()
        await browser.close()
    return sizes


# ---------- sync wrappers for orchestrator ----------
def render_share_card_pdf(src_html: Path, out_pdf: Path) -> int:
    return asyncio.run(html_to_pdf(src_html, out_pdf))


def render_carousel_pngs(slide_paths: list[Path], out_dir: Path) -> list[int]:
    return asyncio.run(render_slides(slide_paths, out_dir))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: renderer.py <edition_dir>")
        sys.exit(1)
    edition = Path(sys.argv[1])
    pdf_size = render_share_card_pdf(edition / "share-card.html", edition / "share-card.pdf")
    print(f"PDF: {pdf_size} bytes")
    slides = sorted((edition / "carousel").glob("slide_*.html"))
    sizes = render_carousel_pngs(slides, edition / "assets")
    print(f"PNGs: {sizes}")
