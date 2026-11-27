"""Cascading sidebar filters: season -> team -> position -> player."""
import pandas as pd
import streamlit as st


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("⚽ Filters")

    seasons = st.sidebar.multiselect(
        "Season", sorted(df["season"].unique()), default=sorted(df["season"].unique())
    )
    d = df[df["season"].isin(seasons)]

    teams = st.sidebar.multiselect("Team", sorted(d["team"].unique()))
    if teams:
        d = d[d["team"].isin(teams)]

    positions = st.sidebar.multiselect("Position", ["GK", "DEF", "MID", "FWD"])
    if positions:
        d = d[d["position"].isin(positions)]

    players = st.sidebar.multiselect("Player", sorted(d["player_name"].unique()))
    if players:
        d = d[d["player_name"].isin(players)]

    st.sidebar.caption(f"{len(d)} rows • {d['player_id'].nunique()} players")

    if not d.empty:
        st.sidebar.download_button(
            "⬇️ Download filtered CSV",
            d.to_csv(index=False).encode("utf-8"),
            file_name="football_filtered.csv",
            mime="text/csv",
        )
    st.sidebar.info("All data is synthetic and randomly generated.")
    return d
