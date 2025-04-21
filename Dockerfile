FROM python:3.11-alpine

# Рабочая директория
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY motion_listener.py .

# Запуск
CMD ["python", "motion_listener.py"]
