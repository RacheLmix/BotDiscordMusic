@echo off
title Shoko Singer
cd /d D:\BotDiscord

start "" java -jar Lavalink\Lavalink.jar
timeout /t 3 >nul
python main.py
