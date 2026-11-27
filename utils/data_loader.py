"""Load and validate the dataset."""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "football_players.csv"

REQUIRED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season", "age",
    "matches_played", "minutes_played", "goals", "assists", "shots",
    "shots_on_target", "key_passes", "pass_accuracy", "tackles",
    "interceptions", "saves", "clean_sheets", "yellow_cards",
    "red_cards", "rating",
]


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Read the CSV (generating it first if it is missing) and validate it."""
    if not DATA_PATH.exists():
        from data_generator import generate_dataset
        generate_dataset().to_csv(DATA_PATH, index=False)

    df = pd.read_csv(DATA_PATH)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"football_players.csv is missing columns: {', '.join(missing)}")
        st.stop()

    return df.dropna(subset=REQUIRED_COLUMNS).reset_index(drop=True)
