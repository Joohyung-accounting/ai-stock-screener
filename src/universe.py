from __future__ import annotations

import io

import pandas as pd
import requests

SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; stock-ranking-agent/1.0)"}

# Used only if the Wikipedia fetch fails (e.g. offline). Not guaranteed to
# match current S&P 500 membership exactly.
FALLBACK_TABLE = pd.DataFrame(
    [
        ("AAPL", "Information Technology"), ("MSFT", "Information Technology"),
        ("NVDA", "Information Technology"), ("AMZN", "Consumer Discretionary"),
        ("GOOGL", "Communication Services"), ("GOOG", "Communication Services"),
        ("META", "Communication Services"), ("BRK-B", "Financials"),
        ("AVGO", "Information Technology"), ("TSLA", "Consumer Discretionary"),
        ("LLY", "Health Care"), ("JPM", "Financials"), ("V", "Financials"),
        ("UNH", "Health Care"), ("XOM", "Energy"), ("MA", "Financials"),
        ("COST", "Consumer Staples"), ("HD", "Consumer Discretionary"),
        ("PG", "Consumer Staples"), ("JNJ", "Health Care"),
        ("NFLX", "Communication Services"), ("MRK", "Health Care"),
        ("ABBV", "Health Care"), ("CVX", "Energy"), ("CRM", "Information Technology"),
        ("BAC", "Financials"), ("KO", "Consumer Staples"),
        ("AMD", "Information Technology"), ("PEP", "Consumer Staples"),
        ("TMO", "Health Care"), ("WMT", "Consumer Staples"),
        ("ADBE", "Information Technology"), ("LIN", "Materials"),
        ("MCD", "Consumer Discretionary"), ("CSCO", "Information Technology"),
        ("ACN", "Information Technology"), ("ABT", "Health Care"),
        ("ORCL", "Information Technology"), ("DIS", "Communication Services"),
        ("WFC", "Financials"), ("TXN", "Information Technology"),
        ("DHR", "Health Care"), ("GE", "Industrials"), ("PM", "Consumer Staples"),
        ("NOW", "Information Technology"), ("IBM", "Information Technology"),
        ("INTU", "Information Technology"), ("CAT", "Industrials"),
        ("VZ", "Communication Services"), ("AMGN", "Health Care"),
    ],
    columns=["ticker", "sector"],
)


def get_sp500_table() -> pd.DataFrame:
    '''
    Fetch the current S&P 500 constituents (ticker + GICS sector) from Wikipedia.

    Falls back to a static table of large-cap tickers if the fetch fails.
    '''
    try:
        response = requests.get(SP500_WIKI_URL, headers=REQUEST_HEADERS, timeout=10)
        response.raise_for_status()
        table = pd.read_html(io.StringIO(response.text))[0]

        table = table.rename(columns={"Symbol": "ticker", "GICS Sector": "sector"})
        table["ticker"] = table["ticker"].astype(str).str.strip().str.replace(".", "-", regex=False)
        table = table[["ticker", "sector"]]

        if len(table) > 50:
            return table
    except Exception as e:
        print(f"Failed to fetch S&P 500 list from Wikipedia: {e}")

    return FALLBACK_TABLE


def get_sp500_tickers() -> list[str]:
    '''
    Fetch the current list of S&P 500 tickers from Wikipedia.
    '''
    return get_sp500_table()["ticker"].tolist()
