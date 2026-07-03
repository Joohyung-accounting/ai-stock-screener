# AI Stock Ranking Agent

A research dashboard that automatically scans the **entire S&P 500** and ranks
stocks using price momentum, volatility, volume trend, RSI, and moving-average
signals — no tickers to type.

This is **not an auto-trading bot**. It's a research/screening tool that helps
you compare stocks systematically. Nothing here is financial advice.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-dashboard-red)

## Features

- **Fully automatic universe** — fetches the current S&P 500 constituent list
  (ticker + GICS sector) live from Wikipedia, with a static fallback if that's
  unreachable. Nothing to configure.
- **Batched price downloads** via `yfinance`, so scanning ~500 tickers stays
  fast (grouped into batches of 50 with threaded requests).
- **Feature engineering** per ticker: 1/3/6-month returns, 20-day annualized
  volatility, 20-vs-60-day volume trend, RSI(14), and distance from the 50-day
  and 200-day moving averages.
- **Rule-based scoring** — each feature is converted to a 0–100 percentile
  score and combined into a single weighted score (rewards momentum and
  volume strength, penalizes volatility and overbought/oversold RSI).
- **Dashboard** (dark theme, sidebar controls):
  - KPI tiles — ranked universe size, market breadth, average score, top
    sector
  - Score distribution histogram with the top-N cutoff marked
  - Average score by sector
  - Top-N ranked stocks (table + bar chart + plain-English "why this pick")
  - Per-stock drill-down: price chart with MA50/MA200 overlay, volume bars
    colored by daily direction, and a radar chart of the underlying factor
    scores

## Project layout

```
app.py                      Streamlit entry point — wires the pipeline to the UI
src/
  universe.py                Fetches S&P 500 tickers + sectors (Wikipedia, with fallback)
  data_loader.py              Batched OHLCV price downloads via yfinance
  feature_engineering.py      Turns raw price history into per-ticker features
  ranking.py                   Percentile scoring + weighted composite score
  charts.py                    Plotly figure builders for the dashboard
  report.py                    Plain-English explanation of a stock's score
docs/experiment-log.md       Running notes on model iterations
.streamlit/config.toml       Dashboard theme (dark)
```

## Installation

```bash
cd stock-ranking-agent
python -m venv .venv
```

### Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Mac/Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Open the URL Streamlit prints (default `http://localhost:8501`), then click
**Run Ranking** in the sidebar. The first run downloads price history for the
full S&P 500 and can take a few minutes; results are cached for an hour so
re-running with the same settings is instant.

## How the score is built

Each feature is converted to a 0–100 percentile rank across the scanned
universe, then combined as a weighted sum:

| Factor | Weight | Direction |
|---|---|---|
| 3-month return | 25% | higher is better |
| 6-month return | 20% | higher is better |
| 1-month return | 15% | higher is better |
| 20-day volatility | 10% | lower is better |
| Distance from 50-day MA | 10% | higher is better |
| Volume trend (20d vs 60d) | 10% | higher is better |
| Distance from 200-day MA | 5% | higher is better |
| RSI health (distance from 60) | 5% | closer to 60 is better |

A ticker needs at least 220 trading days of clean history to be scored (needed
for the 200-day moving average), so very recent IPOs are excluded.

## Important Warning

This project is for education and research only. It is not financial advice
and should not be used as an automatic trading system.
