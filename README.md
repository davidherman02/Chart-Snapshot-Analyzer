# 📊 Chart Snapshot Analyzer

**Автоматический анализ графиков и генерация отчётов**

Система для автоматического создания снимков графиков по заданным условиям, анализа технических паттернов и генерации детальных отчётов. Поддерживает анализ пробоев, дивергенций, изменений тренда и других паттернов без необходимости ручного просмотра каждого графика.

## ✨ Возможности

### 🔍 Автоматический анализ
- **Пробои уровней** - обнаружение пробоев поддержки и сопротивления
- **Дивергенции** - анализ расхождений между ценой и индикаторами
- **Изменения тренда** - выявление смены рыночных настроений
- **Аномалии объёма** - обнаружение необычной торговой активности
- **Технические сигналы** - RSI, MACD, скользящие средние

### 📈 Визуализация
- **Профессиональные графики** с техническими индикаторами
- **Сравнительный анализ** нескольких символов
- **Настраиваемые стили** и параметры отображения
- **Высокое качество** снимков для отчётов

### 📋 Отчёты
- **HTML отчёты** с интерактивными элементами
- **Markdown отчёты** для документации
- **Детальная статистика** по всем паттернам
- **Автоматическая группировка** по типам сигналов

### 🔌 Интеграции
- **Yahoo Finance** - акции, ETF, индексы
- **Binance API** - криптовалютные пары
- **Настраиваемые провайдеры** данных
- **Гибкая конфигурация** через YAML

## 🚀 Быстрый старт

### Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/chart-snapshot-analyzer.git
cd chart-snapshot-analyzer

# Установите зависимости
pip install -r requirements.txt

# Или установите как пакет
pip install -e .
```

### Базовое использование

```python
from main import ChartSnapshotAnalyzer

# Создаём анализатор
analyzer = ChartSnapshotAnalyzer("config.yaml")

# Анализируем список тикеров
tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
reports = analyzer.run_analysis(tickers, "1h")

print(f"Создано отчётов: {len(reports)}")
```

### Командная строка

```bash
# Анализ акций
python main.py --tickers AAPL GOOGL MSFT --timeframe 1h

# Анализ криптовалют
python main.py --tickers BTC/USDT ETH/USDT --timeframe 4h

# С пользовательской конфигурацией
python main.py --tickers SPY QQQ --timeframe 15m --config custom_config.yaml
```

## 📖 Документация

### Конфигурация

Основные настройки находятся в файле `config.yaml`:

```yaml
# API настройки
api:
  provider: yfinance  # yfinance, binance
  rate_limit: 1.0     # задержка между запросами

# Настройки графиков
charts:
  width: 1200
  height: 800
  indicators:
    sma: [20, 50, 200]
    rsi: 14
    macd: [12, 26, 9]

# Анализ паттернов
patterns:
  breakout:
    enabled: true
    lookback_periods: 20
    volume_threshold: 1.5
```

### Поддерживаемые индикаторы

- **SMA** - простые скользящие средние
- **EMA** - экспоненциальные скользящие средние  
- **RSI** - индекс относительной силы
- **MACD** - схождение/расхождение скользящих средних
- **Bollinger Bands** - полосы Боллинджера
- **Volume** - анализ объёма торгов

### Типы паттернов

#### Пробои уровней
- **Пробои сопротивления** - прорыв выше локального максимума
- **Пробои поддержки** - прорыв ниже локального минимума
- **Фильтрация по объёму** - только значимые пробои

#### Дивергенции
- **Бычьи дивергенции** - цена падает, RSI растёт
- **Медвежьи дивергенции** - цена растёт, RSI падает
- **Настраиваемая чувствительность** анализа

#### Изменения тренда
- **Пересечения скользящих средних** (SMA 20/50)
- **MACD сигналы** - бычьи и медвежьи пересечения
- **RSI экстремумы** - перекупленность/перепроданность

## 🛠️ Примеры использования

### Анализ акций

```python
# Анализ крупных технологических компаний
analyzer = ChartSnapshotAnalyzer()
tech_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]
reports = analyzer.run_analysis(tech_stocks, "1d")
```

### Анализ криптовалют

```python
# Настройка для Binance API
config = Config("crypto_config.yaml")
config.set('api.provider', 'binance')
config.set('api.api_key', 'your_api_key')

