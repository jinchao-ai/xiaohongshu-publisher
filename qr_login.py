#!/usr/bin/env python3
"""
小红书扫码登录 - 完整流程
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import tkinter as tk
from PIL import Image, ImageTk


class XiaohongshuQRLogin:
    """小红书扫码登录"""

    def __init__(self):
        self.cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
        self.cookie_file.parent.mkdir(exist_ok=True)
        self.root = None
        self.qr_image_path = "/tmp/xhs_qr_final.png"

    def save_cookies(self, cookies: list):
        """保存cookies"""
        try:
            if cookies:
                self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print("✅ Cookies已保存")
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")

    def show_qr_window(self, image_path: str):
        """显示二维码窗口"""
        try:
            self.root = tk.Tk()
            self.root.title("📱 小红书扫码登录")
            self.root.geometry("350x420")
            self.root.resizable(False, False)

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 350) // 2
            y = (screen_height - 420) // 2
            self.root.geometry(f"350x420+{x}+{y}")

            tk.Label(
                self.root,
                text="请使用小红书APP扫码登录",
                font=("Microsoft YaHei", 14, "bold"),
                pady=15,
            ).pack()

            img = Image.open(image_path)
            img = img.resize((280, 280), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=photo, borderwidth=2, relief="solid").pack(
                pady=10
            )

            tk.Label(
                self.root,
                text="小红书 > 我的 > 右上角扫码",
                font=("Microsoft YaHei", 11),
                fg="#666666",
                pady=10,
            ).pack()

            self.status_label = tk.Label(
                self.root,
                text="等待扫码...",
                font=("Microsoft YaHei", 10),
                fg="#1890FF",
                pady=5,
            )
            self.status_label.pack()

            def run_mainloop():
                self.root.mainloop()

            import threading

            threading.Thread(target=run_mainloop, daemon=True).start()

        except Exception as e:
            print(f"❌ 显示二维码窗口失败: {e}")

    def update_status(self, status: str, color: str = "#1890FF"):
        if self.root and self.status_label:
            self.status_label.config(text=status, fg=color)
            self.root.update()

    async def login(self) -> bool:
        """执行扫码登录"""
        print("\n" + "=" * 60)
        print("🚀 开始扫码登录流程")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            # 1. 访问首页
            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_1_home.png")

            # 2. 点击登录按钮
            print("\n👆 点击'登录'按钮...")
            login_selectors = [
                ".login-btn",
                ".reds-button-new.login-btn",
                '[class*="login-btn"]',
                "text=登录",
            ]

            login_clicked = False
            for selector in login_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        await element.click()
                        print(f"✅ 已点击登录: {selector}")
                        login_clicked = True
                        await asyncio.sleep(2)
                        break
                except:
                    pass

            if not login_clicked:
                print("❌ 未找到登录按钮")
                await page.screenshot(path="/tmp/xhs_error_login.png")
                await browser.close()
                return False

            await page.screenshot(path="/tmp/xhs_2_after_login_click.png")

            # 3. 点击"扫码登录"选项
            print("\n👆 点击'扫码登录'选项...")
            qr_selectors = [
                "text=扫码登录",
                '[class*="qrcode"]',
                '.title:has-text("扫码登录")',
            ]

            qr_clicked = False
            for selector in qr_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        await element.click()
                        print(f"✅ 已点击扫码登录: {selector}")
                        qr_clicked = True
                        await asyncio.sleep(2)
                        break
                except:
                    pass

            # 如果自动点击失败，提示用户
            if not qr_clicked:
                print("⚠️  自动点击扫码登录失败")
                await page.screenshot(path="/tmp/xhs_3_select_type.png")
                print("\n💡 请在浏览器中手动点击'扫码登录'选项")
                print("   看到二维码后告诉我")

                # 等待用户确认
                input("\n👆 按Enter继续（确保已看到二维码）...")

            await page.screenshot(path="/tmp/xhs_4_qr_shown.png")

            # 4. 查找并保存二维码
            print("\n🖼️  查找二维码...")
            await asyncio.sleep(2)

            img_selectors = ['[class*="qrcode"] img', ".qrcode-img", 'img[alt*="qr"]']

            qr_saved = False
            for selector in img_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        if await elem.is_visible():
                            await elem.screenshot(path=self.qr_image_path)
                            print(f"✅ 二维码已保存: {self.qr_image_path}")
                            qr_saved = True
                            break
                    if qr_saved:
                        break
                except:
                    pass

            if not qr_saved:
                print("⚠️  未找到二维码，截图查看...")
                await page.screenshot(path="/tmp/xhs_no_qr.png")
                return False

            # 5. 显示二维码窗口
            print("\n📱 显示二维码窗口...")
            self.show_qr_window(self.qr_image_path)
            self.update_status("等待扫码...")

            # 6. 等待扫码
            print("\n⏳ 请使用小红书APP扫码登录...")
            print("   二维码有效期2分钟")

            # 轮询检测登录
            check_count = 0
            max_checks = 40

            while check_count < max_checks:
                await asyncio.sleep(3)

                try:
                    # 检测登录成功
                    await page.goto("https://creator.xiaohongshu.com")
                    await asyncio.sleep(1)

                    if "login" not in page.url and "creator" in page.url:
                        print("\n" + "=" * 60)
                        print("✅ 登录成功！")
                        print("=" * 60)

                        self.update_status("✅ 登录成功！", "#52C41A")

                        # 保存cookies
                        cookies = await context.cookies()
                        self.save_cookies(cookies)

                        await asyncio.sleep(2)
                        await browser.close()
                        return True

                except:
                    pass

                check_count += 1
                remaining = (max_checks - check_count) * 3
                if check_count % 5 == 0:
                    print(f"⏳ 等待扫码... ({remaining}秒后超时)")
                    self.update_status(f"等待扫码... {remaining}秒")

            print("\n❌ 登录超时")
            self.update_status("❌ 二维码已过期", "#FF4D4F")
            await browser.close()
            return False


async def main():
    login = XiaohongshuQRLogin()
    success = await login.login()

    if success:
        print("\n🎉 登录完成！")
    else:
        print("\n❌ 登录失败")


if __name__ == "__main__":
    asyncio.run(main())
