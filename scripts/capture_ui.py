"""Capture a seeded RAG Workbench UI screenshot for documentation."""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, executable_path="/usr/bin/chromium")
        page = await browser.new_page(viewport={"width": 1200, "height": 1000}, device_scale_factor=1)
        await page.goto("http://127.0.0.1:18001", wait_until="networkidle")
        await page.locator("#question").fill("What is required before a production deployment?")
        await page.locator("#ask").click()
        await page.locator("#answer:not(.hidden)").wait_for()
        await page.locator("#compare").click()
        await page.locator("#comparison:not(.hidden)").wait_for()
        await page.screenshot(path=root / "docs/ui-preview.png", full_page=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
