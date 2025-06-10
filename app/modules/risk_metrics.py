from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from database import Base


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
