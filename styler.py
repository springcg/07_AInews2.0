import re

class WeChatStyler:
    """
    微信公众号文章美化器 (专业增强版)
    """
    
    # --- 核心配色 ---
    COLOR_PRIMARY = "#007AFF"      # 科技蓝
    COLOR_SECONDARY = "#F8FAFF"    # 极浅蓝背景
    COLOR_TEXT_MAIN = "#333333"    # 主文字
    COLOR_TEXT_SUB = "#666666"     # 次要文字
    COLOR_BORDER = "#E1E8F5"       # 边框色
    
    # --- CSS 样式模板 ---
    
    # 全局容器：增加字间距和基础行高
    STYLE_WRAPPER = f"""
        max-width: 677px; 
        margin: 0 auto; 
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
        font-size: 16px;
        color: {COLOR_TEXT_MAIN};
        line-height: 1.8;
        letter-spacing: 0.5px;
    """

    # H2 章节标题：带背景色的药丸形状或精致左边框
    STYLE_H2 = f"""
        display: inline-block;
        background-color: {COLOR_PRIMARY};
        color: #ffffff;
        padding: 5px 20px;
        border-radius: 50px 50px 50px 0;
        margin-top: 40px;
        margin-bottom: 20px;
        font-size: 19px;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,122,255,0.2);
    """

    # H3 行业风向标文字 (引用块中的标题)
    STYLE_H3 = f"""
        margin-top: 5px;
        margin-bottom: 10px;
        font-size: 17px;
        font-weight: bold;
        color: {COLOR_PRIMARY};
    """

    # H4 新闻小标题：加粗并带下划线装饰
    STYLE_H4 = f"""
        margin-top: 25px;
        margin-bottom: 12px;
        font-size: 17px;
        font-weight: bold;
        color: {COLOR_TEXT_MAIN};
        border-left: 4px solid {COLOR_PRIMARY};
        padding-left: 12px;
    """

    # 正文段落：两端对齐
    STYLE_P = f"""
        font-size: 15px;
        color: {COLOR_TEXT_SUB};
        line-height: 1.75;
        margin-bottom: 15px;
        text-align: justify;
    """

    # 引用块：整体背景灰色
    STYLE_BLOCKQUOTE = f"""
        background-color: {COLOR_SECONDARY};
        border: 1px solid {COLOR_BORDER};
        padding: 20px;
        margin: 25px 0;
        border-radius: 12px;
        position: relative;
    """

    # 列表项
    STYLE_LI = f"""
        font-size: 15px;
        color: {COLOR_TEXT_SUB};
        margin-bottom: 10px;
        list-style-type: none;
        padding-left: 0;
    """

    # 链接
    STYLE_LINK = f"""
        color: {COLOR_PRIMARY};
        text-decoration: none;
        font-size: 14px;
        border-bottom: 1px solid {COLOR_PRIMARY};
    """

    # 分割线
    STYLE_HR = f"""
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 122, 255, 0), rgba(0, 122, 255, 0.5), rgba(0, 122, 255, 0));
        margin: 30px 0;
    """

    @classmethod
    def beautify(cls, html_content):
        # 1. 标题替换 (注意顺序，先替换 H4 再替换 H3, H2)
        html_content = re.sub(r'<h4>', f'<h4 style="{cls._clean(cls.STYLE_H4)}">', html_content)
        html_content = re.sub(r'<h3>', f'<h3 style="{cls._clean(cls.STYLE_H3)}">', html_content)
        html_content = re.sub(r'<h2>', f'<h2 style="{cls._clean(cls.STYLE_H2)}">', html_content)
        
        # 2. 块元素
        html_content = re.sub(r'<p>', f'<p style="{cls._clean(cls.STYLE_P)}">', html_content)
        html_content = re.sub(r'<blockquote>', f'<blockquote style="{cls._clean(cls.STYLE_BLOCKQUOTE)}">', html_content)
        html_content = re.sub(r'<hr />', f'<hr style="{cls._clean(cls.STYLE_HR)}">', html_content)
        html_content = re.sub(r'<hr>', f'<hr style="{cls._clean(cls.STYLE_HR)}">', html_content)
        
        # 3. 列表与链接
        html_content = re.sub(r'<li>', f'<li style="{cls._clean(cls.STYLE_LI)}">', html_content)
        html_content = re.sub(r'<a href=', f'<a style="{cls._clean(cls.STYLE_LINK)}" href=', html_content)
        
        # 4. 加粗强调
        html_content = re.sub(r'<strong>', f'<strong style="color:{cls.COLOR_PRIMARY};font-weight:bold;">', html_content)

        # 5. 包装
        wrapper = f'<div style="{cls._clean(cls.STYLE_WRAPPER)}">{html_content}</div>'
        return wrapper

    @staticmethod
    def _clean(css_str):
        return css_str.replace('\n', '').strip()