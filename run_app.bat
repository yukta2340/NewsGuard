@echo off
cd /d "%~dp0NewsGuard-AI-NLP-Based-Fake-News-Classifier-main"
echo ========================================================
echo Starting NewsGuard AI with Live Google News Integration
echo ========================================================
python -m streamlit run app.py
pause
