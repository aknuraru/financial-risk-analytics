def check_limit(var_amount: float, limit_amount: float) -> dict:
    if limit_amount <= 0:
        raise ValueError("Limit must be positive")
    return {"utilization_pct": 100 * var_amount / limit_amount, "breached": bool(var_amount > limit_amount)}
