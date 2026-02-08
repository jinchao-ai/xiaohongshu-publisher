# Xiaohongshu Publisher Automation Agent

🤖 An intelligent automation agent for publishing content to Xiaohongshu (小红书), the leading Chinese lifestyle social media platform.

## Overview

This project provides an automated solution for publishing images and text to Xiaohongshu using Playwright browser automation. The agent handles the entire workflow from login authentication to content publishing.

### Features

- **QR Code Login**: Secure authentication via Xiaohongshu mobile app QR code scanning
- **Cookie Persistence**: Automatically saves and reuses session cookies to avoid repeated logins
- **Image Upload**: Automated image upload from local files
- **Content Management**:智能填写标题和正文内容
- **Publish Automation**:一键发布笔记到平台
- **Browser Visibility**: Headful mode for transparency and manual intervention when needed

## Project Structure

```
xiaohongshu-publisher/
├── SKILL.md                    # Agent skill definition
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── config/
│   └── xiaohongshu.yaml       # Platform configuration
├── scripts/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser_controller.py  # Playwright browser management
│   │   ├── login_handler.py        # Login & authentication
│   │   ├── content_generator.py    # AI content generation
│   │   └── publisher.py           # Publishing logic
│   └── utils/
│       └── __init__.py
└── [test scripts...]
```

## Installation

```bash
# Clone the repository
git clone git@github.com:jinchao-ai/xiaohongshu-publisher.git
cd xiaohongshu-publisher

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Usage

### Quick Start

```bash
# Run the main publisher script
python final_publisher.py
```

### Login (First Time)

For initial login, the script will open a browser window with a QR code. Scan it with your Xiaohongshu mobile app to authenticate. Cookies will be saved automatically for subsequent runs.

### Workflow

1. **Launch Browser**: Opens Chrome in headed mode (visible)
2. **Authentication**: Loads saved cookies or prompts for QR login
3. **Navigate**: Goes directly to the image publishing page
4. **Upload**: Selects and uploads the specified image
5. **Fill Content**: Automatically fills title and body text
6. **Publish**: Clicks the publish button to submit

### Configuration

Edit `config/xiaohongshu.yaml` to customize:

```yaml
xiaohongshu:
  url: https://creator.xiaohongshu.com
  publish_url: https://creator.xiaohongshu.com/publish/publish?from=menu&target=image
  cookie_file: ~/.xiaohongshu_publisher/cookies.json
```

## Scripts Reference

| Script | Description |
|--------|-------------|
| `final_publisher.py` | Main working publish script |
| `login_qr.py` | QR code login with cookie saving |
| `publish_working.py` | Working version of publisher |
| `analyze_*.py` | Debug and analysis scripts |

## Architecture

### Browser Controller

Manages Playwright browser lifecycle:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
```

### Login Handler

QR code authentication with cookie persistence:

```python
# Save cookies after successful login
cookies = await context.cookies()
with open(cookie_file, 'w') as f:
    json.dump(cookies, f, indent=2)

# Load cookies for subsequent sessions
with open(cookie_file) as f:
    cookies = json.load(f)
await context.add_cookies(cookies)
```

### Content Publisher

Automated content filling:

```python
# Fill title
await page.fill('input[placeholder*="标题"]', "Your title here")

# Fill content
await page.fill('textarea', "Your content here")

# Click publish
await page.click("button:has-text('发布')")
```

## Cookie Management

Cookies are stored at:
```
~/.xiaohongshu_publisher/cookies.json
```

### Cookie File Format

```json
[
  {
    "name": "session",
    "value": "xxx",
    "domain": ".xiaohongshu.com",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": false,
    "sameSite": "Lax"
  }
]
```

## Requirements

- Python 3.10+
- Playwright 1.40+
- Chromium browser
- Internet connection
- Xiaohongshu creator account

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `XHS_COOKIE_FILE` | Path to cookie file | `~/.xiaohongshu_publisher/cookies.json` |
| `XHS_IMAGE_PATH` | Default image path | `~/Downloads/` |

## Troubleshooting

### Login Issues

1. **QR Code Not Appearing**
   - Ensure cookies haven't expired
   - Delete `~/.xiaohongshu_publisher/cookies.json` and re-authenticate

2. **Session Expired (401)**
   - Cookies have expired
   - Run login script again to refresh cookies

### Upload Issues

1. **File Chooser Not Opening**
   - Use `page.set_input_files()` instead of file chooser
   - Ensure file path is absolute

2. **Image Not Uploading**
   - Check file format (PNG, JPG supported)
   - Verify file size limits (typically < 20MB)

### Publish Issues

1. **Button Not Clickable**
   - Element may be covered by modal
   - Use JavaScript click as fallback

2. **Content Not Filled**
   - Check placeholder selectors
   - Use browser console to inspect elements

## Best Practices

1. **Session Management**: Regularly refresh cookies to maintain access
2. **Error Handling**: Always verify actions with screenshots
3. **Rate Limiting**: Add delays between publish operations
4. **Content Quality**: Use engaging titles and authentic content
5. **Compliance**: Follow Xiaohongshu community guidelines

## Security Considerations

- Cookies contain sensitive session data
- Store cookies with appropriate file permissions (`chmod 600`)
- Never commit cookies to version control
- Use `.gitignore` to exclude sensitive files

## API Reference

### Main Publisher Class

```python
class XiaohongshuPublisher:
    def __init__(self, cookie_file: str = None):
        """Initialize with optional cookie file path."""
        
    async def login(self) -> bool:
        """Perform QR code login and save cookies."""
        
    async def publish(
        self,
        image_path: str,
        title: str,
        content: str
    ) -> bool:
        """Publish image with title and content."""
        
    async def close(self):
        """Clean up browser resources."""
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Disclaimer

This project is for educational purposes only. Using automation tools may violate platform terms of service. Use at your own risk.

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: See SKILL.md for agent-specific instructions

## Changelog

### v1.0.0 (2024-02-08)

- Initial release
- QR code login implementation
- Cookie persistence
- Image upload automation
- Content filling
- Publish automation

---

Built with 🤖 [OpenCode](https://opencode.ai) - AI-powered software engineering
