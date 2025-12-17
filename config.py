import sys
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    配置类：
    Pydantic Settings 默认优先级：
    1. 系统环境变量 (Environment Variables)
    2. .env 文件 (Dotenv file)
    """
    
    # 定义需要的配置项
    # 注意：变量名建议与环境变量/ .env 中的键名保持一致（不区分大小写）
    DEEPSEEK_API_KEY: str
    WECHAT_APPID: str
    WECHAT_APPSECRET: str
    PUSHPLUS_TOKEN: str
    
    # 如果有不需要强校验或有默认值的配置，可以这样写：
    # debug_mode: bool = False

    # 配置 Pydantic 读取 .env 文件
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # 即使找不到 .env 文件也不报错（因为可能已经设置了系统环境变量）
        env_file_ignore_missing=True 
    )

def get_settings():
    try:
        # 实例化时，Pydantic 会自动按照优先级寻找变量
        return Settings()
    except ValidationError as e:
        print("\n" + "="*30)
        print("❌ 配置初始化失败！")
        print("="*30)
        
        # 提取缺失的字段信息
        for error in e.errors():
            # loc 是错误发生的位置，通常是字段名
            field_name = error['loc'][0]
            print(f"👉 缺失配置项: {field_name}")
            print(f"   原因: 在系统环境变量或 .env 文件中均未找到该配置，且未设置默认值。")
        
        print("\n💡 解决方案:")
        print("1. 在系统环境变量中设置对应的变量。")
        print("2. 在项目根目录创建 .env 文件并写入配置，例如：")
        print(f"   {e.errors()[0]['loc'][0].upper()}=your_value_here")
        print("="*30 + "\n")
        
        # 强制退出程序，避免后续逻辑因缺少 Key 而崩溃
        sys.exit(1)

# 全局实例化一个 settings 对象，供其他文件导入使用
settings = get_settings()