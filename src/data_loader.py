from __future__ import annotations

import pandas as pd
import yfinance as yf

BATCH_SIZE = 50
NEEDED_COLS = {"Open", "High", "Low", "Close", "Volume"}


def download_price_data(tickers: list[str], period: str = "2y") -> dict[str, pd.DataFrame]:
    '''
    Download OHLCV price data for a list of tickers, in batches.

    Returns:
        Dictionary mapping ticker -> dataframe.
    '''
    result: dict[str, pd.DataFrame] = {}

    for i in range(0, len(tickers), BATCH_SIZE):
        batch = tickers[i:i + BATCH_SIZE]

        try:
            data = yf.download(
                batch,
                period=period,
                auto_adjust=True,
                progress=False,
                group_by="ticker",
                threads=True,
            )
        except Exception as e:
            print(f"Failed to download batch {batch}: {e}")
            continue

        if data is None or data.empty:
            continue

        for ticker in batch:
            try:
                df = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
            except KeyError:
                continue

            if df is None or df.empty:
                continue

            df = df.dropna()
            if not NEEDED_COLS.issubset(set(df.columns)):
                continue

            result[ticker] = df

    return result
