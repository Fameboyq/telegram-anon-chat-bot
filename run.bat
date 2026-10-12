@echo off
title Telegram Anonymous Chat Bot
echo ======================================================
echo    Telegram Anonymous Chat Bot - Launcher
echo ======================================================
echo.

if not exist .env (
    echo [!] File .env not found. Creating from .env.example...
    copy .env.example .env
    echo [!] Please open .env and put your BOT_TOKEN from @BotFather!
    notepad .env
    pause
)

echo [*] Installing dependencies if needed...
python -m pip install -r requirements.txt

echo.
echo [*] Starting bot...
python bot.py
pause
