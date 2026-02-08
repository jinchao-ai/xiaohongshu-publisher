#!/usr/bin/env python3
"""
小红书扫码登录 - 全自动版
自动点击，自动检测登录成功
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
            await page.goto("https://creator.xiaohongshu.com", timeout=10000)
            await asyncio.sleep(2)

            if "login" not in page.url and "creator" in page.url:
                return True

            return False
        except:
            return False

    async def try_click_login(self, page) -> bool:
        """尝试自动点击登录"""
        # 点击登录按钮
        clicked = await page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes('登录') && btn.offsetParent !== null) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        return clicked

    async def try_click_qr(self, page) -> bool:
        """尝试点击扫码登录"""
        # 查找并点击扫码登录
        clicked = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (let el of elements) {
                    if (el.textContent && 
                        el.textContent.includes('扫码登录') && 
                        el.offsetParent !== null) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        return clicked

    async def find_qr_code(self, page) -> bool:
        """查找二维码"""
        found = await page.evaluate("""
            () => {
                const images = document.querySelectorAll('img');
                for (let img of images) {
                    if (img.offsetParent !== null && img.src && img.src.includes('data:image')) {
                        return true;
                    }
                }
                return false;
            }
        """)
        return found

    async def login(self) -> bool:
        """执行扫码登录"""
        print("\n" + "=" * 60)
        print("🚀 小红书扫码登录（自动版）")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            # 1. 访问首页
            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_auto_1.png")

            # 2. 点击登录
            print("\n👆 自动点击登录...")
            if await self.try_click_login(page):
                print("✅ 已点击登录按钮")
            else:
                print("❌ 点击登录失败，请手动操作")
                await page.screenshot(path="/tmp/xhs_login_error.png")
                return False

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_auto_2.png")

            # 3. 点击扫码登录
            print("\n👆 自动切换到扫码登录...")
            if await self.try_click_qr(page):
                print("✅ 已切换到扫码登录")
            else:
                print("⚠️  自动切换失败，请手动切换")
                print("💡 请在浏览器中点击'扫码登录'选项")

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_auto_3.png")

            # 4. 检查是否显示二维码
            print("\n🖼️ 检查二维码...")
            qr_found = await self.find_qr_code(page)

            if qr_found:
                print("✅ 已显示二维码")
            else:
                print("⚠️  未检测到二维码，请确认已切换到扫码登录模式")
                print("💡 请在浏览器中完成扫码登录")

            await page.screenshot(path="/tmp/xhs_auto_qr.png")

            # 5. 等待扫码
            print("\n" + "=" * 60)
            print("📱 请用小红书APP扫码登录")
            print("   (检测到登录成功会自动保存Cookies)")
            print("=" * 60)

            # 等待扫码成功
            check_count = 0
            max_checks = 60  # 3分钟

            while check_count < max_checks:
                await asyncio.sleep(3)

                if await self.check_login_success(page):
                    print("\n" + "🎉" * 20)
                    print("✅ 检测到登录成功！")
                    print("🎉" * 20)

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
        print("💡 Cookies已保存，下次无需扫码")
    else:
        print("\n❌ 登录失败，请重试")


if __name__ == "__main__":
    asyncio.run(main())
