from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


# Trade data schema (for potential POST endpoints)
class TradeCreate(BaseModel):
    identifier: str
    action: int
    reason: int
    open_price: float
    close_price: float
    commission: float
    lot_size: float
    opened_at: datetime
    closed_at: datetime
    pips: float
    price_sl: Optional[float] = None
    price_tp: Optional[float] = None
    profit: float
    swap: float
    symbol: str
    contract_size: float
    profit_rate: float
    platform: int
    trading_account_login: int


# Account data schema
class AccountCreate(BaseModel):
    login: int
    account_size: float
    platform: int
    phase: int
    user_id: int
    challenge_id: int


# Risk metric schema
class RiskMetric(BaseModel):
    account_login: int
    timestamp: datetime
    win_ratio: float
    profit_factor: float
    max_drawdown: float
    stop_loss_used: float
    hft_count: int
    max_layering: int
    risk_score: float
    risk_signals: List[str]
    last_trade_at: datetime

    class Config:
        orm_mode = True
