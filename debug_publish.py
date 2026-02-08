#!/usr/bin/env python3
"""
Debug the publish page structure
"""

import asyncio
from playwright.async_api import async_playwright


async def debug():
    print("🔍 Debugging Xiaohongshu publish...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Load cookies
        cookie_file = "/Users/mile/.xiaohongshu_publisher/cookies.json"
        try:
            import json

            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")
        except:
            print("❌ No cookies")

        # Go to page
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(5)

        print(f"📄 URL: {page.url}")
        await page.screenshot(path="/tmp/xhs_d1.png")

        # Find 发布笔记
        print("\n🔍 Looking for 发布笔记...")
        elements = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记') {
                        results.push({
                            tag: el.tagName,
                            className: el.className?.substring(0, 30),
                            visible: el.offsetParent !== null,
                            parent: el.parentElement?.tagName
                        });
                    }
                });
                return results;
            }
        """)
        print(f"Found {len(elements)} elements:")
        for e in elements:
            print(f"  - {e}")

        # Try clicking with page.click
        print("\n🖱️ Trying page.click...")
        try:
            await page.get_by_text("发布笔记").first.click(timeout=5000)
            print("✅ Clicked with Playwright")
        except Exception as e:
            print(f"❌ Playwright click failed: {e}")

        await asyncio.sleep(3)
        print(f"📄 URL after click: {page.url}")
        await page.screenshot(path="/tmp/xhs_d2.png")

        # Get page HTML structure
        print("\n🔍 Page structure...")
        html = await page.evaluate("""
            () => {
                const app = document.querySelector('#app') || document.body;
                return app.innerHTML.substring(0, 3000);
            }
        """)
        print(html[:500])

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
