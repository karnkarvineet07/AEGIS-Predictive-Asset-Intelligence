@echo off
title AEGIS Predictive Asset Intelligence

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate

echo Installing/checking required packages...
pip install -r requirements.txt

echo Training AI model...
python -m ml.train_model

echo Starting AEGIS Dashboard...
start "" cmd /c "python app.py"
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5000"
pause