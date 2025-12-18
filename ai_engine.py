import feedparser
import time
import html
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from config import settings  # 导入你的配置中心
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
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
    {"name": "36氪 - AI专栏", "url": "https://rsshub.app/36kr/newsflashes"},
    {"name": "极客公园", "url": "https://www.geekpark.net/rss"},
    {"name": "APPSO (爱范儿)", "url": "https://www.ifanr.com/app/feed"},
    {"name": "AI前线 (InfoQ)", "url": "https://rsshub.app/infoq/topic/131"},
    # 额外补充一个高质量源，防止部分源临时失效
    {"name": "钛媒体 - AI专题", "url": "https://rsshub.app/tmtpost/column/234"}
]

def clean_html(raw_html):
    """去除 RSS 摘要中的 HTML 标签，节省 Token"""
    if not raw_html:
        return ""
    # 解码 HTML 实体 (如 &nbsp; -> 空格)
    text = html.unescape(raw_html)
    # 简单去除标签（为了保留结构，这里不做得太激进，交给 LLM 理解也可以）
    return text.strip()

def fetch_single_feed(feed):
    """抓取单个 RSS 源，只提取 24 小时内的文章"""
    print(f"📡 正在抓取: {feed['name']}...")
    try:
        # 解析 RSS
        parsed = feedparser.parse(feed['url'])
        entries = []
        
        # 获取当前时间（UTC）
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        one_day_ago = now - timedelta(hours=24)

        for entry in parsed.entries:
            # 尝试获取发布时间
            published_time = None
            if hasattr(entry, 'published_parsed'):
                published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed'):
                published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            
            # 如果没有时间戳，或者时间在 24 小时以内，则保留
            # (有些源没有时间戳，默认保留前 3 条以防漏掉)
            if not published_time or published_time > one_day_ago:
                title = entry.get('title', '无标题')
                link = entry.get('link', '')
                summary = clean_html(entry.get('summary', '')[:200]) # 截断摘要，防止 Token 溢出
                
                entries.append(f"- 来源: {feed['name']}\n  标题: {title}\n  链接: {link}\n  摘要: {summary}\n")
                
                # 每个源最多取前 5 条，防止单个源刷屏
                if len(entries) >= 10:
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
            # 如果是 DeepSeek 或 OpenAI 较新模型，建议开启 json_object 模式
            response_format={"type": "json_object"}, 
            stream=False
        )
        
        # 解析返回的 JSON 字符串为 Python 字典
        raw_json = response.choices[0].message.content
        return json.loads(raw_json)
        
    except Exception as e:
        print(f"❌ 调用 DeepSeek 失败或 JSON 解析错误: {e}")
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