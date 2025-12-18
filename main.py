import time
from datetime import date
from ai_engine import get_aggregated_news, summarize_with_ai
from push_wechat import wechat_client
from push_pushplus import send_pushplus
from styler import WeChatStyler

# main.py

# main.py

# main.py (部分代码修改)

# main.py

def dict_to_html(data):
    parts = []
    parts.append(
        f"<aside><strong>💡 今日风向标：</strong>{data.get('daily_summary', '')}</aside>"
    )

    for i, item in enumerate(data.get("articles", []), 1):
        source = item.get("source", "未知")
        category = item.get("type", "动态")
        parts.append(
            f"<section>"
            f'<h2 style="font-size:17px; margin:0 0 5px 0;">{i}. {item.get("title", "")}</h2>'
            f"<nav>来源：{source} | 类别：{category}</nav>"
            f'<p style="font-size:14px; color:#444; margin:5px 0;">{item.get("description", "")}</p>'
            f'<div style="text-align: right;"><a href="{item.get("link", "#")}">阅读原文 →</a></div>'
            f"</section>"
        )

    return "".join(parts)

# 后面保持 main() 函数中对 WeChatStyler.beautify(raw_html) 的调用即可

def main():
    print("🚀 === AI 每日新闻任务启动 (JSON 模式) ===")
    
    # --- 第一步：抓取与生成 ---
    print("\n1️⃣ 正在抓取 RSS 并生成 AI 结构化数据...")
    raw_content = get_aggregated_news()
    # 此时 ai_data 是一个字典，包含 daily_summary 和 articles
    ai_data = summarize_with_ai(raw_content)
    
    if not ai_data or 'articles' not in ai_data:
        print("❌ 生成内容为空或格式错误，终止任务。")
        return

    # --- 第二步：准备标题和日期 ---
    today_str = date.today().strftime("%Y-%m-%d")
    title = f"AI 每日早报 ({today_str})"
    
    # --- 第三步：推送到 PushPlus (现在会自动格式化) ---
    print("\n2️⃣ 正在通过 PushPlus 推送消息...")
    # 直接把 AI 返回的字典传进去即可
    send_pushplus(ai_data)
    
    # --- 第四步：推送到微信公众号草稿箱 ---
    print("\n3️⃣ 正在生成公众号排版并推送到草稿箱...")
    try:
        # 4.1 将 JSON 字典转成原始 HTML
        raw_html = dict_to_html(ai_data)
        
        # 4.2 调用美化器注入内联 CSS
        print("🎨 正在进行排版美化...")
        styled_content = WeChatStyler.beautify(raw_html)
        
        # 4.3 最终内容：避免三引号带来的多余换行/缩进
        final_content = styled_content.strip()
        
        # 4.4 上传封面图 (保持不变，确保目录下有 cover.jpg)
        media_id = wechat_client.upload_cover_image("cover.jpg")
        
        # 4.5 新建草稿
        # 传入 ai_data['daily_summary'] 作为摘要，让微信卡片显示更专业
        wechat_client.add_draft(
            title=title, 
            content=final_content, 
            thumb_media_id=media_id,
            digest=ai_data.get('daily_summary')
        )
        
    except Exception as e:
        print(f"❌ 微信公众号推送失败: {e}")

    print("\n✅ === 任务全部完成！请去公众号后台查看草稿 === ")

if __name__ == "__main__":
    main()
