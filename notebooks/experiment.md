# Experiment Notes

Use this file to track experiments.

## Version 1

Model type:
- Rule-based ranking

Features:
- 1-month return
- 3-month return
- 6-month return
- 20-day volatility
- volume trend
- RSI
- distance from 50-day moving average
- distance from 200-day moving average

Next improvements:
- ~~Add sector diversification~~ (done in v2)
- ~~Add Streamlit charts for historical performance~~ (done in v2)
- Add backtesting
- Add XGBoost model
- Add earnings/news data

## Version 2

Changes:
- Universe is now auto-selected (full S&P 500 via Wikipedia scrape + sector
  tags) instead of user-typed tickers
- Batched `yfinance` downloads (50 tickers/request) to make scanning ~500
  tickers practical
- Dashboard rebuilt: KPI tiles, score distribution, sector breakdown,
  per-stock drill-down (price/volume chart + factor radar chart)

Next improvements:
- Add backtesting
- Add XGBoost model
- Add earnings/news data
- Persist historical scores to compare rankings over time
