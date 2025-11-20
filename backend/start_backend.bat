@echo off
echo Starting Backend Server...
cd /d %~dp0
.\venv\Scripts\activate          
python main.py 
pause

