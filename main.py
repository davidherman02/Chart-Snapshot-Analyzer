#!/usr/bin/env python3
"""
Автоматический анализ графиков и генерация отчётов
Скрипт для создания снимков графиков по заданным условиям и генерации отчётов
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
import argparse

from src.data_fetcher import DataFetcher
from src.chart_generator import ChartGenerator
from src.pattern_analyzer import PatternAnalyzer
from src.report_generator import ReportGenerator
from src.config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ChartSnapshotAnalyzer:
    """Основной класс для анализа графиков и генерации отчётов"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация анализатора"""
        self.config = Config(config_path)
        self.data_fetcher = DataFetcher(self.config)
        self.chart_generator = ChartGenerator(self.config)
        self.pattern_analyzer = PatternAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Создаём необходимые директории
        self._create_directories()
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            'logs',
            'data',
            'charts',
            'reports',
            'screenshots'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def analyze_tickers(self, tickers: List[str], timeframe: str = "1h") -> Dict[str, Any]:
        """Анализ списка тикеров"""
        results = {}
        
        for ticker in tickers:
            logger.info(f"Анализ тикера: {ticker}")
            
            try:
                # Получаем данные
                data = self.data_fetcher.get_data(ticker, timeframe)
                
                if data is None or data.empty:
                    logger.warning(f"Нет данных для тикера {ticker}")
                    continue
                
                # Создаём график
                chart_path = self.chart_generator.create_chart(
                    ticker, data, timeframe
                )
                
                # Анализируем паттерны
                patterns = self.pattern_analyzer.analyze(data, ticker)
                
                # Сохраняем результаты
                results[ticker] = {
                    'data': data,
                    'chart_path': chart_path,
                    'patterns': patterns,
                    'timestamp': datetime.now()
                }
                
                logger.info(f"Анализ {ticker} завершён")
                
            except Exception as e:
                logger.error(f"Ошибка при анализе {ticker}: {e}")
                continue
        
        return results
    
    def generate_reports(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Генерация отчётов на основе результатов анализа"""
        reports = []
        
        # Отчёт по пробоям
        breakout_report = self.report_generator.generate_breakout_report(analysis_results)
        if breakout_report:
            reports.append(breakout_report)
        
        # Отчёт по дивергенциям
        divergence_report = self.report_generator.generate_divergence_report(analysis_results)
        if divergence_report:
            reports.append(divergence_report)
        
        # Общий отчёт
        general_report = self.report_generator.generate_general_report(analysis_results)
        if general_report:
            reports.append(general_report)
        
        return reports
    
    def run_analysis(self, tickers: List[str], timeframe: str = "1h") -> List[str]:
        """Запуск полного анализа"""
        logger.info(f"Начинаем анализ {len(tickers)} тикеров на таймфрейме {timeframe}")
        
        # Анализируем тикеры
        analysis_results = self.analyze_tickers(tickers, timeframe)
        
        # Генерируем отчёты
        reports = self.generate_reports(analysis_results)
        
        logger.info(f"Анализ завершён. Создано {len(reports)} отчётов")
        
        return reports


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Анализ графиков и генерация отчётов')
    parser.add_argument('--tickers', nargs='+', required=True, 
                       help='Список тикеров для анализа')
    parser.add_argument('--timeframe', default='1h', 
                       help='Таймфрейм для анализа (1m, 5m, 15m, 1h, 4h, 1d)')
    parser.add_argument('--config', default='config.yaml',
                       help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    
    try:
        # Создаём анализатор
        analyzer = ChartSnapshotAnalyzer(args.config)
        
        # Запускаем анализ
        reports = analyzer.run_analysis(args.tickers, args.timeframe)
        
        print(f"\n✅ Анализ завершён!")
        print(f"📊 Проанализировано тикеров: {len(args.tickers)}")
        print(f"📄 Создано отчётов: {len(reports)}")
        print(f"📁 Отчёты сохранены в папке: reports/")
        
        for report in reports:
            print(f"  - {report}")
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
