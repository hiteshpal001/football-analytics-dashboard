import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.theme import POSITION_COLORS, PALETTE, require_data, show

df = st.session_state["filtered_df"]

st.title("🏆 Team Analysis")
require_data(df)

teams = df.groupby("team", as_index=False).agg(
    goals=("goals", "sum"), assists=("assists", "sum"),
    players=("player_id", "nunique"), rating=("rating", "mean"),
    pass_accuracy=("pass_accuracy", "mean"), tackles=("tackles", "sum"),
    shots_on_target=("shots_on_target", "sum"),
).sort_values("goals", ascending=False)

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(teams, x="team", y=["goals", "assists"], barmode="group",
                 title="Goals & assists by team")
    fig.update_layout(xaxis_title=None, yaxis_title="Total", legend_title=None)
    show(fig)

with c2:
    squad = df.groupby(["team", "position"])["player_id"].nunique().reset_index(name="players")
    fig = px.bar(squad, x="team", y="players", color="position",
                 color_discrete_map=POSITION_COLORS, title="Squad composition")
    fig.update_layout(xaxis_title=None, yaxis_title="Players")
    show(fig)

fig = px.scatter(teams, x="players", y="rating", size="goals", text="team",
                 title="Squad size vs average rating (bubble = goals)")
fig.update_traces(textposition="top center")
fig.update_layout(xaxis_title="Players", yaxis_title="Average rating")
show(fig)

st.subheader("Team radar comparison")
options = teams["team"].tolist()
picked = st.multiselect("Pick 2–5 teams", options, default=options[:3], max_selections=5)
if len(picked) < 2:
    st.info("Select at least two teams.")
else:
    dims = ["goals", "assists", "shots_on_target", "tackles", "pass_accuracy", "rating"]
    norm = teams.set_index("team")[dims]
    norm = (norm - norm.min()) / (norm.max() - norm.min()).replace(0, 1)
    fig = go.Figure()
    for i, t in enumerate(picked):
        vals = norm.loc[t].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + vals[:1], theta=[d.replace("_", " ").title() for d in dims] + [dims[0].title()],
            fill="toself", name=t, line_color=PALETTE[i % len(PALETTE)], opacity=0.7))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1], showticklabels=False)))
    show(fig)

st.subheader("Team summary")
st.dataframe(teams.round(2), width="stretch", hide_index=True)
