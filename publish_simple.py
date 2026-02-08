#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Simple Version
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher")
    print("=" * 50)

    # Pick an image from Downloads
    image_path = "/Users/mile/Downloads/ai冲浪去掉水印.png"
    if not Path(image_path).exists():
        image_path = "/Users/mile/Downloads/2025年终总结.png"

    if not Path(image_path).exists():
        print(f"❌ Image not found")
        return

    print(f"📁 Image: {image_path}")

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # Load cookies if exist
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")
        else:
            print("❌ No cookies - need to login first")
            return

        # Step 1: Go to creator center
        print("\n🌐 Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_pub_1.png")

        # Check if logged in
        if "login" in page.url:
            print("⚠️  Not logged in - cookies may be expired")
            print(f"   URL: {page.url}")
            await browser.close()
            return

        print(f"   URL: {page.url}")

        # Step 2: Click 发布笔记
        print("\n🖱️ Clicking 发布笔记...")
        result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记' && el.offsetParent !== null) {
                        el.click();
                        return 'clicked';
                    }
                }
                return 'not found';
            }
        """)
        print(f"   {result}")
        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_pub_2.png")

        # Step 3: Wait for file chooser and upload
        print("\n📤 Uploading image...")
        try:
            async with page.expect_file_chooser(timeout=5000) as fc:
                await page.evaluate("""
                    () => {
                        document.elementFromPoint(400, 300)?.click();
                    }
                """)
                file_chooser = await fc.value
                await file_chooser.set_files(image_path)
                print(f"✅ Selected: {Path(image_path).name}")
        except Exception as e:
            print(f"❌ File chooser: {e}")

        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/xhs_pub_3.png")
        print(f"   URL: {page.url}")

        # Step 4: Fill title
        print("\n📝 Filling title...")
        title = "AI生成的图片太绝了！"

        title_result = await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input');
                for (const inp of inputs) {{
                    const ph = inp.getAttribute('placeholder') || '';
                    if (ph.includes('标题') && inp.offsetParent !== null) {{
                        inp.value = "{title}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return '✅ Title filled';
                    }}
                }}
                return '❌ Title not found';
            }}
        """)
        print(f"   {title_result}")

        # Step 5: Fill content
        print("\n📄 Filling content...")
        content = "AI生成的这张图真的太美了！分享一下~"

        content_result = await page.evaluate(f"""
            () => {{
                const textareas = document.querySelectorAll('textarea');
                for (const ta of textareas) {{
                    const ph = ta.getAttribute('placeholder') || '';
                    if ((ph.includes('正文') || ph.includes('描述')) && ta.offsetParent !== null) {{
                        ta.value = "{content}";
                        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return '✅ Content filled';
                    }}
                }}
                return '❌ Content not found';
            }}
        """)
        print(f"   {content_result}")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/xhs_pub_4.png")

        # Step 6: Publish
        print("\n🚀 Clicking 发布...")
        publish_result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布' && el.offsetParent !== null) {
                        el.click();
                        return '✅ Clicked 发布';
                    }
                }
                return '❌ Not found';
            }
        """)
        print(f"   {publish_result}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_pub_5.png")

        print("\n" + "=" * 50)
        print("✅ Done! Check screenshots in /tmp/xhs_pub_*.png")
        print("=" * 50)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
