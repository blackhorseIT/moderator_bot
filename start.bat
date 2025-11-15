@echo off
chcp 65001 > nul
title Telegram Moderator Bot
echo Starting Telegram Bot...

:: Активация виртуального окружения
call venv\Scripts\activate

:: Запуск бота
python main.py

pause