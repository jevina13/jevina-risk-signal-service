from app.models import Base, Account, Trade, RiskMetric
from fastapi import FastAPI, Depends, HTTPException, Query, Path
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import get_db
import app.schemas as schemas
import app.utils as utils
from app.config import settings
import app.models as models
from datetime import datetime
import requests
import logging
import traceback
import asyncio


# Global task reference
background_task = None

# Setup logging
logging.basicConfig(filename='risk_service.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist
    try:
        logger.info("Starting application lifespan - ensuring DB schema ...")
        from app.database import engine
        # from app.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("DB schema ready - launching background task")

        # Startup
        global background_task

        background_task = asyncio.create_task(calculate_risk_metrics_periodically())

        yield
    except Exception:
        logger.critical("Fatal error during startup:\n%s", traceback.format_exc())
        raise
    # Shutdown
    finally:
        logger.info("Shutting down - cancelling background task")
        if background_task and not background_task.done():
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                logger.info("Background task cancelled cleanly.")

app = FastAPI(lifespan=lifespan)


async def calculate_risk_metrics_periodically():
    """Run risk calculation every 5 minutes"""
    # from time import sleep
    loop = asyncio.get_running_loop()
    while True:
        try:
            # run the sync, CPU-bound job in a default thread-pool
            await loop.run_in_executor(None, calculate_risk_metrics)
            logger.info("Cycle completed ")

            # await asyncio.sleep(300)          # pause 5 min
        except Exception as e:
            logger.error(f"Error in periodic calculation: {str(e)}")
        await asyncio.sleep(300)  # pause 5 minutes


def calculate_risk_metrics():
    """Main risk calculation function"""
    logger.info("Starting risk metrics calculation")
    db = next(get_db())
    try:
        accounts = db.query(models.Account).all()
        for account in accounts:
            # Get last N trades for rolling window
            trades = (db.query(models.Trade)
                     .filter(models.Trade.trading_account_login == account.login)
                     .order_by(models.Trade.closed_at.desc())
                     .limit(settings.WINDOW_SIZE)
                     .all())

            if not trades:
                logger.debug("Account %s - no trades, skipping", account.login)
                continue

            # Calculate metrics
            metrics = utils.calculate_metrics(trades)
            risk_score = utils.calculate_risk_score(metrics)
            risk_signals = utils.generate_risk_signals(metrics)

            # Save to database
            risk_metric = models.RiskMetric(
                account_login=account.login,
                timestamp=datetime.now(),
                win_ratio=metrics['win_ratio'],
                profit_factor=metrics['profit_factor'],
                max_drawdown=metrics['max_drawdown'],
                stop_loss_used=metrics['stop_loss_used'],
                take_profit_used=metrics['take_profit_used'],
                hft_count=metrics['hft_count'],
                max_layering=metrics['max_layering'],
                risk_score=risk_score,
                risk_signals=",".join(risk_signals),
                last_trade_at=metrics['last_trade_at']
            )
            db.add(risk_metric)
            db.commit()

            # Send webhook if risk score exceeds threshold
            if risk_score > settings.RISK_THRESHOLD:
                send_webhook(account.login, risk_score, risk_signals, metrics["last_trade_at"])

        logger.info("Completed risk metrics calculation")
    except Exception:
        logger.error("Exception during risk calculation:\n%s", traceback.format_exc())
    finally:
        db.close()
        logger.debug("DB session closed")


def send_webhook(account_login: int, score: float, signals: list[str], last_trade: datetime):
    payload = {
        "trading_account_login": account_login,
        "risk_signals": signals,
        "risk_score": score,
        "last_trade_at": last_trade.isoformat() if last_trade else None,
    }
    try:
        response = requests.post(settings.WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        logger.info("Webhook sent - account %s (HTTP %s)", account_login, response.status_code)
    except Exception as e:
        logger.error(f"Webhook FAILED - account{e}")


# API Endpoints
@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")


@app.get("/risk-report/{account_login}", response_model=schemas.RiskReport)
def get_risk_report(account_login: int, db: Session = Depends(get_db)):
    # Get latest risk metric for account
    risk_metric = (db.query(models.RiskMetric)
                 .filter(models.RiskMetric.account_login == account_login)
                 .order_by(models.RiskMetric.timestamp.desc())
                 .first())

    if not risk_metric:
        logger.warning(f"Account not found: {account_login}")
        raise HTTPException(status_code=404, detail="Account not found")

    response = {
        "trading_account_login": account_login,
        "risk_signals": risk_metric.risk_signals.split(",") if risk_metric.risk_signals else [],
        "risk_score": risk_metric.risk_score,
        "last_trade_at": risk_metric.last_trade_at
    }

    logger.info(f"GET /risk-report/{account_login} - {response}")
    return response


@app.post("/admin/update-config")
def update_config(new_config: schemas.ConfigUpdate,
            admin_token: str = Query(..., description="Admin token")):

    if admin_token != "secure_admin_token":
        logger.warning(f"User Unauthorized : Wrong token! {admin_token}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Update configuration
    if new_config.window_size is not None:
        settings.WINDOW_SIZE = new_config.window_size
    if new_config.win_ratio_threshold is not None:
        settings.WIN_RATIO_THRESHOLD = new_config.win_ratio_threshold
    if new_config.drawdown_threshold is not None:
        settings.DRAWDOWN_THRESHOLD = new_config.drawdown_threshold
    if new_config.stop_loss_threshold is not None:
        settings.STOP_LOSS_THRESHOLD = new_config.stop_loss_threshold
    if new_config.take_profit_threshold is not None:
        settings.TAKE_PROFIT_THRESHOLD = new_config.take_profit_threshold
    if new_config.risk_threshold is not None:
        settings.RISK_THRESHOLD = new_config.risk_threshold
    if new_config.initial_balance is not None:
        settings.INITIAL_BALANCE = new_config.initial_balance
    if new_config.hft_duration is not None:
        settings.HFT_DURATION = new_config.hft_duration

    logger.info(f"Configuration updated: {new_config.model_dump()}")
    return {"message": f"Configuration updated {new_config}"}


@app.get("/risk/user/{user_id}", response_model=schemas.RiskReport)
def get_user_risk_report(user_id: int = Path(...), db: Session = Depends(get_db)):
    accounts = db.query(models.Account).filter_by(user_id=user_id).all()
    if not accounts:
        logger.warning(f"User ID not found {user_id}.")
        raise HTTPException(status_code=404, detail="User not found")

    account_logins = [a.login for a in accounts]
    trades = (db.query(models.Trade)
                .filter(models.Trade.trading_account_login.in_(account_logins))
                .order_by(models.Trade.closed_at.desc())
                .limit(settings.WINDOW_SIZE)
                .all())

    if not trades:
        logger.warning(f"No trades found for User ID {user_id}. Accounts: {account_logins}")
        raise HTTPException(status_code=404, detail="No trades found for user")

    metrics = utils.calculate_metrics(trades)
    risk_score = utils.calculate_risk_score(metrics)
    risk_signals = utils.generate_risk_signals(metrics)

    response = {
        "trading_account_login": user_id,
        "risk_signals": risk_signals,
        "risk_score": risk_score,
        "last_trade_at": metrics['last_trade_at']
    }

    logger.info(f"GET /risk/user/{user_id} - {response}")
    return response


@app.get("/risk/challenge/{challenge_id}", response_model=schemas.RiskReport)
def get_challenge_risk_report(challenge_id: int = Path(...), db: Session = Depends(get_db)):
    accounts = db.query(models.Account).filter_by(challenge_id=challenge_id).all()
    if not accounts:
        logger.warning(f"Challenge ID not found {challenge_id}.")
        raise HTTPException(status_code=404, detail="Challenge not found")

    account_logins = [a.login for a in accounts]
    trades = (db.query(models.Trade)
                .filter(models.Trade.trading_account_login.in_(account_logins))
                .order_by(models.Trade.closed_at.desc())
                .limit(settings.WINDOW_SIZE)
                .all())

    if not trades:
        logger.warning(f"No trades found for Challenge ID {challenge_id}. Accounts: {account_logins}")
        raise HTTPException(status_code=404, detail="No trades found for challenge")

    metrics = utils.calculate_metrics(trades)
    risk_score = utils.calculate_risk_score(metrics)
    risk_signals = utils.generate_risk_signals(metrics)

    response = {
        "trading_account_login": challenge_id,
        "risk_signals": risk_signals,
        "risk_score": risk_score,
        "last_trade_at": metrics['last_trade_at']
    }

    logger.info(f"GET /risk/challenge/{challenge_id} - {response}")
    return response


@app.get("/health")
def health_check():
    response = {
        "status": "ok",
        "background_task": "running" if background_task and not background_task.done() else "inactive"
    }

    logger.info(f"GET /health/  - {response}")
    return response
