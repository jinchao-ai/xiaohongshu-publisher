#!/usr/bin/env python3
"""
Final working Xiaohongshu Publisher
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher - Final")
    print("=" * 50)

    image_path = "/Users/mile/Downloads/ai冲浪去掉水印.png"
    if not json.load(open("/Users/mile/.xiaohongshu_publisher/cookies.json")):
        print("❌ No cookies")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        with open("/Users/mile/.xiaohongshu_publisher/cookies.json") as f:
            await context.add_cookies(json.load(f))
        print("✅ Cookies loaded")

        # Go to publish page
        print("\n🌐 Opening publish page...")
        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/final_1.png")

        # Upload - click button and handle chooser
        print("\n📤 Clicking 上传图片...")
        async with page.expect_file_chooser():
            await page.click("button:has-text('上传图片')")
        # Now set files
        await page.set_input_files('input[type="file"]', image_path)
        print(f"✅ Selected: {image_path.split('/')[-1]}")

        # Wait for upload
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/final_2.png")

        # Fill title
        print("\n📝 Filling title...")
        await page.fill('input[placeholder*="标题"]', "AI生成的图片太绝了！")
        print("✅ Title filled")

        # Try to find and fill content textarea
        print("\n📄 Looking for content textarea...")
        textarea = page.locator("textarea, [contenteditable]").first
        if await textarea.is_visible():
            await textarea.fill("这张AI生成的图片真的太美了，分享给大家看看！")
            print("✅ Content filled")
        else:
            print("❌ Content textarea not visible yet")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/final_3.png")

        # Click publish
        print("\n🚀 Clicking 发布...")
        await page.click("button:has-text('发布')")
        print("✅ Published!")

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/final_4.png")

        print("\n" + "=" * 50)
        print("✅ Done! Check /tmp/final_*.png")
        print("=" * 50)

        await asyncio.sleep(30)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
