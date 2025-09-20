"""
Модуль для получения данных с бирж и финансовых API
"""

import pandas as pd
import numpy as np
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import yfinance as yf
import ccxt
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Абстрактный класс для провайдеров данных"""
    
    @abstractmethod
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000) -> Optional[pd.DataFrame]:
        """Получение данных"""
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> list:
        """Получение доступных символов"""
        pass


class YahooFinanceProvider(DataProvider):
    """Провайдер данных Yahoo Finance"""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def _rate_limit_wait(self):
        """Ожидание для соблюдения лимита запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000) -> Optional[pd.DataFrame]:
        """Получение данных с Yahoo Finance"""
        try:
            self._rate_limit_wait()
            
            # Конвертируем таймфрейм
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }
            
            interval = interval_map.get(timeframe, '1h')
            
            # Получаем данные
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y", interval=interval)
            
            if data.empty:
                logger.warning(f"Нет данных для символа {symbol}")
                return None
            
            # Ограничиваем количество данных
            if len(data) > limit:
                data = data.tail(limit)
            
            # Переименовываем колонки для единообразия
            data.columns = [col.lower() for col in data.columns]
            
            # Добавляем временную метку
            data['timestamp'] = data.index
            
            logger.info(f"Получено {len(data)} записей для {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения данных для {symbol}: {e}")
            return None
    
    def get_available_symbols(self) -> list:
        """Получение доступных символов (заглушка)"""
        return []


class BinanceProvider(DataProvider):
    """Провайдер данных Binance"""
    
    def __init__(self, api_key: str = "", api_secret: str = "", rate_limit: float = 1.0):
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limit = rate_limit
        self.last_request_time = 0
        
        # Инициализируем клиент Binance
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': False,
            'rateLimit': int(rate_limit * 1000)
        })
    
    def _rate_limit_wait(self):
        """Ожидание для соблюдения лимита запросов"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000) -> Optional[pd.DataFrame]:
        """Получение данных с Binance"""
        try:
            self._rate_limit_wait()
            
            # Конвертируем таймфрейм
            timeframe_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d'
            }
            
            tf = timeframe_map.get(timeframe, '1h')
            
            # Получаем данные
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)
            
            if not ohlcv:
                logger.warning(f"Нет данных для символа {symbol}")
                return None
            
            # Создаём DataFrame
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            
            logger.info(f"Получено {len(data)} записей для {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения данных для {symbol}: {e}")
            return None
    
    def get_available_symbols(self) -> list:
        """Получение доступных символов"""
        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Ошибка получения символов: {e}")
            return []


class DataFetcher:
    """Основной класс для получения данных"""
    
    def __init__(self, config):
        """Инициализация загрузчика данных"""
        self.config = config
        self.provider = self._create_provider()
    
    def _create_provider(self) -> DataProvider:
        """Создание провайдера данных на основе конфигурации"""
        api_config = self.config.get_api_config()
        provider_name = api_config.get('provider', 'yfinance')
        
        if provider_name == 'binance':
            return BinanceProvider(
                api_key=api_config.get('api_key', ''),
                api_secret=api_config.get('api_secret', ''),
                rate_limit=api_config.get('rate_limit', 1.0)
            )
        else:
            return YahooFinanceProvider(
                rate_limit=api_config.get('rate_limit', 1.0)
            )
    
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000) -> Optional[pd.DataFrame]:
        """Получение данных для символа"""
        return self.provider.get_data(symbol, timeframe, limit)
    
    def get_available_symbols(self) -> list:
        """Получение доступных символов"""
        return self.provider.get_available_symbols()
    
    def validate_symbol(self, symbol: str) -> bool:
        """Проверка валидности символа"""
        try:
            data = self.get_data(symbol, '1d', limit=1)
            return data is not None and not data.empty
        except:
            return False
