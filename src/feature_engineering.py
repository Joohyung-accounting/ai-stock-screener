from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    '''
    Calculate Relative Strength Index.
    '''
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    return rsi


def build_features_for_ticker(ticker: str, df: pd.DataFrame) -> dict | None:
    '''
    Build latest feature values for one ticker.
    '''
    if len(df) < 220:
        return None

    close = df["Close"]
    volume = df["Volume"]

    latest_close = close.iloc[-1]

    # Returns
    return_1m = close.pct_change(21).iloc[-1]
    return_3m = close.pct_change(63).iloc[-1]
    return_6m = close.pct_change(126).iloc[-1]

    # Volatility: annualized 20-day volatility
    daily_returns = close.pct_change()
    volatility_20d = daily_returns.rolling(20).std().iloc[-1] * np.sqrt(252)

    # Volume trend
    avg_volume_20d = volume.rolling(20).mean().iloc[-1]
    avg_volume_60d = volume.rolling(60).mean().iloc[-1]
    volume_trend = (avg_volume_20d / avg_volume_60d) - 1

    # RSI
    rsi = calculate_rsi(close).iloc[-1]

    # Moving averages
    ma_50 = close.rolling(50).mean().iloc[-1]
    ma_200 = close.rolling(200).mean().iloc[-1]

    distance_from_ma50 = (latest_close / ma_50) - 1
    distance_from_ma200 = (latest_close / ma_200) - 1

    features = {
        "ticker": ticker,
        "latest_close": latest_close,
        "return_1m": return_1m,
        "return_3m": return_3m,
        "return_6m": return_6m,
        "volatility_20d": volatility_20d,
        "volume_trend": volume_trend,
        "rsi": rsi,
        "distance_from_ma50": distance_from_ma50,
        "distance_from_ma200": distance_from_ma200,
    }

    if any(pd.isna(value) for value in features.values() if value != ticker):
        return None

    return features


def build_latest_features(price_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    '''
    Build latest features for all tickers.
    '''
    rows = []

    for ticker, df in price_data.items():
        features = build_features_for_ticker(ticker, df)
        if features is not None:
            rows.append(features)

    return pd.DataFrame(rows)
