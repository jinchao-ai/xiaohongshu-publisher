#!/usr/bin/env python3
"""
小红书自动发布 - 修复版
正确URL，自动操作
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

        # 打开正确的发布页面
        print("\n🌐 打开发布页面...")
        await page.goto("https://creator.xiaohongshu.com/publish")
        await asyncio.sleep(3)
        print("✅ 页面已打开")

        # 上传图片
        print("\n📤 上传图片...")

        # 查找文件输入框
        await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input[type="file"]');
                for (let input of inputs) {
                    if (input.offsetParent !== null) {
                        input.click();
                        return 'found upload input';
                    }
                }
                return 'not found';
            }
        """)

        await asyncio.sleep(1)

        # 填写标题
        print("\n📝 填写标题...")
        await page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input');
                for (let input of inputs) {
                    const placeholder = input.getAttribute('placeholder') || '';
                    if (placeholder.includes('标题') && input.offsetParent !== null) {
                        input.value = '被这段话治愈了✨｜自我成长';
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        return 'title filled';
                    }
                }
                return 'title not filled';
            }
        """)

        # 填写正文
        print("\n📄 填写正文...")
        await page.evaluate("""
            () => {
                const textareas = document.querySelectorAll('textarea');
                for (let textarea of textareas) {
                    const placeholder = textarea.getAttribute('placeholder') || '';
                    if ((placeholder.includes('正文') || placeholder.includes('描述')) && textarea.offsetParent !== null) {
                        textarea.value = `今天看到这句话，真的被戳中了💫

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
                        return 'content filled';
                    }
                }
                return 'content not filled';
            }
        """)

        # 点击发布按钮
        print("\n🚀 点击发布...")
        result = await page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                for (let el of elements) {
                    const text = el.textContent || '';
                    if ((text.includes('发布') || text.includes('提交')) && el.offsetParent !== null) {
                        el.click();
                        return 'clicked: ' + text.substring(0, 15);
                    }
                }
                return 'not clicked';
            }
        """)

        print(f"   {result}")

        print("\n" + "=" * 60)
        print("✅ 自动操作完成！")
        print("=" * 60)

        await asyncio.sleep(300)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
