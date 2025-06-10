from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from database import Base


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
