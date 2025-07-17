# Скрипт для настройки базы данных на Windows
# Запускать в PowerShell

Write-Host "Установка зависимостей..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "Создание первой миграции..." -ForegroundColor Green
alembic revision --autogenerate -m "Initial migration"

Write-Host "Применение миграций..." -ForegroundColor Green
alembic upgrade head

Write-Host "Проверка базы данных..." -ForegroundColor Green
python check_database.py

Write-Host "Инициализация базы данных завершена!" -ForegroundColor Green
