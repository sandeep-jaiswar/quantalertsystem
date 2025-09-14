from setuptools import setup, find_packages

setup(
    name="quantalertsystem",
    version="1.0.0",
    description="Quantitative alerting platform for stock trading signals",
    author="Sandeep Jaiswar",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "duckdb>=0.9.0",
        "pyarrow>=13.0.0",
        "yfinance>=0.2.18",
        "python-telegram-bot>=20.0",
        "python-dotenv>=1.0.0",
        "pydantic-settings>=2.0.0",
        "schedule>=1.2.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "quant-alert=quantalertsystem.main:main",
        ],
    },
)