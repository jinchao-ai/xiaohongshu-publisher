#!/usr/bin/env python3
"""
Analyze Xiaohongshu creator page - output to file
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def test():
    log = []

    def log_msg(msg):
        print(msg)
        log.append(msg)

    log_msg("🔍 Testing Xiaohongshu...")

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
            log_msg("✅ Cookies loaded")
        else:
            log_msg("❌ No cookies found")

        # Open page
        log_msg("🌐 Opening creator.xiaohongshu.com...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(5)

        log_msg(f"📄 URL: {page.url}")
        log_msg(f"📄 Title: {await page.title()}")

        # Find buttons with publish text
        log_msg("\n🔍 Searching for 发布笔记 button...")
        buttons = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('button, a, div[role="button"], span, div').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    if (text && (text.includes('发布') || text.includes('创作'))) {
                        results.push({
                            tag: el.tagName,
                            text: text.substring(0, 30),
                            className: el.className.substring(0, 50)
                        });
                    }
                });
                return results.slice(0, 10);
            }
        """)
        log_msg(f"Found buttons: {buttons}")

        # Save log
        with open("/tmp/xhs_analysis.log", "w") as f:
            f.write("\n".join(log))
        log_msg("📝 Log saved to /tmp/xhs_analysis.log")

        await page.screenshot(path="/tmp/xhs_analysis.png")
        log_msg("📸 Screenshot saved")

        log_msg("\n⏳ Browser stays open for 2 minutes for manual inspection...")
        await asyncio.sleep(120)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(test())
