import requests
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
    content_md = format_to_markdown(ai_data)
    
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