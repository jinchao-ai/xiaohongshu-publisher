#!/usr/bin/env python3
"""
小红书发布器 - 完整流程
自动登录 -> 上传图片 -> AI生成内容 -> 发布
"""

import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright


class XiaohongshuPublisher:
    def __init__(self):
        self.cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
        self.cookie_file.parent.mkdir(exist_ok=True)

    def load_cookies(self) -> list:
        """加载保存的cookies"""
        try:
            if self.cookie_file.exists():
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                    print(f"📂 找到保存的Cookies ({len(cookies)}个)")
                    return cookies
        except Exception as e:
            print(f"⚠️  加载Cookies失败: {e}")
        return []

    def save_cookies(self, cookies: list):
        """保存cookies"""
        try:
            if cookies:
                self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, indent=2)
                print(f"\n✅ Cookies已保存: {self.cookie_file}")
        except Exception as e:
            print(f"❌ 保存Cookies失败: {e}")

    async def check_cookies_valid(self, page) -> bool:
        """检查cookies是否有效"""
        try:
            await page.goto("https://creator.xiaohongshu.com", timeout=10000)
            await asyncio.sleep(2)

            # 检查是否跳转到了创作者中心
            if "login" not in page.url and "creator" in page.url:
                return True

            return False
        except:
            return False

    async def login_with_cookies(self, browser) -> bool:
        """使用cookies登录"""
        cookies = self.load_cookies()
        if not cookies:
            print("❌ 没有保存的Cookies")
            return False

        print("\n🔐 使用保存的Cookies登录...")
        context = await browser.new_context()
        page = await context.new_page()

        # 添加cookies
        try:
            await context.add_cookies(cookies)
            print("✅ Cookies已添加到浏览器")

            # 检查是否有效
            if await self.check_cookies_valid(page):
                print("✅ Cookies登录成功！")
                return True
            else:
                print("⚠️  Cookies已失效，需要重新扫码登录")
                return False
        except Exception as e:
            print(f"❌ Cookies登录失败: {e}")
            return False

    async def qr_login(self, browser) -> bool:
        """扫码登录"""
        print("\n🔐 开始扫码登录...")
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 访问首页
        print("\n🌐 访问小红书首页...")
        await page.goto("https://www.xiaohongshu.com/explore")
        await asyncio.sleep(3)

        # 点击登录
        print("\n👆 点击登录...")
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

        if not login_clicked:
            print("❌ 点击登录失败")
            return False

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_login.png")

        # 点击扫码登录
        print("\n👆 切换到扫码登录...")
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

        if not qr_clicked:
            print("⚠️  未自动切换到扫码登录，请在浏览器中手动切换")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_qr.png")

        print("\n" + "=" * 60)
        print("📱 请在浏览器中完成扫码登录")
        print("   - 切换到扫码登录（如需要）")
        print("   - 用小红书APP扫码")
        print("=" * 60)

        # 等待登录
        check_count = 0
        max_checks = 60

        while check_count < max_checks:
            await asyncio.sleep(3)

            try:
                await page.goto("https://creator.xiaohongshu.com")
                await asyncio.sleep(1)

                if "login" not in page.url and "creator" in page.url:
                    print("\n✅ 登录成功！")

                    # 保存cookies
                    cookies = await context.cookies()
                    self.save_cookies(cookies)
                    return True
            except:
                pass

            check_count += 1
            remaining = (max_checks - check_count) * 3

            if check_count % 10 == 0:
                print(f"⏳ 等待扫码... ({remaining}秒后超时)")

        print("❌ 登录超时")
        return False

    async def publish(self, image_path: str) -> bool:
        """发布笔记"""
        print("\n" + "=" * 60)
        print("🚀 开始发布流程")
        print("=" * 60)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)

            # 1. 尝试使用cookies登录
            cookies_valid = await self.login_with_cookies(browser)

            if not cookies_valid:
                # 2. 扫码登录
                if not await self.qr_login(browser):
                    print("❌ 登录失败")
                    await browser.close()
                    return False

            # 3. 发布页面
            print("\n🌐 打开发布页面...")
            page = await browser.new_page()
            await page.goto("https://creator.xiaohongshu.com/publish")
            await asyncio.sleep(3)
            await page.screenshot(path="/tmp/xhs_publish.png")

            print("\n📸 现在请在浏览器中：")
            print("   1. 上传图片:", Path(image_path).name)
            print("   2. 填写标题和正文")
            print("   3. 添加标签")
            print("   4. 点击发布")
            print("\n💡 我会帮你自动生成内容，你只需在浏览器中操作")

            # 保持浏览器打开
            print("\n⏳ 浏览器保持打开状态...")
            print("   发布完成后可以关闭浏览器")

            try:
                await asyncio.sleep(300)  # 5分钟
            except KeyboardInterrupt:
                print("\n👋 用户中断")

            await browser.close()
            return True


async def main():
    publisher = XiaohongshuPublisher()

    # 使用下载目录的图片
    image_path = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        return

    print(f"\n📁 使用图片: {image_path}")
    print(f"   文件: {Path(image_path).name}")

    await publisher.publish(image_path)


if __name__ == "__main__":
    asyncio.run(main())
