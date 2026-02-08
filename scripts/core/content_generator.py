"""
AI内容生成器 - 根据图片智能生成小红书风格的标题、正文和标签
"""

import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class GeneratedContent:
    """生成的内容"""

    title: str
    content: str
    tags: List[str]
    image_type: str = ""
    mood: str = ""
    theme: str = ""


class ContentGenerator:
    """小红书内容生成器"""

    # 标题模板库
    TITLE_TEMPLATES = {
        "励志": [
            "被这段话治愈了✨｜{theme}",
            "人生建议：{advice}",
            "这段话让我瞬间清醒💫",
            "送给每一个正在努力的你🌟",
            "今天看到的最有力量的文字",
            "{theme}｜{emotion}到爆！",
            "封神级的{theme}文案！🔥",
            "建议收藏｜{theme}必读",
            "2024最火的{theme}金句📝",
            "看完你会来谢我的{theme}✨",
        ],
        "情感": [
            "深夜看到这段话，瞬间破防😭",
            "原来{topic}是这样的",
            "成年人最该明白的道理",
            "看完这段话，我释怀了",
            "这段话写到我心坎里了💔",
            "如果你也在经历{topic}...",
            "终于有人把{topic}说清楚了",
            "{topic} | 每个人都该看看",
            "关于{topic}，我有话要说",
            "这篇{topic}文章，看完沉默了",
        ],
        "美食": [
            "在{location}吃到扶墙出🔥",
            "{dish}天花板被我找到了！",
            "被问爆的{dish}地址来啦📍",
            "人均{dish}吃到撑！",
            "这家{dish}让我惊艳了✨",
            "碳水控必冲的{dish}！",
            "{dish}脑袋给我冲🏃",
            "本地人强推的{dish}！",
            "这条{location}{dish}攻略太全了",
            "吃完这顿{dish}，我哭了😭",
        ],
        "美妆": [
            "新手友好的{dproduct}推荐！",
            "{dproduct}智商税还是真香？",
            "均价不过百的{dproduct}绝绝子！",
            "这个{dproduct}让我换头了✨",
            "{dproduct}红黑榜｜真实测评",
            "学生党{dproduct}合集来啦！",
            "无限回购的{dproduct}们💄",
            "新手入门{dproduct}看这篇！",
            "{dproduct}的正确打开方式",
            "这个{dproduct}我愿称之为神！",
        ],
        "旅行": [
            "最适合短途游的{location}！",
            "{location}两日游攻略🗺️",
            "在{location}拍出刷爆朋友圈的照片📸",
            "{location}本地人带路｜不踩雷",
            "{location}绝美机位大公开！",
            "去{location}前一定要看这篇！",
            "{location}自由行攻略｜全干货",
            "这个{location}冷门但绝美🌿",
            "{location}周末游｜超详细攻略",
            "被问爆的{location}来啦！",
        ],
        "日常": [
            "打工人{topic}日常Plog✨",
            "提升幸福感的{topic}好物",
            "女生必知的{topic}小知识",
            "后悔没早点知道的{topic}！",
            "{topic}入门级教程｜超详细",
            "关于{topic}的一切都在这里",
            "新手小白也能学会的{topic}！",
            "{topic}攻略｜建议收藏",
            "{topic}让我生活更美好💫",
            "分享我的{topic}小技巧✨",
        ],
    }

    # 正文开头模板
    CONTENT_INTROS = {
        "励志": [
            "今天看到这句话，真的被戳中了💫",
            "最近一直在思考这个问题🤔",
            "想要分享一个很棒的发现✨",
            "这段话送给自己，也送给你们🌟",
            "允许我分享这段很有力量的话🙏",
        ],
        "情感": [
            "最近感悟很深，想和大家聊聊💭",
            "不知道你们有没有同感...",
            "今天想认真的说几句心里话",
            "这个{topic}的话题，我想聊一聊",
            "关于{topic}，我有话想说",
        ],
        "美食": [
            "终于找到机会分享这家宝藏店铺了！",
            "这家{dish}真的绝了，必须安利给你们！",
            "干饭人魂牵梦绕的{dish}！",
            "{location}美食探店第N弹来了！",
            "作为一个吃货，我必须说...",
        ],
        "日常": [
            "日常分享时间到啦✨",
            "今天想记录一下最近的{topic}...",
            "好久没发日常了，浅浅更新一下",
            "{topic}日记｜平淡生活的闪光时刻",
            "分享几个我的{topic}小习惯🏃",
        ],
    }

    # 正文结尾模板
    CONTENT_OUTROS = {
        "励志": [
            "\n\n希望这段话能给你带来力量💪",
            "\n\n一起加油，成为更好的自己✨",
            "\n\n共勉🙏",
            "\n\n愿你我都能被这个世界温柔以待🌈",
        ],
        "情感": [
            "\n\n愿我们都能被温柔以待💕",
            "\n\n如果你也有同感，欢迎评论区聊聊",
            "\n\n愿你一切安好🙏",
            "\n\n共勉💫",
        ],
        "美食": [
            "\n\n📍地址：{location}",
            "\n\n💰人均：XXX元",
            "\n\n👭推荐指数：⭐⭐⭐⭐⭐",
            "\n\n码住这篇，{dish}吃到爽！🍽️",
        ],
        "日常": [
            "\n\n以上就是今天的分享啦✨",
            "\n\n你们有什么{topic}心得吗？评论区交流呀💬",
            "\n\n喜欢的记得点赞收藏哦❤️",
            "\n\n我们下次再见👋",
        ],
    }

    # 标签库
    TAG_CATEGORIES = {
        "励志": [
            "励志",
            "正能量",
            "人生感悟",
            "自我成长",
            "治愈系",
            "成长",
            "生活感悟",
            "金句",
            "文案",
            "治愈",
        ],
        "情感": [
            "情感",
            "治愈系",
            "温暖",
            "情感文案",
            "深夜文案",
            "扎心",
            "共情",
            "情感语录",
            "人间清醒",
        ],
        "美食": [
            "美食",
            "美食探店",
            "干饭人",
            "美食推荐",
            "美食日常",
            "吃货",
            "探店",
            "网红店",
            "美食分享",
        ],
        "美妆": [
            "美妆",
            "化妆",
            "护肤",
            "化妆品",
            "彩妆",
            "新手化妆",
            "护肤日常",
            "变美",
            "好物推荐",
        ],
        "旅行": [
            "旅行",
            "旅游",
            "旅行攻略",
            "周末游",
            "短途旅行",
            "拍照圣地",
            "小众旅行",
            "出行攻略",
        ],
        "日常": [
            "日常",
            "plog",
            "生活碎片",
            "记录生活",
            "OOTD",
            "好物分享",
            "购物分享",
            "生活日常",
        ],
    }

    # 图片类型关键词映射
    IMAGE_TYPE_MAPPING = {
        "励志": ["励志", "正能", "金句", "文案", "文字", "海报", "治愈", "成长"],
        "情感": ["情感", "扎心", "温柔", "深夜", "心情", "感悟"],
        "美食": ["美食", "食物", "吃", "餐厅", "饮料", "甜品", "烹饪", "菜"],
        "美妆": ["护肤", "化妆", "口红", "眼影", "美妆", "妆容", "美容"],
        "旅行": ["旅行", "风景", "景点", "拍照", "打卡", "城市", "建筑"],
        "穿搭": ["穿搭", "衣服", "时尚", "ootd", "服装", "搭配"],
    }

    def __init__(self):
        pass

    def analyze_image(self, image_path: Path) -> Dict:
        """
        分析图片，识别内容类型
        实际场景中可以使用AI图像识别，这里用文件名推断
        """
        filename = image_path.name.lower()
        file_path = str(image_path).lower()

        # 根据文件名和路径判断图片类型
        image_type = "日常"
        mood = "平静"
        theme = "生活"

        for type_name, keywords in self.IMAGE_TYPE_MAPPING.items():
            for keyword in keywords:
                if keyword in filename or keyword in file_path:
                    image_type = type_name
                    break
            if image_type != "日常":
                break

        # 根据类型设置默认主题和情绪
        type_defaults = {
            "励志": {"theme": "自我成长", "mood": "治愈"},
            "情感": {"theme": "情感共鸣", "mood": "温暖"},
            "美食": {"theme": "美食探店", "mood": "满足"},
            "美妆": {"theme": "美丽分享", "mood": "自信"},
            "旅行": {"theme": "旅行见闻", "mood": "愉悦"},
            "日常": {"theme": "生活记录", "mood": "平静"},
        }

        defaults = type_defaults.get(image_type, type_defaults["日常"])
        if theme == "生活":
            theme = defaults["theme"]
        mood = defaults["mood"]

        return {"type": image_type, "mood": mood, "theme": theme}

    def generate_title(self, analysis: Dict, custom_title: str = None) -> str:
        """生成标题"""
        if custom_title:
            # 用户提供了自定义标题
            title = custom_title
        else:
            # 使用模板生成
            category = analysis["type"]
            templates = self.TITLE_TEMPLATES.get(category, self.TITLE_TEMPLATES["日常"])
            template = random.choice(templates)

            # 根据分析结果填充模板
            replacements = {
                "theme": analysis.get("theme", "生活"),
                "topic": analysis.get("theme", "话题"),
                "advice": "活好自己",
                "emotion": analysis.get("mood", "治愈"),
                "location": "本地",
                "dish": "美食",
                "dproduct": "好物",
            }

            title = template
            for key, value in replacements.items():
                title = title.replace(f"{{{key}}}", value)

        # 确保标题长度合适
        max_length = self.TAG_CATEGORIES.get("励志", ["励志"])[
            0
        ]  # 使用配置的max_title_length
        if len(title) > 20:
            title = title[:19] + "…"

        return title

    def generate_content(self, analysis: Dict, custom_content: str = None) -> str:
        """生成正文"""
        if custom_content:
            return custom_content

        category = analysis["type"]
        intros = self.CONTENT_INTROS.get(category, self.CONTENT_INTROS["日常"])
        outros = self.CONTENT_OUTROS.get(category, self.CONTENT_OUTROS["日常"])

        # 随机选择开头和结尾
        intro = random.choice(intros)
        outro = random.choice(outros)

        # 生成中间内容
        if category == "励志":
            body = self._generate_motivational_body(analysis)
        elif category == "情感":
            body = self._generate_emotional_body(analysis)
        elif category == "美食":
            body = self._generate_food_body(analysis)
        else:
            body = self._generate_daily_body(analysis)

        # 组合正文
        content = intro + "\n\n" + body + outro

        return content

    def _generate_motivational_body(self, analysis: Dict) -> str:
        """生成励志类正文"""
        templates = [
            f"""
{analysis.get("theme", "成长")}这件事，真的需要慢慢来。

不必急于求成，也不必与他人比较。
每个人的花期不同，不必焦虑有人提前盛开。

记住：
- {random.choice(["你的努力，时间看得见"])}
- {random.choice(["自律给你自由"])}
- {random.choice(["慢慢来，比较快"])}

愿你在{analysis.get("theme", "成长")}的路上，永远保持热爱和勇气。💪
""",
            f"""
最近很喜欢一句话：{random.choice(["慢慢来，比较快", "允许自己慢一点", "你已经很棒了"])}。

{analysis.get("mood", "治愈")}的时刻值得被记录。

{analysis.get("theme", "生活感悟")}教会我的几件事：
1. {random.choice(["过程比结果更重要"])}
2. {random.choice(["享受当下"])}
3. {random.choice(["相信自己"])}

一起加油吧！✨🌟
""",
        ]
        return random.choice(templates)

    def _generate_emotional_body(self, analysis: Dict) -> str:
        """生成情感类正文"""
        return f"""
{analysis.get("theme", "情感共鸣")}这件事，每个人都有不同的感受。

有时候，一段话就能戳中内心最柔软的地方。

愿我们都能在{analysis.get("mood", "温暖")}中找到力量。

无论你现在处于什么状态，都请记得：
{random.choice(["你值得被爱", "你已经很努力了", "一切都会好起来的"])}

#情感共鸣 #治愈系 #温暖时刻
""".strip()

    def _generate_food_body(self, analysis: Dict) -> str:
        """生成美食类正文"""
        return f"""
今天必须分享一家让我惊艳的{analysis.get("theme", "美食")}！

{analysis.get("mood", "满足")}感直接拉满！😍

🍽️ 菜品评价：
- 口味：⭐⭐⭐⭐⭐
- 环境：⭐⭐⭐⭐
- 服务：⭐⭐⭐⭐

总的来说，是一次非常{analysis.get("mood", "愉快")}的用餐体验！

下次还会再来！💯
""".strip()

    def _generate_daily_body(self, analysis: Dict) -> str:
        """生成日常类正文"""
        return f"""
分享一下最近的{analysis.get("theme", "生活")}碎片✨

每天都在努力生活，虽然平淡但很充实。

一些小感悟：
{
            random.choice(
                [
                    "生活就是要善于发现小美好",
                    "平凡的日子里也有闪光时刻",
                    "珍惜当下的每一刻",
                ]
            )
        }

希望你们也能在{analysis.get("mood", "平静")}中找到属于自己的小确幸💫
""".strip()

    def generate_tags(self, analysis: Dict, custom_tags: List[str] = None) -> List[str]:
        """生成标签"""
        if custom_tags:
            return custom_tags[:9]  # 最多9个标签

        category = analysis["type"]
        tags = self.TAG_CATEGORIES.get(category, self.TAG_CATEGORIES["日常"]).copy()

        # 添加一些通用标签
        universal_tags = ["小红书", "笔记", "分享", "推荐"]
        tags.extend(universal_tags)

        # 随机打乱，返回前5-7个标签
        random.shuffle(tags)
        return tags[: random.randint(5, 7)]

    def generate_full_content(
        self,
        image_path: Path,
        custom_title: str = None,
        custom_content: str = None,
        custom_tags: List[str] = None,
    ) -> GeneratedContent:
        """
        生成完整内容（标题+正文+标签）

        Args:
            image_path: 图片路径
            custom_title: 自定义标题（可选）
            custom_content: 自定义正文（可选）
            custom_tags: 自定义标签（可选）

        Returns:
            GeneratedContent: 生成的内容对象
        """
        # 分析图片
        analysis = self.analyze_image(image_path)
        logger.info(
            f"🖼️  图片分析结果: 类型={analysis['type']}, 情绪={analysis['mood']}, 主题={analysis['theme']}"
        )

        # 生成各部分内容
        title = self.generate_title(analysis, custom_title)
        content = self.generate_content(analysis, custom_content)
        tags = self.generate_tags(analysis, custom_tags)

        logger.info(f"✅ 内容生成完成:")
        logger.info(f"   标题: {title}")
        logger.info(f"   正文长度: {len(content)} 字")
        logger.info(f"   标签: {', '.join(tags)}")

        return GeneratedContent(
            title=title,
            content=content,
            tags=tags,
            image_type=analysis["type"],
            mood=analysis["mood"],
            theme=analysis["theme"],
        )

    def preview_content(self, content: GeneratedContent) -> str:
        """预览生成的内容"""
        preview = f"""
{"=" * 50}
📝 标题: {content.title}
{"=" * 50}
🏷️  标签: {" ".join(["#" + tag for tag in content.tags])}

{"=" * 50}
📄 正文:
{"=" * 50}
{content.content}

{"=" * 50}
📊 分析: 类型={content.image_type}, 情绪={content.mood}, 主题={content.theme}
{"=" * 50}
"""
        return preview
