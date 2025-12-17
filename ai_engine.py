import feedparser
import time
import html
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from config import settings  # 导入你的配置中心

# --- 1. 配置区域 ---
# DeepSeek API 配置
# 注意：DeepSeek 的模型名称通常是 deepseek-chat (对应 V3) 或 deepseek-reasoner (对应 R1)
MODEL_NAME = "deepseek-chat" 
API_BASE_URL = "https://api.deepseek.com"

# RSS 数据源列表
RSS_FEEDS = [
    # --- 综合新闻 ---
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
    {"name": "Hacker News (AI)", "url": "https://hnrss.org/newest?q=AI"},
    # --- 官方技术博客 ---
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "Google DeepMind", "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml"},
    {"name": "Microsoft Research", "url": "https://www.microsoft.com/en-us/research/feed/"},
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
    """调用 DeepSeek 进行筛选和总结"""
    if not content.strip():
        print("⚠️ 过去 24 小时没有检测到重要更新。")
        return None

    print(f"🤖 正在调用 DeepSeek 进行总结 (原始内容长度: {len(content)} 字符)...")
    
    # 初始化 OpenAI 客户端 (DeepSeek 兼容 OpenAI SDK)
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY, 
        base_url=API_BASE_URL
    )

    prompt = f"""
    你是 DeepSeek 驱动的首席AI科技编辑。请从以下 RSS 数据中筛选出最重要的 8-10 条信息，生成一份“每日AI早报”，按照重要程度降序排序,不需要对筛选进行反馈。

    【筛选标准 - 请基于以下维度评估，不重要的直接丢弃】：
    1. **技术突破**：SOTA模型发布、架构创新、性能大幅提升。
    2. **开源生态**：知名项目（如Llama, LangChain）的重大更新。
    3. **行业风向**：OpenAI/Google等巨头的战略动作。
    4. **过滤垃圾**：忽略纯营销软文、微小的Bug修复。

    【输入数据】：
    {content}

    【输出格式要求 (Markdown)】：
    ## 🌪 行业风向标
    > [一句话总结今天的整体技术或市场趋势]

    ---

    ### 核心速览
    #### 1. [新闻标题](按照新闻重要性降序排序)
    - **来源**: [来源名称]
    - **类型**: [技术突破/开源/行业动态]
    - **深度解读**: [用中文简述核心内容，并一句话说明它为什么重要]
    - [🔗 原文链接](URL)

    (依次列出8-10条...)
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, # 降低随机性，让筛选更严谨
            stream=False
        )
        result = response.choices[0].message.content
        print("✅ AI 总结完成！")
        return result
        
    except Exception as e:
        print(f"❌ 调用 DeepSeek 失败: {e}")
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