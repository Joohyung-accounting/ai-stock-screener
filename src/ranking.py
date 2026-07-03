from __future__ import annotations

import pandas as pd


def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    '''
    Convert raw values into 0-100 percentile scores.
    '''
    scores = series.rank(pct=True) * 100

    if not higher_is_better:
        scores = 100 - scores

    return scores


def rank_stocks(features: pd.DataFrame) -> pd.DataFrame:
    '''
    Rule-based ranking model.

    Score idea:
    - Reward momentum
    - Reward positive volume trend
    - Reward price strength above moving averages
    - Penalize high volatility
    - Penalize extreme RSI when too overbought
    '''
    df = features.copy()

    if df.empty:
        return df

    df["score_return_1m"] = percentile_score(df["return_1m"], True)
    df["score_return_3m"] = percentile_score(df["return_3m"], True)
    df["score_return_6m"] = percentile_score(df["return_6m"], True)
    df["score_volume_trend"] = percentile_score(df["volume_trend"], True)
    df["score_low_volatility"] = percentile_score(df["volatility_20d"], False)
    df["score_ma50"] = percentile_score(df["distance_from_ma50"], True)
    df["score_ma200"] = percentile_score(df["distance_from_ma200"], True)

    # RSI scoring:
    # around 50-70 is generally healthier than extremely overbought or extremely weak.
    df["rsi_health"] = 100 - (df["rsi"] - 60).abs()
    df["score_rsi"] = percentile_score(df["rsi_health"], True)

    df["score"] = (
        0.15 * df["score_return_1m"]
        + 0.25 * df["score_return_3m"]
        + 0.20 * df["score_return_6m"]
        + 0.10 * df["score_volume_trend"]
        + 0.10 * df["score_low_volatility"]
        + 0.10 * df["score_ma50"]
        + 0.05 * df["score_ma200"]
        + 0.05 * df["score_rsi"]
    )

    df = df.drop(columns=["rsi_health"]).sort_values("score", ascending=False).reset_index(drop=True)

    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].round(4)

    return df


SUMMARY_COLS = [
    "ticker",
    "score",
    "latest_close",
    "return_1m",
    "return_3m",
    "return_6m",
    "volatility_20d",
    "volume_trend",
    "rsi",
    "distance_from_ma50",
    "distance_from_ma200",
]

FACTOR_SCORE_COLS = [
    "score_return_1m",
    "score_return_3m",
    "score_return_6m",
    "score_volume_trend",
    "score_low_volatility",
    "score_ma50",
    "score_ma200",
    "score_rsi",
]

FACTOR_LABELS = {
    "score_return_1m": "1M Return",
    "score_return_3m": "3M Return",
    "score_return_6m": "6M Return",
    "score_volume_trend": "Volume Trend",
    "score_low_volatility": "Low Volatility",
    "score_ma50": "Above MA50",
    "score_ma200": "Above MA200",
    "score_rsi": "RSI Health",
}
