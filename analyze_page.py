#!/usr/bin/env python3
"""
Analyze Xiaohongshu creator page structure
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def analyze_page():
    print("🔍 Analyzing Xiaohongshu creator page...")

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

        # Go to creator center
        print("🌐 Going to creator center...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)

        # Screenshot
        await page.screenshot(path="/tmp/xhs_creator.png")
        print("📸 Screenshot saved to /tmp/xhs_creator.png")

        # Analyze buttons
        print("\n🔍 Analyzing buttons...")
        buttons = await page.evaluate("""
            () => {
                const results = [];
                const buttons = document.querySelectorAll('button, a, div[role="button"], [class*="button"]');
                for (let btn of buttons) {
                    const text = btn.textContent?.trim() || '';
                    const className = btn.className || '';
                    const role = btn.getAttribute('role') || '';
                    if (text && (text.includes('发布') || text.includes('创作') || text.includes('新建'))) {
                        results.push({
                            text: text.substring(0, 50),
                            className: className.substring(0, 100),
                            tagName: btn.tagName,
                            role: role
                        });
                    }
                }
                return results;
            }
        """)
        print(f"Found {len(buttons)} publish-related buttons:")
        for btn in buttons[:10]:
            print(f"  - {btn}")

        # Analyze inputs
        print("\n🔍 Analyzing inputs...")
        inputs = await page.evaluate("""
            () => {
                const results = [];
                const elements = document.querySelectorAll('input, textarea, [contenteditable]');
                for (let el of elements) {
                    const placeholder = el.getAttribute('placeholder') || '';
                    const tagName = el.tagName;
                    const type = el.getAttribute('type') || '';
                    if (placeholder || tagName === 'TEXTAREA' || el.isContentEditable) {
                        results.push({
                            tagName: tagName,
                            type: type,
                            placeholder: placeholder.substring(0, 50),
                            className: el.className?.substring(0, 50) || ''
                        });
                    }
                }
                return results;
            }
        """)
        print(f"Found {len(inputs)} input/textarea elements:")
        for inp in inputs[:10]:
            print(f"  - {inp}")

        # Check current URL
        print(f"\n🌐 Current URL: {page.url}")

        # Get page title
        print(f"📄 Page title: {await page.title()}")

        # Keep open for manual inspection
        print("\n⏳ Browser will stay open for 60 seconds for manual inspection...")
        await asyncio.sleep(60)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_page())
