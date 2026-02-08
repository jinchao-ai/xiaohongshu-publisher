#!/usr/bin/env python3
"""
小红书自动发布器 - 启动脚本

用法:
  python start_publisher.py                           # 全自动模式（默认）
  python start_publisher.py --interactive              # 交互模式
  python start_publisher.py --image "/path/to/img"    # 指定图片
  python start_publisher.py --help                    # 查看帮助
"""

import sys
import os

# 确保能找到模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts import XiaohongshuPublisher
import asyncio


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🚀 小红书自动发布助手 🚀                                   ║
║                                                               ║
║     全自动发布 · AI智能生成 · 扫码登录                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
📖 使用说明

🅰️ 全自动模式（推荐）
   python start_publisher.py
   python start_publisher.py --image "/path/to/image.jpg"

🅱️ 交互模式
   python start_publisher.py --interactive

🔧 自定义选项
   --image, -i     指定图片路径
   --title, -t     自定义标题
   --content, -c   自定义正文
   --tags          自定义标签 (逗号分隔)
   --no-preview    不预览直接发布
   --no-confirm    发布前不确认
   --interactive, -i  交互模式
   --help, -h      显示帮助

📝 示例
   python start_publisher.py
   python start_publisher.py -i "/Users/mile/Downloads/image.png"
   python start_publisher.py -i "/path/to/img" -t "我的标题" -c "正文内容" --tags "标签1,标签2"

⚠️  注意事项
   1. 首次使用需要扫码登录
   2. 浏览器窗口会保持打开
   3. 按Enter可关闭浏览器窗口
"""
    print(help_text)


async def main():
    import argparse

    print_banner()

    parser = argparse.ArgumentParser(
        description="小红书自动发布器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    parser.add_argument("--help", action="store_true", help="显示帮助")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--image", "-f", metavar="PATH", help="图片路径")
    parser.add_argument("--title", "-t", metavar="TEXT", help="自定义标题")
    parser.add_argument("--content", "-c", metavar="TEXT", help="自定义正文")
    parser.add_argument("--tags", metavar="TAGS", help="自定义标签 (逗号分隔)")
    parser.add_argument("--no-preview", action="store_true", help="不预览直接发布")
    parser.add_argument("--no-confirm", action="store_true", help="发布前不确认")

    args = parser.parse_args()

    if args.help:
        print_help()
        return

    # 默认使用下载目录的图片
    default_image = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

    # 如果没有指定图片，使用默认图片
    image_path = args.image or default_image

    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        print("\n💡 提示: 使用 --image 参数指定图片路径")
        print_help()
        return

    publisher = XiaohongshuPublisher()

    kwargs = {
        "auto_generate": not (args.title or args.content),
        "preview": not args.no_preview,
        "confirm_before_publish": not args.no_confirm,
    }

    if args.title:
        kwargs["custom_title"] = args.title
    if args.content:
        kwargs["custom_content"] = args.content
    if args.tags:
        kwargs["custom_tags"] = [t.strip() for t in args.tags.split(",")]

    if args.interactive:
        await publisher.run_interactive()
    else:
        print(f"\n📁 使用图片: {image_path}")
        print("🔍 浏览器已启动，请观察浏览器窗口...")
        print("=" * 60)

        result = await publisher.run_auto(image_path, **kwargs)

        print("\n" + "=" * 60)
        print("📊 发布结果:")
        print(result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        print("💡 浏览器窗口保持打开，你可以手动关闭")
    except EOFError:
        print("\n\n⚠️  检测到输入结束")
        print("💡 浏览器窗口保持打开，你可以手动关闭")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback

        traceback.print_exc()
