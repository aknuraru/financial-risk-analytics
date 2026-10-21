import numpy as np

def stress_portfolio(value: float, weights, shocks: dict, tickers: list[str]) -> dict:
    w = np.asarray(weights, dtype=float)
    if len(w) != len(tickers) or not np.isclose(w.sum(), 1):
        raise ValueError("Invalid weights")
    if set(shocks) != set(tickers):
        raise ValueError("Provide one shock per ticker")
    impact = sum(w[i] * shocks[ticker] for i, ticker in enumerate(tickers))
    return {"pnl": float(value * impact), "stressed_value": float(value * (1 + impact))}
