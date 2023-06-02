** FOODGRAM**

Foodgram - приложение продуктовый помощник, где пользователи деляться рецептами любимых блюд, фотоографиями.
можно подписаться на любимых поваров, создать список избранных блюд, реализована корзина для ингредиентов которую можно скачать и сохранить для похода в магазин

основной Стэк:
- Python 3.7
- Django 2.2
- Docker
- Postgres
- Nginx
- RestApi


**Ссылка на [проект](http://158.160.9.142/ "Гиперссылка к проекту.")**

**Cсылка на [admin](http://158.160.9.142/admin/ "Гиперссылка к проекту.")**

**Ссылка на [redoc](http://158.160.9.142/api/docs/ "Гиперссылка к проекту.")**

###Для Развертывания на сервере потребуется

** клонироват репозиторий с GitHub:**

```
git@github.com:aleksospishev/foodgram-project-react.git
```

**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
** _Создать на сервере папку Foodgram/infra:_**
```
mkdir foodgram
cd foodgram
mkdir infra
```

**_Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):_**
```
scp docker-compose.yml nginx.conf username@IP:~/foodgram/infra

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение

DB_ENGINE               - django.db.backends.postgresql
DB_NAME                 - postgres
POSTGRES_USER           - postgres
POSTGRES_PASSWORD       - postgres
DB_HOST                 - db
DB_PORT                 - 5432 (порт по умолчанию)
```
**_Создать и запустить контейнеры Docker, выполнить команду на сервере из директории foodgram/infra:**_
```
sudo docker-compose up -d
```
**_Выполнить миграции:_**
```
sudo docker-compose exec web python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker-compose exec web python manage.py collectstatic --noinput
```
**_Наполнить базу данных содержимым из файла ingredients.json:_**
```
sudo docker-compose exec web python manage.py loaddata data/ingredients.json
```
**_Создать суперпользователя:_**
```
sudo docker-compose exec web python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker-compose down -v      - с их удалением
sudo docker-compose stop         - без удаления
```
