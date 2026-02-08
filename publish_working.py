#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Working Version
Go to image publish page directly
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher")
    print("=" * 50)

    # Pick an image
    image_path = "/Users/mile/Downloads/ai冲浪去掉水印.png"
    if not Path(image_path).exists():
        image_path = "/Users/mile/Downloads/2025年终总结.png"
    if not Path(image_path).exists():
        print("❌ No image found")
        return

    print(f"📁 Image: {Path(image_path).name}")

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
        else:
            print("❌ No cookies - need login")
            return

        # Go directly to image publish page
        print("\n🌐 Opening image publish page...")
        await page.goto(
            "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"
        )
        await asyncio.sleep(5)

        print(f"📄 URL: {page.url}")
        await page.screenshot(path="/tmp/xhs_work_1.png")

        # Find file input
        print("\n📤 Finding file input...")
        file_input = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input[type="file"]');
                for (const inp of inputs) {
                    if (inp.offsetParent !== null) {
                        return 'found visible file input';
                    }
                }
                return 'not found';
            }
        """)
        print(f"   {file_input}")

        # Upload file
        print(f"\n📤 Uploading {Path(image_path).name}...")
        try:
            # Use the file chooser
            async with page.expect_file_chooser(timeout=5000) as fc_info:
                # Click on the upload area
                await page.click("text=上传图片")
                await asyncio.sleep(1)

            file_chooser = await fc_info.value
            await file_chooser.set_files(image_path)
            print(f"✅ File selected")
        except Exception as e:
            print(f"❌ File chooser: {e}")
            # Try direct approach
            await page.set_input_files('input[type="file"][visible=true]', image_path)
            print(f"✅ File set directly")

        # Wait for upload
        print("\n⏳ Waiting for upload...")
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/xhs_work_2.png")

        # Check for title input
        print("\n🔍 Looking for title input...")
        title_inputs = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input');
                const results = [];
                inputs.forEach(inp => {
                    const ph = inp.getAttribute('placeholder') || '';
                    const visible = inp.offsetParent !== null;
                    if (ph) results.push({placeholder: ph.substring(0, 30), visible});
                });
                return results;
            }
        """)
        print(f"   Inputs: {title_inputs}")

        # Fill title
        print("\n📝 Filling title...")
        title = "AI生成的图片太绝了！"

        filled = await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input');
                for (const inp of inputs) {{
                    const ph = inp.getAttribute('placeholder') || '';
                    if (ph.includes('标题') && inp.offsetParent !== null) {{
                        inp.value = "{title}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return '✅ Title filled';
                    }}
                }}
                return '❌ Not found';
            }}
        """)
        print(f"   {filled}")

        # Fill content
        print("\n📄 Filling content...")
        content = "这张AI生成的图片真的太美了，分享给大家看看！"

        filled2 = await page.evaluate(f"""
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
                return '❌ Not found';
            }}
        """)
        print(f"   {filled2}")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/xhs_work_3.png")

        # Click publish
        print("\n🚀 Clicking 发布...")
        pub_result = await page.evaluate("""
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
        print(f"   {pub_result}")

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_work_4.png")

        print("\n" + "=" * 50)
        print("✅ Done! Check screenshots in /tmp/xhs_work_*.png")
        print("=" * 50)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
