# Trading Decision Making System

A Python and PostgreSQL project for analyzing 15-minute BTC/USDT candlestick data. The system validates market data, stores OHLCV records, calculates technical indicators, and generates rule-based trading signals with explanations.

## Features

- Imports BTCUSDT 15-minute Binance candle data
- Stores candles and analysis results in PostgreSQL
- Calculates:
  - SMA 20 and SMA 50
  - Moving-average crossovers
  - Bollinger Bands
  - ATR
  - RSI
  - MACD
- Generates `BUY`, `SELL`, or `HOLD` signals
- Adds a reason and volatility risk filter to every signal
- Includes dataset and technical-indicator validation tests

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- db/
|   |   |   |-- models.py
|   |   |   `-- session.py
|   |   `-- services/
|   |       |-- indicators.py
|   |       `-- signals.py
|   |-- scripts/
|   |   |-- create_database.py
|   |   |-- ingest_candles.py
|   |   |-- calculate_indicators.py
|   |   |-- generate_signals.py
|   |   `-- verify_db.py
|   `-- .env.example
|-- data/
|-- Scripts/
|-- tests/
`-- README.md
```

## Requirements

- Python 3.10 or newer
- PostgreSQL
- Python packages:
  - pandas
  - numpy
  - SQLAlchemy
  - psycopg2-binary
  - python-dotenv
  - pytest

