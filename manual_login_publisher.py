#!/usr/bin/env python3
"""
小红书发布器 - 先手动登录，再自动发布
适合首次使用或Cookie失效时
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts import XiaohongshuPublisher
from scripts.core.login_handler import LoginHandler


async def publish_with_manual_login(image_path: str):
    """先手动登录，然后自动发布"""

    publisher = XiaohongshuPublisher()

    print("\n" + "=" * 60)
    print("🚀 小红书发布器（先登录后发布）")
    print("=" * 60)

    # 1. 初始化浏览器
    print("\n📦 步骤1: 初始化浏览器...")
    if not await publisher.initialize():
        print("❌ 浏览器初始化失败")
        return

    # 2. 导航到登录页面
    print("\n🌐 步骤2: 打开发登录页面...")
    await publisher.browser.navigate("https://creator.xiaohongshu.com/login")
    await asyncio.sleep(3)

    print("\n" + "=" * 60)
    print("💡 请在浏览器中手动完成以下操作：")
    print("   1. 点击右上角「登 录」按钮")
    print("   2. 选择「扫码登录」")
    print("   3. 用小红书APP扫码")
    print("   4. 登录成功后告诉我")
    print("=" * 60)

    # 3. 等待用户确认登录成功
    while True:
        user_input = (
            input("\n👆 请输入 'y' 表示已登录成功，或 's' 查看当前页面状态: ")
            .strip()
            .lower()
        )

        if user_input == "s":
            # 查看当前页面状态
            current_url = await publisher.browser.page.url()
            page_title = await publisher.browser.page.title()
            print(f"   当前URL: {current_url}")
            print(f"   页面标题: {page_title}")

            # 截图
            await publisher.browser.screenshot(path="/tmp/xhs_current_status.png")
            print(f"📸 截图已保存: /tmp/xhs_current_status.png")
            continue

        elif user_input == "y":
            # 检查是否真的登录成功
            print("\n🔍 检查登录状态...")
            await asyncio.sleep(2)

            # 尝试访问创作者中心首页
            await publisher.browser.navigate("https://creator.xiaohongshu.com")
            await asyncio.sleep(2)

            current_url = await publisher.browser.page.url()
            if "login" not in current_url:
                print(f"✅ 检测到已登录! (URL: {current_url})")

                # 保存cookies
                print("\n💾 正在保存登录状态...")
                await publisher.login_handler.save_browser_cookies()
                print("✅ 登录状态已保存，下次无需扫码")

                break
            else:
                print("⚠️  检测到仍在登录页面，请确认已成功扫码")
                continue
        else:
            print("   无效输入，请输入 'y' 或 's'")

    # 4. 生成内容
    print("\n📝 步骤3: AI生成内容...")
    content = publisher.content_generator.generate_full_content(image_path)
    print(publisher.content_generator.preview_content(content))

    # 5. 确认发布
    print("\n" + "=" * 60)
    confirm = input("以上内容是否满意？(y/n/q=退出): ").strip().lower()

    if confirm == "q":
        print("👋 已取消发布")
        await publisher.browser.close()
        return

    if confirm != "y":
        print("⚠️  内容未确认，请在浏览器中手动编辑...")
        input("编辑完成后按Enter继续...")

    # 6. 导航到发布页面
    print("\n🌐 步骤4: 打开发布页面...")
    await publisher.browser.navigate("https://creator.xiaohongshu.com/publish")
    await asyncio.sleep(3)

    # 7. 上传图片
    print(f"\n📤 步骤5: 上传图片...")
    print(f"   图片路径: {image_path}")
    print("   💡 请在浏览器中上传图片，或按Enter自动尝试...")

    input("   按Enter继续，或直接在浏览器中操作...")

    # 尝试自动上传
    upload_success = await publisher._upload_image(image_path)
    if not upload_success:
        print("   ⚠️  自动上传失败，请手动上传")

    await asyncio.sleep(3)

    # 8. 填写内容
    print("\n📝 步骤6: 填写标题和正文...")
    print("   💡 请在浏览器中填写内容，或按Enter自动尝试...")

    input("   按Enter继续，或直接在浏览器中操作...")

    # 尝试自动填写
    await publisher._fill_title(content.title)
    await publisher._fill_content(content.content)

    for tag in content.tags:
        await publisher._add_tag(tag)
        await asyncio.sleep(0.3)

    # 9. 发布
    print("\n🚀 步骤7: 发布...")
    print("   💡 请在浏览器中点击发布按钮")
    print("   发布成功后告诉我")

    input("   按Enter结束（浏览器将保持打开）...")

    # 结束
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("💡 浏览器保持打开状态，你可以手动关闭")
    print("=" * 60)


async def main():
    import argparse

    print("\n" + "=" * 60)
    print("🚀 小红书发布器 - 手动登录版")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="小红书发布器（手动登录）")
    parser.add_argument("--image", "-i", help="图片路径")
    args = parser.parse_args()

    # 默认图片
    default_image = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"
    image_path = args.image or default_image

    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        return

    print(f"\n📁 使用图片: {image_path}")

    await publish_with_manual_login(image_path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
