@echo off
echo Starting AI PDF Invoice Processor Dashboard...
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Dependencies installed (pip install -r requirements.txt)
echo 3. .env file with GEMINI_API_KEY configured
echo.
echo Opening dashboard in your browser...
echo.
streamlit run app_streamlit.py
pause
