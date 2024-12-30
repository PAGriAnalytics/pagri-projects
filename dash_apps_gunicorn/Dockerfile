# Dockerfile
FROM python:3.12-slim

# Установите рабочую директорию в /app
WORKDIR /flask_app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY flask_app/. .

# Установка Nginx
RUN apt-get update && apt-get install -y nginx && \
    rm /etc/nginx/sites-enabled/default && \
    rm /etc/nginx/sites-available/default

# Скопируйте конфигурацию Nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Скопируйте статические файлы в контейнер
COPY nginx/html /var/www/mysite/html

# Открытие портов
EXPOSE 80
EXPOSE 5000

# Запуск Nginx и Flask приложения
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 app:app & nginx -g 'daemon off;'"]
