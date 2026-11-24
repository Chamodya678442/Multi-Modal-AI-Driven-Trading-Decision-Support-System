from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Index,
    func
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class MarketCandle(Base):
    """
    Stores 15-minute candlestick market data (OHLCV + trade flow)
    for cryptocurrency pairs collected from Binance.
    """
    __tablename__ = "market_candles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(20), default="BTCUSDT", nullable=False, index=True)
    timeframe = Column(String(10), default="15m", nullable=False)
    open_time = Column(DateTime(timezone=True), unique=True, nullable=False, index=True)
    close_time = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    quote_volume = Column(Float, nullable=False)
    trades_count = Column(Integer, nullable=False)
    taker_buy_base = Column(Float, nullable=False)
    taker_buy_quote = Column(Float, nullable=False)

    # One-to-one relationship with TechnicalIndicator
    indicator = relationship(
        "TechnicalIndicator",
        back_populates="candle",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # One-to-many relationship with TradingSignal
    signals = relationship(
        "TradingSignal",
        back_populates="candle",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_candle_symbol_time", "symbol", "open_time"),
    )

    def __repr__(self):
        return f"<MarketCandle(symbol={self.symbol}, open_time={self.open_time}, close={self.close})>"


class TechnicalIndicator(Base):
    """
    Stores computed technical indicators for each candle:
    SMA 20, SMA 50, MA Crossover, Bollinger Bands, ATR, RSI, MACD.
    """
    __tablename__ = "technical_indicators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candle_id = Column(
        Integer,
        ForeignKey("market_candles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    sma_20 = Column(Float, nullable=True)
    sma_50 = Column(Float, nullable=True)
    ma_crossover = Column(Integer, default=0)  # +1: Golden Cross, -1: Death Cross, 0: None
    bb_upper = Column(Float, nullable=True)
    bb_middle = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    atr_14 = Column(Float, nullable=True)
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)

    candle = relationship("MarketCandle", back_populates="indicator")

    def __repr__(self):
        return f"<TechnicalIndicator(candle_id={self.candle_id}, rsi={self.rsi_14})>"


class TradingSignal(Base):
    """
    Stores generated BUY / SELL / HOLD recommendations and explanations.
    """
    __tablename__ = "trading_signals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candle_id = Column(
        Integer,
        ForeignKey("market_candles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    signal = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    strategy = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)     # For Semester 7 ML confidence
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candle = relationship("MarketCandle", back_populates="signals")

    def __repr__(self):
        return f"<TradingSignal(candle_id={self.candle_id}, signal={self.signal})>"
