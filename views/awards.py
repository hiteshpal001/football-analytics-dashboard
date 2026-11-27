"""Awards page: Player of the Season cards + Best XI drawn on a pitch."""
import plotly.graph_objects as go
import streamlit as st

from utils.theme import POSITION_COLORS, require_data, show

df = st.session_state["filtered_df"]

st.title("⭐ Awards")
st.caption("Player of the Season and Best XI (4-3-3). Uses the sidebar filters. "
           "Only players with at least 900 minutes in a season are eligible.")
require_data(df)

MIN_MINUTES = 900
FORMATION = {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3}
# x positions (0-100) per line, y = height on the pitch
LINE_Y = {"GK": 8, "DEF": 30, "MID": 56, "FWD": 82}
LINE_X = {
    1: [50],
    3: [22, 50, 78],
    4: [14, 38, 62, 86],
}


def eligible(season_df):
    pool = season_df[season_df["minutes_played"] >= MIN_MINUTES]
    return pool if not pool.empty else season_df  # fall back so the page never breaks


def rank(season_df):
    """Highest rating first; goals + assists breaks ties."""
    d = season_df.copy()
    d["contrib"] = d["goals"] + d["assists"]
    return d.sort_values(["rating", "contrib"], ascending=False)


# ---------- Player of the Season cards ----------
st.subheader("🏅 Player of the Season")
seasons = sorted(df["season"].unique())
cols = st.columns(len(seasons))
for col, season in zip(cols, seasons):
    best = rank(eligible(df[df["season"] == season])).iloc[0]
    with col:
        st.markdown(f"**{season}**")
        st.metric(best["player_name"], f"{best['rating']:.1f} rating")
        st.caption(f"{best['team']} • {best['position']} • "
                   f"{int(best['goals'])} goals • {int(best['assists'])} assists")

# ---------- Best XI ----------
st.subheader("🧤 Best XI (4-3-3)")
season = st.selectbox("Season", seasons, index=len(seasons) - 1)
pool = rank(eligible(df[df["season"] == season]))

xi, missing = [], []
for pos, n in FORMATION.items():
    picks = pool[pool["position"] == pos].head(n)
    if len(picks) < n:
        missing.append(f"{pos} ({len(picks)}/{n})")
    xi.append((pos, picks))

if missing:
    st.info("Not enough players for a full XI with the current filters: " + ", ".join(missing))

fig = go.Figure()
# pitch markings
fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, fillcolor="#14532d",
              line=dict(color="white", width=2), layer="below")
fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color="white", width=1))
fig.add_shape(type="circle", x0=40, y0=40, x1=60, y1=60, line=dict(color="white", width=1))
fig.add_shape(type="rect", x0=25, y0=0, x1=75, y1=16, line=dict(color="white", width=1))
fig.add_shape(type="rect", x0=25, y0=84, x1=75, y1=100, line=dict(color="white", width=1))

for pos, picks in xi:
    if picks.empty:
        continue
    xs = LINE_X[FORMATION[pos]][: len(picks)]
    fig.add_trace(go.Scatter(
        x=xs, y=[LINE_Y[pos]] * len(picks), mode="markers+text", name=pos,
        marker=dict(size=34, color=POSITION_COLORS[pos], line=dict(color="white", width=2)),
        text=[f"{r:.1f}" for r in picks["rating"]], textfont=dict(color="black", size=12),
        customdata=picks[["player_name", "team", "goals", "assists"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>"
                      "Goals %{customdata[2]} • Assists %{customdata[3]}<extra></extra>",
    ))
    # names under the markers
    for x, name in zip(xs, picks["player_name"]):
        fig.add_annotation(x=x, y=LINE_Y[pos] - 7, text=name, showarrow=False,
                           font=dict(color="white", size=11))

fig.update_xaxes(visible=False, range=[-2, 102], fixedrange=True)
fig.update_yaxes(visible=False, range=[-2, 102], scaleanchor="x", fixedrange=True)
fig.update_layout(height=620, showlegend=True, legend_title=None,
                  title=f"Best XI — {season}")
show(fig)

xi_table = [r for _, picks in xi for r in picks.to_dict("records")]
if xi_table:
    st.dataframe(
        [{"Pos": r["position"], "Player": r["player_name"], "Team": r["team"],
          "Rating": r["rating"], "Goals": r["goals"], "Assists": r["assists"]}
         for r in xi_table],
        width="stretch", hide_index=True,
    )
