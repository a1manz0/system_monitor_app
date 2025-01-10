
# SystemMonitorApp

## Описание
SystemMonitorApp — это десктопное приложение, разработанное с использованием библиотеки Tkinter, которое отображает использование ресурсов компьютера в реальном времени, включая загрузку ЦП, ОЗУ и диска. Приложение также предоставляет возможность записи этих данных в базу данных SQLite.

## Технические требования
- Python 3.x
- psutil (библиотека для мониторинга системы)

## Установка

1. Клонируйте репозиторий:
```
git clone https://github.com/a1manz0/system_monitor_app.git
cd system_monitor_app
```
2. Создайте и активируйте виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
3. Установите зависимости:
```
pip install -r requirements.txt
```
## Использование
Запустите приложение:
```
python3 src/main.py
```
## Тестирование
Запустите тесты:
```
python3 -m unittest discover -s tests
```
