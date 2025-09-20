#!/usr/bin/env python3
"""
Установочный скрипт для системы анализа графиков
"""

from setuptools import setup, find_packages
import os

# Читаем README файл
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Система автоматического анализа графиков и генерации отчётов"

# Читаем requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="chart-snapshot-analyzer",
    version="1.0.0",
    author="Chart Analysis Team",
    author_email="chart.analysis@example.com",
    description="Автоматический анализ графиков и генерация отчётов",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/chart-snapshot-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chart-analyzer=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    keywords=[
        "trading", "analysis", "charts", "technical-analysis", 
        "finance", "cryptocurrency", "stocks", "patterns",
        "breakouts", "divergences", "reports", "automation"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/chart-snapshot-analyzer/issues",
        "Source": "https://github.com/your-username/chart-snapshot-analyzer",
        "Documentation": "https://chart-snapshot-analyzer.readthedocs.io/",
    },
)
