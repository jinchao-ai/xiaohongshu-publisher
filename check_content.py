#!/usr/bin/env python3
"""
Check content textarea structure
"""

import asyncio
from playwright.async_api import async_playwright


async def check():
    print("🔍 Checking content textarea...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        import json

        with open("/Users/mile/.xiaohongshu_publisher/cookies.json") as f:
            await context.add_cookies(json.load(f))

        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/chk_1.png")

        # Get all textareas
        print("\n🔍 Looking for textareas...")
        textareas = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('textarea, [contenteditable]').forEach(el => {
                    const ph = el.getAttribute('placeholder') || '';
                    const tag = el.tagName;
                    const cls = el.className?.substring(0, 50) || '';
                    const visible = el.offsetParent !== null;
                    results.push({
                        tag, placeholder: ph.substring(0, 30), className: cls, visible
                    });
                });
                return results;
            }
        """)
        print(f"Found: {textareas}")

        # Get all elements that might be content inputs
        print("\n🔍 Looking for all inputs/areas...")
        all_inputs = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if ((text.includes('正文') || text.includes('描述') || text.includes('分享'))
                        && text.length < 30 && results.length < 10) {
                        results.push({
                            tag: el.tagName,
                            text: text.substring(0, 30),
                            className: el.className?.substring(0, 50)
                        });
                    }
                });
                return results;
            }
        """)
        print(f"Found: {all_inputs}")

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(check())
