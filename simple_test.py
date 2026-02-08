#!/usr/bin/env python3
"""
简单的小红书登录测试 - 打开页面后保持打开状态
"""

import asyncio
from playwright.async_api import async_playwright


async def main():
    print("=" * 60)
    print("🚀 小红书登录测试")
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

        await page.goto(url, timeout=30000)

        print(f"✅ 页面加载成功")
        print(f"📝 当前URL: {page.url}")
        print(f"📝 页面标题: {await page.title()}")

        # 截图
        await page.screenshot(path="/tmp/xhs_login_current.png")
        print(f"📸 截图已保存: /tmp/xhs_login_current.png")

        print("\n" + "=" * 60)
        print("💡 现在请在浏览器中操作：")
        print("   1. 点击右上角「登 录」按钮")
        print("   2. 选择「扫码登录」")
        print("   3. 用小红书APP扫码")
        print("   4. 登录成功后告诉我")
        print("=" * 60)

        print("\n⏳ 浏览器保持打开状态...")
        print("   按 Ctrl+C 退出")

        # 保持运行
        try:
            while True:
                await asyncio.sleep(10)
                # 检查是否登录成功
                current_url = page.url
                if "login" not in current_url and "creator" in current_url:
                    print(f"\n✅ 检测到已登录! URL: {current_url}")
        except KeyboardInterrupt:
            print("\n\n👋 用户退出")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试结束")
