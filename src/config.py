"""
Модуль конфигурации для анализа графиков
"""

import yaml
import os
from typing import Dict, Any, List


class Config:
    """Класс для управления конфигурацией"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация конфигурации"""
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        if not os.path.exists(self.config_path):
            # Создаём конфигурацию по умолчанию
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            'api': {
                'provider': 'binance',  # binance, yfinance, alpha_vantage
                'api_key': '',
                'api_secret': '',
                'rate_limit': 1.0  # секунды между запросами
            },
            'charts': {
                'width': 1200,
                'height': 800,
                'dpi': 100,
                'style': 'darkgrid',
                'indicators': {
                    'sma': [20, 50, 200],
                    'ema': [12, 26],
                    'rsi': 14,
                    'macd': [12, 26, 9],
                    'bollinger': [20, 2],
                    'volume': True
                }
            },
            'patterns': {
                'breakout': {
                    'enabled': True,
                    'lookback_periods': 20,
                    'volume_threshold': 1.5
                },
                'divergence': {
                    'enabled': True,
                    'rsi_periods': 14,
                    'min_divergence_strength': 0.3
                },
                'support_resistance': {
                    'enabled': True,
                    'min_touches': 2,
                    'tolerance': 0.02
                }
            },
            'reports': {
                'format': 'html',  # html, pdf, markdown
                'include_charts': True,
                'include_indicators': True,
                'include_patterns': True
            },
            'output': {
                'charts_dir': 'charts',
                'reports_dir': 'reports',
                'screenshots_dir': 'screenshots',
                'data_dir': 'data'
            }
        }
    
    def _save_config(self, config: Dict[str, Any]):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации по ключу"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Установка значения конфигурации"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def get_api_config(self) -> Dict[str, Any]:
        """Получение конфигурации API"""
        return self.get('api', {})
    
    def get_charts_config(self) -> Dict[str, Any]:
        """Получение конфигурации графиков"""
        return self.get('charts', {})
    
    def get_patterns_config(self) -> Dict[str, Any]:
        """Получение конфигурации паттернов"""
        return self.get('patterns', {})
    
    def get_reports_config(self) -> Dict[str, Any]:
        """Получение конфигурации отчётов"""
        return self.get('reports', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Получение конфигурации вывода"""
        return self.get('output', {})
