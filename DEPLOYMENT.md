# 🚀 Инструкции по развертыванию

## Локальное развертывание

### Быстрый старт

1. **Клонирование и установка**
```bash
git clone <repository-url>
cd Aibot
python run.py
```

2. **Ручная установка**
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp env_example.txt .env
# Отредактируйте .env и добавьте OpenAI API ключ

# Запуск
python app.py
```

### Требования к системе

- Python 3.8+
- 4GB RAM (рекомендуется)
- 2GB свободного места на диске
- Интернет-соединение для OpenAI API

## Развертывание в Docker

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов
COPY requirements.txt .
COPY . .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя
RUN useradd -m -u 1000 sherlock
RUN chown -R sherlock:sherlock /app
USER sherlock

# Открытие порта
EXPOSE 5000

# Запуск приложения
CMD ["python", "app.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  sherlock-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Запуск с Docker
```bash
# Сборка и запуск
docker-compose up --build

# Или с Docker
docker build -t sherlock-bot .
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key sherlock-bot
```

## Развертывание в облаке

### Heroku

1. **Создание Procfile**
```
web: gunicorn app:app
```

2. **Добавление gunicorn в requirements.txt**
```
gunicorn==20.1.0
```

3. **Развертывание**
```bash
heroku create sherlock-bot-app
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

### AWS EC2

1. **Подготовка сервера**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip python3-venv -y

# Установка Nginx
sudo apt install nginx -y
```

2. **Настройка приложения**
```bash
# Клонирование
git clone <repository-url>
cd Aibot

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install gunicorn

# Настройка переменных
cp env_example.txt .env
# Отредактируйте .env
```

3. **Настройка systemd**
```bash
sudo nano /etc/systemd/system/sherlock-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Sherlock Holmes AI Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Aibot
Environment="PATH=/home/ubuntu/Aibot/venv/bin"
ExecStart=/home/ubuntu/Aibot/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

4. **Запуск сервиса**
```bash
sudo systemctl daemon-reload
sudo systemctl enable sherlock-bot
sudo systemctl start sherlock-bot
```

5. **Настройка Nginx**
```bash
sudo nano /etc/nginx/sites-available/sherlock-bot
```

Содержимое:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sherlock-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Google Cloud Platform

1. **Создание App Engine**
```yaml
# app.yaml
runtime: python39
entrypoint: gunicorn app:app

env_variables:
  OPENAI_API_KEY: "your_key"

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10
```

2. **Развертывание**
```bash
gcloud app deploy
```

## Настройка безопасности

### Переменные окружения
```bash
# .env
OPENAI_API_KEY=your_openai_api_key
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

### HTTPS настройка
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com
```

### Firewall настройка
```bash
# UFW
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## Мониторинг и логирование

### Логирование
```python
# Добавьте в app.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/sherlock.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Sherlock Bot startup')
```

### Мониторинг с Prometheus
```python
# requirements.txt
prometheus-flask-exporter==0.22.4

# app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

## Масштабирование

### Горизонтальное масштабирование
```yaml
# docker-compose.yml
version: '3.8'

services:
  sherlock-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    deploy:
      replicas: 3
    restart: unless-stopped
```

### Балансировка нагрузки
```nginx
upstream sherlock_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://sherlock_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Резервное копирование

### Скрипт резервного копирования
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/sherlock-bot"

# Создание резервной копии базы данных
python3 -c "
import chromadb
client = chromadb.Client()
collection = client.get_collection('sherlock_knowledge')
results = collection.get()
import json
with open('$BACKUP_DIR/db_backup_$DATE.json', 'w') as f:
    json.dump(results, f)
"

# Создание резервной копии файлов
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /app

echo "Backup completed: $DATE"
```

### Автоматическое резервное копирование
```bash
# crontab -e
0 2 * * * /path/to/backup.sh
```

## Устранение неполадок

### Частые проблемы

1. **Ошибка OpenAI API**
   - Проверьте правильность API ключа
   - Убедитесь в наличии средств на счете
   - Проверьте лимиты API

2. **Проблемы с ChromaDB**
   - Перезапустите приложение
   - Проверьте права доступа к папке
   - Очистите кэш ChromaDB

3. **Проблемы с веб-скрапингом**
   - Проверьте доступность сайта
   - Убедитесь в отсутствии блокировок
   - Проверьте robots.txt

### Логи и отладка
```bash
# Просмотр логов
tail -f logs/sherlock.log

# Проверка статуса сервиса
sudo systemctl status sherlock-bot

# Проверка портов
netstat -tlnp | grep 5000
```

## Обновление приложения

### Процесс обновления
```bash
# Остановка сервиса
sudo systemctl stop sherlock-bot

# Обновление кода
git pull origin main

# Обновление зависимостей
source venv/bin/activate
pip install -r requirements.txt

# Запуск сервиса
sudo systemctl start sherlock-bot
```

### Откат изменений
```bash
# Откат к предыдущей версии
git reset --hard HEAD~1

# Перезапуск сервиса
sudo systemctl restart sherlock-bot
``` 