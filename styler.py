import re

class WeChatStyler:
    """
    微信公众号文章美化器
    核心逻辑：通过正则替换，将裸奔的 HTML 标签加上内联 CSS 样式
    """
    
    # --- 样式配置 (科技蓝主题) ---
    COLOR_PRIMARY = "#007AFF"      # 主色调（科技蓝）
    COLOR_SECONDARY = "#F2F8FF"    # 浅色背景（用于引用块）
    COLOR_TEXT = "#333333"         # 正文颜色
    COLOR_LIGHT_TEXT = "#888888"   # 辅助文本颜色
    
    # --- CSS 样式模板 ---
    STYLE_H2 = f"""
        display: block;
        border-left: 4px solid {COLOR_PRIMARY};
        padding-left: 10px;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 18px;
        font-weight: bold;
        color: {COLOR_TEXT};
        line-height: 1.4;
    """
    
    STYLE_H3 = f"""
        margin-top: 20px;
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
        color: {COLOR_TEXT};
    """
    
    STYLE_P = f"""
        font-size: 15px;
        color: {COLOR_TEXT};
        line-height: 1.75;
        margin-bottom: 15px;
        text-align: justify; 
    """
    
    STYLE_BLOCKQUOTE = f"""
        background-color: {COLOR_SECONDARY};
        border-left: 3px solid {COLOR_PRIMARY};
        padding: 15px;
        margin: 20px 0;
        color: #555;
        font-size: 14px;
        border-radius: 4px;
    """
    
    STYLE_LI = f"""
        font-size: 15px;
        color: {COLOR_TEXT};
        line-height: 1.75;
        margin-bottom: 8px;
    """
    
    STYLE_STRONG = f"""
        color: {COLOR_PRIMARY};
        font-weight: bold;
    """
    
    STYLE_LINK = f"""
        color: {COLOR_PRIMARY};
        text-decoration: none;
        border-bottom: 1px dashed {COLOR_PRIMARY};
    """

    @classmethod
    def beautify(cls, html_content):
        """
        输入原始 HTML，输出美化后的 HTML
        """
        # 1. 给 <h2> 添加样式 (通常用作大标题)
        html_content = re.sub(
            r'<h2>', 
            f'<h2 style="{cls._clean(cls.STYLE_H2)}">', 
            html_content
        )
        
        # 2. 给 <h3> 添加样式 (小标题)
        html_content = re.sub(
            r'<h3>', 
            f'<h3 style="{cls._clean(cls.STYLE_H3)}">', 
            html_content
        )
        
        # 3. 给 <p> 添加样式
        html_content = re.sub(
            r'<p>', 
            f'<p style="{cls._clean(cls.STYLE_P)}">', 
            html_content
        )
        
        # 4. 给 <blockquote> 添加样式 (引用/摘要)
        html_content = re.sub(
            r'<blockquote>', 
            f'<blockquote style="{cls._clean(cls.STYLE_BLOCKQUOTE)}">', 
            html_content
        )
        
        # 5. 给 <li> 添加样式 (列表项)
        html_content = re.sub(
            r'<li>', 
            f'<li style="{cls._clean(cls.STYLE_LI)}">', 
            html_content
        )
        
        # 6. 给 <strong> 添加样式 (加粗文字)
        html_content = re.sub(
            r'<strong>', 
            f'<strong style="{cls._clean(cls.STYLE_STRONG)}">', 
            html_content
        )
        
        # 7. 给 <a> 添加样式 (链接)
        html_content = re.sub(
            r'<a href=', 
            f'<a style="{cls._clean(cls.STYLE_LINK)}" href=', 
            html_content
        )

        # 8. 包装最外层容器 (确保在微信里有左右边距)
        wrapper = f"""
        <div style="max-width: 677px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;">
            {html_content}
        </div>
        """
        return wrapper

    @staticmethod
    def _clean(css_str):
        """去除换行符和多余空格，压缩 CSS"""
        return css_str.replace('\n', '').strip()