#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Follow user workflow:
1. Click 发布笔记
2. Upload image
3. Fill title
4. Fill content
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
        else:
            print("❌ No cookies found")
            return

        # Go to creator center
        print("🌐 Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_step1_creator.png")

        # Step 1: Click 发布笔记
        print("\n1️⃣ Clicking 发布笔记...")
        result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记' && el.offsetParent !== null) {
                        el.click();
                        return '✅ Clicked 发布笔记';
                    }
                }
                return '❌ Not found';
            }
        """)
        print(f"   {result}")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_step2_after_click.png")

        # Step 2: Upload image - wait for file chooser
        print("\n2️⃣ Uploading image...")
        async with page.expect_file_chooser() as fc_info:
            # Click on upload area
            await page.evaluate("""
                () => {
                    const all = document.querySelectorAll('*');
                    for (let el of all) {
                        if (el.offsetParent !== null) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 200 && rect.height > 200) {
                                el.click();
                                return 'clicked';
                            }
                        }
                    }
                    return 'not clicked';
                }
            """)
            await asyncio.sleep(1)

        try:
            file_chooser = await fc_info.timeout(5000)
            await file_chooser.set_files(image_path)
            print(f"✅ Image selected: {Path(image_path).name}")
        except Exception as e:
            print(f"❌ File chooser: {e}")
            # Alternative: directly set file input value
            await page.evaluate(f"""
                () => {{
                    const inputs = document.querySelectorAll('input[type="file"]');
                    for (let input of inputs) {{
                        if (input.offsetParent !== null) {{
                            // Create DataTransfer
                            const dt = new DataTransfer();
                            dt.items.add(new File([new ArrayBuffer(1)], "{Path(image_path).name}", {{type: "image/png"}}));
                            input.files = dt.files;
                            input.dispatchEvent(new Event('change', {{bubbles: true}}));
                            return 'file set';
                        }}
                    }}
                    return 'no input';
                }}
            """)

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_step3_uploaded.png")

        # Step 3: Fill title
        print("\n3️⃣ Filling title...")
        title = "被这段话治愈了✨｜自我成长"

        title_result = await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input');
                for (let input of inputs) {{
                    const ph = input.getAttribute('placeholder') || '';
                    if (ph.includes('标题') && input.offsetParent !== null) {{
                        input.value = '{title}';
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                        input.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return '✅ Title filled';
                    }}
                }}
                return '❌ Title input not found';
            }}
        """)
        print(f"   {title_result}")

        await asyncio.sleep(1)

        # Step 4: Fill content
        print("\n4️⃣ Filling content...")
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
        print(f"   {content_result}")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/xhs_step4_filled.png")

        # Step 5: Click publish
        print("\n5️⃣ Ready to publish...")
        await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (let el of all) {
                    const text = el.textContent?.trim() || '';
                    if ((text.includes('发布') || text.includes('提交')) && el.offsetParent !== null) {
                        el.click();
                        return '✅ Clicked: ' + text.substring(0, 20);
                    }
                }
                return '❌ Publish button not found';
            }
        """)

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_step5_published.png")

        print("\n" + "=" * 50)
        print("✅ Done! Browser stays open for 2 minutes...")
        print("=" * 50)

        await asyncio.sleep(120)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
