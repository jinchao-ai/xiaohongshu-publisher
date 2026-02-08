#!/usr/bin/env python3
"""
Debug Xiaohongshu publish page structure
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def debug():
    print("🔍 Debugging Xiaohongshu publish page...")

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, viewport={"width": 1440, "height": 900}
        )
        context = await browser.new_context()
        page = await context.new_page()

        # Load cookies
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")

        # Go to publish page directly
        print("🌐 Going to publish page...")
        await page.goto("https://creator.xiaohongshu.com/publish")
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/xhs_publish_direct.png")

        print(f"\n📄 URL: {page.url}")
        print(f"📄 Title: {await page.title()}")

        # Find all inputs with placeholders
        print("\n🔍 All inputs:")
        inputs = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('input, textarea').forEach(el => {
                    const ph = el.getAttribute('placeholder') || '';
                    const tag = el.tagName.toLowerCase();
                    const type = el.getAttribute('type') || '';
                    const visible = el.offsetParent !== null;
                    if (ph || tag === 'textarea') {
                        results.push({
                            tag, type, placeholder: ph.substring(0, 30),
                            visible, className: el.className.substring(0, 40)
                        });
                    }
                });
                return results;
            }
        """)
        for inp in inputs:
            print(
                f"  [{'✓' if inp['visible'] else ' '}] {inp['tag']} ({inp['type']}): {inp['placeholder']}"
            )

        # Find all buttons/links with publish text
        print("\n🔍 Buttons/links:")
        elements = await page.evaluate("""
            () => {
                const results = [];
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = el.textContent?.trim() || '';
                    if ((text.includes('发布') || text.includes('提交') || text.includes('上传'))
                        && el.offsetParent !== null && results.length < 20) {
                        results.push({
                            tag: el.tagName,
                            text: text.substring(0, 30),
                            className: el.className.substring(0, 50)
                        });
                    }
                }
                return results;
            }
        """)
        for el in elements:
            print(f"  - {el['tag']}: {el['text']}")

        # Check for file input
        print("\n🔍 File inputs:")
        file_inputs = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('input[type="file"]').forEach(el => {
                    results.push({
                        visible: el.offsetParent !== null,
                        className: el.className.substring(0, 50)
                    });
                });
                return results;
            }
        """)
        print(f"  Found {len(file_inputs)} file inputs")
        for fi in file_inputs:
            print(f"  - visible: {fi['visible']}, class: {fi['className']}")

        # Check page HTML structure (simplified)
        print("\n🔍 Page structure:")
        structure = await page.evaluate("""
            () => {
                const main = document.querySelector('main') || document.querySelector('#app') || document.body;
                return main.innerHTML.substring(0, 2000);
            }
        """)
        print(structure[:1000] + "...")

        print("\n⏳ Keeping browser open for 5 minutes for manual inspection...")
        await asyncio.sleep(300)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
