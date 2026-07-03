import pandas as pd
import streamlit as st

from src.charts import (
    factor_radar_chart,
    price_volume_chart,
    score_distribution_chart,
    sector_score_chart,
    top_scores_chart,
)
from src.data_loader import download_price_data
from src.feature_engineering import build_latest_features
from src.ranking import SUMMARY_COLS, rank_stocks
from src.report import explain_stock
from src.universe import get_sp500_table

st.set_page_config(
    page_title="AI Stock Ranking Agent",
    page_icon="📈",
    layout="wide",
)

CUSTOM_CSS = """
<style>
.kpi-card {
    background-color: #1a1a19;
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 10px;
    padding: 18px 20px;
    height: 100%;
}
.kpi-label {
    font-size: 0.78rem;
    color: #898781;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.82rem;
    color: #c3c2b7;
    margin-top: 6px;
}
.kpi-value.good { color: #0ca30c; }
.kpi-value.critical { color: #d03b3b; }
.kpi-value.warning { color: #fab219; }

.pick-card {
    background-color: #1a1a19;
    border: 1px solid rgba(255,255,255,0.10);
    border-left: 3px solid #3987e5;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.pick-rank {
    color: #898781;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.pick-ticker {
    color: #ffffff;
    font-size: 1.1rem;
    font-weight: 700;
}
.pick-score {
    color: #3987e5;
    font-weight: 700;
}
.pick-reason {
    color: #c3c2b7;
    font-size: 0.9rem;
    margin-top: 4px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", css_class: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {css_class}">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


@st.cache_data(ttl=86400)
def load_universe() -> pd.DataFrame:
    return get_sp500_table()


@st.cache_data(ttl=3600, show_spinner=False)
def load_price_data(tickers: list[str], period: str) -> dict[str, pd.DataFrame]:
    return download_price_data(tickers, period=period)


with st.sidebar:
    st.title("📈 Stock Ranking Agent")
    st.caption("Automatically scans the S&P 500 — no tickers to type.")
    st.divider()
    st.subheader("Settings")
    period = st.selectbox("Historical data period", ["1y", "2y", "5y"], index=1)
    top_n = st.slider("Number of top stocks to show", 3, 30, 10)
    run_button = st.button("Run Ranking", use_container_width=True, type="primary")
    st.divider()
    st.caption(
        "Momentum, volatility, volume trend, RSI, and moving-average factors. "
        "Research tool only — not financial advice."
    )

st.title("📈 AI Stock Ranking Agent")
st.write("Live dashboard covering the full S&P 500 universe.")

if run_button:
    universe = load_universe()
    tickers = universe["ticker"].tolist()
    sector_map = dict(zip(universe["ticker"], universe["sector"]))

    with st.spinner(f"Downloading price data for {len(tickers)} tickers..."):
        prices = load_price_data(tickers, period)

    if not prices:
        st.error("No price data was downloaded. Please try again later.")
        st.stop()

    with st.spinner("Building features..."):
        features = build_latest_features(prices)

    if features.empty:
        st.error("Not enough historical data to build features.")
        st.stop()

    features["sector"] = features["ticker"].map(sector_map).fillna("Unknown")

    with st.spinner("Ranking stocks..."):
        ranked = rank_stocks(features)

    st.session_state["ranked"] = ranked
    st.session_state["prices"] = prices
    st.session_state["tickers_scanned"] = len(tickers)

if "ranked" not in st.session_state:
    st.info("Click **Run Ranking** in the sidebar to scan the S&P 500.")
    st.stop()

ranked: pd.DataFrame = st.session_state["ranked"]
prices: dict = st.session_state["prices"]
tickers_scanned: int = st.session_state["tickers_scanned"]

top_df = ranked.head(top_n)

# --- KPI row ---
advancing = int((ranked["return_3m"] > 0).sum())
advancing_pct = advancing / len(ranked) * 100
breadth_class = "good" if advancing_pct >= 50 else "critical"

avg_score = top_df["score"].mean()
top_sector = top_df["sector"].mode().iloc[0] if not top_df.empty else "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.markdown(
    kpi_card("Ranked Universe", f"{len(ranked)}", f"of {tickers_scanned} S&P 500 tickers"),
    unsafe_allow_html=True,
)
col2.markdown(
    kpi_card(
        "Market Breadth (3M)",
        f"{advancing_pct:.0f}%",
        f"{advancing} of {len(ranked)} advancing",
        breadth_class,
    ),
    unsafe_allow_html=True,
)
col3.markdown(
    kpi_card(f"Avg Score (Top {top_n})", f"{avg_score:.1f}", "out of 100"),
    unsafe_allow_html=True,
)
col4.markdown(
    kpi_card(f"Top Sector (Top {top_n})", top_sector, "most represented"),
    unsafe_allow_html=True,
)

st.write("")

# --- Overview charts ---
chart_col1, chart_col2 = st.columns(2)
cutoff_score = top_df["score"].min() if not top_df.empty else 0
chart_col1.plotly_chart(score_distribution_chart(ranked, cutoff_score), use_container_width=True)
chart_col2.plotly_chart(sector_score_chart(ranked), use_container_width=True)

st.plotly_chart(top_scores_chart(top_df), use_container_width=True)

# --- Top ranked table ---
st.subheader("Top Ranked Stocks")
st.dataframe(
    top_df[SUMMARY_COLS + ["sector"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.1f"),
        "latest_close": st.column_config.NumberColumn("Close", format="dollar"),
        "return_1m": st.column_config.NumberColumn("1M Return", format="percent"),
        "return_3m": st.column_config.NumberColumn("3M Return", format="percent"),
        "return_6m": st.column_config.NumberColumn("6M Return", format="percent"),
        "volatility_20d": st.column_config.NumberColumn("Volatility", format="percent"),
        "volume_trend": st.column_config.NumberColumn("Volume Trend", format="percent"),
        "rsi": st.column_config.NumberColumn("RSI", format="%.1f"),
        "distance_from_ma50": st.column_config.NumberColumn("vs MA50", format="percent"),
        "distance_from_ma200": st.column_config.NumberColumn("vs MA200", format="percent"),
    },
)

# --- Explanations ---
st.subheader("Why These Picks")
for rank, (_, row) in enumerate(top_df.iterrows(), start=1):
    reason_text = explain_stock(row).split(". Main signals: ")[1]
    st.markdown(
        f"""
        <div class="pick-card">
            <div class="pick-rank">#{rank} — {row['sector']}</div>
            <div class="pick-ticker">{row['ticker']} <span class="pick-score">{row['score']:.1f}/100</span></div>
            <div class="pick-reason">{reason_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Drill-down ---
st.divider()
st.subheader("🔍 Stock Detail")

selected_ticker = st.selectbox("Select a ticker to inspect", ranked["ticker"].tolist())
selected_row = ranked[ranked["ticker"] == selected_ticker].iloc[0]

d1, d2, d3, d4 = st.columns(4)
d1.markdown(kpi_card("Score", f"{selected_row['score']:.1f}"), unsafe_allow_html=True)
d2.markdown(kpi_card("Latest Close", f"${selected_row['latest_close']:.2f}"), unsafe_allow_html=True)
rsi_val = selected_row["rsi"]
rsi_class = "warning" if rsi_val >= 70 or rsi_val <= 30 else "good"
d3.markdown(kpi_card("RSI", f"{rsi_val:.1f}", css_class=rsi_class), unsafe_allow_html=True)
d4.markdown(kpi_card("Sector", selected_row["sector"]), unsafe_allow_html=True)

detail_col1, detail_col2 = st.columns([2, 1])
detail_col1.plotly_chart(price_volume_chart(prices[selected_ticker], selected_ticker), use_container_width=True)
detail_col2.plotly_chart(factor_radar_chart(selected_row), use_container_width=True)

st.info(explain_stock(selected_row))

# --- Full table ---
with st.expander("Full Feature Table (all ranked stocks)"):
    st.dataframe(ranked, use_container_width=True, hide_index=True)
