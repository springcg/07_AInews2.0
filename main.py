import time
from datetime import date
from ai_engine import get_aggregated_news, summarize_with_ai
from push_pushplus import send_pushplus


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
            # 现在没有微信公众附带超链接权限
            # f'<div style="text-align: right;"><a href="{item.get("link", "#")}">阅读原文 →</a></div>'
            f"</section>"
        )

    return "".join(parts)


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
    
    # --- 第四步：推送到微信公众号草稿箱（暂未启用） ---
    # 如需启用，取消以下注释，并在 .env 中配置 WECHAT_APPID 和 WECHAT_APPSECRET
    # from push_wechat import wechat_client
    # from styler import WeChatStyler
    # print("\n3️⃣ 正在生成公众号排版并推送到草稿箱...")
    # try:
    #     raw_html = dict_to_html(ai_data)
    #     styled_content = WeChatStyler.beautify(raw_html)
    #     final_content = styled_content.strip()
    #     media_id = wechat_client.upload_cover_image("cover.jpg")
    #     wechat_client.add_draft(
    #         title=title,
    #         content=final_content,
    #         thumb_media_id=media_id,
    #         digest=ai_data.get('daily_summary')
    #     )
    # except Exception as e:
    #     print(f"❌ 微信公众号推送失败: {e}")

    print("\n✅ === 任务完成！ === ")

if __name__ == "__main__":
    main()
