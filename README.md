## AI 每日新闻机器人 (v2.0)

一个每天自动抓取多源 AI 相关 RSS、用 DeepSeek 总结，并推送到 PushPlus 和微信公众号草稿箱的脚本。

### 一、环境准备

- **Python 版本**: 建议 Python 3.10+
- **创建虚拟环境（推荐）**：
  ```bash
  python -m venv .venv
  .venv\\Scripts\\activate  # Windows PowerShell
  # 或
  source .venv/bin/activate     # Linux / macOS
  ```
- **安装依赖**：
  ```bash
  pip install -r requirements.txt
  ```

### 二、配置 .env

1. 复制示例文件：
   ```bash
   cp .env.example .env  # Windows 可直接复制文件
   ```
2. 打开 `.env`，填写以下字段：
   - `DEEPSEEK_API_KEY`：DeepSeek 提供的 API Key
   - `WECHAT_APPID` / `WECHAT_APPSECRET`：你的公众号开发配置
   - `PUSHPLUS_TOKEN`：PushPlus 个人推送 Token

> 注意：`.env` 和 `wechat_token.json` 已在 `.gitignore` 中忽略，不会被提交到版本库。

### 三、如何运行

#### 1. 本地 dry-run 预览（不推送）

```bash
python main.py --dry-run
```

- 终端会打印一份完整的 Markdown 版「AI 每日早报」，不推送到任何渠道。

#### 2. 正常推送

```bash
python main.py
```

可选参数：
- `--no-wechat`：只推送到 PushPlus，不创建公众号草稿。
- `--no-pushplus`：只创建公众号草稿，不推送 PushPlus。

示例：
```bash
# 只推送到公众号
python main.py --no-pushplus

# 只推送 PushPlus
python main.py --no-wechat
```

### 四、定时任务示例

#### Windows 任务计划程序

1. 打开“任务计划程序” -> 创建基本任务。
2. 触发器选择“每天”，设置时间，例如早上 8:30。
3. 操作选择“启动程序”，填写：
   - 程序/脚本：`python`
   - 参数：`e:/code/python/cursor/07_news2/main.py`
   - 起始于：项目目录 `e:/code/python/cursor/07_news2`

#### Linux crontab

```bash
crontab -e
# 每天早上 8:30 运行
30 8 * * * /usr/bin/python3 /path/to/07_news2/main.py >> /var/log/ai_news.log 2>&1
```

### 五、开发与测试小提示

- 单独测试 RSS 抓取与总结：
  ```bash
  python ai_engine.py
  ```
- 单独测试微信公众号链路：
  ```bash
  python push_wechat.py
  ```
- 单独测试 PushPlus：
  ```bash
  python push_pushplus.py
  ```

后续如需扩展新的 RSS 源或推送渠道，优先在现有模块中按照中文注释的说明进行修改即可。