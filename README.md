# Микросервис для скачивания файлов

Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить локально

1. Для работы микросервиса нужен Python версии не ниже 3.6.

```bash
pip install -r requirements.txt
```
2. Запустить:
```bash
python server.py
```
Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Как развернуть на сервере

Для запуска используется [Docker Compose](https://docs.docker.com/compose/install/).
В корне проекта расположен файл `docker-compose.yaml`.

1. Убедитесь, что у вас установлены:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

2. Клонируйте репозиторий и перейдите в папку: `git clone https://github.com/MrGrose/async-download-service.git`

3. Собрать сборку: `docker compose -f docker-compose.yaml build`

4. Запустите сервис Docker Compose: `docker compose -f docker-compose.yaml up -d`

5. Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу http://127.0.0.1:8080/.

6. Остановка контейнера: `docker compose -f docker-compose.yaml down -v`

7. Просмотр логов: `docker compose -f docker-compose.yaml logs -f service`

8. Пересборка образа (например, после изменений в коде): 

    - `docker compose -f docker-compose.yaml build`
    - `docker compose -f docker-compose.yaml up -d`

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).


