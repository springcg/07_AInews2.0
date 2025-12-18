import requests
import os
import base64
import io
from datetime import date
from config import settings  # 导入配置中心

def format_to_markdown(data):
    """
    将 JSON 字典格式化为经典的 Markdown 样式，保持与之前 AI 输出一致
    """
    # 1. 行业风向标部分
    md = f"## 🌪 行业风向标\n"
    md += f"> {data.get('daily_summary', '')}\n\n"
    md += "---\n\n"
    
    # 2. 核心速览部分
    md += "### 核心速览\n"
    for i, item in enumerate(data.get('articles', []), 1):
        md += f"#### {i}. {item.get('title')}\n"
        md += f"- **来源**: {item.get('source')}\n"
        md += f"- **类型**: {item.get('type', '行业动态')}\n"
        md += f"- **深度解读**: {item.get('description')}\n"
        md += f"- [🔗 原文链接]({item.get('link')})\n\n"
        
    md += "---\n"
    md += f"> *Generated Sun's Workflow | {date.today()}*"
    return md

def _build_cover_block(image_path: str = "cover.jpg") -> str:
    cover_url = (settings.PUSHPLUS_COVER_URL or "").strip()
    if cover_url:
        return f'<p><img src="{cover_url}" style="max-width:100%;height:auto;" /></p>\n\n'

    if not os.path.exists(image_path):
        return ""

    try:
        file_size = os.path.getsize(image_path)
        max_bytes = 500 * 1024
        if file_size > max_bytes:
            try:
                from PIL import Image  # pyright: ignore[reportMissingImports]
            except Exception:
                print(
                    f"⚠️ cover.jpg 体积过大({file_size/1024:.0f}KB)，PushPlus 已跳过封面；"
                    f"可设置 PUSHPLUS_COVER_URL 为公网图片链接，或安装 pillow 后自动压缩。"
                )
                return ""

            with Image.open(image_path) as image:
                image = image.convert("RGB")
                max_width = 720
                if image.width > max_width:
                    new_height = int(image.height * (max_width / image.width))
                    image = image.resize((max_width, new_height))
                buf = io.BytesIO()
                image.save(buf, format="JPEG", quality=70, optimize=True)
                jpg_bytes = buf.getvalue()
        else:
            with open(image_path, "rb") as f:
                jpg_bytes = f.read()

        b64 = base64.b64encode(jpg_bytes).decode("ascii")
        return (
            f'<p><img src="data:image/jpeg;base64,{b64}" style="max-width:100%;height:auto;" /></p>\n\n'
        )
    except Exception as e:
        print(f"⚠️ 处理 PushPlus 封面图失败，已跳过: {e}")
        return ""

def send_pushplus(ai_data):
    """
    通过 PushPlus 推送消息。
    现在接收 AI 生成的字典对象 (ai_data)
    """
    # 检查 Token 是否配置
    if not settings.PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过 PushPlus 推送。")
        return

    print("🚀 正在构造 Markdown 样式并推送...")
    
    # --- 关键修改：将字典转回 Markdown 字符串 ---
    content_md = _build_cover_block() + format_to_markdown(ai_data)
    
    url = "http://www.pushplus.plus/send"
    
    # 构造请求数据
    data = {
        "token": settings.PUSHPLUS_TOKEN,    # 从配置中心获取 Token
        "title": f"AI早报 {date.today()}",   # 自动加上今天的日期
        "content": content_md,               # 使用格式化后的 Markdown
        "template": "markdown"               # 指定使用 Markdown 渲染
    }
    
    try:
        # 发送请求
        response = requests.post(url, json=data)
        response.raise_for_status() 
        
        result = response.json()
        
        # 检查业务层面的错误
        if result.get("code") == 200:
            print(f"✅ PushPlus 推送成功! (样式：经典 Markdown)")
        else:
            print(f"❌ PushPlus 推送失败: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ PushPlus 请求出错: {e}")

# --- 测试入口 ---
if __name__ == "__main__":
    # 模拟 AI 输出的 JSON 字典进行测试
    test_json = {
        "daily_summary": "今日 AI 行业聚焦于大模型效率提升与开源生态补完。",
        "articles": [
            {
                "title": "DeepSeek V3 震撼发布",
                "source": "机器之心",
                "type": "技术突破",
                "description": "这是目前最强的开源模型之一，性能逼近 GPT-4o。",
                "link": "https://www.example.com"
            }
        ]
    }
    send_pushplus(test_json)
