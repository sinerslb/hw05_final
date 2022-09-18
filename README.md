# Yatube

Проект Yatube - задание в рамках обучающего курса Яндекс.Практикума Backend-разработчик на Python 
Yatube - это социальная сеть для объединения людей по интересам.

##### Возможности:
* Публиация постов с картинками, как самстоятельных, без темы, так и внутри тематических сообществ.
* Подписка на любимых авторов.
* Комментирование постов.

### Установка

1. Установить Python версии 3.7.9
2. Клонировать репозиторий
3. Установить и запустить виртуальное окружение 
   для Windows

        python -m venv venv
        source venv/scripts/activate

   для Linux или Mac

        python3 -m venv venv
        source venv/bin/activate

4. Установить зависимости

        pip install -r requirements.txt

5. Создать файл .env в директории yatube с settings.py

        SECRET_KEY=my_secret_key
        DEBUG=FALSE

6. Из директории yatube с manage.py выполнить миграции

        python manage.py migrate

7. Создать суперпользователя

        python manage.py createsuperuser

8. Запустить

        python manage.py runserver

### Автор
Андреев Алексей
