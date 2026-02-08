#!/usr/bin/env python3
"""
Simple test - just open page and analyze
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def test():
    print("🔍 Testing Xiaohongshu...")

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Load cookies
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")

        # Open page
        print("🌐 Opening creator.xiaohongshu.com...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(5)

        print(f"📄 URL: {page.url}")
        print(f"📄 Title: {await page.title()}")

        # Check if logged in
        body_text = await page.evaluate(
            "() => document.body.innerText.substring(0, 500)"
        )
        print(f"\n📝 Page content preview:\n{body_text[:300]}...")

        await page.screenshot(path="/tmp/xhs_simple_test.png")

        # Find buttons
        buttons = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('button, a, div[role="button"]').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text && text.length < 30) {
                        results.push({tag: el.tagName, text: text.substring(0, 20)});
                    }
                });
                return results.slice(0, 15);
            }
        """)
        print(f"\n🔘 Buttons found: {buttons}")

        print("\n⏳ Keeping open for 5 minutes...")
        await asyncio.sleep(300)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test())