analyzer = ChartSnapshotAnalyzer(config)
crypto_pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
reports = analyzer.run_analysis(crypto_pairs, "4h")
```

### Сравнительный анализ

```python
# Создание сравнительного графика
chart_generator = ChartGenerator(config)
comparison_chart = chart_generator.create_comparison_chart(
    symbols=["SPY", "QQQ", "IWM"],
    data_dict=analysis_data,
    timeframe="1d"
)
```

### Пользовательские паттерны

```python
# Настройка чувствительности анализа
config.set('patterns.breakout.volume_threshold', 1.2)
config.set('patterns.divergence.min_divergence_strength', 0.2)

# Более агрессивный поиск паттернов
analyzer = ChartSnapshotAnalyzer(config)
```

## 📊 Структура проекта

```
chart-snapshot-analyzer/
├── main.py                 # Основной модуль
├── config.yaml            # Конфигурация
├── requirements.txt       # Зависимости
├── setup.py              # Установочный скрипт
├── src/                  # Исходный код
│   ├── __init__.py
│   ├── config.py         # Управление конфигурацией
│   ├── data_fetcher.py   # Получение данных
│   ├── chart_generator.py # Создание графиков
│   ├── pattern_analyzer.py # Анализ паттернов
│   └── report_generator.py # Генерация отчётов
├── examples/             # Примеры использования
│   └── example_usage.py
├── charts/              # Сохранённые графики
├── reports/             # Сгенерированные отчёты
├── logs/               # Логи работы
└── data/               # Кэшированные данные
```

## 🔧 Разработка

### Установка для разработки

```bash
# Клонируйте репозиторий
git clone https://github.com/your-username/chart-snapshot-analyzer.git
cd chart-snapshot-analyzer

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости для разработки
pip install -e ".[dev]"
```

### Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=src

# Проверка стиля кода
flake8 src/
black src/
```

### Добавление новых провайдеров

```python
class CustomProvider(DataProvider):
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000):
        # Ваша реализация
        pass
    
    def get_available_symbols(self):
        # Ваша реализация
        pass
```

## 📈 Производительность

### Оптимизация запросов
- **Кэширование данных** для повторного использования
- **Настраиваемые лимиты** запросов к API
- **Пакетная обработка** множественных символов

### Масштабирование
- **Параллельная обработка** символов
- **Асинхронные запросы** к API
- **Инкрементальный анализ** больших датасетов

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста:

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Рекомендации
- Следуйте существующему стилю кода
- Добавляйте тесты для новых функций
- Обновляйте документацию
- Используйте осмысленные сообщения коммитов

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🆘 Поддержка

### Часто задаваемые вопросы

**Q: Как добавить новый индикатор?**
A: Расширьте класс `TechnicalIndicators` в `src/chart_generator.py`

**Q: Можно ли использовать другие источники данных?**
A: Да, создайте новый провайдер, наследуясь от `DataProvider`

**Q: Как настроить чувствительность анализа?**
A: Измените параметры в секции `patterns` файла `config.yaml`

### Получение помощи

- 📧 Email: chart.analysis@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/chart-snapshot-analyzer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/chart-snapshot-analyzer/discussions)

## 🏷️ Теги

`trading` `analysis` `charts` `technical-analysis` `finance` `cryptocurrency` `stocks` `patterns` `breakouts` `divergences` `reports` `automation` `python` `matplotlib` `pandas` `yfinance` `binance`

## 📊 Статистика

![GitHub stars](https://img.shields.io/github/stars/your-username/chart-snapshot-analyzer?style=social)
![GitHub forks](https://img.shields.io/github/forks/your-username/chart-snapshot-analyzer?style=social)
![GitHub issues](https://img.shields.io/github/issues/your-username/chart-snapshot-analyzer)
![GitHub license](https://img.shields.io/github/license/your-username/chart-snapshot-analyzer)
![Python version](https://img.shields.io/pypi/pyversions/chart-snapshot-analyzer)

---

**Сделано с ❤️ для трейдеров и аналитиков**
