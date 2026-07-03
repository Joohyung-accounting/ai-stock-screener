from __future__ import annotations

import pandas as pd


def explain_stock(row: pd.Series) -> str:
    '''
    Create a simple natural-language explanation for one stock.
    '''
    ticker = row["ticker"]
    score = row["score"]

    reasons = []

    if row["return_3m"] > 0:
        reasons.append("positive 3-month momentum")
    else:
        reasons.append("weak 3-month momentum")

    if row["return_6m"] > 0:
        reasons.append("positive 6-month trend")

    if row["volume_trend"] > 0:
        reasons.append("recent volume above longer-term average")

    if row["distance_from_ma50"] > 0:
        reasons.append("price is above the 50-day moving average")

    if row["distance_from_ma200"] > 0:
        reasons.append("price is above the 200-day moving average")

    if row["volatility_20d"] > 0.6:
        reasons.append("high volatility risk")

    if row["rsi"] > 75:
        reasons.append("RSI looks overbought")
    elif row["rsi"] < 35:
        reasons.append("RSI looks weak/oversold")

    reason_text = "; ".join(reasons)

    return f"**{ticker}** — Score: **{score:.2f}/100**. Main signals: {reason_text}."


def explain_top_picks(ranked_df: pd.DataFrame) -> list[str]:
    '''
    Explain top ranked stocks.
    '''
    explanations = []

    for _, row in ranked_df.iterrows():
        explanations.append(explain_stock(row))

    return explanations
