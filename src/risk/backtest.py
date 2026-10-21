import pandas as pd
from src.risk.metrics import risk_metrics

def rolling_backtest(returns: pd.Series, value: float, confidence: float = 0.95, window: int = 250) -> pd.DataFrame:
    if len(returns) <= window or window < 20:
        raise ValueError("Need more returns than rolling window")
    rows = []
    for i in range(window, len(returns)):
        forecast = risk_metrics(returns.iloc[i-window:i], value, confidence)["var"]
        actual_loss = float(-returns.iloc[i] * value)
        rows.append({"date": returns.index[i], "var": forecast, "actual_loss": actual_loss, "breach": bool(actual_loss > forecast)})
    return pd.DataFrame(rows).set_index("date")
