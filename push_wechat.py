import os
import json
import time
import requests
from config import settings  # 导入你的配置中心

class WeChatClient:
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.secret = settings.WECHAT_APPSECRET
        # Token 缓存文件的路径 (放在当前目录下)
        self.token_file = "wechat_token.json"

    def _get_access_token_from_wechat(self):
        """
        直接从微信服务器获取新的 Access Token
        """
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }
        
        print("🔄 正在向微信 API 请求新的 Access Token...")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # 检查 HTTP 网络错误
            data = response.json()
            
            # 检查微信业务逻辑错误 (例如 appid 填错)
            if "errcode" in data and data["errcode"] != 0:
                raise Exception(f"微信API报错: {data.get('errmsg')} (错误码: {data.get('errcode')})")
                
            return data["access_token"], data["expires_in"]
            
        except Exception as e:
            print(f"❌ 获取 Token 失败: {e}")
            raise

    def get_access_token(self):
        """
        获取 Access Token 的主入口
        逻辑：读取本地缓存 -> 检查是否过期 -> (过期则)重新获取 -> 返回 Token
        """
        current_time = time.time()
        
        # 1. 尝试读取本地缓存文件
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    cache = json.load(f)
                    
                expires_at = cache.get("expires_at", 0)
                
                # 2. 检查是否过期
                # 我们预留 200 秒的缓冲时间，防止卡在临界点
                if current_time < expires_at - 200:
                    # print("✅ 使用本地缓存的 Access Token") # 调试用，实际运行可注释
                    return cache["access_token"]
                else:
                    print("⚠️ 本地 Token 已过期或即将过期")
            except Exception:
                print("⚠️ 本地缓存文件损坏，将重新获取")

        # 3. 如果没有缓存或已过期，执行远程获取
        token, expires_in = self._get_access_token_from_wechat()
        
        # 4. 保存到本地文件
        self._save_token_to_file(token, expires_in, current_time)
        
        return token

    def _save_token_to_file(self, token, expires_in, current_time):
        """将 Token 和过期时间写入文件"""
        try:
            expiration_time = int(current_time + expires_in)
            data = {
                "access_token": token,
                "expires_at": expiration_time
            }
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
            print(f"💾 新 Token 已缓存，有效期至: {time.ctime(expiration_time)} (当前时间: {time.ctime(current_time)})")
        except Exception as e:
            print(f"❌ Token 写入本地文件失败: {e}")
            raise
# 方便外部调用的单例实例
wechat_client = WeChatClient()

if __name__ == "__main__":
    # 测试代码：直接运行此文件可测试 Token 获取是否成功
    try:
        token = wechat_client.get_access_token()
        print(f"测试成功！Token: {token[:15]}...")
    except Exception as e:
        print("测试失败，请检查 .env 配置")