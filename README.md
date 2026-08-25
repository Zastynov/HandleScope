# HandleScope

Telegram username checker and generator.

## Возможности

- Проверка username в Telegram
- Массовая проверка из TXT
- Генерация username
- Генерация с основой или без неё
- Поиск свободных username
- Проверка Fragment
- Русский и английский интерфейс

## Установка

Откройте Termux и выполните:

    git clone https://github.com/Zastynov/HandleScope.git
    cd HandleScope
    pip install -r requirements.txt

## Настройка

Создайте файл `.env` в папке проекта.

Добавьте:

    TG_API_ID=
    TG_API_HASH=
    TG_SESSION=handlescope
    FRAGMENT_ENABLED=true

Укажите свои Telegram API ID и API Hash.

## Запуск

Выполните:

    python app.py

При первом запуске Telegram может попросить авторизацию аккаунта.

## Массовая проверка

Для массовой проверки используется TXT-файл.

Можно указать только название файла:

    users.txt

Если файл находится в папке проекта.

Или указать полный путь:

    /sdcard/Download/users.txt

Каждый username должен находиться на отдельной строке.

Пример:

    username1
    username2
    username3

## Лицензия

MIT License
