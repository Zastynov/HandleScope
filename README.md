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
- Работа на Windows, Linux, macOS и Android через Termux

## Установка

### Windows

Установите Python 3.11 или новее.

Клонируйте репозиторий:

    git clone https://github.com/Zastynov/HandleScope.git

Перейдите в папку:

    cd HandleScope

Установите зависимости:

    pip install -r requirements.txt

### Linux / macOS

    git clone https://github.com/Zastynov/HandleScope.git
    cd HandleScope
    pip install -r requirements.txt

### Android / Termux

Установите Termux, затем выполните:

    pkg update
    pkg install git python
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

### Windows

В командной строке или PowerShell:

    cd HandleScope
    python app.py

### Linux / macOS / Termux

    cd HandleScope
    python app.py

При первом запуске Telegram может попросить авторизацию аккаунта.

## Массовая проверка

Для массовой проверки используется TXT-файл.

Можно указать название файла:

    users.txt

или полный путь:

    /sdcard/Download/users.txt

На Windows можно использовать, например:

    C:\Users\User\Downloads\users.txt

Каждый username должен находиться на отдельной строке.

Пример:

    username1
    username2
    username3

## Получение Telegram API

Для работы программы нужны Telegram API ID и API Hash.

Их можно получить через Telegram API development tools.

## Лицензия

MIT License
