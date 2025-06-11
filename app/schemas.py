from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .enums import Phase, Action


# Risk report response schema
class RiskReport(BaseModel):
    trading_account_login: int
    risk_signals: List[str]
    risk_score: float
    last_trade_at: datetime

    class Config:
        from_attributes = True


# Webhook notification schema
class WebhookNotification(BaseModel):
    trading_account_login: int
    risk_signals: List[str]
    risk_score: float
    last_trade_at: datetime


# Configuration update schema
class ConfigUpdate(BaseModel):
    window_size: Optional[int] = None
    win_ratio_threshold: Optional[float] = None
    drawdown_threshold: Optional[float] = None
    stop_loss_threshold: Optional[float] = None
    risk_threshold: Optional[float] = None
    initial_balance: Optional[float] = None
    hft_duration: Optional[int] = None


# Trade data schema (for potential POST endpoints)
class TradeCreate(BaseModel):
    identifier: str
    action: Action
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
    phase: Phase
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
        from_attributes = True


# Health check response
class HealthCheck(BaseModel):
    status: str
    db_status: str
    last_calculation: Optional[datetime] = None
    accounts_processed: int
