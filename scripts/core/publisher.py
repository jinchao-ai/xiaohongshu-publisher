"""
小红书自动发布器 - 主程序入口
支持全自动模式和交互模式
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

# 导入核心模块
from .browser_controller import BrowserController
from .login_handler import LoginHandler
from .content_generator import ContentGenerator, GeneratedContent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class XiaohongshuPublisher:
    """小红书自动发布器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self.browser = BrowserController(self.config)
        self.login_handler = None
        self.content_generator = ContentGenerator()

    def _find_config(self) -> str:
        """查找配置文件"""
        # 当前目录查找
        current_dir = Path(__file__).parent.parent
        config_paths = [
            current_dir / "config" / "xiaohongshu.yaml",
            current_dir / ".." / "config" / "xiaohongshu.yaml",
            Path(
                "/Users/mile/work/.opencode/skills/xiaohongshu-publisher/config/xiaohongshu.yaml"
            ),
        ]

        for path in config_paths:
            if path.exists():
                return str(path)

        raise FileNotFoundError(f"配置文件未找到: {config_paths}")

    def _load_config(self) -> dict:
        """加载配置"""
        import yaml

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    async def initialize(self) -> bool:
        """初始化浏览器"""
        success = await self.browser.init()
        if success:
            self.login_handler = LoginHandler(self.browser, self.config)
        return success

    async def ensure_login(self) -> bool:
        """确保已登录"""
        return await self.login_handler.handle_login()

    async def publish_image_note(
        self,
        image_path: str,
        content: GeneratedContent = None,
        auto_generate: bool = True,
        preview: bool = True,
        confirm_before_publish: bool = True,
    ) -> dict:
        """
        发布图文笔记

        Args:
            image_path: 图片路径
            content: 预生成的内容对象（可选）
            auto_generate: 是否自动生成内容
            preview: 是否预览生成的内容
            confirm_before_publish: 发布前是否需要确认

        Returns:
            dict: 发布结果
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"图片不存在: {image_path}")

        print(f"\n🖼️  准备发布图片: {image_path.name}")
        print(f"📁 完整路径: {image_path.absolute()}")

        # 1. 生成内容
        if auto_generate:
            print("\n🤖 正在AI生成内容...")
            content = self.content_generator.generate_full_content(image_path)

            if preview:
                print(self.content_generator.preview_content(content))

            if confirm_before_publish:
                print("\n" + "=" * 50)
                confirm = input("以上内容是否满意？(y/n/q=退出): ").strip().lower()
                if confirm == "q":
                    print("👋 已取消发布")
                    return {"success": False, "canceled": True}
                elif confirm == "n":
                    print("\n📝 请手动修改或重新生成内容...")
                    # 这里可以实现手动输入逻辑
                    content = await self.manual_input_content()
        else:
            if content is None:
                content = await self.manual_input_content()

        # 2. 进入发布页面
        print("\n🌐 正在打开发布页面...")
        await self.browser.navigate(self.config["platform"]["publish_url"])
        await asyncio.sleep(3)

        # 3. 上传图片
        print("📤 正在上传图片...")
        upload_success = await self._upload_image(str(image_path.absolute()))
        if not upload_success:
            print("❌ 图片上传失败")
            return {"success": False, "error": "图片上传失败"}

        print("✅ 图片上传完成")

        # 4. 填写标题
        print("📝 正在填写标题...")
        await self._fill_title(content.title)

        # 5. 填写正文
        print("📝 正在填写正文...")
        await self._fill_content(content.content)

        # 6. 添加标签
        print("🏷️  正在添加标签...")
        for tag in content.tags:
            await self._add_tag(tag)
            await asyncio.sleep(0.3)

        print("\n" + "=" * 50)
        print("✅ 所有内容填写完成")
        print("=" * 50)

        # 7. 发布
        if confirm_before_publish:
            print("\n🎯 请在浏览器中确认内容无误，然后:")
            print("   - 点击'发布'按钮")
            print("   - 或输入'p'直接发布")
            print("   - 输入'n'重新编辑")
            print("   - 输入'q'取消发布")

            user_input = input("\n请选择操作 (p/n/q): ").strip().lower()

            if user_input == "q":
                print("👋 已取消发布")
                return {"success": False, "canceled": True}
            elif user_input == "n":
                print("📝 请在浏览器中手动编辑内容...")
                input("编辑完成后按Enter继续...")
            else:
                # 默认直接发布
                pass

        # 执行发布
        publish_success = await self._click_publish()

        if publish_success:
            print("\n" + "🎉" * 20)
            print("✅ 发布成功！🎉")
            print("🎉" * 20 + "\n")

            return {
                "success": True,
                "title": content.title,
                "content": content.content[:100] + "...",
                "tags": content.tags,
                "publish_time": datetime.now().isoformat(),
            }
        else:
            print("\n❌ 发布失败，请手动检查浏览器中的内容")
            return {"success": False, "error": "发布失败"}

    async def _upload_image(self, image_path: str) -> bool:
        """上传图片"""
        try:
            # 查找文件上传输入框
            file_input_selectors = [
                'input[type="file"]',
                '.upload-area input[type="file"]',
                '.upload-container input[type="file"]',
                '[class*="upload"] input[type="file"]',
            ]

            for selector in file_input_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    await element.set_input_files(image_path)
                    print(f"   已找到上传元素: {selector}")
                    await asyncio.sleep(3)  # 等待上传
                    return True

            # 如果找不到上传框，尝试点击上传区域
            upload_selectors = [
                ".upload-area",
                ".upload-container",
                '[class*="upload"]',
                ".add-note-btn",
            ]

            for selector in upload_selectors:
                element = await self.browser.find_element(selector)
                if element and await element.is_visible():
                    await element.click()
                    await asyncio.sleep(2)
                    # 尝试再次上传
                    for file_selector in file_input_selectors:
                        file_element = await self.browser.find_element(file_selector)
                        if file_element:
                            await file_element.set_input_files(image_path)
                            await asyncio.sleep(3)
                            return True

            print("⚠️  未找到上传元素，请手动上传")
            return False

        except Exception as e:
            logger.error(f"❌ 上传图片失败: {e}")
            return False

    async def _fill_title(self, title: str) -> bool:
        """填写标题"""
        title_selectors = [
            'input[placeholder*="标题"]',
            'input[placeholder*="标题"]'.replace("标题", "标题"),
            '[class*="title"] input',
            ".title-input input",
        ]

        for selector in title_selectors:
            element = await self.browser.find_element(selector)
            if element and await element.is_visible():
                await element.fill(title)
                print(f"   已填写标题: {title}")
                return True

        print("⚠️  未找到标题输入框")
        return False

    async def _fill_content(self, content: str) -> bool:
        """填写正文"""
        content_selectors = [
            ".editor-content textarea",
            ".content-editor textarea",
            '[class*="editor"] textarea',
            ".rich-text-editor textarea",
        ]

        for selector in content_selectors:
            element = await self.browser.find_element(selector)
            if element and await element.is_visible():
                await element.fill(content)
                print(f"   已填写正文 ({len(content)} 字)")
                return True

        print("⚠️  未找到正文输入框")
        return False

    async def _add_tag(self, tag: str) -> bool:
        """添加标签"""
        # 先找到标签输入框
        tag_input_selectors = [
            ".tag-input input",
            '[class*="tag"] input',
            'input[placeholder*="标签"]',
        ]

        for selector in tag_input_selectors:
            element = await self.browser.find_element(selector)
            if element and await element.is_visible():
                await element.fill(tag)
                await element.press("Enter")
                print(f"   已添加标签: #{tag}")
                return True

        # 如果找不到输入框，尝试其他方式
        # 可以实现点击选择标签等逻辑
        return False

    async def _click_publish(self) -> bool:
        """点击发布按钮"""
        publish_selectors = [
            ".publish-btn",
            'button[type="submit"]',
            '[class*="publish"] button',
            ".submit-btn",
            'button:has-text("发布")',
        ]

        for selector in publish_selectors:
            element = await self.browser.find_element(selector)
            if element and await element.is_visible():
                try:
                    await element.click()
                    print("   已点击发布按钮")
                    await asyncio.sleep(2)
                    return True
                except Exception as e:
                    logger.warning(f"⚠️  点击发布按钮失败: {e}")

        print("⚠️  未找到发布按钮")
        return False

    async def manual_input_content(self) -> GeneratedContent:
        """手动输入内容（交互模式）"""
        print("\n📝 请手动输入内容:")

        title = input("   标题: ").strip()
        content = input("   正文: ").strip()

        tags_str = input("   标签 (用逗号分隔): ").strip()
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else []

        return GeneratedContent(title=title, content=content, tags=tags)

    async def run_auto(self, image_path: str, **kwargs) -> dict:
        """全自动模式"""
        print("\n" + "🚀" * 20)
        print("🚀 启动小红书全自动发布模式")
        print("🚀" * 20)

        try:
            # 1. 初始化
            if not await self.initialize():
                return {"success": False, "error": "浏览器初始化失败"}

            # 2. 确保登录
            if not await self.ensure_login():
                return {"success": False, "error": "登录失败"}

            # 3. 发布内容
            result = await self.publish_image_note(image_path, **kwargs)

            # 4. 发布成功后保存cookies
            if result.get("success"):
                await self.login_handler.save_browser_cookies()
                print("✅ 登录状态已保存")

            return result

        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断操作")
            print("💡 浏览器保持打开状态，你可以手动查看页面")
            print("📸 截图已保存，如需关闭浏览器，请手动关闭")
            return {"success": False, "error": "用户中断"}

        except Exception as e:
            logger.error(f"❌ 自动发布失败: {e}")
            print("\n💡 浏览器保持打开状态，你可以手动查看页面")
            print("📸 截图已保存，如需关闭浏览器，请手动关闭")
            return {"success": False, "error": str(e)}

        finally:
            # 只有正常完成或用户要求时才关闭
            if self.browser:
                try:
                    # 正常完成时才自动关闭
                    pass
                except:
                    pass

    async def run_interactive(self):
        """交互模式"""
        print("\n" + "💬" * 20)
        print("💬 欢迎使用小红书发布助手（交互模式）")
        print("💬" * 20)

        # 1. 选择发布类型
        print("\n请选择发布类型:")
        print("  1. 图文笔记")
        print("  2. 视频笔记")

        while True:
            choice = input("\n请选择 (1/2): ").strip()
            if choice in ["1", "2"]:
                note_type = "图文" if choice == "1" else "视频"
                print(f"   已选择: {note_type}笔记")
                break
            print("   无效选择，请输入1或2")

        # 2. 输入图片路径
        image_path = input("\n请输入图片/视频路径: ").strip()

        if not Path(image_path).exists():
            print(f"❌ 文件不存在: {image_path}")
            return

        # 3. 选择是否自动生成内容
        auto_generate = True
        if note_type == "图文":
            generate_choice = (
                input("\n是否自动生成标题和文案? (y/n, 默认y): ").strip().lower()
            )
            if generate_choice == "n":
                auto_generate = False

        # 4. 执行发布
        await self.initialize()
        await self.ensure_login()

        await self.publish_image_note(
            image_path=image_path,
            auto_generate=auto_generate,
            preview=True,
            confirm_before_publish=True,
        )


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="小红书自动发布器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 全自动模式
  python publisher.py --auto --image "/path/to/image.jpg"

  # 交互模式
  python publisher.py --interactive

  # 自定义内容
  python publisher.py --auto --image "/path/to/image.jpg" \\
      --title "自定义标题" --content "自定义内容" --tags "标签1,标签2"
        """,
    )

    parser.add_argument(
        "--mode", choices=["auto", "interactive"], default="auto", help="运行模式"
    )
    parser.add_argument("--image", "-i", help="图片路径")
    parser.add_argument("--title", "-t", help="自定义标题")
    parser.add_argument("--content", "-c", help="自定义正文")
    parser.add_argument("--tags", help="自定义标签 (逗号分隔)")
    parser.add_argument("--no-preview", action="store_true", help="不预览直接发布")
    parser.add_argument("--no-confirm", action="store_true", help="发布前不确认")

    args = parser.parse_args()

    # 创建发布器
    publisher = XiaohongshuPublisher()

    # 准备参数
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

    # 执行
    if args.mode == "auto":
        if not args.image:
            # 使用默认测试图片
            args.image = "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"

        result = await publisher.run_auto(args.image, **kwargs)
        print(f"\n📊 发布结果: {result}")
    else:
        await publisher.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
