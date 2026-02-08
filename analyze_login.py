#!/usr/bin/env python3
"""
分析小红书登录页面结构，找到切换二维码的方式
"""

import asyncio
from playwright.async_api import async_playwright


async def analyze_login_page():
    print("=" * 60)
    print("🔍 分析小红书登录页面结构")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 访问登录页面
        print("\n🌐 访问登录页面...")
        await page.goto("https://creator.xiaohongshu.com/login")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        # 截图
        await page.screenshot(path="/tmp/analyze_login.png")
        print("📸 截图已保存: /tmp/analyze_login.png")

        # 分析页面元素
        print("\n🔍 分析页面元素...")

        # 1. 查找所有按钮
        print("\n🔘 所有按钮:")
        buttons = await page.query_selector_all("button")
        for i, btn in enumerate(buttons[:10]):
            try:
                text = await btn.text_content()
                classes = await btn.get_attribute("class")
                visible = await btn.is_visible()
                role = await btn.get_attribute("role")
                print(
                    f"  {i + 1}. text='{text}' class='{classes}' visible={visible} role={role}"
                )
            except:
                pass

        # 2. 查找所有链接
        print("\n🔗 所有链接:")
        links = await page.query_selector_all("a")
        for i, link in enumerate(links[:10]):
            try:
                text = await link.text_content()
                href = await link.get_attribute("href")
                visible = await link.is_visible()
                print(f"  {i + 1}. text='{text}' href='{href}' visible={visible}")
            except:
                pass

        # 3. 查找图片（二维码）
        print("\n🖼️  所有图片:")
        images = await page.query_selector_all("img")
        for i, img in enumerate(images[:10]):
            try:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt")
                visible = await img.is_visible()
                width = await img.get_attribute("width")
                height = await img.get_attribute("height")
                print(f"  {i + 1}. src={src[:50] if src else 'N/A'}...")
                print(f"      alt={alt} visible={visible} size={width}x{height}")
            except:
                pass

        # 4. 查找表单元素
        print("\n📝 表单元素:")
        inputs = await page.query_selector_all("input")
        for i, inp in enumerate(inputs[:10]):
            try:
                type_attr = await inp.get_attribute("type")
                placeholder = await inp.get_attribute("placeholder")
                visible = await inp.is_visible()
                name = await inp.get_attribute("name")
                print(
                    f"  {i + 1}. type={type_attr} placeholder='{placeholder}' name={name} visible={visible}"
                )
            except:
                pass

        # 5. 查找包含特定文本的元素
        print("\n🔍 查找包含文本的元素:")
        texts_to_find = ["扫码", "登录", "手机", "验证码", "切换"]

        for text in texts_to_find:
            # 使用JavaScript查找包含特定文本的元素
            elements = await page.evaluate(f"""
                () => {{
                    const all = document.querySelectorAll('*');
                    const found = [];
                    for (let el of all) {{
                        if (el.textContent && el.textContent.includes('{text}') && el.offsetParent !== null) {{
                            found.push({{
                                tag: el.tagName,
                                class: el.className,
                                text: el.textContent.substring(0, 30)
                            }});
                        }}
                    }}
                    return found.slice(0, 3);
                }}
            """)

            if elements:
                print(f"\n包含 '{text}' 的元素:")
                for el in elements:
                    print(
                        f"  - <{el['tag']}> class='{el['class']}' text='{el['text']}'"
                    )

        # 6. 查找可点击的div/span
        print("\n👆 可点击的div/span:")
        clickables = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('div, span, li');
                const found = [];
                for (let el of all) {
                    if (el.offsetParent !== null &&
                        (el.onclick || el.click || getComputedStyle(el).cursor === 'pointer')) {
                        found.push({
                            tag: el.tagName,
                            class: el.className.substring(0, 100),
                            text: el.textContent.substring(0, 50)
                        });
                    }
                }
                return found.slice(0, 10);
            }
        """)

        for el in clickables:
            print(f"  - <{el['tag']}> class='{el['class']}' text='{el['text']}'")

        print("\n" + "=" * 60)
        print("💡 分析完成，请查看截图")
        print("=" * 60)

        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(analyze_login_page())
