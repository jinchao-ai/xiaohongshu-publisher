#!/usr/bin/env python3
"""
小红书发布 - 登录并发布
先扫码登录保存cookies，然后跳转到发布页面
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    print("\n" + "=" * 60)
    print("🚀 小红书登录并发布")
    print("=" * 60)

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"
    cookie_file.parent.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 1. 访问首页并登录
        print("\n🌐 访问小红书首页...")
        await page.goto("https://www.xiaohongshu.com/explore")
        await asyncio.sleep(3)

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

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_step1.png")

        print("\n👆 点击扫码登录...")
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

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/xhs_step2.png")

        print("\n" + "=" * 60)
        print("📱 请在浏览器中：")
        print("   1. 确保已切换到'扫码登录'")
        print("   2. 用小红书APP扫码登录")
        print("   3. 登录成功后会自动保存cookies")
        print("=" * 60)

        # 等待登录
        print("\n⏳ 等待扫码登录...")
        check_count = 0
        max_checks = 40

        while check_count < max_checks:
            await asyncio.sleep(3)

            try:
                await page.goto("https://creator.xiaohongshu.com")
                await asyncio.sleep(1)

                if "login" not in page.url and "creator" in page.url:
                    print("\n✅ 登录成功！")

                    # 保存cookies
                    cookies = await context.cookies()
                    with open(cookie_file, "w") as f:
                        json.dump(cookies, f, indent=2)
                    print(f"\n💾 Cookies已保存: {cookie_file}")

                    # 跳转到发布页面
                    print("\n🌐 跳转发布页面...")
                    await page.goto("https://creator.xiaohongshu.com/publish")
                    await asyncio.sleep(3)
                    await page.screenshot(path="/tmp/xhs_publish.png")

                    print("\n" + "=" * 60)
                    print("🎉 现在可以在浏览器中发布笔记了！")
                    print("   - 上传图片")
                    print("   - 填写内容")
                    print("   - 点击发布")
                    print("=" * 60)

                    # 保持打开
                    await asyncio.sleep(600)
                    await browser.close()
                    return
            except Exception as e:
                print(f"错误: {e}")

            check_count += 1
            remaining = (max_checks - check_count) * 3

            if check_count % 10 == 0:
                print(f"⏳ 等待扫码... ({remaining}秒后超时)")

        print("\n❌ 登录超时")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
