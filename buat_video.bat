@echo off
cd /d "%~dp0"
python -m src.pipeline --no-upload
pause
