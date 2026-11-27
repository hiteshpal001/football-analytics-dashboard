"""Five headline KPIs, always computed from the currently filtered data."""
import pandas as pd


def total_players(df: pd.DataFrame) -> int:
    return int(df["player_id"].nunique())


def total_goals(df: pd.DataFrame) -> int:
    return int(df["goals"].sum())


def total_assists(df: pd.DataFrame) -> int:
    return int(df["assists"].sum())


def total_minutes(df: pd.DataFrame) -> int:
    return int(df["minutes_played"].sum())


def average_rating(df: pd.DataFrame) -> float:
    return float(df["rating"].mean())
