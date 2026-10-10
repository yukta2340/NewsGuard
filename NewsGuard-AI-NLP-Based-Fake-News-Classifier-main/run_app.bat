@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting NewsGuard AI with Live Google News Integration
echo ========================================================
python -m streamlit run app.py
pause
