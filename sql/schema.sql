CREATE TABLE IF NOT EXISTS market_prices (
    ticker TEXT NOT NULL,
    price_date DATE NOT NULL,
    close_price DOUBLE PRECISION NOT NULL CHECK (close_price > 0),
    PRIMARY KEY (ticker, price_date)
);
CREATE TABLE IF NOT EXISTS risk_metrics (
    calculation_date DATE NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence > 0 AND confidence < 1),
    portfolio_value DOUBLE PRECISION NOT NULL CHECK (portfolio_value > 0),
    var_amount DOUBLE PRECISION NOT NULL,
    es_amount DOUBLE PRECISION NOT NULL,
    model_name TEXT NOT NULL,
    PRIMARY KEY (calculation_date, confidence, model_name)
);
CREATE TABLE IF NOT EXISTS risk_limits (
    limit_name TEXT PRIMARY KEY,
    limit_amount DOUBLE PRECISION NOT NULL CHECK (limit_amount > 0)
);
CREATE TABLE IF NOT EXISTS limit_breaches (
    calculation_date DATE NOT NULL,
    limit_name TEXT NOT NULL REFERENCES risk_limits(limit_name),
    observed_value DOUBLE PRECISION NOT NULL,
    limit_amount DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (calculation_date, limit_name)
);
