# styler.py

import re

class WeChatStyler:
    """
    微信公众号美化器 - 极简清晰版
    """
    # 核心配色：深灰与科技蓝
    COLOR_BLUE = "#0052d9"
    COLOR_BG = "#f6f6f6"
    COLOR_TEXT = "#333333"
    COLOR_SUB = "#888888"

    @classmethod
    def beautify(cls, html_content):
        # 1. 优化段落：增加行高和行间距，解决文字拥挤问题
        html_content = re.sub(r'<p>', f'<p style="font-size: 15px; color: {cls.COLOR_TEXT}; line-height: 1.8; margin-bottom: 12px; text-align: justify;">', html_content)
        
        # 2. 优化引用块：作为简单的摘要框
        html_content = re.sub(r'<blockquote>', f'<blockquote style="border-left: 3px solid {cls.COLOR_BLUE}; padding: 10px 15px; background: {cls.COLOR_BG}; margin: 15px 0; color: #555; font-size: 14px;">', html_content)
        
        # 3. 优化链接：简洁的蓝色下划线
        html_content = re.sub(r'<a href=', f'<a style="color: {cls.COLOR_BLUE}; text-decoration: none; border-bottom: 1px solid {cls.COLOR_BLUE};" href=', html_content)

        # 4. 外层容器：确保左右留白
        wrapper = f"""
        <div style="padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', sans-serif;">
            {html_content}
        </div>
        """
        return wrapper