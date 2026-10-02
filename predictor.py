"""Das Poisson-Modell: Daten einlesen, Teamstärken und Wahrscheinlichkeiten berechnen.

Geplante Funktionen (Schritte 2–7):
    load_matches()             -> CSV einlesen und prüfen
    calculate_team_stats()     -> Tore / Gegentore pro Spiel je Team
    calculate_team_strength()  -> Angriffs- und Abwehrstärke
    calculate_expected_goals() -> λ für Heim- und Auswärtsteam
    poisson_probability()      -> P(X = k)
    predict_match()            -> Heimsieg / Remis / Auswärtssieg + wahrscheinlichstes Ergebnis
"""
