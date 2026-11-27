"""Shared look & feel: CSS, Plotly styling and a safe chart/empty-state helper."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

GREEN = "#00ff85"
PALETTE = ["#00ff85", "#2dd4bf", "#facc15", "#60a5fa", "#f472b6", "#fb923c"]
POSITION_COLORS = {"GK": "#facc15", "DEF": "#60a5fa", "MID": "#2dd4bf", "FWD": "#00ff85"}

_template = pio.templates["plotly_dark"]
_template.layout.update(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=PALETTE,
    margin=dict(l=10, r=10, t=50, b=10),
)
pio.templates.default = "plotly_dark"

CSS = """
<style>
div[data-testid="stMetric"] {
    background: #161b22; border: 1px solid #00ff8533;
    border-left: 4px solid #00ff85; border-radius: 10px; padding: 14px 16px;
}
div[data-testid="stMetricValue"] { color: #00ff85; }
h1, h2, h3 { letter-spacing: .2px; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def show(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch")


def require_data(df) -> None:
    """Stop the page with a friendly message when filters return nothing."""
    if df is None or df.empty:
        st.warning("No data matches the current filters. Widen the selection in the sidebar.")
        st.stop()
