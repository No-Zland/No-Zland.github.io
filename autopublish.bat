@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 博客自动发布
python autopublish.py %*
echo.
echo 监听已结束，按任意键关闭窗口。
pause >nul
