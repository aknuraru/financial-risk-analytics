# Financial Risk Analytics Dashboard

Educational market-risk analytics prototype for a long-only, daily-rebalanced portfolio of AAPL, MSFT and NVDA in USD.

## Setup (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
python -m src.data.run_ingestion
python -m pytest -q
streamlit run app/main.py
```

Run from the repository root. Market data ingestion needs internet access. The PostgreSQL database is available on localhost port 5432; change the port if occupied. Keep `.env` out of Git.

## Models and assumptions
- Adjusted historical daily closes, USD; ticker coverage is synchronized on dates.
- Constant-weight daily-rebalanced portfolio; ignores fees, dividends beyond adjusted price treatment, taxes, liquidity, FX and intraday changes.
- Historical one-day VaR uses the discrete higher empirical quantile of portfolio loss.
- ES is the average of the worst `(1-confidence)` proportion of losses, with fractional weighting at the tail boundary.
- Stress shocks are direct percentage changes to stock prices, not calibrated forecasts.
- Rolling backtesting forecasts using only earlier observations and compares against the next daily loss. No formal regulatory model approval is implied.
- Dashboard risk limits are configurable demo inputs; no production alert service.

## Roadmap
1. Project environment and PostgreSQL
2. Ingest market data and validate
3. Compute returns, VaR, ES, volatility
4. Stress test scenarios
5. Rolling backtest
6. VaR limits
7. Streamlit dashboard
8. pytest and GitHub

## Next improvements
- Persist daily risk metrics and breaches in PostgreSQL.
- Add a robust trading calendar, handling for delistings and corporate actions.
- Add Kupiec unconditional coverage and Christoffersen independence tests.
- Implement position-based P&L and FX exposures; document mark-to-market assumptions.
- Add automated jobs, logging, authentication, CI and database migrations.

Not investment advice or a production risk model.
