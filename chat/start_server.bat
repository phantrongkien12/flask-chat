@echo off
cd /d %~dp0
if exist venv\Scripts\activate (
  call venv\Scripts\activate
) else (
  python -m venv venv
  call venv\Scripts\activate
  pip install -r requirements.txt
)
python app.py
pause
