#!/usr/bin/env python3
"""
Debug version - understand what happens when clicking 发布笔记
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def debug():
    print("🔍 Debugging 发布笔记 click...")

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

        # Go to page
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)

        # Analyze the 发布笔记 element
        print("\n🔍 Analyzing 发布笔记 element...")
        analysis = await page.evaluate("""
            () => {
                const results = [];
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记') {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        results.push({
                            tag: el.tagName,
                            text: text,
                            visible: el.offsetParent !== null,
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            pointerEvents: style.pointerEvents,
                            clickable: rect.width > 0 && rect.height > 0,
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            parent: el.parentElement?.tagName || 'none'
                        });
                    }
                }
                return results;
            }
        """)
        print(f"Found {len(analysis)} elements:")
        for r in analysis:
            print(f"  - {r}")

        # Try clicking with evaluate
        print("\n🖱️ Trying JavaScript click...")
        click_result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记' && el.offsetParent !== null) {
                        console.log('Found element:', el.tagName, el.className);
                        el.click();
                        console.log('Clicked successfully');
                        return 'clicked';
                    }
                }
                return 'not found';
            }
        """)
        print(f"Result: {click_result}")

        await asyncio.sleep(2)
        print(f"\n📄 URL after click: {page.url}")

        await page.screenshot(path="/tmp/xhs_debug_click.png")

        # Wait and check for any changes
        await asyncio.sleep(3)
        print(f"📄 URL after 3s: {page.url}")

        await asyncio.sleep(300)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
