import plotly.express as px
import streamlit as st

from utils import kpis
from utils.theme import POSITION_COLORS, require_data, show

df = st.session_state["filtered_df"]

st.title("📊 Overview")
st.caption("Synthetic data — headline numbers update with the sidebar filters.")
require_data(df)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Players", f"{kpis.total_players(df):,}")
c2.metric("Goals", f"{kpis.total_goals(df):,}")
c3.metric("Assists", f"{kpis.total_assists(df):,}")
c4.metric("Minutes", f"{kpis.total_minutes(df):,}")
c5.metric("Avg rating", f"{kpis.average_rating(df):.2f}")

left, right = st.columns(2)

with left:
    top = (df.groupby(["player_name", "position"], as_index=False)["goals"].sum()
             .nlargest(10, "goals").sort_values("goals"))
    fig = px.bar(top, x="goals", y="player_name", color="position", orientation="h",
                 color_discrete_map=POSITION_COLORS, title="Top 10 scorers")
    fig.update_layout(yaxis_title=None, xaxis_title="Goals")
    show(fig)

with right:
    by_pos = df.groupby("position", as_index=False)["goals"].sum()
    fig = px.pie(by_pos, names="position", values="goals", hole=0.45,
                 color="position", color_discrete_map=POSITION_COLORS,
                 title="Goals share by position")
    show(fig)

left, right = st.columns(2)

with left:
    fig = px.histogram(df, x="rating", nbins=20, title="Rating distribution")
    fig.update_layout(xaxis_title="Rating", yaxis_title="Player-seasons")
    show(fig)

with right:
    trend = df.groupby("season", as_index=False)[["goals", "assists"]].sum()
    fig = px.line(trend, x="season", y=["goals", "assists"], markers=True,
                  title="Goals & assists by season")
    fig.update_layout(yaxis_title="Total", legend_title=None, xaxis_title=None)
    show(fig)
