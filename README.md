# Foodgram

## О проекте:
**Сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», так же скачать список понравившихся ингридиендов**

## Технологии:
- Python 3.11.1 
- Django 4.1 
- Django REST framework 
- React 
- Docker 
- Nginx
- PostgreSQL

## Для проверки работы:

- домен https://nsknsk.ddnsking.com
- ip 84.201.143.238

## Запуск проекта на локальном компьютере

- 1 Для запуска проекта необходимо иметь установленные: 
- node.js 
- python 
- pip.

- 2 клонировать проект: git clone git@github.com:Alex09k/foodgram-project-react.git 
- backend: cd backend python -m venv venv


## Установка возможна при налиичи на локальом компьютере Docker compose

## Запустите проект из корня с помощью команды:
- docker compose up

## Примините миграции:
- docker compose exec backend python manage.py migrate

## Соберите статику Django с помощью команды:
- docker compose exec backend python manage.py collectstatic

## Скопируйте статику командой:
- docker compose exec backend cp -r /app/static/. /static/

## создайте  файл .env и заполните его такими данными:

- DB_ENGINE='django.db.backends.postgresql' # указываем, что работаем с postgresql
- DB_NAME='foodgram' # имя базы данных
- POSTGRES_USER='foodgram' # логин для подключения к базе данных
- POSTGRES_PASSWORD='password' # пароль для подключения к БД (установите свой)
- DB_HOST='127.0.0.1' # название сервиса (контейнера)
- DB_PORT='5432' # порт для подключения к БД
- SECRET_KEY = <секретный ключ из одноименного параметра>

# По адресу http://127.0.0.1:8000/ сайт будет доступен.
 
 ## Для взаимодействия с приложением через API предусмотрены следующие методы:

- /api/recipes/- принимает GET и POST, PUT, DELETE  для добавления новых и получения существующих рецептов редактирование рецептов и удаление
- /api/ingredients/ - принимает GET , для  получения существующих ингридиентов
- /api/tags/ - принимае  GET, для получения существующих тегов
- /api/users/ - принимает GET и POST, для добавления новых и получения пользователей

## Учетная запись администратора:

- логин: admin
- почта:admin@mail.ru 
- пароль: sowbars12345

## Авторы:
- backend: Кривов Александр
- frontend: yandex-practicum
- DevOps: Кривов Александр
