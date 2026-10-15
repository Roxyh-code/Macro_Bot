@echo off
setlocal
cd /d "%~dp0"

REM 强制 Python 用 UTF-8（避免 GBK/emoji 问题）
set PYTHONUTF8=1

REM 记录每次触发时间
echo ===== %date% %time% =====>> runner.log

REM 使用 py launcher（若可用），否则回退到 python
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%~dp0run_and_send_brief.py" >> run_stdout.log 2>> run_stderr.log
) else (
    python "%~dp0run_and_send_brief.py" >> run_stdout.log 2>> run_stderr.log
)

REM 记录退出码
echo exit_code=%errorlevel%>> runner.log
