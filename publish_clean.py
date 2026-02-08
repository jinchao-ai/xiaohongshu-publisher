#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Cleaner version
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    print("🚀 Xiaohongshu Publisher")
    print("=" * 50)

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
    image_path = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return

    print(f"📁 Image: {Path(image_path).name}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            viewport={"width": 1440, "height": 900},
            args=["--no-sandbox"],
        )
        context = await browser.new_context()
        page = await context.new_page()

        # Load cookies
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")
        else:
            print("❌ No cookies found - please login first")
            return

        # Step 1: Go to creator center
        print("\n[1/6] Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_1_creator.png")

        # Step 2: Click 发布笔记 button
        print("\n[2/6] Looking for 发布笔记 button...")

        # Try multiple ways to find the button
        clicked = False

        # Method 1: page.get_by_text
        try:
            btn = page.get_by_text("发布笔记").first
            if await btn.is_visible(timeout=3000):
                await btn.click()
                clicked = True
                print("✅ Clicked via get_by_text")
        except:
            pass

        if not clicked:
            # Method 2: JavaScript
            result = await page.evaluate("""
                () => {
                    const all = document.querySelectorAll('*');
                    for (let el of all) {
                        const text = el.textContent?.trim() || '';
                        if (text === '发布笔记' && el.offsetParent !== null) {
                            el.click();
                            return 'clicked';
                        }
                    }
                    return 'not found';
                }
            """)
            if result == "clicked":
                clicked = True
                print("✅ Clicked via JavaScript")

        if not clicked:
            print("❌ Could not find 发布笔记 button")
            await page.screenshot(path="/tmp/xhs_error_button.png")
            await asyncio.sleep(10)
            await browser.close()
            return

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_2_after_click.png")

        # Step 3: Upload image
        print("\n[3/6] Uploading image...")

        # Wait for file chooser
        try:
            async with page.expect_file_chooser(timeout=5000) as fc:
                # Try clicking in the center area
                await page.mouse.click(400, 300)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠️ No file chooser automatically: {e}")

        # Try direct file input approach
        upload_result = await page.evaluate(f"""
            () => {{
                // Find visible file input
                const inputs = document.querySelectorAll('input[type="file"]');
                for (let inp of inputs) {{
                    if (inp.offsetParent !== null) {{
                        // Try to trigger upload dialog
                        inp.click();
                        return 'file input clicked';
                    }}
                }}

                // Try clicking upload area
                const areas = document.querySelectorAll('[class*="upload"], [class*="Upload"]');
                for (let area of areas) {{
                    if (area.offsetParent !== null) {{
                        area.click();
                        return 'upload area clicked';
                    }}
                }}

                return 'no upload found';
            }}
        """)
        print(f"   {upload_result}")

        # Try setting files via FileChooser if available
        await asyncio.sleep(2)

        # Check current state
        current_url = page.url
        print(f"   Current URL: {current_url}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_3_upload.png")

        # Step 4: Fill title
        print("\n[4/6] Filling title...")
        title = "被这段话治愈了✨｜自我成长"

        title_filled = await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input');
                for (let inp of inputs) {{
                    const ph = inp.getAttribute('placeholder') || '';
                    if (ph.includes('标题') && inp.offsetParent !== null) {{
                        inp.value = "{title.replace('"', '\\"')}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return '✅ Title filled';
                    }}
                }}
                return '❌ Title input not found';
            }}
        """)
        print(f"   {title_filled}")

        await asyncio.sleep(1)

        # Step 5: Fill content
        print("\n[5/6] Filling content...")
        content = """今天看到这句话，真的被戳中了💫

自我成长这件事，真的需要慢慢来。

不必急于求成，也不必与他人比较。
每个人的花期不同，不必焦虑有人提前盛开。

记住：
- 你的努力，时间看得见
- 自律给你自由
- 慢慢来，比较快

愿你在自我成长的路上，永远保持热爱和勇气。💪

#自我成长 #治愈 #正能量"""

        content_filled = await page.evaluate(f"""
            () => {{
                const textareas = document.querySelectorAll('textarea');
                for (let ta of textareas) {{
                    const ph = ta.getAttribute('placeholder') || '';
                    if ((ph.includes('正文') || ph.includes('描述')) && ta.offsetParent !== null) {{
                        ta.value = `{content}`;
                        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                        ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return '✅ Content filled';
                    }}
                }}
                return '❌ Content textarea not found';
            }}
        """)
        print(f"   {content_filled}")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/xhs_4_filled.png")

        # Step 6: Publish
        print("\n[6/6] Clicking publish...")
        publish_result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = el.textContent?.trim() || '';
                    if ((text.includes('发布') || text.includes('提交'))
                        && !text.includes('笔记') && el.offsetParent !== null) {
                        el.click();
                        return '✅ Clicked: ' + text.substring(0, 20);
                    }
                }
                return '❌ Publish button not found';
            }
        """)
        print(f"   {publish_result}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_5_done.png")

        print("\n" + "=" * 50)
        print("✅ Done! Check screenshots in /tmp/xhs_*.png")
        print("=" * 50)

        # Keep browser open
        print("\n⏳ Browser stays open for 3 minutes...")
        await asyncio.sleep(180)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
