"""
Тесты для модуля анализа паттернов
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pattern_analyzer import PatternAnalyzer
from src.config import Config


class TestPatternAnalyzer(unittest.TestCase):
    """Тесты для PatternAnalyzer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.config = Config()
        self.analyzer = PatternAnalyzer(self.config)
        
        # Создаём тестовые данные
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        # Генерируем реалистичные OHLCV данные
        base_price = 100
        price_changes = np.random.normal(0, 0.02, 100)
        prices = [base_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        self.test_data = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
    
    def test_analyze_basic(self):
        """Тест базового анализа"""
        result = self.analyzer.analyze(self.test_data, "TEST")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], "TEST")
        self.assertIn('breakouts', result)
        self.assertIn('divergences', result)
        self.assertIn('trend_changes', result)
        self.assertIn('volume_anomalies', result)
        self.assertIn('technical_signals', result)
    
    def test_detect_breakouts(self):
        """Тест обнаружения пробоев"""
        breakouts = self.analyzer._detect_breakouts(self.test_data)
        
        self.assertIsInstance(breakouts, list)
        for breakout in breakouts:
            self.assertIn('type', breakout)
            self.assertIn('timestamp', breakout)
            self.assertIn('price', breakout)
            self.assertIn('volume', breakout)
            self.assertIn('strength', breakout)
    
    def test_detect_divergences(self):
        """Тест обнаружения дивергенций"""
        divergences = self.analyzer._detect_divergences(self.test_data)
        
        self.assertIsInstance(divergences, list)
        for divergence in divergences:
            self.assertIn('type', divergence)
            self.assertIn('timestamp', divergence)
            self.assertIn('price', divergence)
            self.assertIn('rsi', divergence)
            self.assertIn('strength', divergence)
    
    def test_detect_support_resistance(self):
        """Тест обнаружения поддержки и сопротивления"""
        levels = self.analyzer._detect_support_resistance(self.test_data)
        
        self.assertIsInstance(levels, list)
        for level in levels:
            self.assertIn('type', level)
            self.assertIn('level', level)
            self.assertIn('touches', level)
            self.assertIn('strength', level)
    
    def test_detect_trend_changes(self):
        """Тест обнаружения изменений тренда"""
        trend_changes = self.analyzer._detect_trend_changes(self.test_data)
        
        self.assertIsInstance(trend_changes, list)
        for change in trend_changes:
            self.assertIn('type', change)
            self.assertIn('timestamp', change)
            self.assertIn('price', change)
    
    def test_detect_volume_anomalies(self):
        """Тест обнаружения аномалий объёма"""
        anomalies = self.analyzer._detect_volume_anomalies(self.test_data)
        
        self.assertIsInstance(anomalies, list)
        for anomaly in anomalies:
            self.assertIn('type', anomaly)
            self.assertIn('timestamp', anomaly)
            self.assertIn('volume', anomaly)
    
    def test_analyze_technical_signals(self):
        """Тест анализа технических сигналов"""
        signals = self.analyzer._analyze_technical_signals(self.test_data)
        
        self.assertIsInstance(signals, dict)
        # Проверяем наличие основных сигналов
        if 'rsi' in signals:
            self.assertIn('current', signals['rsi'])
            self.assertIn('overbought', signals['rsi'])
            self.assertIn('oversold', signals['rsi'])
    
    def test_calculate_rsi(self):
        """Тест расчёта RSI"""
        rsi = self.analyzer._calculate_rsi(self.test_data['close'], 14)
        
        if rsi is not None:
            self.assertIsInstance(rsi, pd.Series)
            self.assertEqual(len(rsi), len(self.test_data))
            # RSI должен быть между 0 и 100
            valid_rsi = rsi.dropna()
            if len(valid_rsi) > 0:
                self.assertTrue((valid_rsi >= 0).all())
                self.assertTrue((valid_rsi <= 100).all())
    
    def test_calculate_macd(self):
        """Тест расчёта MACD"""
        macd, signal, histogram = self.analyzer._calculate_macd(self.test_data['close'])
        
        if macd is not None:
            self.assertIsInstance(macd, pd.Series)
            self.assertEqual(len(macd), len(self.test_data))
            self.assertIsInstance(signal, pd.Series)
            self.assertIsInstance(histogram, pd.Series)
    
    def test_cluster_levels(self):
        """Тест кластеризации уровней"""
        test_levels = pd.Series([100.0, 100.1, 100.2, 105.0, 105.1, 110.0])
        clustered = self.analyzer._cluster_levels(test_levels, 0.02)
        
        self.assertIsInstance(clustered, dict)
        # Проверяем, что уровни сгруппированы правильно
        self.assertGreater(len(clustered), 0)
        for level, touches in clustered.items():
            self.assertIsInstance(touches, list)
            self.assertGreater(len(touches), 0)


if __name__ == '__main__':
    unittest.main()
