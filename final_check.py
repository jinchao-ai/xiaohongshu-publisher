#!/usr/bin/env python3
"""
Check content textarea after upload - fixed
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def check():
    print("🔍 Checking page structure...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        with open("/Users/mile/.xiaohongshu_publisher/cookies.json") as f:
            await context.add_cookies(json.load(f))

        # Upload file first using set_input_files
        print("📤 Uploading image...")
        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(3)

        # Find and use file input
        file_result = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input[type="file"]');
                for (const inp of inputs) {
                    if (inp.offsetParent !== null) {
                        // This is the upload input
                        inp.click();
                        return 'found file input';
                    }
                }
                return 'not found';
            }
        """)
        print(f"File input: {file_result}")

        # Wait for file chooser
        try:
            async with page.expect_file_chooser(timeout=5000) as fc:
                await asyncio.sleep(0.5)
            await fc.value.set_files("/Users/mile/Downloads/ai冲浪去掉水印.png")
            print("✅ File selected via chooser")
        except Exception as e:
            print(f"❌ {e}")

        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/chk_after.png")

        # Check all elements for textarea/content
        print("\n🔍 Checking page structure...")
        structure = await page.evaluate("""
            () => {
                const elements = [];
                document.querySelectorAll('*').forEach(el => {
                    const text = el.textContent?.trim() || '';
                    const tag = el.tagName.toLowerCase();
                    const ph = el.getAttribute('placeholder') || '';
                    const cls = el.className?.substring(0, 30) || '';

                    // Look for content-related elements
                    if ((ph.includes('正文') || ph.includes('分享') || ph.includes('说点什么') ||
                         text.includes('添加描述') || text.includes('说点什么')) &&
                        elements.length < 15) {
                        elements.push({tag, placeholder: ph.substring(0, 20), text: text.substring(0, 30), className: cls.substring(0, 30)});
                    }
                });
                return elements;
            }
        """)
        print(f"Content-related: {structure}")

        # Check for all textareas
        print("\n🔍 All textareas...")
        textareas = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('textarea')).map(el => ({
                    placeholder: el.getAttribute('placeholder')?.substring(0, 30),
                    visible: el.offsetParent !== null
                }));
            }
        """)
        print(f"Textareas: {textareas}")

        # Check for contenteditable
        print("\n🔍 Contenteditable...")
        editors = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('[contenteditable]')).map(el => ({
                    placeholder: el.getAttribute('placeholder')?.substring(0, 30) || 'none',
                    visible: el.offsetParent !== null
                }));
            }
        """)
        print(f"Contenteditable: {editors}")

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(check())
