#!/usr/bin/env python3
"""
Simple check of textarea after upload
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def check():
    print("🔍 Checking textarea...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        with open("/Users/mile/.xiaohongshu_publisher/cookies.json") as f:
            await context.add_cookies(json.load(f))

        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(3)

        # Upload
        try:
            async with page.expect_file_chooser() as fc:
                await page.click('button:has-text("上传图片")')
            await fc.value.set_files("/Users/mile/Downloads/ai冲浪去掉水印.png")
            print("✅ Uploaded")
        except Exception as e:
            print(f"❌ {e}")

        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/simple_check.png")

        # Check textareas
        print("\nTextareas found:")
        textareas = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('textarea')).map(el => ({
                    placeholder: el.getAttribute('placeholder') || 'none',
                    visible: el.offsetParent !== null
                }));
            }
        """)
        for ta in textareas:
            print(f"  - {ta}")

        # Check for any editable area
        print("\nContenteditable:")
        editors = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('[contenteditable]')).map(el => ({
                    visible: el.offsetParent !== null
                }));
            }
        """)
        print(f"  Found {len(editors)}")

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(check())
