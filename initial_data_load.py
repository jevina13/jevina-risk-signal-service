from app.models import Base, Account, Trade
from dotenv import load_dotenv
from app.database import engine
import pandas as pd
import os

load_dotenv(".env")

# Get CSV paths from environment
ACCOUNTS_CSV = os.getenv("ACCOUNTS_CSV_PATH")
TRADES_CSV = os.getenv("TRADES_CSV_PATH")


def load_data():
    # Create tables
    Base.metadata.create_all(bind=engine)

    if not ACCOUNTS_CSV or not os.path.exists(ACCOUNTS_CSV):
        raise FileNotFoundError(f"Accounts CSV path not found: {ACCOUNTS_CSV}")

    # Load accounts
    accounts_df = pd.read_csv(ACCOUNTS_CSV)

    accounts_df.to_sql('accounts', engine, if_exists='append', index=False)
    print(" accounts loaded ")

    if not TRADES_CSV or not os.path.exists(TRADES_CSV):
        raise FileNotFoundError(f"Trades CSV path not found: {TRADES_CSV}")

    # Load trades
    trades_df = pd.read_csv(TRADES_CSV)

    # Handle index column
    if 'Unnamed: 0' in trades_df.columns:
        trades_df = trades_df.drop(columns=['Unnamed: 0'])

    # Handle duplicates
    trades_df = trades_df.drop_duplicates(subset='identifier', keep='first')
    print(f"Loaded {len(trades_df)} trades after deduplication")

    # Handle large integers in identifier
    trades_df['identifier'] = trades_df['identifier'].astype(str)

    # Convert datetime columns
    for col in ['opened_at', 'closed_at']:
        trades_df[col] = pd.to_datetime(trades_df[col])

    trades_df.to_sql('trades', engine, if_exists='append', index=False)
    print(" data loaded ")


if __name__ == "__main__":
    load_data()
    print("Initial data loaded successfully")
