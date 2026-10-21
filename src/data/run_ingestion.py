import os
from dotenv import load_dotenv
from src.data.ingest import download_prices, save_prices

load_dotenv()
url = os.getenv("DATABASE_URL")
if not url:
    raise RuntimeError("Set DATABASE_URL in .env")
prices = download_prices()
save_prices(prices, url)
print(f"Loaded {len(prices)} days for {list(prices.columns)}")
