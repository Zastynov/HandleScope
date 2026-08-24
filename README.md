# HandleScope

Telegram username checker and generator.

## Возможности

- Проверка username в Telegram
- Массовая проверка из `.txt`
- Генерация username
- Генерация с основой или без неё
- Поиск свободных username
- Проверка Fragment
- Русский и английский интерфейс

## Установка

```bash
git clone https://github.com/YOUR_USERNAME/handlescope.git
cd handlescope
pip install -r requirements.txt
Настройка
Создай файл .env:
TG_API_ID=
TG_API_HASH=
TG_SESSION=handlescope
FRAGMENT_ENABLED=true
Укажи свои Telegram API ID и API Hash.
Запуск
python app.py
Массовая проверка
Для массовой проверки используется .txt файл.
Можно указать название файла:
users.txt
или полный путь:
/sdcard/Download/users.txt
Каждый username должен находиться на отдельной строке.
Лицензия
MIT License EOF
