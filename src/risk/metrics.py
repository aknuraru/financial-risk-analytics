import numpy as np
import pandas as pd


def portfolio_returns(prices: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    if prices.empty or prices.isna().any().any() or (prices <= 0).any().any():
        raise ValueError("Prices must be positive, complete and nonempty")
    w = np.asarray(weights, dtype=float)
    if len(w) != prices.shape[1] or not np.isfinite(w).all() or not np.isclose(w.sum(), 1):
        raise ValueError("Weights must match assets and sum to 1")
    if (w < 0).any():
        raise ValueError("This example requires long-only weights")
    result = prices.pct_change().iloc[1:] @ w
    if result.empty:
        raise ValueError("At least two price observations are required")
    return result


def risk_metrics(returns: pd.Series, value: float, confidence: float = 0.95) -> dict:
    if not 0 < confidence < 1 or not np.isfinite(value) or value <= 0:
        raise ValueError("Invalid confidence or portfolio value")
    r = np.asarray(returns, dtype=float)
    if r.size < 20 or not np.isfinite(r).all():
        raise ValueError("At least 20 finite return observations required")
    losses = -r * value
    # Discrete historical quantile: no interpolated, unobserved loss threshold.
    var = float(np.quantile(losses, confidence, method="higher"))
    # Equal-probability observations; worst tail with fractional boundary weight.
    tail_count = (1 - confidence) * len(losses)
    sorted_losses = np.sort(losses)[::-1]
    whole = int(np.floor(tail_count))
    fraction = tail_count - whole
    tail_sum = sorted_losses[:whole].sum()
    if fraction > 1e-12:
        tail_sum += fraction * sorted_losses[whole]
    es = float(tail_sum / tail_count)
    volatility = float(np.std(r, ddof=1) * np.sqrt(252))
    return {"var": var, "es": es, "volatility_annual": volatility}
