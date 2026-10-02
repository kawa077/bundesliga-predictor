"""Erzeugt data.csv aus den Rohdaten von football-data.co.uk.

Dieses Skript muss nur einmal ausgeführt werden:
    python prepare_data.py

Die Rohdatei enthält über 100 Spalten (Wettquoten, Schüsse, Karten ...).
Für das Modell brauchen wir nur Heimteam, Auswärtsteam und die Tore.
"""

import pandas as pd

SOURCE_URL = "https://www.football-data.co.uk/mmz4281/2526/D1.csv"
SEASON = "2025-26"
OUTPUT_FILE = "data.csv"

# Spaltennamen in der Rohdatei -> verständliche Namen in data.csv
COLUMN_NAMES = {
    "HomeTeam": "HomeTeam",
    "AwayTeam": "AwayTeam",
    "FTHG": "HomeGoals",  # Full Time Home Goals
    "FTAG": "AwayGoals",  # Full Time Away Goals
}

# Englische Kurznamen der Rohdaten -> offizielle deutsche Vereinsnamen
TEAM_NAMES = {
    "Augsburg": "FC Augsburg",
    "Bayern Munich": "Bayern München",
    "Dortmund": "Borussia Dortmund",
    "Ein Frankfurt": "Eintracht Frankfurt",
    "FC Koln": "1. FC Köln",
    "Freiburg": "SC Freiburg",
    "Hamburg": "Hamburger SV",
    "Heidenheim": "1. FC Heidenheim",
    "Hoffenheim": "TSG Hoffenheim",
    "Leverkusen": "Bayer Leverkusen",
    "M'gladbach": "Borussia Mönchengladbach",
    "Mainz": "1. FSV Mainz 05",
    "RB Leipzig": "RB Leipzig",
    "St Pauli": "FC St. Pauli",
    "Stuttgart": "VfB Stuttgart",
    "Union Berlin": "1. FC Union Berlin",
    "Werder Bremen": "Werder Bremen",
    "Wolfsburg": "VfL Wolfsburg",
}


def main() -> None:
    """Lädt die Rohdaten, behält nur die benötigten Spalten und speichert sie."""
    # "utf-8-sig" entfernt ein unsichtbares Steuerzeichen (BOM) am Dateianfang
    raw_matches = pd.read_csv(SOURCE_URL, encoding="utf-8-sig")

    matches = raw_matches[list(COLUMN_NAMES)].rename(columns=COLUMN_NAMES)
    matches.insert(0, "Season", SEASON)

    unknown_teams = set(matches["HomeTeam"]) - set(TEAM_NAMES)
    if unknown_teams:
        raise ValueError(f"Kein deutscher Name hinterlegt für: {sorted(unknown_teams)}")

    matches["HomeTeam"] = matches["HomeTeam"].map(TEAM_NAMES)
    matches["AwayTeam"] = matches["AwayTeam"].map(TEAM_NAMES)

    matches.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"{len(matches)} Spiele in {OUTPUT_FILE} gespeichert.")


if __name__ == "__main__":
    main()
