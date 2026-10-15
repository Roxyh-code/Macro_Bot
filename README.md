# Macro Bot

这是一个用于抓取美中宏观数据并将简报发送到 Discord 的 Python 自动化脚本集合。项目从 FRED 获取数据，整理出 US vs CN 的宏观简报，再通过 Discord Bot 推送消息。

## 目录说明

- `fetch_us_macro.py`: 拉取美国宏观数据（10Y/2Y Treasury、真实利率、HY OAS、VIX 等）
- `fetch_cn_macro.py`: 拉取中国宏观代理数据（CPI、汇率、工业生产、私人信贷/GDP 等）
- `make_macro_brief.py`: 整合数据，生成宏观简报文本
- `run_and_send_brief.py`: 生成简报并发送到 Discord
- `send_discord.py`: 发送测试消息到 Discord
- `check_cn_series.py`: 检查中国宏观代理序列是否可用
- `runner.cmd`: Windows 定时任务入口脚本

## 运行前准备

1. 创建并填写环境变量文件
   ```bash
   copy .env.example .env
   ```
   然后编辑 `.env`：
   ```env
   FRED_API_KEY=your_fred_api_key_here
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_CHANNEL_ID=your_discord_channel_id_here
   ```

2. 安装依赖
   ```bash
   python -m pip install -r requirements.txt
   ```

3. 验证抓数脚本
   ```bash
   python fetch_us_macro.py
   python fetch_cn_macro.py
   python make_macro_brief.py
   ```

4. 测试 Discord 发送
   ```bash
   python send_discord.py
   ```

## Windows 定时任务

使用 `runner.cmd` 可设为 Windows 任务计划程序，每天固定时间触发脚本：

```cmd
runner.cmd
```

如果使用 Windows 任务计划程序，建议将工作目录设置为项目根目录，并使用 `cmd /c` 调用脚本。

## 注意事项

- 不要将 `.env` 提交到 GitHub
- 不要提交真实的 Discord Token、Bot Token 或 FRED API Key
- 本项目中已加入 `.gitignore`，用于忽略日志、缓存和环境变量文件

## 许可

本项目仅用于学习和自动化脚本实验用途。