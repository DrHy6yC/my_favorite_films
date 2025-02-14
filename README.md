# my_favorite_films
Example for RecPlace
win (for mac and linux)

1) Создать виртуальное окружение - python -m venv venv (python3 -m venv venv)
2) Активировать виртуальное окружение - venv\Scripts\activate (source venv/bin/activate)
3) Обновить pip - python.exe -m pip install --upgrade pip (python -m pip install --upgrade pip)
4) Установить необходимые пакеты с помощью pip - pip install -r requirements.txt
5) Создать .env по примеру из example.env
6) Запустить контейнер - docker-compose up -d (docker compose up -d)
7) запустить приложение - python main.py 
8) Тут находится документация (Swagger) - http://localhost:8081/docs#
9) При первом запуске создать таблицы методом  create_all_tables  перейдя по ссылке - http://localhost:8081/create_all_tables