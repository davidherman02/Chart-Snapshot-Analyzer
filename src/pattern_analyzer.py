"""
Модуль для анализа технических паттернов и сигналов
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Класс для анализа технических паттернов"""
    
    def __init__(self, config):
        """Инициализация анализатора паттернов"""
        self.config = config
        self.patterns_config = config.get_patterns_config()
    
    def analyze(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Основной метод анализа паттернов"""
        patterns = {
            'symbol': symbol,
            'timestamp': pd.Timestamp.now(),
            'breakouts': [],
            'divergences': [],
            'support_resistance': [],
            'trend_changes': [],
            'volume_anomalies': [],
            'technical_signals': {}
        }
        
        try:
            # Анализ пробоев
            if self.patterns_config.get('breakout', {}).get('enabled', True):
                patterns['breakouts'] = self._detect_breakouts(data)
            
            # Анализ дивергенций
            if self.patterns_config.get('divergence', {}).get('enabled', True):
                patterns['divergences'] = self._detect_divergences(data)
            
            # Анализ поддержки и сопротивления
            if self.patterns_config.get('support_resistance', {}).get('enabled', True):
                patterns['support_resistance'] = self._detect_support_resistance(data)
            
            # Анализ изменений тренда
            patterns['trend_changes'] = self._detect_trend_changes(data)
            
            # Анализ аномалий объёма
            patterns['volume_anomalies'] = self._detect_volume_anomalies(data)
            
            # Технические сигналы
            patterns['technical_signals'] = self._analyze_technical_signals(data)
            
            logger.info(f"Анализ паттернов для {symbol} завершён")
            
        except Exception as e:
            logger.error(f"Ошибка анализа паттернов для {symbol}: {e}")
        
        return patterns
    
    def _detect_breakouts(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение пробоев уровней"""
        breakouts = []
        breakout_config = self.patterns_config.get('breakout', {})
        lookback = breakout_config.get('lookback_periods', 20)
        volume_threshold = breakout_config.get('volume_threshold', 1.5)
        
        try:
            # Находим локальные максимумы и минимумы
            highs = data['high'].rolling(window=lookback, center=True).max()
            lows = data['low'].rolling(window=lookback, center=True).min()
            
            # Пробои сопротивления (продажи)
            resistance_breaks = data['close'] > highs.shift(1)
            resistance_breaks = resistance_breaks & (data['close'] > data['open'])
            
            # Пробои поддержки (покупки)
            support_breaks = data['close'] < lows.shift(1)
            support_breaks = support_breaks & (data['close'] < data['open'])
            
            # Фильтруем по объёму
            avg_volume = data['volume'].rolling(window=lookback).mean()
            high_volume = data['volume'] > (avg_volume * volume_threshold)
            
            # Находим индексы пробоев
            resistance_indices = data[resistance_breaks & high_volume].index
            support_indices = data[support_breaks & high_volume].index
            
            # Формируем результаты
            for idx in resistance_indices:
                breakouts.append({
                    'type': 'resistance_breakout',
                    'timestamp': idx,
                    'price': data.loc[idx, 'close'],
                    'volume': data.loc[idx, 'volume'],
                    'strength': self._calculate_breakout_strength(data, idx, 'resistance')
                })
            
            for idx in support_indices:
                breakouts.append({
                    'type': 'support_breakout',
                    'timestamp': idx,
                    'price': data.loc[idx, 'close'],
                    'volume': data.loc[idx, 'volume'],
                    'strength': self._calculate_breakout_strength(data, idx, 'support')
                })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения пробоев: {e}")
        
        return breakouts
    
    def _detect_divergences(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение дивергенций"""
        divergences = []
        divergence_config = self.patterns_config.get('divergence', {})
        rsi_period = divergence_config.get('rsi_periods', 14)
        min_strength = divergence_config.get('min_divergence_strength', 0.3)
        
        try:
            # Рассчитываем RSI
            rsi = self._calculate_rsi(data['close'], rsi_period)
            
            if rsi is None or len(rsi) < 20:
                return divergences
            
            # Находим пики и впадины в цене и RSI
            price_peaks, price_peaks_props = find_peaks(data['close'], distance=5)
            price_troughs, price_troughs_props = find_peaks(-data['close'], distance=5)
            
            rsi_peaks, rsi_peaks_props = find_peaks(rsi, distance=5)
            rsi_troughs, rsi_troughs_props = find_peaks(-rsi, distance=5)
            
            # Анализируем бычьи дивергенции (цена падает, RSI растёт)
            for i, price_trough in enumerate(price_troughs):
                if i == 0:
                    continue
                
                prev_price_trough = price_troughs[i-1]
                price_slope = (data['close'].iloc[price_trough] - 
                              data['close'].iloc[prev_price_trough]) / (price_trough - prev_price_trough)
                
                # Находим соответствующие RSI впадины
                rsi_troughs_in_range = rsi_troughs[
                    (rsi_troughs >= prev_price_trough) & (rsi_troughs <= price_trough)
                ]
                
                if len(rsi_troughs_in_range) >= 2:
                    rsi_slope = (rsi.iloc[rsi_troughs_in_range[-1]] - 
                               rsi.iloc[rsi_troughs_in_range[0]]) / (rsi_troughs_in_range[-1] - rsi_troughs_in_range[0])
                    
                    # Проверяем дивергенцию
                    if price_slope < 0 and rsi_slope > 0:
                        strength = abs(price_slope * rsi_slope)
                        if strength > min_strength:
                            divergences.append({
                                'type': 'bullish_divergence',
                                'timestamp': data.index[price_trough],
                                'price': data['close'].iloc[price_trough],
                                'rsi': rsi.iloc[price_trough],
                                'strength': strength
                            })
            
            # Анализируем медвежьи дивергенции (цена растёт, RSI падает)
            for i, price_peak in enumerate(price_peaks):
                if i == 0:
                    continue
                
                prev_price_peak = price_peaks[i-1]
                price_slope = (data['close'].iloc[price_peak] - 
                              data['close'].iloc[prev_price_peak]) / (price_peak - prev_price_peak)
                
                # Находим соответствующие RSI пики
                rsi_peaks_in_range = rsi_peaks[
                    (rsi_peaks >= prev_price_peak) & (rsi_peaks <= price_peak)
                ]
                
                if len(rsi_peaks_in_range) >= 2:
                    rsi_slope = (rsi.iloc[rsi_peaks_in_range[-1]] - 
                               rsi.iloc[rsi_peaks_in_range[0]]) / (rsi_peaks_in_range[-1] - rsi_peaks_in_range[0])
                    
                    # Проверяем дивергенцию
                    if price_slope > 0 and rsi_slope < 0:
                        strength = abs(price_slope * rsi_slope)
                        if strength > min_strength:
                            divergences.append({
                                'type': 'bearish_divergence',
                                'timestamp': data.index[price_peak],
                                'price': data['close'].iloc[price_peak],
                                'rsi': rsi.iloc[price_peak],
                                'strength': strength
                            })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения дивергенций: {e}")
        
        return divergences
    
    def _detect_support_resistance(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение уровней поддержки и сопротивления"""
        levels = []
        sr_config = self.patterns_config.get('support_resistance', {})
        min_touches = sr_config.get('min_touches', 2)
        tolerance = sr_config.get('tolerance', 0.02)
        
        try:
            # Находим локальные максимумы и минимумы
            highs = data['high'].rolling(window=5, center=True).max()
            lows = data['low'].rolling(window=5, center=True).min()
            
            # Сопротивления (локальные максимумы)
            resistance_candidates = data[data['high'] == highs]['high']
            resistance_levels = self._cluster_levels(resistance_candidates, tolerance)
            
            for level, touches in resistance_levels.items():
                if len(touches) >= min_touches:
                    levels.append({
                        'type': 'resistance',
                        'level': level,
                        'touches': len(touches),
                        'strength': len(touches) / len(data) * 100,
                        'last_touch': max(touches)
                    })
            
            # Поддержки (локальные минимумы)
            support_candidates = data[data['low'] == lows]['low']
            support_levels = self._cluster_levels(support_candidates, tolerance)
            
            for level, touches in support_levels.items():
                if len(touches) >= min_touches:
                    levels.append({
                        'type': 'support',
                        'level': level,
                        'touches': len(touches),
                        'strength': len(touches) / len(data) * 100,
                        'last_touch': max(touches)
                    })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения поддержки/сопротивления: {e}")
        
        return levels
    
    def _detect_trend_changes(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение изменений тренда"""
        trend_changes = []
        
        try:
            # Рассчитываем скользящие средние
            sma_20 = data['close'].rolling(window=20).mean()
            sma_50 = data['close'].rolling(window=50).mean()
            
            # Находим пересечения
            sma_crossovers = (sma_20 > sma_50) & (sma_20.shift(1) <= sma_50.shift(1))
            sma_crossunders = (sma_20 < sma_50) & (sma_20.shift(1) >= sma_50.shift(1))
            
            # Бычьи пересечения
            bullish_crosses = data[sma_crossovers]
            for idx in bullish_crosses.index:
                trend_changes.append({
                    'type': 'bullish_crossover',
                    'timestamp': idx,
                    'price': data.loc[idx, 'close'],
                    'sma_20': sma_20.loc[idx],
                    'sma_50': sma_50.loc[idx]
                })
            
            # Медвежьи пересечения
            bearish_crosses = data[sma_crossunders]
            for idx in bearish_crosses.index:
                trend_changes.append({
                    'type': 'bearish_crossover',
                    'timestamp': idx,
                    'price': data.loc[idx, 'close'],
                    'sma_20': sma_20.loc[idx],
                    'sma_50': sma_50.loc[idx]
                })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения изменений тренда: {e}")
        
        return trend_changes
    
    def _detect_volume_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Обнаружение аномалий объёма"""
        anomalies = []
        
        try:
            # Рассчитываем средний объём
            avg_volume = data['volume'].rolling(window=20).mean()
            volume_std = data['volume'].rolling(window=20).std()
            
            # Аномально высокий объём (больше 2 стандартных отклонений)
            high_volume = data['volume'] > (avg_volume + 2 * volume_std)
            
            for idx in data[high_volume].index:
                anomalies.append({
                    'type': 'high_volume',
                    'timestamp': idx,
                    'volume': data.loc[idx, 'volume'],
                    'avg_volume': avg_volume.loc[idx],
                    'deviation': (data.loc[idx, 'volume'] - avg_volume.loc[idx]) / volume_std.loc[idx]
                })
            
        except Exception as e:
            logger.error(f"Ошибка обнаружения аномалий объёма: {e}")
        
        return anomalies
    
    def _analyze_technical_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Анализ технических сигналов"""
        signals = {}
        
        try:
            # RSI сигналы
            rsi = self._calculate_rsi(data['close'], 14)
            if rsi is not None:
                signals['rsi'] = {
                    'current': rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None,
                    'overbought': rsi.iloc[-1] > 70 if not pd.isna(rsi.iloc[-1]) else False,
                    'oversold': rsi.iloc[-1] < 30 if not pd.isna(rsi.iloc[-1]) else False
                }
            
            # MACD сигналы
            macd, signal_line, histogram = self._calculate_macd(data['close'])
            if macd is not None and signal_line is not None:
                signals['macd'] = {
                    'current': macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else None,
                    'signal': signal_line.iloc[-1] if not pd.isna(signal_line.iloc[-1]) else None,
                    'histogram': histogram.iloc[-1] if not pd.isna(histogram.iloc[-1]) else None,
                    'bullish_crossover': macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2],
                    'bearish_crossover': macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]
                }
            
            # Тренд
            sma_20 = data['close'].rolling(window=20).mean()
            sma_50 = data['close'].rolling(window=50).mean()
            signals['trend'] = {
                'sma_20': sma_20.iloc[-1] if not pd.isna(sma_20.iloc[-1]) else None,
                'sma_50': sma_50.iloc[-1] if not pd.isna(sma_50.iloc[-1]) else None,
                'bullish': sma_20.iloc[-1] > sma_50.iloc[-1] if not pd.isna(sma_20.iloc[-1]) and not pd.isna(sma_50.iloc[-1]) else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа технических сигналов: {e}")
        
        return signals
    
    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> Optional[pd.Series]:
        """Расчёт RSI"""
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return None
    
    def _calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[Optional[pd.Series], Optional[pd.Series], Optional[pd.Series]]:
        """Расчёт MACD"""
        try:
            ema_fast = data.ewm(span=fast).mean()
            ema_slow = data.ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            return macd, signal_line, histogram
        except:
            return None, None, None
    
    def _cluster_levels(self, levels: pd.Series, tolerance: float) -> Dict[float, List]:
        """Кластеризация уровней"""
        clustered = {}
        sorted_levels = levels.sort_values()
        
        for level in sorted_levels:
            found_cluster = False
            for cluster_level in clustered.keys():
                if abs(level - cluster_level) / cluster_level <= tolerance:
                    clustered[cluster_level].append(level)
                    found_cluster = True
                    break
            
            if not found_cluster:
                clustered[level] = [level]
        
        return clustered
    
    def _calculate_breakout_strength(self, data: pd.DataFrame, idx: pd.Timestamp, breakout_type: str) -> float:
        """Расчёт силы пробоя"""
        try:
            if breakout_type == 'resistance':
                # Сила пробоя сопротивления
                lookback = 20
                recent_high = data['high'].loc[idx-pd.Timedelta(days=lookback):idx].max()
                breakout_strength = (data.loc[idx, 'close'] - recent_high) / recent_high
            else:
                # Сила пробоя поддержки
                lookback = 20
                recent_low = data['low'].loc[idx-pd.Timedelta(days=lookback):idx].min()
                breakout_strength = (recent_low - data.loc[idx, 'close']) / recent_low
            
            return max(0, breakout_strength)
        except:
            return 0.0
