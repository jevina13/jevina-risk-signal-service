import pandas as pd
from app.models import Base, Account, Trade
from app.database import engine


def load_data():
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Initial")

    # Load accounts
    accounts_df = pd.read_csv("test_data/test_task_accounts.csv")

    accounts_df.to_sql('accounts', engine, if_exists='append', index=False)
    print(" accounts loaded ")
    
    # Load trades
    trades_df = pd.read_csv("test_data/test_task_trades.csv")

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
