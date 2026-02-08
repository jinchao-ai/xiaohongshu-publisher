#!/usr/bin/env python3
"""
Quick debug - analyze 发布笔记 element
"""

import asyncio
from playwright.async_api import async_playwright


async def debug():
    print("🔍 Analyzing 发布笔记...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)

        # Get element info
        info = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                let result = {count: 0, elements: []};
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记') {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        result.count++;
                        result.elements.push({
                            tag: el.tagName,
                            display: style.display,
                            clickable: rect.width > 0 && rect.height > 0,
                            text: el.textContent?.trim()
                        });
                    }
                }
                return result;
            }
        """)
        print(f"Found {info['count']} elements:")
        for e in info["elements"][:5]:
            print(f"  - {e}")

        # Try clicking with JS
        print("\n🖱️ Clicking...")
        result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    if (el.textContent?.trim() === '发布笔记' && el.offsetParent !== null) {
                        console.log('Clicking element:', el.tagName);
                        el.click();
                        return 'clicked';
                    }
                }
                return 'not found';
            }
        """)
        print(f"Result: {result}")

        await asyncio.sleep(2)
        print(f"URL: {page.url}")

        await page.screenshot(path="/tmp/xhs_qd.png")

        await asyncio.sleep(3)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug())
