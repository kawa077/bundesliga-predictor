// Schickt die ausgewählten Teams an den Server und zeigt die Vorhersage an.
// Hier wird nichts berechnet – nur angezeigt und formatiert.

const form = document.getElementById("prediction-form");
const resultSection = document.getElementById("result");
const errorMessage = document.getElementById("error-message");

// 0.6385 -> "63,9 %"
function formatPercent(value) {
    return (value * 100).toLocaleString("de-DE", {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
    }) + " %";
}

// 2.44 -> "2,44"
function formatGoals(value) {
    return value.toLocaleString("de-DE", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
    resultSection.hidden = true;
}

function showPrediction(prediction) {
    errorMessage.hidden = true;

    document.getElementById("home-name").textContent = prediction.home_team;
    document.getElementById("away-name").textContent = prediction.away_team;
    document.getElementById("home-goals").textContent = formatGoals(prediction.expected_home_goals);
    document.getElementById("away-goals").textContent = formatGoals(prediction.expected_away_goals);

    const outcomes = [
        ["home-win", prediction.home_win],
        ["draw", prediction.draw],
        ["away-win", prediction.away_win],
    ];
    for (const [id, probability] of outcomes) {
        document.getElementById(id).textContent = formatPercent(probability);
        document.getElementById(id + "-bar").style.width = (probability * 100) + "%";
    }

    document.getElementById("most-likely-score").textContent =
        prediction.most_likely_score.replace(":", " : ");
    document.getElementById("most-likely-probability").textContent =
        formatPercent(prediction.most_likely_score_probability);

    resultSection.hidden = false;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault(); // verhindert das Neuladen der Seite

    const homeTeam = document.getElementById("home-team").value;
    const awayTeam = document.getElementById("away-team").value;

    if (homeTeam === awayTeam) {
        showError("Bitte zwei unterschiedliche Teams auswählen.");
        return;
    }

    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam }),
        });
        const data = await response.json();

        if (!response.ok) {
            showError(data.error);
            return;
        }
        showPrediction(data);
    } catch (error) {
        showError("Der Server ist nicht erreichbar.");
    }
});
