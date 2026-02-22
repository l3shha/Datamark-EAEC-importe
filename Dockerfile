FROM python:3.11-slim

WORKDIR /app

# Копируем requirements
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Порт для приложения
EXPOSE 8000

# Команда для запуска (выберите нужную)
# Для FastAPI:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Для Flask (раскомментируйте если нужно):
# CMD ["python", "app.py"]