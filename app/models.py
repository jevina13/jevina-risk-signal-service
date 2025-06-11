from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from .database import Base


class Account(Base):
    __tablename__ = 'accounts'
    login = Column(Integer, primary_key=True)
    account_size = Column(Float)
    platform = Column(Integer)
    phase = Column(Integer)
    user_id = Column(Integer)
    challenge_id = Column(Integer)


class Trade(Base):
    __tablename__ = 'trades'
    identifier = Column(String, primary_key=True)
    action = Column(Integer)
    reason = Column(Integer)
    open_price = Column(Float)
    close_price = Column(Float)
    commission = Column(Float)
    lot_size = Column(Float)
    opened_at = Column(DateTime)
    closed_at = Column(DateTime)
    pips = Column(Float)
    price_sl = Column(Float)
    price_tp = Column(Float)
    profit = Column(Float)
    swap = Column(Float)
    symbol = Column(String)
    contract_size = Column(Float)
    profit_rate = Column(Float)
    platform = Column(Integer)
    trading_account_login = Column(Integer, ForeignKey('accounts.login'))


class RiskMetric(Base):
    __tablename__ = 'risk_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_login = Column(Integer, ForeignKey('accounts.login'))
    timestamp = Column(DateTime)
    win_ratio = Column(Float)
    profit_factor = Column(Float)
    max_drawdown = Column(Float)
    stop_loss_used = Column(Float)
    hft_count = Column(Integer)
    max_layering = Column(Integer)
    risk_score = Column(Float)
    risk_signals = Column(String)
    last_trade_at = Column(DateTime)
