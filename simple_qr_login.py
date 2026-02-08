#!/usr/bin/env python3
"""
简化版小红书扫码登录
直接访问首页，选择扫码登录方式
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
import tkinter as tk
from PIL import Image, ImageTk


class SimpleQRLogin:
    """简化版扫码登录"""

    def __init__(self):
        self.cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
        self.cookie_file.parent.mkdir(exist_ok=True)
        self.root = None

    def get_cookies(self) -> list:
        """获取保存的cookies"""
        try:
            if self.cookie_file.exists():
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except:
            pass
        return []

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

    async def show_qr_window(self, qr_image_path: str):
        """显示二维码窗口"""
        try:
            self.root = tk.Tk()
            self.root.title("📱 小红书扫码登录")
            self.root.geometry("350x400")
            self.root.resizable(False, False)

            # 居中
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 350) // 2
            y = (screen_height - 400) // 2
            self.root.geometry(f"350x400+{x}+{y}")

            # 标题
            tk.Label(
                self.root,
                text="请使用小红书APP扫码登录",
                font=("Microsoft YaHei", 14, "bold"),
                pady=15,
            ).pack()

            # 二维码
            img = Image.open(qr_image_path)
            img = img.resize((250, 250), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=photo, borderwidth=2, relief="solid").pack(
                pady=10
            )

            # 提示
            tk.Label(
                self.root,
                text="打开小红书 > 我的 > 右上角扫码",
                font=("Microsoft YaHei", 11),
                fg="#666666",
                pady=10,
            ).pack()

            # 状态
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
        """更新状态"""
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
            context = await browser.new_context()
            page = await context.new_page()

            # 1. 访问首页
            print("\n🌐 访问小红书首页...")
            await page.goto("https://www.xiaohongshu.com/explore")
            await asyncio.sleep(3)

            # 截图
            await page.screenshot(path="/tmp/xhs_explore_initial.png")
            print("📸 初始页面截图已保存")

            # 2. 点击"我的"标签打开登录
            print("\n👆 点击'我的'标签...")
            my_selectors = ["text=我的", 'a:has-text("我的")', '[class*="my"]']

            clicked = False
            for selector in my_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        await element.click()
                        print(f"✅ 已点击: {selector}")
                        clicked = True
                        await asyncio.sleep(2)
                        break
                except:
                    pass

            if not clicked:
                print("⚠️  未找到'我的'标签，尝试截图查看...")
                await page.screenshot(path="/tmp/xhs_no_my.png")

            await page.screenshot(path="/tmp/xhs_after_my_click.png")
            print("📸 点击后截图已保存")

            # 3. 查找登录方式（二维码/手机号）
            print("\n🔍 查找登录方式...")

            # 等待登录对话框
            await asyncio.sleep(2)

            # 查找二维码选项
            qr_selectors = [
                "text=扫码登录",
                'button:has-text("扫码")',
                '[class*="qrcode"]',
            ]

            qr_visible = False
            for selector in qr_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible():
                        print(f"✅ 找到扫码登录选项: {selector}")
                        await element.click()
                        qr_visible = True
                        await asyncio.sleep(2)
                        break
                except:
                    pass

            # 4. 查找二维码图片
            print("\n🖼️  查找二维码...")
            await asyncio.sleep(2)

            img_selectors = ['[class*="qrcode"] img', 'img[alt*="qr"]', ".qrcode-img"]

            qr_saved = False
            for selector in img_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for elem in elements:
                        if await elem.is_visible():
                            await elem.screenshot(path="/tmp/xhs_qr.png")
                            print(f"✅ 二维码已保存: /tmp/xhs_qr.png")
                            qr_saved = True
                            break
                    if qr_saved:
                        break
                except:
                    pass

            if not qr_saved:
                print("❌ 未找到二维码，截图查看...")
                await page.screenshot(path="/tmp/xhs_no_qr.png")
                return False

            # 5. 显示二维码窗口
            print("\n📱 显示二维码...")
            self.show_qr_window("/tmp/xhs_qr.png")
            print("✅ 二维码窗口已显示")

            # 6. 等待扫码
            print("\n⏳ 请使用小红书APP扫码登录（2分钟内有效）...")
            self.update_status("等待扫码...")

            # 轮询检测登录
            check_count = 0
            max_checks = 40  # 2分钟 (40 * 3秒)

            while check_count < max_checks:
                await asyncio.sleep(3)

                # 检查是否登录成功（尝试访问创作者中心）
                try:
                    await page.goto("https://creator.xiaohongshu.com")
                    await asyncio.sleep(1)

                    current_url = page.url
                    if "login" not in current_url and "creator" in current_url:
                        print("\n" + "=" * 60)
                        print("✅ 登录成功！")
                        print("=" * 60)

                        self.update_status("✅ 登录成功！", "#52C41A")

                        # 保存cookies
                        cookies = await context.cookies()
                        self.save_cookies(cookies)

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
    login = SimpleQRLogin()

    # 尝试使用已保存的cookies
    cookies = login.get_cookies()
    if cookies:
        print("\n📂 发现已保存的cookies，尝试使用...")
        # 这里可以添加加载cookies的逻辑

    # 执行扫码登录
    success = await login.login()

    if success:
        print("\n🎉 登录完成！cookies已保存。")
    else:
        print("\n❌ 登录失败")


if __name__ == "__main__":
    asyncio.run(main())
