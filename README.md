# 📊 Chart Snapshot Analyzer

**Automatic Chart Analysis & Report Generation**

A system for automated chart snapshots based on predefined conditions, technical pattern analysis, and detailed report generation. Supports detection of breakouts, divergences, trend changes, and other patterns without the need to manually review each chart.  

## ✨ Features

### 🔍 Automatic Analysis
- **Breakouts** – detect support and resistance breakouts  
- **Divergences** – analyze discrepancies between price and indicators  
- **Trend changes** – identify market sentiment shifts  
- **Volume anomalies** – detect unusual trading activity  
- **Technical signals** – RSI, MACD, moving averages  

### 📈 Visualization
- **Professional charts** with technical indicators  
- **Comparative analysis** across multiple symbols  
- **Customizable styles** and display parameters  
- **High-quality snapshots** for reporting  

### 📋 Reports
- **HTML reports** with interactive elements  
- **Markdown reports** for documentation  
- **Detailed statistics** for all patterns  
- **Automatic grouping** by signal type  

### 🔌 Integrations
- **Yahoo Finance** – stocks, ETFs, indices  
- **Binance API** – crypto pairs  
- **Custom data providers** supported  
- **Flexible configuration** via YAML  

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/chart-snapshot-analyzer.git
cd chart-snapshot-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Basic Usage

```python
from main import ChartSnapshotAnalyzer

# Create analyzer
analyzer = ChartSnapshotAnalyzer("config.yaml")

# Analyze tickers
tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]
reports = analyzer.run_analysis(tickers, "1h")

print(f"Reports generated: {len(reports)}")
```

### Command Line

```bash
# Analyze stocks
python main.py --tickers AAPL GOOGL MSFT --timeframe 1h

# Analyze cryptocurrencies
python main.py --tickers BTC/USDT ETH/USDT --timeframe 4h

# With custom config
python main.py --tickers SPY QQQ --timeframe 15m --config custom_config.yaml
```

## 📖 Documentation

### Configuration

Main settings are in `config.yaml`:

```yaml
# API settings
api:
  provider: yfinance  # yfinance, binance
  rate_limit: 1.0     # delay between requests

# Chart settings
charts:
  width: 1200
  height: 800
  indicators:
    sma: [20, 50, 200]
    rsi: 14
    macd: [12, 26, 9]

# Pattern analysis
patterns:
  breakout:
    enabled: true
    lookback_periods: 20
    volume_threshold: 1.5
```

### Supported Indicators

- **SMA** – Simple Moving Average  
- **EMA** – Exponential Moving Average  
- **RSI** – Relative Strength Index  
- **MACD** – Moving Average Convergence Divergence  
- **Bollinger Bands**  
- **Volume** – trade volume analysis  

### Pattern Types

#### Breakouts
- **Resistance breakouts** – price breaks above local high  
- **Support breakouts** – price breaks below local low  
- **Volume filtering** – only significant breakouts  

#### Divergences
- **Bullish divergences** – price falls, RSI rises  
- **Bearish divergences** – price rises, RSI falls  
- **Customizable sensitivity**  

#### Trend Changes
- **Moving average crossovers** (SMA 20/50)  
- **MACD signals** – bullish/bearish crossovers  
- **RSI extremes** – overbought/oversold levels  

## 🛠️ Usage Examples

### Stock Analysis

```python
# Analyze large-cap tech companies
analyzer = ChartSnapshotAnalyzer()
tech_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]
reports = analyzer.run_analysis(tech_stocks, "1d")
```

### Crypto Analysis

```python
# Configure Binance API
config = Config("crypto_config.yaml")
config.set('api.provider', 'binance')
config.set('api.api_key', 'your_api_key')

analyzer = ChartSnapshotAnalyzer(config)
crypto_pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
reports = analyzer.run_analysis(crypto_pairs, "4h")
```

### Comparative Analysis

```python
# Create comparison chart
chart_generator = ChartGenerator(config)
comparison_chart = chart_generator.create_comparison_chart(
    symbols=["SPY", "QQQ", "IWM"],
    data_dict=analysis_data,
    timeframe="1d"
)
```

### Custom Patterns

```python
# Adjust sensitivity
config.set('patterns.breakout.volume_threshold', 1.2)
config.set('patterns.divergence.min_divergence_strength', 0.2)

# More aggressive pattern detection
analyzer = ChartSnapshotAnalyzer(config)
```

## 📊 Project Structure

```
chart-snapshot-analyzer/
├── main.py                 # Main module
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── setup.py                # Setup script
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py           # Config management
│   ├── data_fetcher.py     # Data fetching
│   ├── chart_generator.py  # Chart generation
│   ├── pattern_analyzer.py # Pattern analysis
│   └── report_generator.py # Report generation
├── examples/               # Usage examples
│   └── example_usage.py
├── charts/                 # Saved charts
├── reports/                # Generated reports
├── logs/                   # Logs
└── data/                   # Cached data
```

## 🔧 Development

### Dev Installation

```bash
# Clone repository
git clone https://github.com/your-username/chart-snapshot-analyzer.git
cd chart-snapshot-analyzer

# Create virtual env
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scriptsctivate     # Windows

# Install dev dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src

# Code style checks
flake8 src/
black src/
```

### Adding New Providers

```python
class CustomProvider(DataProvider):
    def get_data(self, symbol: str, timeframe: str, limit: int = 1000):
        # Your implementation
        pass
    
    def get_available_symbols(self):
        # Your implementation
        pass
```

## 📈 Performance

### Query Optimization
- **Data caching** for reuse  
- **Customizable API rate limits**  
- **Batch processing** for multiple symbols  

### Scalability
- **Parallel symbol processing**  
- **Asynchronous API requests**  
- **Incremental analysis** of large datasets  

## 🤝 Contributing

We welcome contributions! Please:  

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/amazing-feature`)  
3. Commit changes (`git commit -m 'Add amazing feature'`)  
4. Push branch (`git push origin feature/amazing-feature`)  
5. Open a Pull Request  

### Guidelines
- Follow existing code style  
- Add tests for new features  
- Update documentation  
- Use meaningful commit messages  

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.  

## 🆘 Support

### FAQ

**Q: How to add a new indicator?**  
A: Extend the `TechnicalIndicators` class in `src/chart_generator.py`  

**Q: Can I use other data sources?**  
A: Yes, by creating a new provider inheriting from `DataProvider`  

**Q: How to tune analysis sensitivity?**  
A: Edit parameters in the `patterns` section of `config.yaml`  

### Get Help

- 📧 Email: chart.analysis@example.com  
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/chart-snapshot-analyzer/issues)  
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/chart-snapshot-analyzer/discussions)  

## 🏷️ Tags

`trading` `analysis` `charts` `technical-analysis` `finance` `cryptocurrency` `stocks` `patterns` `breakouts` `divergences` `reports` `automation` `python` `matplotlib` `pandas` `yfinance` `binance`

## 📊 Badges

![GitHub stars](https://img.shields.io/github/stars/your-username/chart-snapshot-analyzer?style=social)  
![GitHub forks](https://img.shields.io/github/forks/your-username/chart-snapshot-analyzer?style=social)  
![GitHub issues](https://img.shields.io/github/issues/your-username/chart-snapshot-analyzer)  
![GitHub license](https://img.shields.io/github/license/your-username/chart-snapshot-analyzer)  
![Python version](https://img.shields.io/pypi/pyversions/chart-snapshot-analyzer)  

---

**Made with ❤️ for traders and analysts**  
