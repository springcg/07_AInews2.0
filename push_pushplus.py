import requests
from datetime import date
from config import settings  # 导入配置中心

def send_pushplus(content):
    """
    通过 PushPlus 推送 Markdown 消息到微信
    """
    # 检查 Token 是否配置
    if not settings.PUSHPLUS_TOKEN:
        print("⚠️ 未配置 PUSHPLUS_TOKEN，跳过 PushPlus 推送。")
        return

    print("🚀 正在通过 PushPlus 推送消息...")
    
    url = "http://www.pushplus.plus/send"
    
    # 构造请求数据
    data = {
        "token": settings.PUSHPLUS_TOKEN,    # 从配置中心获取 Token
        "title": f"AI早报 {date.today()}",   # 自动加上今天的日期
        "content": content,
        "template": "markdown"               # 指定使用 Markdown 渲染
    }
    
    try:
        # 发送请求
        response = requests.post(url, json=data)
        response.raise_for_status() # 检查网络层面的错误 (如 404, 500)
        
        result = response.json()
        
        # 检查业务层面的错误 (PushPlus 成功通常返回 code 200)
        if result.get("code") == 200:
            print(f"✅ PushPlus 推送成功! (消息ID: {result.get('data')})")
        else:
            print(f"❌ PushPlus 推送失败: {result.get('msg')}")
            
    except Exception as e:
        print(f"❌ PushPlus 请求出错: {e}")

# --- 测试入口 ---
if __name__ == "__main__":
    # 确保 .env 里填了 PUSHPLUS_TOKEN 才能测试成功
    test_content = """
# 🎉 PushPlus 测试成功
- **时间**: 刚刚
- **状态**: ✅ API 连通
- **来源**: Python 脚本

> 祝你今天代码无 Bug！
    """
    
    send_pushplus(test_content)