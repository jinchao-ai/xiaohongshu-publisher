#!/usr/bin/env python3
"""
Check content textarea after upload
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def check():
    print("🔍 Checking content textarea after upload...")

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

        # Upload image
        print("📤 Uploading image...")
        try:
            async with page.expect_file_chooser(timeout=5000) as fc:
                await page.click("text=上传图片")
            await fc.value.set_files("/Users/mile/Downloads/ai冲浪去掉水印.png")
            print("✅ Uploaded")
        except Exception as e:
            print(f"❌ {e}")

        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/chk_upload.png")

        # Check textareas
        print("\n🔍 Looking for textareas after upload...")
        textareas = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('textarea, [contenteditable]').forEach(el => {
                    const ph = el.getAttribute('placeholder') || '';
                    const tag = el.tagName;
                    const visible = el.offsetParent !== null;
                    results.push({tag, placeholder: ph.substring(0, 30), visible});
                });
                return results;
            }
        """)
        print(f"Textareas: {textareas}")

        # Get HTML structure around textarea
        print("\n🔍 Page structure after upload...")
        html = await page.evaluate("""
            () => {
                const app = document.querySelector('#app') || document.body;
                return app.innerHTML.substring(0, 4000);
            }
        """)
        print(html[:1000])

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(check())
