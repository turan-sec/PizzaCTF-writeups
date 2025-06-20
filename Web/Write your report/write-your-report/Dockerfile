# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN apt-get update \
    && apt-get install -y cron curl gnupg wget poppler-utils \
       libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
       libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
       libpangocairo-1.0-0 libgtk-3-0 \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt selenium playwright \
    && playwright install chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app/

# Initialize the database at build time
RUN python - <<EOF
import models
models.init_db()
EOF

# Add cron job to run bot.py every minute
env > /etc/environment
RUN echo "* * * * * cd /app && /usr/local/bin/python3 bot.py http://127.0.0.1:80 >> /app/bot.log 2>&1" > /etc/cron.d/bot-cron \
    && chmod 0644 /etc/cron.d/bot-cron \
    && crontab /etc/cron.d/bot-cron

# Ensure cron is running and expose port 80 for incoming traffic
EXPOSE 80

# Use Flask's CLI to bind to all interfaces on port 80
ENV FLASK_APP=app.py

# Start cron and then the Flask app
CMD service cron start && flask run --host=0.0.0.0 --port=80
