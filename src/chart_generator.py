"""
Модуль для создания графиков с техническими индикаторами
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import os
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Класс для расчёта технических индикаторов"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Простое скользящее среднее"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Экспоненциальное скользящее среднее"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Индекс относительной силы (RSI)"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD индикатор"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Полосы Боллинджера"""
        sma = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr


class ChartGenerator:
    """Класс для создания графиков"""
    
    def __init__(self, config):
        """Инициализация генератора графиков"""
        self.config = config
        self.charts_config = config.get_charts_config()
        self.output_config = config.get_output_config()
        
        # Настройка стиля matplotlib
        self._setup_style()
    
    def _setup_style(self):
        """Настройка стиля графиков"""
        style = self.charts_config.get('style', 'darkgrid')
        sns.set_style(style)
        plt.rcParams['figure.dpi'] = self.charts_config.get('dpi', 100)
        plt.rcParams['font.size'] = 10
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчёт технических индикаторов"""
        indicators = {}
        indicators_config = self.charts_config.get('indicators', {})
        
        # SMA
        if 'sma' in indicators_config:
            for period in indicators_config['sma']:
                indicators[f'sma_{period}'] = TechnicalIndicators.sma(data['close'], period)
        
        # EMA
        if 'ema' in indicators_config:
            for period in indicators_config['ema']:
                indicators[f'ema_{period}'] = TechnicalIndicators.ema(data['close'], period)
        
        # RSI
        if 'rsi' in indicators_config:
            period = indicators_config['rsi']
            indicators['rsi'] = TechnicalIndicators.rsi(data['close'], period)
        
        # MACD
        if 'macd' in indicators_config:
            fast, slow, signal = indicators_config['macd']
            macd, signal_line, histogram = TechnicalIndicators.macd(
                data['close'], fast, slow, signal
            )
            indicators['macd'] = macd
            indicators['macd_signal'] = signal_line
            indicators['macd_histogram'] = histogram
        
        # Bollinger Bands
        if 'bollinger' in indicators_config:
            period, std_dev = indicators_config['bollinger']
            upper, middle, lower = TechnicalIndicators.bollinger_bands(
                data['close'], period, std_dev
            )
            indicators['bb_upper'] = upper
            indicators['bb_middle'] = middle
            indicators['bb_lower'] = lower
        
        # ATR
        indicators['atr'] = TechnicalIndicators.atr(
            data['high'], data['low'], data['close']
        )
        
        return indicators
    
    def create_chart(self, symbol: str, data: pd.DataFrame, timeframe: str) -> str:
        """Создание графика с индикаторами"""
        try:
            # Рассчитываем индикаторы
            indicators = self._calculate_indicators(data)
            
            # Создаём фигуру
            fig = plt.figure(figsize=(
                self.charts_config.get('width', 1200) / 100,
                self.charts_config.get('height', 800) / 100
            ))
            
            # Определяем количество субплотов
            n_plots = 2 if self.charts_config.get('indicators', {}).get('volume', True) else 1
            if 'rsi' in indicators:
                n_plots += 1
            if 'macd' in indicators:
                n_plots += 1
            
            # Основной график цены
            ax1 = plt.subplot(n_plots, 1, 1)
            self._plot_price_chart(ax1, data, indicators, symbol, timeframe)
            
            plot_idx = 2
            
            # RSI
            if 'rsi' in indicators:
                ax_rsi = plt.subplot(n_plots, 1, plot_idx)
                self._plot_rsi(ax_rsi, data, indicators['rsi'])
                plot_idx += 1
            
            # MACD
            if 'macd' in indicators:
                ax_macd = plt.subplot(n_plots, 1, plot_idx)
                self._plot_macd(ax_macd, data, indicators)
                plot_idx += 1
            
            # Объём
            if self.charts_config.get('indicators', {}).get('volume', True):
                ax_vol = plt.subplot(n_plots, 1, plot_idx)
                self._plot_volume(ax_vol, data)
            
            # Настройка макета
            plt.tight_layout()
            
            # Сохранение графика
            charts_dir = self.output_config.get('charts_dir', 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{symbol}_{timeframe}_{timestamp}.png"
            filepath = os.path.join(charts_dir, filename)
            
            plt.savefig(filepath, dpi=self.charts_config.get('dpi', 100), 
                       bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"График сохранён: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Ошибка создания графика для {symbol}: {e}")
            return None
    
    def _plot_price_chart(self, ax, data: pd.DataFrame, indicators: Dict, symbol: str, timeframe: str):
        """Построение основного графика цены"""
        # Свечи
        ax.plot(data.index, data['close'], label='Close', linewidth=1, color='blue')
        
        # SMA
        for key, value in indicators.items():
            if key.startswith('sma_'):
                period = key.split('_')[1]
                ax.plot(data.index, value, label=f'SMA {period}', alpha=0.7)
        
        # EMA
        for key, value in indicators.items():
            if key.startswith('ema_'):
                period = key.split('_')[1]
                ax.plot(data.index, value, label=f'EMA {period}', alpha=0.7, linestyle='--')
        
        # Bollinger Bands
        if 'bb_upper' in indicators:
            ax.fill_between(data.index, indicators['bb_lower'], indicators['bb_upper'], 
                           alpha=0.1, color='gray', label='Bollinger Bands')
            ax.plot(data.index, indicators['bb_upper'], color='gray', alpha=0.5)
            ax.plot(data.index, indicators['bb_lower'], color='gray', alpha=0.5)
        
        ax.set_title(f'{symbol} - {timeframe}', fontsize=14, fontweight='bold')
        ax.set_ylabel('Цена', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Форматирование оси времени
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_rsi(self, ax, data: pd.DataFrame, rsi: pd.Series):
        """Построение графика RSI"""
        ax.plot(data.index, rsi, label='RSI', color='purple', linewidth=1)
        ax.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought')
        ax.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold')
        ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5)
        
        ax.set_title('RSI', fontsize=12)
        ax.set_ylabel('RSI', fontsize=10)
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def _plot_macd(self, ax, data: pd.DataFrame, indicators: Dict):
        """Построение графика MACD"""
        ax.plot(data.index, indicators['macd'], label='MACD', color='blue', linewidth=1)
        ax.plot(data.index, indicators['macd_signal'], label='Signal', color='red', linewidth=1)
        
        # Гистограмма MACD
        colors = ['green' if val >= 0 else 'red' for val in indicators['macd_histogram']]
        ax.bar(data.index, indicators['macd_histogram'], color=colors, alpha=0.6, width=0.8)
        
        ax.set_title('MACD', fontsize=12)
        ax.set_ylabel('MACD', fontsize=10)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    def _plot_volume(self, ax, data: pd.DataFrame):
        """Построение графика объёма"""
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(data['close'], data['open'])]
        
        ax.bar(data.index, data['volume'], color=colors, alpha=0.6, width=0.8)
        ax.set_title('Объём', fontsize=12)
        ax.set_ylabel('Объём', fontsize=10)
        ax.grid(True, alpha=0.3)
    
    def create_comparison_chart(self, symbols: list, data_dict: dict, timeframe: str) -> str:
        """Создание сравнительного графика для нескольких символов"""
        try:
            fig, ax = plt.subplots(figsize=(
                self.charts_config.get('width', 1200) / 100,
                self.charts_config.get('height', 600) / 100
            ))
            
            colors = plt.cm.tab10(np.linspace(0, 1, len(symbols)))
            
            for i, symbol in enumerate(symbols):
                if symbol in data_dict:
                    data = data_dict[symbol]
                    # Нормализуем данные для сравнения
                    normalized_price = (data['close'] / data['close'].iloc[0]) * 100
                    ax.plot(data.index, normalized_price, label=symbol, 
                           color=colors[i], linewidth=2)
            
            ax.set_title(f'Сравнение символов - {timeframe}', fontsize=14, fontweight='bold')
            ax.set_ylabel('Нормализованная цена (100 = начальная)', fontsize=12)
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
            
            # Сохранение графика
            charts_dir = self.output_config.get('charts_dir', 'charts')
            os.makedirs(charts_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{timeframe}_{timestamp}.png"
            filepath = os.path.join(charts_dir, filename)
            
            plt.savefig(filepath, dpi=self.charts_config.get('dpi', 100), 
                       bbox_inches='tight', facecolor='white')
            plt.close()
            
            logger.info(f"Сравнительный график сохранён: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Ошибка создания сравнительного графика: {e}")
            return None
