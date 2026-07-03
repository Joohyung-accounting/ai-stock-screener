from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.ranking import FACTOR_LABELS, FACTOR_SCORE_COLS

# Dark-surface palette (see dataviz skill reference palette).
SURFACE = "#1a1a19"
PAGE = "#0d0d0d"
INK_PRIMARY = "#ffffff"
INK_SECONDARY = "#c3c2b7"
INK_MUTED = "#898781"
GRID = "#2c2c2a"
AXIS = "#383835"

BLUE = "#3987e5"
AQUA = "#199e70"
YELLOW = "#c98500"

GOOD = "#0ca30c"
CRITICAL = "#d03b3b"

BASE_LAYOUT = dict(
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(color=INK_SECONDARY, family="system-ui, -apple-system, 'Segoe UI', sans-serif"),
    margin=dict(l=10, r=10, t=30, b=10),
    hoverlabel=dict(bgcolor=PAGE, font_color=INK_PRIMARY, bordercolor=AXIS),
)

AXIS_STYLE = dict(
    gridcolor=GRID,
    zerolinecolor=AXIS,
    linecolor=AXIS,
    tickfont=dict(color=INK_MUTED),
)


def score_distribution_chart(ranked: pd.DataFrame, cutoff_score: float) -> go.Figure:
    '''
    Histogram of scores across the full ranked universe, with the top-N cutoff marked.
    '''
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=ranked["score"],
            nbinsx=30,
            marker=dict(color=BLUE),
            hovertemplate="Score %{x}<br>Count %{y}<extra></extra>",
        )
    )
    fig.add_vline(
        x=cutoff_score,
        line=dict(color=INK_SECONDARY, width=1.5, dash="dash"),
        annotation_text="Top-N cutoff",
        annotation_font_color=INK_SECONDARY,
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Score Distribution (Full Universe)", font=dict(color=INK_PRIMARY, size=15)),
        xaxis=dict(title="Score", **AXIS_STYLE),
        yaxis=dict(title="Number of Stocks", **AXIS_STYLE),
        bargap=0.05,
        showlegend=False,
        height=340,
    )
    return fig


def sector_score_chart(ranked: pd.DataFrame) -> go.Figure:
    '''
    Average score by sector, single-hue bars sorted by value (one series, no rank-based coloring).
    '''
    sector_avg = (
        ranked.groupby("sector")
        .agg(avg_score=("score", "mean"), count=("ticker", "count"))
        .sort_values("avg_score", ascending=True)
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=sector_avg["avg_score"],
            y=sector_avg.index,
            orientation="h",
            marker=dict(color=BLUE),
            customdata=sector_avg["count"],
            hovertemplate="%{y}<br>Avg score %{x:.1f}<br>%{customdata} stocks<extra></extra>",
        )
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Average Score by Sector", font=dict(color=INK_PRIMARY, size=15)),
        xaxis=dict(title="Average Score", **AXIS_STYLE),
        yaxis=dict(title="", **AXIS_STYLE),
        showlegend=False,
        height=340,
    )
    return fig


def top_scores_chart(ranked_top: pd.DataFrame) -> go.Figure:
    '''
    Horizontal bar chart of the top-N tickers by score, single hue, sorted descending.
    '''
    ordered = ranked_top.sort_values("score", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=ordered["score"],
            y=ordered["ticker"],
            orientation="h",
            marker=dict(color=BLUE),
            hovertemplate="%{y}<br>Score %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text="Top Ranked Stocks", font=dict(color=INK_PRIMARY, size=15)),
        xaxis=dict(title="Score", range=[0, 100], **AXIS_STYLE),
        yaxis=dict(title="", **AXIS_STYLE),
        showlegend=False,
        height=max(340, 28 * len(ordered)),
    )
    return fig


def price_volume_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    '''
    Price line (with MA50/MA200 overlay) stacked above a volume bar chart,
    colored by day-over-day direction. Two stacked panels, not a dual-axis plot.
    '''
    close = df["Close"]
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    prev_close = close.shift(1)
    volume_color = [GOOD if c >= p else CRITICAL for c, p in zip(close, prev_close)]

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.04,
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=close, name="Close", line=dict(color=BLUE, width=2)),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=ma50, name="MA50", line=dict(color=AQUA, width=1.5)),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=ma200, name="MA200", line=dict(color=YELLOW, width=1.5)),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", marker=dict(color=volume_color)),
        row=2,
        col=1,
    )

    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(text=f"{ticker} — Price & Volume", font=dict(color=INK_PRIMARY, size=15)),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color=INK_SECONDARY)),
        height=480,
        showlegend=True,
    )
    fig.update_xaxes(**AXIS_STYLE, row=1, col=1)
    fig.update_xaxes(**AXIS_STYLE, row=2, col=1)
    fig.update_yaxes(title="Price", **AXIS_STYLE, row=1, col=1)
    fig.update_yaxes(title="Volume", **AXIS_STYLE, row=2, col=1)
    return fig


def factor_radar_chart(row: pd.Series) -> go.Figure:
    '''
    Radar chart of the 0-100 factor sub-scores for a single stock (one series, one color).
    '''
    labels = [FACTOR_LABELS[col] for col in FACTOR_SCORE_COLS]
    values = [row[col] for col in FACTOR_SCORE_COLS]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor="rgba(57, 135, 229, 0.25)",
            line=dict(color=BLUE, width=2),
            hovertemplate="%{theta}: %{r:.0f}<extra></extra>",
        )
    )
    layout = dict(BASE_LAYOUT)
    layout["margin"] = dict(l=80, r=80, t=50, b=40)

    fig.update_layout(
        **layout,
        title=dict(text="Factor Breakdown", font=dict(color=INK_PRIMARY, size=15)),
        polar=dict(
            domain=dict(x=[0.08, 0.92], y=[0.05, 0.95]),
            bgcolor=SURFACE,
            radialaxis=dict(
                range=[0, 100],
                gridcolor=GRID,
                linecolor=AXIS,
                tickfont=dict(color=INK_MUTED, size=9),
            ),
            angularaxis=dict(gridcolor=GRID, linecolor=AXIS, tickfont=dict(color=INK_SECONDARY, size=11)),
        ),
        showlegend=False,
        height=420,
    )
    return fig
