@echo off
echo Устанавливаю зависимости...
pip install -r requirements.txt

echo.
echo Загружаю переменные из .env...
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if not "%%A"=="" if not "%%A:~0,1%"=="#" set "%%A=%%B"
)

echo.
echo Запускаю бота...
python bot.py
pause
