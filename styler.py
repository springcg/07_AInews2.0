# styler.py
import re

class WeChatStyler:
    """
    微信公众号文章美化器 - 紧凑版
    """
    
    COLOR_PRIMARY = "#007AFF"
    COLOR_TEXT_SUB = "#888888"

    # 1. 减小全局容器内边距
    STYLE_WRAPPER = """
        max-width: 677px; 
        margin: 0 auto; 
        padding: 10px;
        font-family: -apple-system, sans-serif;
        line-height: 1.6;
    """

    # 2. 压缩摘要盒间距
    STYLE_SUMMARY_BOX = f"""
        background-color: #F8FAFF;
        padding: 12px;
        margin-bottom: 15px;
        border-radius: 8px;
        font-size: 14px;
        color: #555;
    """

    # 3. 压缩卡片间距
    STYLE_SECTION = """
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #f0f0f0;
    """

    # 4. 新增：来源与类别的同行样式
    STYLE_META = f"""
        font-size: 12px;
        color: {COLOR_TEXT_SUB};
        margin-bottom: 8px;
    """

    # 5. 链接样式
    STYLE_LINK = f"""
        color: {COLOR_PRIMARY};
        text-decoration: none;
        font-size: 13px;
        font-weight: bold;
    """

    @classmethod
    def beautify(cls, html_content):
        # 结构映射替换
        html_content = re.sub(r'<aside>', f'<div style="{cls._clean(cls.STYLE_SUMMARY_BOX)}">', html_content)
        html_content = re.sub(r'</aside>', '</div>', html_content)
        html_content = re.sub(r'<section>', f'<div style="{cls._clean(cls.STYLE_SECTION)}">', html_content)
        html_content = re.sub(r'</section>', '</div>', html_content)
        html_content = re.sub(r'<nav>', f'<div style="{cls._clean(cls.STYLE_META)}">', html_content)
        html_content = re.sub(r'</nav>', '</div>', html_content)
        html_content = re.sub(r'<a href=', f'<a style="{cls._clean(cls.STYLE_LINK)}" href=', html_content)
        
        return f'<div style="{cls._clean(cls.STYLE_WRAPPER)}">{html_content}</div>'

    @staticmethod
    def _clean(css_str):
        return css_str.replace('\n', ' ').strip()