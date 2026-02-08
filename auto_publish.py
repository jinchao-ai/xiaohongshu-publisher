#!/usr/bin/env python3
"""
小红书自动发布 - 上传图片、填写内容、点击发布
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright


async def main():
    print("\n" + "=" * 60)
    print("🚀 小红书自动发布")
    print("=" * 60)

    cookie_file = Path.home() / ".xiaohongshu_publisher" / "cookies.json"

    # 图片路径
    image_path = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        return

    print(f"\n📁 使用图片: {Path(image_path).name}")

    async with async_playwright() as p:
        # 启动浏览器并加载cookies
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 加载cookies
        if cookie_file.exists():
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✅ Cookies已加载")
        else:
            print("⚠️  未找到Cookies")

        # 打开发布页面
        print("\n🌐 打开发布页面...")
        await page.goto("https://creator.xiaohongshu.com/publish")
        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/publish_1.png")
        print("✅ 页面已打开")

        # 1. 上传图片
        print("\n📤 上传图片...")
        await page.screenshot(path="/tmp/publish_2.png")

        # 尝试查找文件上传输入框
        upload_success = await page.evaluate("""
            () => {
                // 查找文件上传输入框
                const inputs = document.querySelectorAll('input[type="file"]');
                for (let input of inputs) {
                    if (input.offsetParent !== null) {
                        return 'input[type="file"] found';
                    }
                }
                // 查找上传区域
                const uploads = document.querySelectorAll('[class*="upload"]');
                for (let el of uploads) {
                    if (el.offsetParent !== null) {
                        return 'upload area found';
                    }
                }
                return 'not found';
            }
        """)

        print(f"   上传元素检测: {upload_success}")

        # 尝试点击上传区域
        click_upload = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (let el of elements) {
                    if (el.textContent && el.textContent.includes('上传') && el.offsetParent !== null) {
                        el.click();
                        return 'clicked upload';
                    }
                }
                return 'not clicked';
            }
        """)

        print(f"   点击上传: {click_upload}")

        await asyncio.sleep(2)
        await page.screenshot(path="/tmp/publish_3.png")

        # 2. 填写标题
        print("\n📝 填写标题...")

        # 查找标题输入框
        title_filled = await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input');
                for (let input of inputs) {
                    const placeholder = input.getAttribute('placeholder') || '';
                    if ((placeholder.includes('标题') || placeholder.includes('title')) && input.offsetParent !== null) {
                        input.value = '被这段话治愈了✨｜自我成长';
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        return 'title filled';
                    }
                }
                return 'title not filled';
            }
        """)

        print(f"   填写标题: {title_filled}")

        # 3. 填写正文
        print("\n📄 填写正文...")

        # 查找正文编辑框
        content_filled = await page.evaluate("""
            () => {
                const textareas = document.querySelectorAll('textarea');
                for (let textarea of textareas) {
                    const placeholder = textarea.getAttribute('placeholder') || '';
                    if ((placeholder.includes('正文') || placeholder.includes('内容') || placeholder.includes('描述')) && textarea.offsetParent !== null) {
                        textarea.value = `今天看到这句话，真的被戳中了💫

允许我分享这段很有力量的话🙏

自我成长这件事，真的需要慢慢来。

不必急于求成，也不必与他人比较。
每个人的花期不同，不必焦虑有人提前盛开。

记住：
- 你的努力，时间看得见
- 自律给你自由
- 慢慢来，比较快

愿你在自我成长的路上，永远保持热爱和勇气。💪

#自我成长 #治愈 #正能量`;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        textarea.dispatchEvent(new Event('change', { bubbles: true }));
                        return 'content filled';
                    }
                }
                return 'content not filled';
            }
        """)

        print(f"   填写正文: {content_filled}")

        await asyncio.sleep(1)
        await page.screenshot(path="/tmp/publish_4.png")

        # 4. 点击发布
        print("\n🚀 点击发布...")

        publish_clicked = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (let el of elements) {
                    const text = el.textContent || '';
                    if ((text.includes('发布') || text.includes('提交') || text.includes('完成')) && el.offsetParent !== null) {
                        el.click();
                        return 'clicked publish: ' + text.substring(0, 20);
                    }
                }
                return 'publish not clicked';
            }
        """)

        print(f"   点击发布: {publish_clicked}")

        await asyncio.sleep(3)
        await page.screenshot(path="/tmp/publish_5.png")

        print("\n" + "=" * 60)
        print("✅ 自动操作完成！")
        print("=" * 60)

        print("\n💡 请在浏览器中确认：")
        print("   - 图片是否上传成功")
        print("   - 标题和正文是否填写正确")
        print("   - 点击最终发布按钮")

        await asyncio.sleep(300)  # 保持5分钟
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
