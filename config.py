"""
Конфигурация приложения
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'https://sandbox-api.datamark.by')
API_USERNAME = os.getenv('API_USERNAME')
API_PASSWORD = os.getenv('API_PASSWORD')

# Константы из документации API
PRODUCT_GROUP = "shoes"  # Таблица 4.2.1.2
CODE_TYPE = 20  # п. В.2.1.1
COUNTRY_CODE = 643  # РФ, Таблица 4.3.1
REASON_CODE = "import"  # Таблица 4.3.5

# Настройки приложения
MAX_WAIT_TIME = int(os.getenv('MAX_WAIT_TIME', '300'))  # Максимальное время ожидания в секундах
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))  # Интервал проверки статуса в секундах

# Логирование
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
