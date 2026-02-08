#!/usr/bin/env python3
"""
小红书扫码登录 - 检测版
引导用户手动操作，自动检测登录成功
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


class XiaohongshuLogin:
    def __init__(self):
        self.cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
        self.cookie_file.parent.mkdir(exist_ok=True)

    def save_cookies(self, cookies: list):
        try:
            if cookies:
                self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print("\n✅ Cookies已保存:", self.cookie_file)
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")

    async def check_login_success(self, page) -> bool:
        """检查是否登录成功"""
        try:
            # 访问创作者中心
            await page.goto("https://creator.xiaohongshu.com", timeout=10000)
            await asyncio.sleep(2)

            # 检查URL
            if "login" not in page.url and "creator" in page.url:
                return True

            # 检查页面内容
            content = await page.content()
            if "我的" in content or "创作" in content:
                # 检查是否有用户信息
                user_elements = await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('我的') && el.offsetParent !== null) {
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                if user_elements:
                    return True

            return False
        except:
            return False

    async def login(self) -> bool:
        """执行扫码登录"""
        print("\n" + "=" * 60)
        print("🚀 小红书扫码登录")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            # 1. 访问首页
            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_login_1.png")

            # 2. 点击登录
            print("\n👆 请在浏览器中点击右上角'登录'按钮")

            # 等待用户点击登录
            input("\n👆 点击登录按钮后按Enter继续...")

            await page.screenshot(path="/tmp/xhs_login_2.png")

            # 3. 提示选择扫码登录
            print("\n📱 请在浏览器登录框中点击'扫码登录'选项切换到二维码模式")
            print("   （如果已经显示二维码则跳过此步）")

            input("👆 切换到扫码登录后按Enter继续...")

            await asyncio.sleep(1)
            await page.screenshot(path="/tmp/xhs_login_3.png")

            # 4. 等待扫码
            print("\n" + "=" * 60)
            print("📱 现在请用小红书APP扫码登录")
            print("   - 打开小红书APP")
            print("   - 点击我的 > 右上角扫码")
            print("   - 对准电脑屏幕扫码")
            print("=" * 60)

            # 检测扫码成功
            print("\n🔍 自动检测登录状态...")
            check_count = 0
            max_checks = 60  # 3分钟

            while check_count < max_checks:
                await asyncio.sleep(3)

                if await self.check_login_success(page):
                    print("\n" + "🎉" * 20)
                    print("✅ 检测到登录成功！")
                    print("🎉" * 20)

                    # 保存cookies
                    cookies = await context.cookies()
                    self.save_cookies(cookies)

                    await asyncio.sleep(2)
                    await browser.close()
                    return True

                check_count += 1
                remaining = (max_checks - check_count) * 3

                if check_count % 10 == 0:
                    print(f"⏳ 等待扫码中... ({remaining}秒后超时)")
                    await page.screenshot(path=f"/tmp/xhs_check_{check_count}.png")

            print("\n❌ 登录超时")
            await browser.close()
            return False


async def main():
    login = XiaohongshuLogin()
    success = await login.login()

    if success:
        print("\n🎉 登录成功！")
        print("💡 Cookies已保存，下次运行无需重新扫码")
    else:
        print("\n❌ 登录失败，请重试")


if __name__ == "__main__":
    asyncio.run(main())
