"""Das Poisson-Modell: Daten einlesen, Teamstärken und Wahrscheinlichkeiten berechnen."""

import pandas as pd

REQUIRED_COLUMNS = ["Season", "HomeTeam", "AwayTeam", "HomeGoals", "AwayGoals"]

# 18 Teams, jedes spielt gegen jedes andere zweimal: 18 * 17 = 306
NUMBER_OF_TEAMS = 18
MATCHES_PER_SEASON = NUMBER_OF_TEAMS * (NUMBER_OF_TEAMS - 1)


def load_matches(file_path: str = "data.csv") -> pd.DataFrame:
    """Liest die Spieldaten aus der CSV-Datei und prüft, ob sie vollständig sind.

    Gibt eine Tabelle (DataFrame) zurück, in der jede Zeile ein Spiel ist.
    Wirft einen ValueError, wenn die Daten unbrauchbar sind.
    """
    matches = pd.read_csv(file_path)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in matches.columns]
    if missing_columns:
        raise ValueError(f"Fehlende Spalten in {file_path}: {missing_columns}")

    # Leerzeichen am Rand der Teamnamen entfernen (" Bayern Munich" -> "Bayern Munich")
    matches["HomeTeam"] = matches["HomeTeam"].str.strip()
    matches["AwayTeam"] = matches["AwayTeam"].str.strip()

    # Spiele mit fehlenden Werten (z. B. noch nicht gespielt) entfernen
    matches = matches.dropna(subset=REQUIRED_COLUMNS)

    # Tore müssen ganze Zahlen sein; "abc" würde hier einen Fehler auslösen
    matches["HomeGoals"] = matches["HomeGoals"].astype(int)
    matches["AwayGoals"] = matches["AwayGoals"].astype(int)

    if (matches["HomeGoals"] < 0).any() or (matches["AwayGoals"] < 0).any():
        raise ValueError("Die Daten enthalten negative Torzahlen.")

    if len(matches) != MATCHES_PER_SEASON:
        raise ValueError(
            f"Erwartet {MATCHES_PER_SEASON} Spiele, gefunden {len(matches)}. "
            "Die Saison ist unvollständig."
        )

    team_count = matches["HomeTeam"].nunique()
    if team_count != NUMBER_OF_TEAMS:
        raise ValueError(f"Erwartet {NUMBER_OF_TEAMS} Teams, gefunden {team_count}.")

    return matches


def get_teams(matches: pd.DataFrame) -> list[str]:
    """Gibt alle Teams der Saison alphabetisch sortiert zurück (für die Dropdowns)."""
    return sorted(matches["HomeTeam"].unique())


def calculate_team_stats(matches: pd.DataFrame) -> pd.DataFrame:
    """Berechnet für jedes Team Spiele, Tore und Gegentore – gesamt und pro Spiel.

    Jedes Spiel taucht zweimal auf: einmal aus Sicht des Heimteams
    und einmal aus Sicht des Auswärtsteams. Beide Sichten werden addiert.
    """
    # Sicht der Heimteams: eigene Tore = HomeGoals, Gegentore = AwayGoals
    home_stats = matches.groupby("HomeTeam").agg(
        games=("HomeGoals", "count"),
        goals_scored=("HomeGoals", "sum"),
        goals_conceded=("AwayGoals", "sum"),
    )

    # Sicht der Auswärtsteams: eigene Tore = AwayGoals, Gegentore = HomeGoals
    away_stats = matches.groupby("AwayTeam").agg(
        games=("AwayGoals", "count"),
        goals_scored=("AwayGoals", "sum"),
        goals_conceded=("HomeGoals", "sum"),
    )

    # Zeilen mit gleichem Teamnamen werden addiert (Heim + Auswärts)
    team_stats = home_stats.add(away_stats)
    team_stats.index.name = "Team"

    team_stats["goals_scored_per_game"] = team_stats["goals_scored"] / team_stats["games"]
    team_stats["goals_conceded_per_game"] = team_stats["goals_conceded"] / team_stats["games"]

    return team_stats


# Folgt in den nächsten Schritten:
#   calculate_team_strength()  -> Angriffsstärke und Abwehrschwäche         (Schritt 4)
#   calculate_expected_goals() -> λ für Heim- und Auswärtsteam              (Schritt 5)
#   poisson_probability()      -> P(X = k)                                  (Schritt 6)
#   predict_match()            -> Heimsieg / Remis / Auswärtssieg           (Schritt 7)
