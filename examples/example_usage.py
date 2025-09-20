#!/usr/bin/env python3
"""
Примеры использования системы анализа графиков
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import ChartSnapshotAnalyzer
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_analysis():
    """Базовый пример анализа"""
    print("=== Базовый пример анализа ===")
    
    # Создаём анализатор
    analyzer = ChartSnapshotAnalyzer("config.yaml")
    
    # Список тикеров для анализа
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    # Запускаем анализ
    reports = analyzer.run_analysis(tickers, "1h")
    
    print(f"Создано отчётов: {len(reports)}")
    for report in reports:
        print(f"  - {report}")


def example_crypto_analysis():
    """Пример анализа криптовалют"""
    print("\n=== Пример анализа криптовалют ===")
    
    # Создаём анализатор с конфигурацией для криптовалют
    analyzer = ChartSnapshotAnalyzer("config.yaml")
    
    # Криптовалютные пары
    crypto_tickers = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "ADA/USDT"]
    
    # Запускаем анализ на дневном таймфрейме
    reports = analyzer.run_analysis(crypto_tickers, "1d")
    
    print(f"Создано отчётов: {len(reports)}")
    for report in reports:
        print(f"  - {report}")


def example_custom_config():
    """Пример с пользовательской конфигурацией"""
    print("\n=== Пример с пользовательской конфигурацией ===")
    
    # Создаём анализатор
    analyzer = ChartSnapshotAnalyzer("config.yaml")
    
    # Изменяем настройки для более чувствительного анализа
    analyzer.config.set('patterns.breakout.volume_threshold', 1.2)
    analyzer.config.set('patterns.divergence.min_divergence_strength', 0.2)
    
    # Анализируем с более коротким таймфреймом
    tickers = ["SPY", "QQQ", "IWM"]
    reports = analyzer.run_analysis(tickers, "15m")
    
    print(f"Создано отчётов: {len(reports)}")
    for report in reports:
        print(f"  - {report}")


def example_individual_analysis():
    """Пример индивидуального анализа символа"""
    print("\n=== Индивидуальный анализ ===")
    
    analyzer = ChartSnapshotAnalyzer("config.yaml")
    
    # Анализируем один символ
    symbol = "AAPL"
    data = analyzer.data_fetcher.get_data(symbol, "1h")
    
    if data is not None:
        # Создаём график
        chart_path = analyzer.chart_generator.create_chart(symbol, data, "1h")
        print(f"График создан: {chart_path}")
        
        # Анализируем паттерны
        patterns = analyzer.pattern_analyzer.analyze(data, symbol)
        
        print(f"\nРезультаты анализа для {symbol}:")
        print(f"  Пробои: {len(patterns['breakouts'])}")
        print(f"  Дивергенции: {len(patterns['divergences'])}")
        print(f"  Изменения тренда: {len(patterns['trend_changes'])}")
        print(f"  Аномалии объёма: {len(patterns['volume_anomalies'])}")
        
        # Технические сигналы
        if patterns['technical_signals']:
            signals = patterns['technical_signals']
            if 'rsi' in signals and signals['rsi']['current']:
                print(f"  RSI: {signals['rsi']['current']:.2f}")
            if 'macd' in signals and signals['macd']['current']:
                print(f"  MACD: {signals['macd']['current']:.4f}")


if __name__ == "__main__":
    try:
        # Запускаем примеры
        example_basic_analysis()
        example_crypto_analysis()
        example_custom_config()
        example_individual_analysis()
        
        print("\n✅ Все примеры выполнены успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка выполнения примеров: {e}")
        print(f"❌ Ошибка: {e}")
