#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Handle file chooser properly
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher - File Chooser Version")
    print("=" * 50)

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
    image_path = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return

    print(f"📁 Image: {Path(image_path).name}")

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
            print("❌ No cookies - please login first")
            return

        # Step 1: Go to creator center
        print("\n[1/6] Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_v3_1.png")

        # Step 2: Click 发布笔记
        print("\n[2/6] Clicking 发布笔记...")
        result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布笔记' && el.offsetParent !== null) {
                        el.click();
                        return 'clicked 发布笔记';
                    }
                }
                return 'not found';
            }
        """)
        print(f"   {result}")
        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_v3_2.png")

        # Step 3: Handle file chooser
        print("\n[3/6] Waiting for file chooser...")
        file_chooser = None
        try:
            async with page.expect_file_chooser(timeout=10000) as fc_info:
                await asyncio.sleep(1)
            file_chooser = fc_info.value
            print("✅ File chooser appeared!")
        except Exception as e:
            print(f"❌ No file chooser: {e}")

        if file_chooser:
            await file_chooser.set_files(image_path)
            print(f"✅ Selected: {Path(image_path).name}")
        else:
            print("⚠️ Could not get file chooser")

        # Wait for upload to complete
        print("\n   Waiting for upload...")
        await asyncio.sleep(5)
        await page.screenshot(path="/tmp/xhs_v3_3.png")

        print(f"   Current URL: {page.url}")

        # Step 4: Fill title
        print("\n[4/6] Filling title...")
        title = "被这段话治愈了✨｜自我成长"

        # Try multiple selector strategies
        title_filled = await page.evaluate(f"""
            () => {{
                // Strategy 1: placeholder
                const inputs1 = document.querySelectorAll('input[placeholder*="标题"]');
                for (const inp of inputs1) {{
                    if (inp.offsetParent !== null) {{
                        inp.value = "{title.replace('"', '\\"')}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'title filled (placeholder)';
                    }}
                }}

                // Strategy 2: aria-label
                const inputs2 = document.querySelectorAll('input[aria-label*="标题"]');
                for (const inp of inputs2) {{
                    if (inp.offsetParent !== null) {{
                        inp.value = "{title.replace('"', '\\"')}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'title filled (aria-label)';
                    }}
                }}

                // Strategy 3: find by nearby text
                const containers = document.querySelectorAll('[class*="title"], [class*="Title"]');
                for (const cont of containers) {{
                    const inp = cont.querySelector('input');
                    if (inp && inp.offsetParent !== null) {{
                        inp.value = "{title.replace('"', '\\"')}";
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'title filled (by container)';
                    }}
                }}

                return 'title not found';
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
                // Strategy 1: textarea with placeholder
                const textareas1 = document.querySelectorAll('textarea[placeholder*="正文"]');
                for (const ta of textareas1) {{
                    if (ta.offsetParent !== null) {{
                        ta.value = `{content}`;
                        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'content filled (textarea placeholder)';
                    }}
                }}

                // Strategy 2: contenteditable
                const editables = document.querySelectorAll('[contenteditable="true"]');
                for (const ed of editables) {{
                    if (ed.offsetParent !== null) {{
                        ed.innerText = `{content}`;
                        ed.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'content filled (contenteditable)';
                    }}
                }}

                // Strategy 3: by container class
                const containers = document.querySelectorAll('[class*="content"], [class*="Content"], [class*="editor"]');
                for (const cont of containers) {{
                    const ta = cont.querySelector('textarea');
                    const ed = cont.querySelector('[contenteditable]');
                    if (ta && ta.offsetParent !== null) {{
                        ta.value = `{content}`;
                        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'content filled (ta in container)';
                    }}
                    if (ed && ed.offsetParent !== null) {{
                        ed.innerText = `{content}`;
                        ed.dispatchEvent(new Event('input', {{bubbles: true}}));
                        return 'content filled (ed in container)';
                    }}
                }}

                return 'content not found';
            }}
        """)
        print(f"   {content_filled}")
        await page.screenshot(path="/tmp/xhs_v3_4.png")

        # Step 6: Publish
        print("\n[6/6] Clicking publish...")
        publish_result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布' && el.offsetParent !== null) {
                        el.click();
                        return 'clicked 发布';
                    }
                }
                return 'not found';
            }
        """)
        print(f"   {publish_result}")
        await page.screenshot(path="/tmp/xhs_v3_5.png")

        print("\n" + "=" * 50)
        print("✅ Done!")
        print("=" * 50)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
