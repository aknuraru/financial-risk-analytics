import numpy as np
import pandas as pd
import pytest
from src.risk.metrics import portfolio_returns, risk_metrics
from src.risk.stress import stress_portfolio
from src.risk.backtest import rolling_backtest
from src.risk.limits import check_limit

def test_es_at_least_var():
    rng = np.random.default_rng(123)
    r = pd.Series(rng.normal(0, 0.01, 500))
    m = risk_metrics(r, 100000, .95)
    assert m["es"] >= m["var"]

def test_portfolio_weights():
    prices = pd.DataFrame({"A":[100,110,121],"B":[100,100,100]})
    r = portfolio_returns(prices, np.array([.5,.5]))
    assert np.allclose(r.values,[.05,.05])

def test_stress():
    s = stress_portfolio(100000,[.4,.6],{"A":-.2,"B":-.1},["A","B"])
    assert s["pnl"] == pytest.approx(-14000)

def test_limit():
    assert check_limit(600,500)["breached"] is True

def test_backtest_no_lookahead():
    r = pd.Series(np.linspace(-.02,.02,80),index=pd.date_range("2025-01-01",periods=80))
    bt = rolling_backtest(r,100000,.95,40)
    expected = risk_metrics(r.iloc[:40],100000,.95)["var"]
    assert bt.iloc[0]["var"] == pytest.approx(expected)
