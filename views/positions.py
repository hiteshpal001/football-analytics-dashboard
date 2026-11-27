import plotly.express as px
import streamlit as st

from utils.theme import POSITION_COLORS, require_data, show

df = st.session_state["filtered_df"]

st.title("🎽 Position Analysis")
require_data(df)

order = [p for p in ["GK", "DEF", "MID", "FWD"] if p in df["position"].unique()]

c1, c2 = st.columns(2)
with c1:
    fig = px.box(df, x="position", y="rating", color="position", points="all",
                 category_orders={"position": order}, color_discrete_map=POSITION_COLORS,
                 title="Rating distribution by position")
    fig.update_layout(showlegend=False, xaxis_title=None)
    show(fig)

with c2:
    avg = (df.groupby("position")[["goals", "assists", "tackles", "key_passes"]]
             .mean().reindex(order).reset_index())
    fig = px.bar(avg, x="position", y=["goals", "assists", "tackles", "key_passes"],
                 barmode="group", title="Average stats per player-season")
    fig.update_layout(xaxis_title=None, yaxis_title="Average", legend_title=None)
    show(fig)

fig = px.scatter(df, x="pass_accuracy", y="rating", color="position", hover_name="player_name",
                 color_discrete_map=POSITION_COLORS, title="Pass accuracy vs rating")
show(fig)

st.subheader("Deep dive")
tabs = st.tabs(order)
for tab, pos in zip(tabs, order):
    with tab:
        sub = df[df["position"] == pos]
        stat = "saves" if pos == "GK" else ("tackles" if pos == "DEF" else
               ("assists" if pos == "MID" else "goals"))
        top = (sub.groupby("player_name", as_index=False)
                  .agg(**{stat: (stat, "sum"), "avg_rating": ("rating", "mean")})
                  .nlargest(5, stat))
        st.markdown(f"**Top 5 by {stat}**")
        st.dataframe(top.round(2), width="stretch", hide_index=True)
