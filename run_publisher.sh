#!/usr/bin/env python3
"""
运行小红书发布器，60秒后自动退出
"""
import asyncio
import subprocess
import sys
import os

# 先进入目录
os.chdir("/Users/mile/work/.opencode/skills/xiaohongshu-publisher")

# 运行发布器
result = subprocess.run(
    [sys.executable, "auto_detect_login.py",
     "--image", "/Users/mile/Downloads/jimeng-2025-12-11-2160-现代简约励志海报设计，采用温暖的橙黄色渐变背景，从底部的深橙色过渡到顶部的浅黄色....png"],
    capture_output=False,
    text=True
)
