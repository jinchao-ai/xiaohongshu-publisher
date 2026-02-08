#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Final Version
Click 发布笔记 in nav, upload, fill, publish
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher")
    print("=" * 50)

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
    image_path = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return

    print(f"📁 Image: {Path(image_path).name}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Load cookies
        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")
        else:
            print("❌ No cookies - please login first")
            return

        # Step 1: Go to creator center
        print("\n[1/5] Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_final_1.png")
        print(f"   URL: {page.url}")

        # Step 2: Click 发布笔记 in navigation
        print("\n[2/5] Clicking 发布笔记...")

        click_result = await page.evaluate("""
            () => {
                // Find navigation element with 发布笔记
                const navItems = document.querySelectorAll('.d-topbar, nav, [class*="nav"], [class*="menu"]');
                for (const nav of navItems) {
                    const links = nav.querySelectorAll('a, div, span, li');
                    for (const link of links) {
                        const text = link.textContent?.trim() || '';
                        if (text === '发布笔记' && link.offsetParent !== null) {
                            link.click();
                            return 'clicked nav item: 发布笔记';
                        }
                    }
                }

                // Fallback: search all elements
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记' && el.offsetParent !== null) {
                        el.click();
                        return 'clicked: 发布笔记';
                    }
                }
                return 'not found';
            }
        """)
        print(f"   {click_result}")

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_final_2.png")
        print(f"   URL after click: {page.url}")

        # Step 3: Upload image
        print("\n[3/5] Uploading image...")

        # Wait for upload page
        await asyncio.sleep(2)

        # Try file chooser
        try:
            async with page.expect_file_chooser(timeout=5000) as fc_info:
                # Click in the upload area
                await page.evaluate("""
                    () => {
                        const uploadAreas = document.querySelectorAll('[class*="upload"], [class*="Upload"], .drop-zone');
                        for (const area of uploadAreas) {
                            if (area.offsetParent !== null) {
                                area.click();
                                return 'clicked upload area';
                            }
                        }
                        // Try center click
                        document.elementFromPoint(400, 300)?.click();
                        return 'tried click';
                    }
                """)
        except Exception as e:
            print(f"   ⚠️ No file chooser: {e}")

        await asyncio.sleep(1)

        # Check current state
        current_url = page.url
        print(f"   Current URL: {current_url}")

        # Screenshot
        await page.screenshot(path="/tmp/xhs_final_3.png")

        # Step 4: Fill title
        print("\n[4/5] Filling title...")
        title = "被这段话治愈了✨｜自我成长"

        title_result = await page.evaluate(f"""
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
        print(f"   {title_result}")

        # Fill content
        print("\n[5/5] Filling content...")
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

        content_result = await page.evaluate(f"""
            () => {{
                const textareas = document.querySelectorAll('textarea, [contenteditable]');
                for (let ta of textareas) {{
                    const ph = ta.getAttribute('placeholder') || '';
                    if ((ph.includes('正文') || ph.includes('描述')) && ta.offsetParent !== null) {{
                        ta.value = `{content}`;
                        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                        ta.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return '✅ Content filled';
                    }}
                }}
                return '❌ Content area not found';
            }}
        """)
        print(f"   {content_result}")

        await page.screenshot(path="/tmp/xhs_final_4.png")

        # Click publish button
        print("\n✅ Ready to publish...")
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
                return '❌ Publish button not found';
            }
        """)
        print(f"   {publish_result}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_final_5.png")

        print("\n" + "=" * 50)
        print("✅ Done! Check screenshots in /tmp/xhs_final_*.png")
        print("=" * 50)

        # Keep open for inspection
        print("\n⏳ Browser stays open for 2 minutes...")
        await asyncio.sleep(120)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
