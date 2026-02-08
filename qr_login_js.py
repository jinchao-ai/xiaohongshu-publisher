#!/usr/bin/env python3
"""
小红书扫码登录 - JavaScript点击版
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import tkinter as tk
from PIL import Image, ImageTk


class XiaohongshuQRLogin:
    def __init__(self):
        self.cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
        self.cookie_file.parent.mkdir(exist_ok=True)
        self.root = None
        self.qr_image_path = "/tmp/xhs_qr_final.png"

    def save_cookies(self, cookies: list):
        try:
            if cookies:
                self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print("✅ Cookies已保存")
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")

    def show_qr_window(self, image_path: str):
        try:
            self.root = tk.Tk()
            self.root.title("📱 小红书扫码登录")
            self.root.geometry("350x420")

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
        print("\n" + "=" * 60)
        print("🚀 开始扫码登录流程")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await context.new_page()

            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_1.png")

            print("\n👆 点击'登录'按钮...")

            # 使用JavaScript点击登录按钮
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
                print("✅ 已点击登录按钮（JavaScript）")
            else:
                print("❌ 未找到登录按钮")
                await page.screenshot(path="/tmp/xhs_error.png")
                await browser.close()
                return False

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_2.png")

            print("\n👆 点击'扫码登录'选项...")

            # 使用JavaScript点击扫码登录
            await asyncio.sleep(1)

            qr_clicked = await page.evaluate("""
                () => {
                    // 查找包含"扫码登录"的元素
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

            if not qr_clicked:
                print("⚠️  自动点击扫码登录失败，请手动点击")
            else:
                print("✅ 已点击扫码登录选项（JavaScript）")

            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/xhs_3.png")

            print("\n🖼️  查找二维码...")
            await asyncio.sleep(2)

            # 查找二维码图片
            qr_saved = await page.evaluate("""
                () => {
                    const images = document.querySelectorAll('img');
                    for (let img of images) {
                        if (img.offsetParent !== null && img.src && img.src.includes('data:image')) {
                            // 找到base64图片，保存
                            return img.src;
                        }
                    }
                    return null;
                }
            """)

            if qr_saved:
                # 保存base64图片
                import base64

                header, encoded = qr_saved.split(",", 1)
                data = base64.b64decode(encoded)
                with open(self.qr_image_path, "wb") as f:
                    f.write(data)
                print(f"✅ 二维码已保存: {self.qr_image_path}")
            else:
                print("❌ 未找到二维码")
                await page.screenshot(path="/tmp/xhs_no_qr.png")
                return False

            # 5. 显示二维码窗口
            print("\n📱 显示二维码窗口...")
            self.show_qr_window(self.qr_image_path)
            self.update_status("等待扫码...")

            # 6. 等待扫码
            print("\n⏳ 请使用小红书APP扫码登录（2分钟内有效）...")

            check_count = 0
            max_checks = 40

            while check_count < max_checks:
                await asyncio.sleep(3)

                try:
                    await page.goto("https://creator.xiaohongshu.com")
                    await asyncio.sleep(1)

                    if "login" not in page.url and "creator" in page.url:
                        print("\n" + "=" * 60)
                        print("✅ 登录成功！")
                        print("=" * 60)
                        self.update_status("✅ 登录成功！", "#52C41A")

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
        print("\n🎉 登录成功！Cookies已保存。")
    else:
        print("\n❌ 登录失败")


if __name__ == "__main__":
    asyncio.run(main())
