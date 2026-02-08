#!/usr/bin/env python3
"""
Xiaohongshu Publisher V2 - Robust automation with proper selectors
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, expect


async def publish():
    print("🚀 Xiaohongshu Publisher V2")
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

        # Navigate to creator center
        print("🌐 Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com")
        await asyncio.sleep(3)

        # Screenshot
        await page.screenshot(path="/tmp/xhs_v2_creator.png")
        print("📸 Creator center screenshot saved")

        # Try to find and click "发布笔记" button
        print("\n🔍 Looking for publish button...")

        # Method 1: Find by text content
        publish_btn = page.get_by_text("发布笔记", exact=False).first
        if await publish_btn.is_visible(timeout=5000):
            print("✅ Found '发布笔记' button")
            await publish_btn.click()
            await asyncio.sleep(2)
        else:
            # Method 2: Find by role
            print("Trying alternative selectors...")
            buttons = page.locator("button")
            for btn in await buttons.all():
                text = await btn.text_content()
                if text and "发布" in text:
                    print(f"✅ Found button: {text[:30]}")
                    await btn.click()
                    await asyncio.sleep(2)
                    break

        # Screenshot after clicking
        await page.screenshot(path="/tmp/xhs_v2_after_click.png")

        # Now try to find file input
        print("\n🔍 Looking for file upload...")

        # Method: Use file chooser
        async with page.expect_file_chooser() as fc_info:
            # Try to click on upload area
            upload_clicked = await page.evaluate("""
                () => {
                    // Try various upload selectors
                    const selectors = [
                        '.upload-area',
                        '[class*="upload"]',
                        '[class*="Upload"]',
                        '[data-testid="upload"]',
                        '.drop-zone',
                        '.upload-container'
                    ];

                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) {
                            el.click();
                            return 'clicked: ' + sel;
                        }
                    }

                    // Fallback: click center of page
                    const center = document.elementFromPoint(window.innerWidth/2 - 200, window.innerHeight/2);
                    if (center) {
                        center.click();
                        return 'clicked center';
                    }

                    return 'no upload found';
                }
            """)
            print(f"Upload attempt: {upload_clicked}")

        # Wait for file chooser
        try:
            file_chooser = await fc_info.wait_for_event("filechooser", timeout=5000)
            print("✅ File chooser opened!")
            await file_chooser.set_files(image_path)
            print(f"✅ Selected: {Path(image_path).name}")
        except Exception as e:
            print(f"❌ No file chooser: {e}")

        # Wait for upload
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_v2_after_upload.png")

        # Fill in title
        print("\n📝 Filling title...")
        title = "被这段话治愈了✨｜自我成长"

        # Try native fill first
        try:
            await page.get_by_placeholder("标题").fill(title)
            print("✅ Title filled (by placeholder)")
        except:
            # Fallback to JavaScript
            await page.evaluate(f"""
                () => {{
                    const inputs = document.querySelectorAll('input');
                    for (const input of inputs) {{
                        if (input.getAttribute('placeholder')?.includes('标题')) {{
                            input.value = '{title}';
                            input.dispatchEvent(new Event('input', {{bubbles: true}}));
                            return 'title filled';
                        }}
                    }}
                    return 'title not found';
                }}
            """)
            print("✅ Title filled (JavaScript)")

        # Fill in content
        print("\n📄 Filling content...")
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

        try:
            textareas = page.locator("textarea")
            for textarea in await textareas.all():
                placeholder = await textarea.get_attribute("placeholder") or ""
                if "正文" in placeholder or "描述" in placeholder:
                    await textarea.fill(content)
                    print("✅ Content filled")
                    break
            else:
                raise Exception("No textarea found")
        except:
            await page.evaluate(f"""
                () => {{
                    const textareas = document.querySelectorAll('textarea');
                    for (const ta of textareas) {{
                        if (ta.getAttribute('placeholder')?.includes('正文') ||
                            ta.getAttribute('placeholder')?.includes('描述')) {{
                            ta.value = `{content}`;
                            ta.dispatchEvent(new Event('input', {{bubbles: true}}));
                            return 'content filled';
                        }}
                    }}
                    return 'content not filled';
                }}
            """)
            print("✅ Content filled (JavaScript)")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/xhs_v2_filled.png")

        # Click publish
        print("\n🚀 Clicking publish...")

        # Try different publish buttons
        publish_success = await page.evaluate("""
            () => {
                // Find all clickable elements with publish text
                const allElements = document.querySelectorAll('*');
                const publishKeywords = ['发布笔记', '发布', '提交', '确认发布'];

                for (const el of allElements) {
                    const text = el.textContent?.trim() || '';
                    for (const keyword of publishKeywords) {
                        if (text.includes(keyword) && el.offsetParent !== null) {
                            // Check if it's actually clickable
                            const style = window.getComputedStyle(el);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                el.click();
                                return 'clicked: ' + text.substring(0, 30);
                            }
                        }
                    }
                }
                return 'not clicked';
            }
        """)

        print(f"Publish: {publish_success}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_v2_publish.png")

        print("\n" + "=" * 50)
        print("✅ Automation complete!")
        print("=" * 50)

        # Keep open for 2 minutes
        await asyncio.sleep(120)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
