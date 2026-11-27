"""Generate the synthetic football dataset.

Run:  python data_generator.py
All names, clubs and statistics are random and fictional.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
OUT_PATH = Path(__file__).resolve().parent / "football_players.csv"

TEAMS = [
    "Northbridge FC", "Riverside United", "Harbor City", "Ironvale Rovers",
    "Sunhill Athletic", "Crestwood Town", "Redmont FC", "Lakeshore Wanderers",
    "Stonegate City", "Valley Albion",
]
SEASONS = ["2022/23", "2023/24", "2024/25"]
POSITION_COUNTS = {"GK": 10, "DEF": 40, "MID": 40, "FWD": 30}  # 120 players
NATIONALITIES = [
    "India", "Brazil", "Spain", "England", "France", "Germany",
    "Argentina", "Portugal", "Nigeria", "Japan", "Netherlands", "Italy",
]
FIRST = ["Aarav", "Luca", "Mateo", "Noah", "Kai", "Rohan", "Diego", "Omar",
         "Leon", "Ethan", "Ravi", "Hugo", "Samuel", "Ivan", "Arjun", "Felix",
         "Tariq", "Jonas", "Rafael", "Elias"]
LAST = ["Sharma", "Silva", "Garcia", "Muller", "Rossi", "Okafor", "Tanaka",
        "Dubois", "Santos", "Novak", "Patel", "Costa", "Fischer", "Reyes",
        "Andersen", "Moreau", "Khan", "Ferrari", "Mendes", "Kovac"]

# Average yearly output per position (Poisson means) for a full-fitness season
GOALS = {"GK": 0.05, "DEF": 1.5, "MID": 4.5, "FWD": 11}
ASSISTS = {"GK": 0.2, "DEF": 1.8, "MID": 5, "FWD": 4.5}
SHOTS_EXTRA = {"GK": 0, "DEF": 12, "MID": 28, "FWD": 45}
KEY_PASSES = {"GK": 3, "DEF": 12, "MID": 38, "FWD": 25}
TACKLES = {"GK": 1, "DEF": 55, "MID": 38, "FWD": 14}
INTERCEPT = {"GK": 1, "DEF": 40, "MID": 25, "FWD": 8}
PASS_ACC = {"GK": 72, "DEF": 84, "MID": 86, "FWD": 78}


def _minmax(s: pd.Series) -> pd.Series:
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng else s * 0


def generate_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # ---- fixed player profiles (stable across seasons) ----
    profiles = []
    pid = 1
    for pos, count in POSITION_COUNTS.items():
        for _ in range(count):
            profiles.append({
                "player_id": pid,
                "player_name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                "position": pos,
                "nationality": rng.choice(NATIONALITIES),
                "team": rng.choice(TEAMS),
                "age0": int(rng.integers(18, 33)),
                "skill": float(np.clip(rng.normal(1.0, 0.25), 0.5, 1.6)),
            })
            pid += 1

    # make names unique by adding a suffix if a duplicate appears
    seen = {}
    for p in profiles:
        n = p["player_name"]
        seen[n] = seen.get(n, 0) + 1
        if seen[n] > 1:
            p["player_name"] = f"{n} {seen[n]}"

    rows = []
    for p in profiles:
        team = p["team"]
        for i, season in enumerate(SEASONS):
            if i > 0 and rng.random() < 0.12:  # occasional transfer
                team = rng.choice([t for t in TEAMS if t != team])
            pos, skill = p["position"], p["skill"]
            matches = int(rng.integers(8, 39))
            load = matches / 38
            minutes = int(matches * rng.uniform(55, 90))

            goals = int(rng.poisson(GOALS[pos] * skill * load))
            assists = int(rng.poisson(ASSISTS[pos] * skill * load))
            shots = goals + int(rng.poisson(SHOTS_EXTRA[pos] * load))
            sot = goals + int(rng.binomial(shots - goals, 0.4)) if shots > goals else goals
            key_passes = int(rng.poisson(KEY_PASSES[pos] * skill * load))
            tackles = int(rng.poisson(TACKLES[pos] * load))
            interceptions = int(rng.poisson(INTERCEPT[pos] * load))
            saves = int(rng.poisson(70 * load)) if pos == "GK" else 0
            clean_sheets = (int(rng.binomial(matches, 0.3 if pos in ("GK", "DEF") else 0.0)))
            pass_acc = float(np.clip(rng.normal(PASS_ACC[pos], 4), 60, 95))

            rows.append({
                "player_id": p["player_id"],
                "player_name": p["player_name"],
                "team": team,
                "position": pos,
                "season": season,
                "nationality": p["nationality"],
                "age": p["age0"] + i,
                "matches_played": matches,
                "minutes_played": minutes,
                "goals": goals,
                "assists": assists,
                "shots": shots,
                "shots_on_target": sot,
                "key_passes": key_passes,
                "pass_accuracy": round(pass_acc, 1),
                "tackles": tackles,
                "interceptions": interceptions,
                "saves": saves,
                "clean_sheets": clean_sheets,
                "yellow_cards": int(min(rng.poisson(2.5 * load), 10)),
                "red_cards": int(min(rng.binomial(1, 0.04), 3)),
            })

    df = pd.DataFrame(rows)

    # ---- rating: weighted blend of min-max normalised components ----
    defensive = df["tackles"] + df["interceptions"] + df["saves"] // 3
    score = (
        0.30 * _minmax(df["goals"])
        + 0.20 * _minmax(df["assists"])
        + 0.20 * _minmax(df["pass_accuracy"])
        + 0.15 * _minmax(defensive)
        + 0.15 * _minmax(df["minutes_played"])
    )
    df["rating"] = (5.0 + _minmax(score) * 4.5).round(1)  # 5.0 - 9.5
    return df


if __name__ == "__main__":
    data = generate_dataset()
    data.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(data)} rows ({data['player_id'].nunique()} players) -> {OUT_PATH}")
