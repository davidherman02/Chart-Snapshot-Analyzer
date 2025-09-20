"""
Модуль для генерации автоматических отчётов
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from jinja2 import Template
import json

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Класс для генерации отчётов"""
    
    def __init__(self, config):
        """Инициализация генератора отчётов"""
        self.config = config
        self.reports_config = config.get_reports_config()
        self.output_config = config.get_output_config()
        
        # Создаём директорию для отчётов
        reports_dir = self.output_config.get('reports_dir', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
    
    def generate_breakout_report(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Генерация отчёта по пробоям"""
        try:
            breakout_data = []
            
            for symbol, data in analysis_results.items():
                if 'patterns' in data and 'breakouts' in data['patterns']:
                    breakouts = data['patterns']['breakouts']
                    for breakout in breakouts:
                        breakout_data.append({
                            'symbol': symbol,
                            'type': breakout['type'],
                            'timestamp': breakout['timestamp'],
                            'price': breakout['price'],
                            'volume': breakout['volume'],
                            'strength': breakout['strength']
                        })
            
            if not breakout_data:
                logger.info("Нет пробоев для отчёта")
                return None
            
            # Сортируем по силе пробоя
            breakout_df = pd.DataFrame(breakout_data)
            breakout_df = breakout_df.sort_values('strength', ascending=False)
            
            # Генерируем HTML отчёт
            report_path = self._generate_html_report(
                'breakout_report.html',
                'Отчёт по пробоям уровней',
                self._get_breakout_template(),
                {
                    'breakouts': breakout_df.to_dict('records'),
                    'total_breakouts': len(breakout_df),
                    'resistance_breakouts': len(breakout_df[breakout_df['type'] == 'resistance_breakout']),
                    'support_breakouts': len(breakout_df[breakout_df['type'] == 'support_breakout']),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            logger.info(f"Отчёт по пробоям создан: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчёта по пробоям: {e}")
            return None
    
    def generate_divergence_report(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Генерация отчёта по дивергенциям"""
        try:
            divergence_data = []
            
            for symbol, data in analysis_results.items():
                if 'patterns' in data and 'divergences' in data['patterns']:
                    divergences = data['patterns']['divergences']
                    for divergence in divergences:
                        divergence_data.append({
                            'symbol': symbol,
                            'type': divergence['type'],
                            'timestamp': divergence['timestamp'],
                            'price': divergence['price'],
                            'rsi': divergence['rsi'],
                            'strength': divergence['strength']
                        })
            
            if not divergence_data:
                logger.info("Нет дивергенций для отчёта")
                return None
            
            # Сортируем по силе дивергенции
            divergence_df = pd.DataFrame(divergence_data)
            divergence_df = divergence_df.sort_values('strength', ascending=False)
            
            # Генерируем HTML отчёт
            report_path = self._generate_html_report(
                'divergence_report.html',
                'Отчёт по дивергенциям',
                self._get_divergence_template(),
                {
                    'divergences': divergence_df.to_dict('records'),
                    'total_divergences': len(divergence_df),
                    'bullish_divergences': len(divergence_df[divergence_df['type'] == 'bullish_divergence']),
                    'bearish_divergences': len(divergence_df[divergence_df['type'] == 'bearish_divergence']),
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            logger.info(f"Отчёт по дивергенциям создан: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчёта по дивергенциям: {e}")
            return None
    
    def generate_general_report(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Генерация общего отчёта"""
        try:
            # Собираем статистику
            stats = self._calculate_statistics(analysis_results)
            
            # Генерируем HTML отчёт
            report_path = self._generate_html_report(
                'general_report.html',
                'Общий отчёт по анализу',
                self._get_general_template(),
                {
                    'statistics': stats,
                    'analysis_results': analysis_results,
                    'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            )
            
            logger.info(f"Общий отчёт создан: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации общего отчёта: {e}")
            return None
    
    def generate_markdown_report(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Генерация отчёта в формате Markdown"""
        try:
            reports_dir = self.output_config.get('reports_dir', 'reports')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = os.path.join(reports_dir, f'markdown_report_{timestamp}.md')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# Отчёт по анализу графиков\n\n")
                f.write(f"**Дата генерации:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Статистика
                stats = self._calculate_statistics(analysis_results)
                f.write(f"## Статистика\n\n")
                f.write(f"- Проанализировано символов: {stats['total_symbols']}\n")
                f.write(f"- Общее количество пробоев: {stats['total_breakouts']}\n")
                f.write(f"- Общее количество дивергенций: {stats['total_divergences']}\n")
                f.write(f"- Общее количество изменений тренда: {stats['total_trend_changes']}\n\n")
                
                # Детали по символам
                f.write(f"## Детали по символам\n\n")
                for symbol, data in analysis_results.items():
                    f.write(f"### {symbol}\n\n")
                    
                    if 'patterns' in data:
                        patterns = data['patterns']
                        
                        # Пробои
                        if 'breakouts' in patterns and patterns['breakouts']:
                            f.write(f"**Пробои:**\n")
                            for breakout in patterns['breakouts']:
                                f.write(f"- {breakout['type']} на {breakout['price']:.4f} "
                                       f"(сила: {breakout['strength']:.2f})\n")
                            f.write("\n")
                        
                        # Дивергенции
                        if 'divergences' in patterns and patterns['divergences']:
                            f.write(f"**Дивергенции:**\n")
                            for divergence in patterns['divergences']:
                                f.write(f"- {divergence['type']} на {divergence['price']:.4f} "
                                       f"(RSI: {divergence['rsi']:.2f}, сила: {divergence['strength']:.2f})\n")
                            f.write("\n")
                        
                        # Технические сигналы
                        if 'technical_signals' in patterns:
                            signals = patterns['technical_signals']
                            f.write(f"**Технические сигналы:**\n")
                            
                            if 'rsi' in signals and signals['rsi']['current']:
                                rsi = signals['rsi']
                                f.write(f"- RSI: {rsi['current']:.2f}")
                                if rsi['overbought']:
                                    f.write(" (перекупленность)")
                                elif rsi['oversold']:
                                    f.write(" (перепроданность)")
                                f.write("\n")
                            
                            if 'macd' in signals and signals['macd']['current']:
                                macd = signals['macd']
                                f.write(f"- MACD: {macd['current']:.4f}, Signal: {macd['signal']:.4f}")
                                if macd['bullish_crossover']:
                                    f.write(" (бычье пересечение)")
                                elif macd['bearish_crossover']:
                                    f.write(" (медвежье пересечение)")
                                f.write("\n")
                            
                            f.write("\n")
                    
                    f.write("---\n\n")
            
            logger.info(f"Markdown отчёт создан: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации Markdown отчёта: {e}")
            return None
    
    def _calculate_statistics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Расчёт статистики анализа"""
        stats = {
            'total_symbols': len(analysis_results),
            'total_breakouts': 0,
            'total_divergences': 0,
            'total_trend_changes': 0,
            'total_volume_anomalies': 0,
            'symbols_with_breakouts': 0,
            'symbols_with_divergences': 0,
            'breakout_types': {'resistance_breakout': 0, 'support_breakout': 0},
            'divergence_types': {'bullish_divergence': 0, 'bearish_divergence': 0}
        }
        
        for symbol, data in analysis_results.items():
            if 'patterns' in data:
                patterns = data['patterns']
                
                # Пробои
                if 'breakouts' in patterns:
                    breakouts = patterns['breakouts']
                    stats['total_breakouts'] += len(breakouts)
                    if breakouts:
                        stats['symbols_with_breakouts'] += 1
                    
                    for breakout in breakouts:
                        if breakout['type'] in stats['breakout_types']:
                            stats['breakout_types'][breakout['type']] += 1
                
                # Дивергенции
                if 'divergences' in patterns:
                    divergences = patterns['divergences']
                    stats['total_divergences'] += len(divergences)
                    if divergences:
                        stats['symbols_with_divergences'] += 1
                    
                    for divergence in divergences:
                        if divergence['type'] in stats['divergence_types']:
                            stats['divergence_types'][divergence['type']] += 1
                
                # Изменения тренда
                if 'trend_changes' in patterns:
                    stats['total_trend_changes'] += len(patterns['trend_changes'])
                
                # Аномалии объёма
                if 'volume_anomalies' in patterns:
                    stats['total_volume_anomalies'] += len(patterns['volume_anomalies'])
        
        return stats
    
    def _generate_html_report(self, filename: str, title: str, template: str, data: Dict[str, Any]) -> str:
        """Генерация HTML отчёта"""
        reports_dir = self.output_config.get('reports_dir', 'reports')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(reports_dir, f"{timestamp}_{filename}")
        
        # Рендерим шаблон
        template_obj = Template(template)
        html_content = template_obj.render(**data)
        
        # Сохраняем файл
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _get_breakout_template(self) -> str:
        """Шаблон для отчёта по пробоям"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .resistance { color: #dc3545; }
        .support { color: #28a745; }
        .strength { font-weight: bold; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p class="timestamp">Сгенерировано: {{ generation_time }}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ total_breakouts }}</div>
                <div class="stat-label">Всего пробоев</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ resistance_breakouts }}</div>
                <div class="stat-label">Пробои сопротивления</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ support_breakouts }}</div>
                <div class="stat-label">Пробои поддержки</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Символ</th>
                    <th>Тип</th>
                    <th>Время</th>
                    <th>Цена</th>
                    <th>Объём</th>
                    <th>Сила</th>
                </tr>
            </thead>
            <tbody>
                {% for breakout in breakouts %}
                <tr>
                    <td><strong>{{ breakout.symbol }}</strong></td>
                    <td class="{% if breakout.type == 'resistance_breakout' %}resistance{% else %}support{% endif %}">
                        {{ breakout.type.replace('_', ' ').title() }}
                    </td>
                    <td>{{ breakout.timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>{{ "%.4f"|format(breakout.price) }}</td>
                    <td>{{ "{:,.0f}".format(breakout.volume) }}</td>
                    <td class="strength">{{ "%.2f"|format(breakout.strength) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
        """
    
    def _get_divergence_template(self) -> str:
        """Шаблон для отчёта по дивергенциям"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .bullish { color: #28a745; }
        .bearish { color: #dc3545; }
        .strength { font-weight: bold; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p class="timestamp">Сгенерировано: {{ generation_time }}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ total_divergences }}</div>
                <div class="stat-label">Всего дивергенций</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ bullish_divergences }}</div>
                <div class="stat-label">Бычьи дивергенции</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ bearish_divergences }}</div>
                <div class="stat-label">Медвежьи дивергенции</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Символ</th>
                    <th>Тип</th>
                    <th>Время</th>
                    <th>Цена</th>
                    <th>RSI</th>
                    <th>Сила</th>
                </tr>
            </thead>
            <tbody>
                {% for divergence in divergences %}
                <tr>
                    <td><strong>{{ divergence.symbol }}</strong></td>
                    <td class="{% if divergence.type == 'bullish_divergence' %}bullish{% else %}bearish{% endif %}">
                        {{ divergence.type.replace('_', ' ').title() }}
                    </td>
                    <td>{{ divergence.timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>{{ "%.4f"|format(divergence.price) }}</td>
                    <td>{{ "%.2f"|format(divergence.rsi) }}</td>
                    <td class="strength">{{ "%.2f"|format(divergence.strength) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
        """
    
    def _get_general_template(self) -> str:
        """Шаблон для общего отчёта"""
        return """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-box { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; margin-top: 5px; }
        .symbol-section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .symbol-title { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px; }
        .pattern-list { margin: 10px 0; }
        .pattern-item { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <p class="timestamp">Сгенерировано: {{ generation_time }}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{{ statistics.total_symbols }}</div>
                <div class="stat-label">Проанализировано символов</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ statistics.total_breakouts }}</div>
                <div class="stat-label">Всего пробоев</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ statistics.total_divergences }}</div>
                <div class="stat-label">Всего дивергенций</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{{ statistics.total_trend_changes }}</div>
                <div class="stat-label">Изменений тренда</div>
            </div>
        </div>
        
        {% for symbol, data in analysis_results.items() %}
        <div class="symbol-section">
            <div class="symbol-title">{{ symbol }}</div>
            
            {% if data.patterns.breakouts %}
            <div class="pattern-list">
                <strong>Пробои:</strong>
                {% for breakout in data.patterns.breakouts %}
                <div class="pattern-item">
                    {{ breakout.type.replace('_', ' ').title() }} - {{ "%.4f"|format(breakout.price) }} 
                    (сила: {{ "%.2f"|format(breakout.strength) }})
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if data.patterns.divergences %}
            <div class="pattern-list">
                <strong>Дивергенции:</strong>
                {% for divergence in data.patterns.divergences %}
                <div class="pattern-item">
                    {{ divergence.type.replace('_', ' ').title() }} - {{ "%.4f"|format(divergence.price) }} 
                    (RSI: {{ "%.2f"|format(divergence.rsi) }}, сила: {{ "%.2f"|format(divergence.strength) }})
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if data.patterns.technical_signals %}
            <div class="pattern-list">
                <strong>Технические сигналы:</strong>
                {% if data.patterns.technical_signals.rsi %}
                <div class="pattern-item">
                    RSI: {{ "%.2f"|format(data.patterns.technical_signals.rsi.current) }}
                    {% if data.patterns.technical_signals.rsi.overbought %}(перекупленность){% endif %}
                    {% if data.patterns.technical_signals.rsi.oversold %}(перепроданность){% endif %}
                </div>
                {% endif %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """
