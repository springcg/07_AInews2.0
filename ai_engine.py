import feedparser
import time
import html
import re
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from config import settings
import json

# --- 1. 配置区域 ---
# DeepSeek API 配置
# 注意：DeepSeek 的模型名称通常是 deepseek-chat (对应 V3) 或 deepseek-reasoner (对应 R1)
MODEL_NAME = "deepseek-chat" 
API_BASE_URL = "https://api.deepseek.com"

# RSS 数据源列表
# ai_engine.py

# RSS 数据源列表：已去除国外源，替换为中文高质量科技媒体
RSS_FEEDS = [
    # 中文源
    {"name": "36氪", "url": "https://36kr.com/feed"},
    {"name": "爱范儿", "url": "https://www.ifanr.com/feed"},
    {"name": "少数派", "url": "https://sspai.com/feed"},
    # 英文源（AI 相关）
    {"name": "Hacker News AI", "url": "https://hnrss.org/newest?q=AI"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
]

def clean_html(raw_html):
    """去除 RSS 摘要中的 HTML 标签，节省 Token"""
    if not raw_html:
        return ""
    # 解码 HTML 实体 (如 &nbsp; -> 空格)
    text = html.unescape(raw_html)
    # 去除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 合并多余空白
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_single_feed(feed):
    """抓取单个 RSS 源，只提取 24 小时内的文章"""
    print(f"📡 正在抓取: {feed['name']}...")
    try:
        # 解析 RSS
        parsed = feedparser.parse(feed['url'])
        entries = []
        
        # 使用 UTC 时间进行统一比较
        now_utc = datetime.now(timezone.utc)
        one_day_ago = now_utc - timedelta(hours=24)

        for entry in parsed.entries:
            # 尝试获取发布时间（统一转为 UTC aware datetime）
            published_time = None
            time_struct = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
            if time_struct:
                # mktime + fromtimestamp 得到的是本地时间，转为 UTC
                published_time = datetime.fromtimestamp(
                    time.mktime(time_struct), tz=timezone.utc
                )
            
            if not published_time or published_time > one_day_ago:
                title = entry.get('title', '无标题')
                link = entry.get('link', '')
                summary = clean_html(entry.get('summary', '')[:200]) # 截断摘要，防止 Token 溢出
                
                entries.append(f"- 来源: {feed['name']}\n  标题: {title}\n  链接: {link}\n  摘要: {summary}\n")
                
                # 每个源最多取 5 条，控制总量和 Token 消耗
                if len(entries) >= 5:
                    break
        return entries
    except Exception as e:
        print(f"❌ 抓取 {feed['name']} 失败: {e}")
        return []

def get_aggregated_news():
    """并发抓取所有 RSS 并合并文本"""
    all_content = []
    # 使用线程池并发抓取，提高速度
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_single_feed, RSS_FEEDS)
    
    for res in results:
        all_content.extend(res)
    
    return "\n".join(all_content)

def summarize_with_ai(content):
    if not content.strip():
        return None

    print(f"🤖 正在调用 DeepSeek 进行总结 (JSON 模式)...")
    
    client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=API_BASE_URL)

    # 修改 Prompt，明确 JSON 结构
    prompt = f"""
    请从以下 RSS 数据中筛选出最重要的 15-20 条 AI 行业信息，并严格以 JSON 格式输出。
    
    JSON 结构要求：
    {{
        "daily_summary": "一句话总结今日行业趋势",
        "articles": [
            {{
                "title": "新闻标题",
                "source": "来源名称",
                "type": "技术突破/开源/行业动态",
                "description": "核心内容解读（中文，一百字左右说明重要性）",
                "link": "原文链接URL"
            }}
        ]
    }}

    【待处理数据】：
    {content}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}, 
            stream=False,
            timeout=60  # 60 秒超时
        )
        
        raw_json = response.choices[0].message.content
        return json.loads(raw_json)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return None
    except Exception as e:
        print(f"⚠️ 第一次调用失败: {e}，正在重试...")
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
                stream=False,
                timeout=60
            )
            raw_json = response.choices[0].message.content
            return json.loads(raw_json)
        except Exception as retry_e:
            print(f"❌ 重试仍然失败: {retry_e}")
            return None

# --- 主函数用于测试 ---
if __name__ == "__main__":
    # 1. 获取原始内容
    raw_content = get_aggregated_news()
    #print(raw_content)
    
    if raw_content:
        # 2. 生成总结
        ai_summary = summarize_with_ai(raw_content)
        if ai_summary:
            print("\n" + "="*20 + " 生成结果预览 " + "="*20)
            print(ai_summary)
    else:
        print("没有抓取到任何新闻。")