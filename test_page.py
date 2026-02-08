#!/usr/bin/env python3
"""
测试小红书登录页面加载
"""

import asyncio
from playwright.async_api import async_playwright


async def test_login_page():
    print("=" * 60)
    print("🧪 测试小红书登录页面加载")
    print("=" * 60)

    async with async_playwright() as p:
        # 启动浏览器
        print("\n🚀 启动浏览器...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 访问登录页面
        url = "https://creator.xiaohongshu.com/login"
        print(f"\n🌐 正在访问: {url}")

        try:
            await page.goto(url, timeout=30000)
            print(f"✅ 页面加载成功")
            print(f"📝 当前URL: {page.url}")
            print(f"📝 页面标题: {await page.title()}")
        except Exception as e:
            print(f"❌ 页面加载失败: {e}")
            return

        # 等待页面加载
        print("\n⏳ 等待页面完全加载...")
        await asyncio.sleep(5)

        # 截图
        screenshot_path = "/tmp/xhs_test_login.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 截图已保存: {screenshot_path}")

        # 检查页面内容
        print("\n🔍 页面内容检查:")
        print(f"  - 页面包含文本: {await page.text_content('body')[:200]}...")

        # 查找所有按钮
        print("\n🔘 页面上的按钮:")
        buttons = await page.query_selector_all("button")
        for i, btn in enumerate(buttons[:5]):
            text = await btn.text_content()
            visible = await btn.is_visible()
            print(f"  {i + 1}. '{text}' (可见: {visible})")

        # 查找登录相关元素
        print("\n🔍 查找登录相关元素:")
        login_texts = ["登录", "login", "qrcode", "扫码"]
        for text in login_texts:
            elements = await page.query_selector_all(f"text={text}")
            if elements:
                print(f"  ✅ 找到包含 '{text}' 的元素: {len(elements)} 个")

        print("\n" + "=" * 60)
        print("💡 请查看截图确认页面是否正常加载")
        print("=" * 60)

        # 保持浏览器打开
        print("\n⏳ 浏览器保持打开 60秒...")
        await asyncio.sleep(60)

        await browser.close()
        print("✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_login_page())
