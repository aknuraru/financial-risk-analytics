import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine, text

TICKERS = ["AAPL", "MSFT", "NVDA"]


def download_prices(period="5y") -> pd.DataFrame:
    raw = yf.download(TICKERS, period=period, auto_adjust=True, progress=False, threads=False)
    if raw.empty:
        raise RuntimeError("Market download returned no data")
    prices = raw["Close"][TICKERS].dropna().sort_index()
    prices.index = pd.to_datetime(prices.index).tz_localize(None).normalize()
    if len(prices) < 300 or (prices <= 0).any().any():
        raise ValueError("Insufficient or invalid market data")
    return prices


def save_prices(prices: pd.DataFrame, database_url: str):
    from pathlib import Path
    engine = create_engine(database_url)
    schema = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
    with engine.begin() as conn:
        for stmt in schema.read_text().split(";"):
            if stmt.strip():
                conn.execute(text(stmt))
        # Idempotent upsert for reruns
        for date, row in prices.iterrows():
            for ticker, price in row.items():
                conn.execute(text("""INSERT INTO market_prices (ticker,price_date,close_price)
                    VALUES (:ticker,:day,:price) ON CONFLICT (ticker,price_date)
                    DO UPDATE SET close_price=EXCLUDED.close_price"""),
                    {"ticker": ticker, "day": date.date(), "price": float(price)})


def load_prices(database_url: str) -> pd.DataFrame:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        data = pd.read_sql(text("SELECT ticker, price_date, close_price FROM market_prices ORDER BY price_date"), conn)
    if data.empty:
        raise ValueError("Database is empty. Run ingestion first")
    data["price_date"] = pd.to_datetime(data["price_date"])
    prices = data.pivot(index="price_date", columns="ticker", values="close_price")
    return prices[TICKERS].dropna()
