import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Risk calculation parameters
    RISK_THRESHOLD = 80
    WINDOW_SIZE = 100  # Last N trades for rolling window
    INITIAL_BALANCE = 100000
    HFT_DURATION = 60  # Seconds
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://webhook.site/d80c41f8-1c7d-4d91-8409-4b35c29dcdae")

    # Signal thresholds
    WIN_RATIO_THRESHOLD = 0.3
    DRAWDOWN_THRESHOLD = 0.5
    STOP_LOSS_THRESHOLD = 0.5


settings = Settings()
