#!/usr/bin/env python3
"""
小红书发布器 - 自动检测登录状态版
打开浏览器后，自动检测登录状态，登录成功后自动继续发布流程
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from scripts import XiaohongshuPublisher


async def publish_auto_detect_login(image_path: str):
    """自动检测登录状态并发布"""

    publisher = XiaohongshuPublisher()

    print("\n" + "=" * 60)
    print("🚀 小红书发布器（自动检测登录）")
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

    # 截图
    await publisher.browser.screenshot(path="/tmp/xhs_login_step1.png")
    print("📸 登录页面截图已保存")

    print("\n" + "=" * 60)
    print("💡 请在浏览器中手动操作：")
    print("   1. 点击右上角「登 录」按钮")
    print("   2. 选择「扫码登录」")
    print("   3. 用小红书APP扫码")
    print("=" * 60)

    # 3. 自动检测登录状态
    print("\n🔍 自动检测登录状态...")
    print("   (每10秒检测一次，最多等待5分钟)\n")

    login_detected = False
    max_wait_time = 300  # 5分钟
    check_interval = 10  # 每10秒
    elapsed = 0

    while elapsed < max_wait_time:
        remaining = max_wait_time - elapsed

        # 检测是否已登录
        await publisher.browser.navigate("https://creator.xiaohongshu.com")
        await asyncio.sleep(2)

        current_url = await publisher.browser.page.url()
        page_title = await publisher.browser.page.title()

        print(
            f"⏰ [{datetime.now().strftime('%H:%M:%S')}] 检查... (剩余 {remaining}秒)"
        )
        print(f"   URL: {current_url}")
        print(f"   标题: {page_title}")

        # 检测登录成功的标志
        if "login" not in current_url and "creator" in current_url:
            print("\n" + "=" * 60)
            print("✅ 检测到已登录成功！")
            print("=" * 60)

            # 保存cookies
            print("\n💾 正在保存登录状态...")
            await publisher.login_handler.save_browser_cookies()
            print("✅ 登录状态已保存，下次无需扫码")

            login_detected = True
            break

        # 没登录，继续等待
        await asyncio.sleep(check_interval)
        elapsed += check_interval

    if not login_detected:
        print("\n" + "=" * 60)
        print("⚠️  等待超时，未检测到登录状态")
        print("💡 请在浏览器中手动登录，然后告诉我")
        print("=" * 60)
        return

    # 4. 生成内容
    print("\n📝 步骤3: AI生成内容...")
    content = publisher.content_generator.generate_full_content(image_path)
    content_preview = publisher.content_generator.preview_content(content)

    # 打印内容预览
    print("\n" + "=" * 60)
    print("🤖 AI生成的内容预览:")
    print("=" * 60)
    print(content_preview)

    # 5. 导航到发布页面
    print("\n🌐 步骤4: 打开发布页面...")
    await publisher.browser.navigate("https://creator.xiaohongshu.com/publish")
    await asyncio.sleep(3)

    await publisher.browser.screenshot(path="/tmp/xhs_publish_page.png")
    print("📸 发布页面截图已保存")

    # 6. 上传图片
    print("\n📤 步骤5: 上传图片...")
    print(f"   图片路径: {image_path}")

    upload_success = await publisher._upload_image(image_path)
    if upload_success:
        print("✅ 图片上传成功")
    else:
        print("⚠️  自动上传失败，请手动上传")
        print("   💡 在浏览器中上传图片后，回到终端按Enter继续")

    await asyncio.sleep(3)

    # 7. 填写内容
    print("\n📝 步骤6: 填写标题和正文...")

    title_success = await publisher._fill_title(content.title)
    if title_success:
        print("✅ 标题填写成功")
    else:
        print("⚠️  标题填写失败，请手动填写")

    content_success = await publisher._fill_content(content.content)
    if content_success:
        print("✅ 正文填写成功")
    else:
        print("⚠️  正文填写失败，请手动填写")

    # 填写标签
    for tag in content.tags:
        tag_success = await publisher._add_tag(tag)
        await asyncio.sleep(0.3)

    if content.tags:
        print(f"✅ 已填写 {len(content.tags)} 个标签")

    await publisher.browser.screenshot(path="/tmp/xhs_content_filled.png")
    print("📸 内容填写完成截图已保存")

    # 8. 发布
    print("\n" + "=" * 60)
    print("🚀 步骤7: 发布")
    print("=" * 60)
    print("   💡 请在浏览器中点击发布按钮")
    print("   📸 截图已保存，可查看最终效果")

    await publisher.browser.screenshot(path="/tmp/xhs_before_publish.png")

    # 截图留念
    print("\n📸 所有步骤截图已保存到 /tmp/ 目录:")
    print("   - xhs_login_step1.png (登录页面)")
    print("   - xhs_publish_page.png (发布页面)")
    print("   - xhs_content_filled.png (内容填写后)")
    print("   - xhs_before_publish.png (发布前)")

    print("\n" + "=" * 60)
    print("✅ 发布流程指导完成！")
    print("💡 请在浏览器中完成最终发布")
    print("=" * 60)


async def main():
    import argparse

    print("\n" + "=" * 60)
    print("🚀 小红书发布器 - 自动检测登录版")
    print("=" * 60)

    parser = argparse.ArgumentParser(description="小红书发布器（自动检测登录）")
    parser.add_argument("--image", "-i", help="图片路径")
    args = parser.parse_args()

    # 默认图片
    default_image = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"
    image_path = args.image or default_image

    if not Path(image_path).exists():
        print(f"❌ 图片不存在: {image_path}")
        return

    print(f"\n📁 使用图片: {image_path}")
    print("🔍 浏览器已启动，请观察浏览器窗口...")

    await publish_auto_detect_login(image_path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
