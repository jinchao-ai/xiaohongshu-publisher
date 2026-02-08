#!/usr/bin/env python3
"""
Xiaohongshu Publisher - Handle upload properly
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def publish():
    print("🚀 Xiaohongshu Publisher")
    print("=" * 50)

    image_path = "/Users/mile/Downloads/ai冲浪去掉水印.png"
    if not Path(image_path).exists():
        image_path = "/Users/mile/Downloads/2025年终总结.png"

    if not Path(image_path).exists():
        print(f"❌ Image not found")
        return

    print(f"📁 Image: {Path(image_path).name}")

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        if cookie_file.exists():
            with open(cookie_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies loaded")
        else:
            print("❌ No cookies")
            return

        print("\n🌐 Opening creator center...")
        await page.goto("https://creator.xiaohongshu.com/new/home")
        await asyncio.sleep(3)

        # Click 发布笔记
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
        await asyncio.sleep(3)

        # Wait for the page to load
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_new_1.png")

        print(f"   URL: {page.url}")

        # Try to find upload input
        print("\n📤 Looking for upload input...")
        upload_result = await page.evaluate("""
            () => {
                // Find file inputs
                const inputs = document.querySelectorAll('input[type="file"]');
                for (const inp of inputs) {
                    if (inp.offsetParent !== null) {
                        return 'found visible file input';
                    }
                }
                // Try to trigger upload dialog
                const btn = document.querySelector('[class*="upload"], [class*="Upload"]');
                if (btn) {
                    btn.click();
                    return 'clicked upload area';
                }
                return 'no upload found';
            }
        """)
        print(f"   {upload_result}")
        await asyncio.sleep(2)

        # Check if we can set files directly
        print("\n📁 Setting files directly...")
        set_result = await page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input[type="file"]');
                for (const inp of inputs) {{
                    if (inp.offsetParent !== null) {{
                        // Try to create a file
                        const file = new File([new ArrayBuffer(1)], "{Path(image_path).name}", {{type: "image/png"}});
                        const dt = new DataTransfer();
                        dt.items.add(file);
                        inp.files = dt.files;
                        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return 'file set on input';
                    }}
                }}
                return 'no input found';
            }}
        """)
        print(f"   {set_result}")

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/xhs_new_2.png")

        # Check for title input
        print("\n🔍 Looking for title input...")
        title_result = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input');
                const results = [];
                inputs.forEach(inp => {
                    const ph = inp.getAttribute('placeholder') || '';
                    if (ph) {
                        results.push({placeholder: ph.substring(0, 30), visible: inp.offsetParent !== null});
                    }
                });
                return results;
            }
        """)
        print(f"   Inputs with placeholders: {title_result[:5]}")

        # Try to fill title
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

        # Try to fill content
        print("\n📄 Filling content...")
        content = "AI生成的这张图真的太美了！分享一下~"

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
        await page.screenshot(path="/tmp/xhs_new_3.png")

        # Click publish
        print("\n🚀 Clicking 发布...")
        pub_result = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.trim() || '';
                    if (text === '发布' && el.offsetParent !== null) {
                        el.click();
                        return '✅ Clicked';
                    }
                }
                return '❌ Not found';
            }
        """)
        print(f"   {pub_result}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_new_4.png")

        print("\n" + "=" * 50)
        print("✅ Done!")
        print("=" * 50)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(publish())
