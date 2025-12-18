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

    def upload_cover_image(self, image_path):
        """
        上传封面图片到微信'永久素材'库
        返回: media_id (这是发文章必须的封面ID)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"❌ 找不到封面图: {image_path}，请确保目录下有一张名为 cover.jpg 的图片！")

        token = self.get_access_token()
        # 永久素材上传接口
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        
        print(f"📤 正在上传封面图: {image_path} ...")
        
        try:
            # 打开图片并上传
            with open(image_path, 'rb') as f:
                files = {'media': f}
                # 注意：上传文件不需要手动设置 Content-Type，requests 会自动处理
                resp = requests.post(url, files=files)
                
            data = resp.json()
            
            if "media_id" not in data:
                raise Exception(f"图片上传失败: {data}")
                
            print(f"✅ 图片上传成功! Media ID: {data['media_id']}")
            return data['media_id']
            
        except Exception as e:
            print(f"❌ 上传过程出错: {e}")
            raise

    def add_draft(self, title, content, thumb_media_id, digest=None): # 增加 digest 参数
        token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        article_payload = {
            "articles": [
                {
                    "title": title,
                    "author": "AI助手",
                    "digest": digest or "今日AI要闻汇总", # 优先使用传入的摘要
                    "content": content,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0
                }
            ]
        }

        # 发送请求 (注意处理中文编码)
        resp = requests.post(
            url, 
            data=json.dumps(article_payload, ensure_ascii=False).encode('utf-8')
        )
        data = resp.json()
        
        if "media_id" in data:
            print(f"🎉 草稿创建成功！Media ID: {data['media_id']}")
            return data['media_id']
        else:
            raise Exception(f"草稿创建失败: {data}")

# 方便外部调用的单例实例
wechat_client = WeChatClient()

if __name__ == "__main__":
    print("🚀 开始执行微信推送测试...")
    
    try:
        # 1. 确保目录下有一张名为 cover.jpg 的图片
        # 如果没有，请随便找一张 jpg 图片重命名放进去
        media_id = wechat_client.upload_cover_image("cover.jpg")
        
        # 2. 准备测试内容
        test_title = "Python自动推送测试"
        test_content = """
        <h1>你好！Success!</h1>
        <p>这是来自 Python 代码的测试消息。</p>
        <p>如果你看到这个，说明 API 链路已经打通。</p>
        <hr>
        <p>Generated by 07_news2 project.</p>
        """
        
        # 3. 发送草稿
        wechat_client.add_draft(test_title, test_content, media_id)
        
        print("\n✨ 全部完成！请前往微信公众号后台 -> 内容与互动 -> 草稿箱 查看结果！")
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")