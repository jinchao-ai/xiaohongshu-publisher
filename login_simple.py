#!/usr/bin/env python3
"""
小红书扫码登录 - 简化版
直接在浏览器中扫码，不显示额外窗口
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
                print("✅ Cookies已保存到:", self.cookie_file)
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")

    async def login(self) -> bool:
        """执行扫码登录"""
        print("\n" + "=" * 60)
        print("🚀 开始扫码登录")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            # 1. 访问首页
            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_1.png")

            # 2. 点击登录按钮
            print("\n👆 点击'登录'按钮...")
            login_clicked = await page.evaluate("""
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

            if login_clicked:
                print("✅ 已点击登录按钮")
            else:
                print("❌ 未找到登录按钮")
                await page.screenshot(path="/tmp/xhs_error.png")
                await browser.close()
                return False

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_2.png")

            # 3. 点击扫码登录
            print("\n👆 点击'扫码登录'...")
            qr_clicked = await page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {
                        if (el.textContent && el.textContent.includes('扫码登录') && el.offsetParent !== null) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }
            """)

            if qr_clicked:
                print("✅ 已点击扫码登录")
            else:
                print("⚠️  未自动点击扫码登录，请在浏览器中手动点击")

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_3.png")

            # 4. 等待用户扫码
            print("\n" + "=" * 60)
            print("📱 现在请在浏览器中完成以下操作：")
            print("   1. 点击切换到'扫码登录'（如果还没切换）")
            print("   2. 用小红书APP扫码")
            print("   3. 登录成功后浏览器会自动跳转")
            print("=" * 60)

            # 5. 等待扫码成功
            print("\n⏳ 等待扫码登录成功...")
            print("   (检测到登录成功会自动保存cookies并退出)")

            check_count = 0
            max_checks = 60  # 3分钟

            while check_count < max_checks:
                await asyncio.sleep(3)

                try:
                    # 检查是否跳转到创作者中心
                    await page.goto("https://creator.xiaohongshu.com")
                    await asyncio.sleep(1)

                    if "login" not in page.url and "creator" in page.url:
                        print("\n" + "🎉" * 20)
                        print("✅ 登录成功！")
                        print("🎉" * 20)

                        # 保存cookies
                        cookies = await context.cookies()
                        self.save_cookies(cookies)

                        await asyncio.sleep(2)
                        await browser.close()
                        return True

                except Exception as e:
                    print(f"检查错误: {e}")

                check_count += 1
                remaining = (max_checks - check_count) * 3

                if check_count % 10 == 0:
                    print(f"⏳ 等待中... ({remaining}秒后超时)")
                    await page.screenshot(path=f"/tmp/xhs_check_{check_count}.png")

            print("\n❌ 登录超时")
            await browser.close()
            return False


async def main():
    login = XiaohongshuLogin()
    success = await login.login()

    if success:
        print("\n🎉 登录成功！Cookies已保存，下次无需扫码。")
    else:
        print("\n❌ 登录失败")


if __name__ == "__main__":
    asyncio.run(main())
