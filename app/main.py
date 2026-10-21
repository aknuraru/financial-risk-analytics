import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from src.data.ingest import load_prices, TICKERS
from src.risk.metrics import portfolio_returns, risk_metrics
from src.risk.stress import stress_portfolio
from src.risk.backtest import rolling_backtest
from src.risk.limits import check_limit

load_dotenv()
st.set_page_config(page_title="Financial Risk Analytics", layout="wide")
st.title("Financial Risk Analytics")
st.caption("Educational prototype — historical, long-only, daily-rebalanced USD portfolio")
url = os.getenv("DATABASE_URL")
if not url:
    st.error("Set DATABASE_URL in .env and start PostgreSQL")
    st.stop()
try:
    prices = load_prices(url)
except Exception as exc:
    st.error(f"Unable to load prices: {exc}. Run the ingestion command first.")
    st.stop()

value = st.sidebar.number_input("Portfolio value (USD)", min_value=1000.0, value=100000.0, step=10000.0)
confidence = st.sidebar.selectbox("Confidence", [0.95, 0.99])
w_a = st.sidebar.slider("AAPL weight (%)", 0, 100, 40)
w_m = st.sidebar.slider("MSFT weight (%)", 0, 100-w_a, 35)
w_n = 100-w_a-w_m
st.sidebar.write(f"NVDA weight: {w_n}%")
weights = np.array([w_a, w_m, w_n]) / 100
returns = portfolio_returns(prices[TICKERS], weights)
metrics = risk_metrics(returns, value, confidence)
limit = st.sidebar.number_input("VaR limit (USD)", min_value=1.0, value=2500.0)
status = check_limit(metrics["var"], limit)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Portfolio", f"${value:,.0f}")
c2.metric("1-day VaR", f"${metrics['var']:,.0f}")
c3.metric("1-day ES", f"${metrics['es']:,.0f}")
c4.metric("Annualized volatility", f"{metrics['volatility_annual']:.1%}")
st.subheader("Risk limits")
st.write(f"VaR limit utilization: {status['utilization_pct']:.1f}%")
if status["breached"]:
    st.error("VaR risk limit exceeded")
else:
    st.success("VaR within configured limit")

st.subheader("Portfolio cumulative returns")
cumulative = (1 + returns).cumprod() - 1
fig = go.Figure()
fig.add_trace(go.Scatter(x=cumulative.index, y=cumulative.values, name="Cumulative return"))
fig.update_layout(yaxis_tickformat=".1%")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Stress testing")
scenario = st.selectbox("Scenario", ["All stocks -20%", "NVDA -35%, others -10%", "All stocks +10%"])
scenarios = {
    "All stocks -20%": {t:-0.20 for t in TICKERS},
    "NVDA -35%, others -10%": {"AAPL":-0.10,"MSFT":-0.10,"NVDA":-0.35},
    "All stocks +10%": {t:0.10 for t in TICKERS},
}
stress = stress_portfolio(value, weights, scenarios[scenario], TICKERS)
st.metric("Stress P&L", f"${stress['pnl']:,.0f}")
st.write(f"Stressed portfolio value: ${stress['stressed_value']:,.0f}")

st.subheader("Rolling VaR backtest")
window = st.selectbox("Lookback days", [100, 250, 500], index=1)
if len(returns) > window:
    bt = rolling_backtest(returns, value, confidence, window)
    breaches = int(bt["breach"].sum())
    st.write(f"Breaches: {breaches} / {len(bt)} ({breaches/len(bt):.2%}); expected ≈ {1-confidence:.0%}")
    chart = go.Figure()
    chart.add_trace(go.Scatter(x=bt.index,y=bt["var"],name="Forecast VaR"))
    chart.add_trace(go.Scatter(x=bt.index,y=bt["actual_loss"],name="Realized loss"))
    st.plotly_chart(chart,use_container_width=True)
    st.download_button("Download backtest CSV",bt.to_csv().encode(),"backtest.csv","text/csv")
else:
    st.info("Not enough data for this lookback window")
