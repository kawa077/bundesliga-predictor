"""Flask-Webserver: zeigt die Webseite an und gibt Vorhersagen als JSON zurück.

Hier findet keine Mathematik statt – alle Berechnungen liegen in predictor.py.

Start:
    python app.py
Danach im Browser öffnen: http://127.0.0.1:5000
"""

from flask import Flask, jsonify, render_template, request

import predictor

app = Flask(__name__)

# Daten und Teamstärken werden einmal beim Start berechnet, nicht bei jeder Anfrage
matches = predictor.load_matches("data.csv")
team_strength = predictor.calculate_team_strength(predictor.calculate_team_stats(matches))
teams = predictor.get_teams(matches)


@app.route("/")
def index():
    """Zeigt die Startseite mit den beiden Team-Dropdowns."""
    return render_template("index.html", teams=teams)


@app.route("/predict", methods=["POST"])
def predict():
    """Nimmt zwei Teamnamen als JSON entgegen und gibt die Vorhersage als JSON zurück.

    Erwartet: {"home_team": "...", "away_team": "..."}
    """
    data = request.get_json(silent=True) or {}
    home_team = data.get("home_team")
    away_team = data.get("away_team")

    if not home_team or not away_team:
        return jsonify({"error": "Bitte Heim- und Auswärtsteam angeben."}), 400

    try:
        prediction = predictor.predict_match(matches, team_strength, home_team, away_team)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(prediction)


if __name__ == "__main__":
    app.run(debug=True)
