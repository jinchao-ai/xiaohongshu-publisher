#!/usr/bin/env python3
"""
Debug the publish page - check for image/video toggle
"""

import asyncio
from playwright.async_api import async_playwright


async def debug():
    print("🔍 Debugging Xiaohongshu publish page...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Load cookies
        cookie_file = "/Users/mile/.xiaohongshu_publisher/cookies.json"
        import json

        with open(cookie_file) as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print("✅ Cookies loaded")

        # Go directly to image publish page
        print("\n🌐 Going to image publish page...")
        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(5)

        print(f"📄 URL: {page.url}")
        await page.screenshot(path="/tmp/xhs_img_1.png")

        # Find all clickable elements
        print("\n🔍 Looking for all clickable elements...")
        elements = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if ((text.includes('发布') || text.includes('图片') || text.includes('上传') || text.includes('图文'))
                        && text.length < 30 && results.length < 15) {
                        results.push({
                            tag: el.tagName,
                            text: text.substring(0, 20),
                            className: el.className?.substring(0, 40)
                        });
                    }
                });
                return results;
            }
        """)
        print(f"Found: {elements}")

        # Find inputs
        print("\n🔍 Looking for inputs...")
        inputs = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('input, textarea').forEach(el => {
                    const ph = el.getAttribute('placeholder') || '';
                    const type = el.getAttribute('type') || '';
                    if (ph || type) {
                        results.push({
                            tag: el.tagName,
                            type: type,
                            placeholder: ph.substring(0, 30),
                            visible: el.offsetParent !== null
                        });
                    }
                });
                return results;
            }
        """)
        print(f"Inputs: {inputs}")

        # Find buttons
        print("\n🔍 Looking for buttons...")
        buttons = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('button').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text) {
                        results.push({
                            text: text.substring(0, 20),
                            visible: el.offsetParent !== null
                        });
                    }
                });
                return results.slice(0, 10);
            }
        """)
        print(f"Buttons: {buttons}")

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
