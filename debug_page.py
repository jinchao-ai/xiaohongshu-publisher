#!/usr/bin/env python3
"""
调试工具：查看小红书登录页面结构
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_page():
    """调试登录页面"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("🌐 正在打开登录页面...")
        await page.goto("https://creator.xiaohongshu.com/login")
        await page.wait_for_load_state("networkidle")

        # 等待页面加载
        await asyncio.sleep(3)

        # 截图
        await page.screenshot(path="/tmp/xhs_login_page.png")
        print("📸 截图已保存: /tmp/xhs_login_page.png")

        # 打印页面标题
        print(f"📝 页面标题: {await page.title()}")

        # 打印所有可见的按钮和链接
        print("\n🔍 页面上的按钮和链接:")
        buttons = await page.query_selector_all(
            "button, a, [role='button'], .el-button"
        )
        for i, btn in enumerate(buttons[:20]):
            try:
                text = await btn.text_content()
                classes = await btn.get_attribute("class")
                visible = await btn.is_visible()
                if visible:
                    print(
                        f"  {i + 1}. {text[:30] if text else 'No text'} (class: {classes[:50] if classes else 'N/A'})"
                    )
            except:
                pass

        # 打印所有图片
        print("\n🖼️  页面上的图片:")
        images = await page.query_selector_all("img")
        for i, img in enumerate(images[:10]):
            try:
                src = await img.get_attribute("src")
                alt = await img.get_attribute("alt")
                visible = await img.is_visible()
                if visible:
                    print(f"  {i + 1}. src: {src[:50] if src else 'N/A'}... alt: {alt}")
            except:
                pass

        # 打印所有输入框
        print("\n📝 页面上的输入框:")
        inputs = await page.query_selector_all("input")
        for i, inp in enumerate(inputs[:10]):
            try:
                type_attr = await inp.get_attribute("type")
                placeholder = await inp.get_attribute("placeholder")
                visible = await inp.is_visible()
                if visible:
                    print(f"  {i + 1}. type: {type_attr}, placeholder: {placeholder}")
            except:
                pass

        # 打印页面HTML结构（简化版）
        print("\n📄 页面HTML结构（部分）:")
        html = await page.content()
        # 只打印前2000个字符
        print(html[:2000])

        print("\n" + "=" * 50)
        print("💡 请查看截图 /tmp/xhs_login_page.png")
        print("=" * 50)

        # 保持打开
        await asyncio.sleep(30)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(debug_page())
