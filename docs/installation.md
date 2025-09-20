# Установка Chart Snapshot Analyzer

## Системные требования

### Минимальные требования
- **Python**: 3.8 или выше
- **ОС**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: 4 GB (рекомендуется 8 GB)
- **Дисковое пространство**: 1 GB свободного места

### Рекомендуемые требования
- **Python**: 3.10 или выше
- **RAM**: 8 GB или больше
- **Дисковое пространство**: 5 GB для кэша данных

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/chart-snapshot-analyzer.git
cd chart-snapshot-analyzer
```

### 2. Создание виртуального окружения

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

**Базовая установка:**
```bash
pip install -r requirements.txt
```

**Установка как пакет:**
```bash
pip install -e .
```

**Установка с дополнительными возможностями:**
```bash
# Для разработки
pip install -e ".[dev]"

# Для документации
pip install -e ".[docs]"

# Все возможности
pip install -e ".[dev,docs]"
```

## Проверка установки

### Тест базовой функциональности

```python
from main import ChartSnapshotAnalyzer

# Создаём анализатор
analyzer = ChartSnapshotAnalyzer()

# Проверяем, что всё работает
print("✅ Установка прошла успешно!")
```

### Запуск тестов

```bash
# Все тесты
python -m pytest

# С покрытием кода
python -m pytest --cov=src

# Конкретный тест
python -m pytest tests/test_pattern_analyzer.py
```

### Проверка командной строки

```bash
# Справка
python main.py --help

# Тестовый запуск
python main.py --tickers AAPL --timeframe 1h
```

## Настройка API ключей

### Yahoo Finance (по умолчанию)
Никаких ключей не требуется - работает из коробки.

### Binance API

1. Зарегистрируйтесь на [Binance](https://www.binance.com/)
2. Создайте API ключ в разделе "API Management"
3. Обновите `config.yaml`:

```yaml
api:
  provider: binance
  api_key: "your_api_key_here"
  api_secret: "your_api_secret_here"
```

### Alpha Vantage (опционально)

1. Получите бесплатный ключ на [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Обновите конфигурацию:

```yaml
api:
  provider: alpha_vantage
  api_key: "your_alpha_vantage_key"
```

## Устранение проблем

### Ошибки установки зависимостей

**Проблема**: Ошибки при установке matplotlib
```bash
# Решение для Ubuntu/Debian
sudo apt-get install python3-tk

# Решение для macOS
brew install python-tk

# Решение для Windows
# Установите Visual C++ Build Tools
```

**Проблема**: Ошибки с ccxt
```bash
# Обновите pip
pip install --upgrade pip

# Установите зависимости вручную
pip install ccxt[async]
```

### Проблемы с правами доступа

**Windows:**
```cmd
# Запустите PowerShell как администратор
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS:**
```bash
# Установите права на выполнение
chmod +x main.py
```

### Проблемы с памятью

Если возникают ошибки нехватки памяти:

1. Уменьшите количество анализируемых символов
2. Используйте более длинные таймфреймы
3. Очистите кэш данных:

```python
import shutil
import os

# Очистка кэша
if os.path.exists('data'):
    shutil.rmtree('data')
```

## Обновление

### Обновление до новой версии

```bash
# Получите последние изменения
git pull origin main

# Обновите зависимости
pip install -r requirements.txt --upgrade

# Переустановите пакет
pip install -e . --upgrade
```

### Обновление конфигурации

При обновлении проверьте файл `config.yaml` на предмет новых параметров:

```bash
# Сравните с примером
git diff HEAD~1 config.yaml
```

## Docker (опционально)

### Создание Docker образа

```bash
# Создайте Dockerfile
cat > Dockerfile << EOF
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "main.py", "--help"]
EOF

# Соберите образ
docker build -t chart-analyzer .

# Запустите контейнер
docker run -it chart-analyzer --tickers AAPL --timeframe 1h
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  chart-analyzer:
    build: .
    volumes:
      - ./charts:/app/charts
      - ./reports:/app/reports
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
```

## Производительность

### Оптимизация для больших объёмов данных

1. **Увеличьте лимит памяти Python:**
```bash
export PYTHONHASHSEED=0
export PYTHONUNBUFFERED=1
```

2. **Используйте более мощное железо:**
   - SSD для быстрого доступа к данным
   - Больше RAM для кэширования
   - Быстрый интернет для API запросов

3. **Настройте конфигурацию:**
```yaml
api:
  rate_limit: 0.5  # Уменьшите задержку между запросами

patterns:
  breakout:
    lookback_periods: 10  # Уменьшите период анализа
```

## Поддержка

Если у вас возникли проблемы с установкой:

1. Проверьте [FAQ](faq.md)
2. Создайте [Issue](https://github.com/your-username/chart-snapshot-analyzer/issues)
3. Обратитесь в [Discussions](https://github.com/your-username/chart-snapshot-analyzer/discussions)

---

**Следующий шаг**: [Быстрый старт](quickstart.md)
