FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    supervisor \
    nginx \
    netcat \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY start-container.sh /usr/local/bin/start-container.sh
RUN chmod +x /usr/local/bin/start-container.sh

COPY todo.ini /app/todo.ini
RUN chown www-data:www-data /app/todo.ini && \
    chmod 644 /app/todo.ini

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /var/uwsgi \
&& chown -R www-data:www-data /var/uwsgi \
&& chmod -R 777 /var/uwsgi

RUN rm /etc/nginx/nginx.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf

COPY . .

EXPOSE 9009

ENTRYPOINT ["start-container.sh"]