# Macro Bot

This project collects US and China macroeconomic data and sends a concise brief to Discord. It fetches data from FRED, compiles a US vs. CN macro summary, and pushes the result through a Discord bot.

## Project Structure

- `fetch_us_macro.py`: pulls US macro data such as 10Y/2Y Treasury yields, real rates, HY OAS, and VIX
- `fetch_cn_macro.py`: pulls China macro proxy data such as CPI, FX, industrial production, and private credit/GDP
- `make_macro_brief.py`: combines the fetched data and generates the macro brief text
- `run_and_send_brief.py`: generates the brief and posts it to Discord
- `send_discord.py`: sends a quick test message to Discord
- `check_cn_series.py`: checks whether the China proxy series are available
- `runner.cmd`: Windows scheduler entry point for automated runs

## Before You Run

1. Create and fill in your environment file:
   ```bash
   copy .env.example .env
   ```
   Then edit `.env`:
   ```env
   FRED_API_KEY=your_fred_api_key_here
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   DISCORD_CHANNEL_ID=your_discord_channel_id_here
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Verify the fetch scripts:
   ```bash
   python fetch_us_macro.py
   python fetch_cn_macro.py
   python make_macro_brief.py
   ```

4. Test Discord delivery:
   ```bash
   python send_discord.py
   ```

## Windows Scheduled Task

You can use `runner.cmd` with Windows Task Scheduler to trigger the workflow on a schedule:

```cmd
runner.cmd
```

If you run it via Windows Task Scheduler, set the working directory to the project folder and invoke it with `cmd /c`.

## Important Notes

- Do not commit `.env` to GitHub
- Do not expose real Discord tokens or FRED API keys
- This project includes `.gitignore` to ignore logs, caches, and environment files

## License

This project is intended for learning and automation experiments only.