import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.theme import POSITION_COLORS, PALETTE, require_data, show

df = st.session_state["filtered_df"]

st.title("👤 Player Analysis")
require_data(df)

# One row per player (sum of counts, mean of rates) across the selected seasons
agg = df.groupby(["player_id", "player_name", "team", "position"], as_index=False).agg(
    goals=("goals", "sum"), assists=("assists", "sum"),
    shots_on_target=("shots_on_target", "sum"), key_passes=("key_passes", "sum"),
    tackles=("tackles", "sum"), pass_accuracy=("pass_accuracy", "mean"),
    rating=("rating", "mean"), minutes=("minutes_played", "sum"),
)

st.subheader("Compare players")
names = sorted(agg["player_name"].unique())
chosen = st.multiselect("Pick 2–6 players", names, default=names[:3], max_selections=6)

if len(chosen) < 2:
    st.info("Select at least two players to draw the radar chart.")
else:
    metrics = ["goals", "assists", "shots_on_target", "key_passes", "tackles", "pass_accuracy"]
    norm = agg[metrics] / agg[metrics].max().replace(0, 1)  # 0–1 scale per metric
    fig = go.Figure()
    for i, name in enumerate(chosen):
        idx = agg.index[agg["player_name"] == name][0]
        vals = norm.loc[idx, metrics].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=[m.replace("_", " ").title() for m in metrics] + [metrics[0].title()],
            fill="toself", name=name, line_color=PALETTE[i % len(PALETTE)], opacity=0.7))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1], showticklabels=False)),
                      title="Normalised performance profile")
    show(fig)

c1, c2 = st.columns(2)
with c1:
    fig = px.scatter(agg, x="assists", y="goals", color="position", hover_name="player_name",
                     color_discrete_map=POSITION_COLORS, title="Goals vs assists")
    show(fig)

with c2:
    fig = px.scatter(agg, x="shots_on_target", y="goals", color="position",
                     hover_name="player_name", color_discrete_map=POSITION_COLORS,
                     title="Shots on target vs goals (with trend line)")
    if len(agg) >= 2 and agg["shots_on_target"].nunique() > 1:
        slope, intercept = np.polyfit(agg["shots_on_target"], agg["goals"], 1)
        xs = np.array([agg["shots_on_target"].min(), agg["shots_on_target"].max()])
        fig.add_trace(go.Scatter(x=xs, y=slope * xs + intercept, mode="lines",
                                 name="Trend", line=dict(color="white", dash="dash")))
    show(fig)

st.subheader("Player statistics")
query = st.text_input("Search player or team", placeholder="e.g. Silva, Northbridge")
table = df
if query:
    q = query.strip()
    mask = (df["player_name"].str.contains(q, case=False, na=False)
            | df["team"].str.contains(q, case=False, na=False))
    table = df[mask]

if table.empty:
    st.warning("No players match that search.")
else:
    st.dataframe(table.sort_values("rating", ascending=False), width="stretch", hide_index=True)
    st.download_button("⬇️ Download this table", table.to_csv(index=False).encode("utf-8"),
                       file_name="player_stats.csv", mime="text/csv")
