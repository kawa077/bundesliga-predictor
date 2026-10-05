# Bundesliga Predictor

Eine Web-App, die mit einem **Poisson-Modell** die Wahrscheinlichkeiten für den Ausgang von Bundesliga-Spielen berechnet: Heimsieg, Remis, Auswärtssieg und wahrscheinlichstes Endergebnis.

Grundlage sind alle 306 Spiele der Bundesliga-Saison **2025/26**.

```
Bayern München – Borussia Dortmund

Erwartete Tore:   Bayern München 2,44  –  Borussia Dortmund 1,21

Heimsieg:      63,9 %
Remis:         18,5 %
Auswärtssieg:  17,7 %

Wahrscheinlichstes Ergebnis: 2 : 1 (9,5 %)
```

## Technologien

| Bereich | Technologie | Aufgabe |
|---|---|---|
| Daten | **pandas** | CSV einlesen, prüfen, Statistiken pro Team berechnen |
| Mathematik | **NumPy** | Wahrscheinlichkeiten als Arrays, Ergebnis-Matrix |
| Webserver | **Flask** | Webseite ausliefern, Vorhersagen als JSON zurückgeben |
| Oberfläche | HTML, CSS, JavaScript | Teamauswahl und Anzeige, ohne Framework |

## Projektstruktur

```
bundesliga-predictor/
├── predictor.py        # das komplette Modell (Daten, Teamstärken, Poisson)
├── app.py              # Flask: verbindet Webseite und Modell, rechnet selbst nichts
├── prepare_data.py     # erzeugt data.csv aus den Rohdaten (einmalig)
├── data.csv            # 306 Spiele der Saison 2025/26
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js       # schickt die Teams an den Server und zeigt das Ergebnis an
```

Die gesamte Berechnung liegt in `predictor.py`. Flask und JavaScript sind nur für Ein- und Ausgabe zuständig.

## Daten

Die Spieldaten stammen von [football-data.co.uk](https://www.football-data.co.uk/germanym.php). `prepare_data.py` lädt die Rohdatei mit über 100 Spalten, behält nur die benötigten Spalten und übersetzt die Teamnamen ins Deutsche:

```
Season,HomeTeam,AwayTeam,HomeGoals,AwayGoals
2025-26,Bayern München,RB Leipzig,6,0
```

Beim Einlesen (`load_matches()`) wird geprüft:

- Sind alle Spalten vorhanden?
- Gibt es fehlende Werte oder negative Torzahlen?
- Sind es genau **306 Spiele** und **18 Teams**? Jedes Team spielt zweimal gegen jedes andere, also 18 × 17 = 306.

## So funktioniert das Modell

### 1. Teamstatistiken

Für jedes Team werden aus allen 34 Spielen die Tore und Gegentore pro Spiel berechnet. Jedes Spiel wird dabei aus beiden Blickwinkeln gezählt: Ein 6:0 von Bayern gegen Leipzig sind für Bayern 6 Tore und für Leipzig 6 Gegentore.

Über die ganze Liga gilt:

$$\text{Liga-Tore pro Spiel} = \frac{990 \text{ Tore}}{18 \text{ Teams} \times 34 \text{ Spiele}} \approx 1{,}62$$

### 2. Angriffsstärke und Abwehrschwäche

Jedes Team wird mit dem Liga-Durchschnitt verglichen:

$$\text{Angriffsstärke} = \frac{\text{Tore des Teams pro Spiel}}{\text{Tore der Liga pro Spiel}}$$

$$\text{Abwehrschwäche} = \frac{\text{Gegentore des Teams pro Spiel}}{\text{Gegentore der Liga pro Spiel}}$$

**Beispiele:**

- **Bayern, Angriff:** 3,59 / 1,62 = **2,22**. Bayern trifft 2,22-mal so oft wie ein durchschnittliches Team.
- **Dortmund, Abwehr:** 1,00 / 1,62 = **0,62**. Dortmund kassiert nur 62 % der durchschnittlichen Gegentore.

| Wert | Angriffsstärke | Abwehrschwäche |
|---|---|---|
| > 1 | besser als der Durchschnitt | **schlechter** als der Durchschnitt |
| = 1 | Durchschnitt | Durchschnitt |
| < 1 | schlechter als der Durchschnitt | **besser** als der Durchschnitt |

Deshalb heißt der Wert *Abwehr**schwäche***: Bei der Abwehr ist ein kleiner Wert gut.

### 3. Erwartete Tore (λ)

$$\lambda_{\text{Heim}} = \text{Liga-Heimtore pro Spiel} \times \text{Angriff}_{\text{Heim}} \times \text{Abwehrschwäche}_{\text{Auswärts}}$$

$$\lambda_{\text{Auswärts}} = \text{Liga-Auswärtstore pro Spiel} \times \text{Angriff}_{\text{Auswärts}} \times \text{Abwehrschwäche}_{\text{Heim}}$$

In der Saison 2025/26 fielen im Schnitt **1,78 Heimtore** und **1,46 Auswärtstore** pro Spiel. Weil das Modell für Heim- und Auswärtsteam mit diesen getrennten Werten startet, ist der **Heimvorteil** enthalten.

**Beispiel Bayern (Heim) gegen Dortmund:**

$$\lambda_{\text{Bayern}} = 1{,}78 \times 2{,}22 \times 0{,}62 = 2{,}44 \qquad \lambda_{\text{Dortmund}} = 1{,}46 \times 1{,}27 \times 0{,}65 = 1{,}21$$

λ ist die durchschnittliche Anzahl Tore, die man in diesem Spiel erwarten würde, wenn man es sehr oft wiederholt.

### 4. Die Poisson-Verteilung

Aus λ berechnet die Poisson-Verteilung, wie wahrscheinlich genau *k* Tore sind:

$$P(X = k) = \frac{e^{-\lambda} \cdot \lambda^k}{k!}$$

**Beispiel:** Die Wahrscheinlichkeit, dass Bayern (λ = 2,44) genau 2 Tore schießt:

$$P(X = 2) = \frac{e^{-2{,}44} \cdot 2{,}44^2}{2!} = \frac{0{,}0872 \cdot 5{,}954}{2} \approx 25{,}9\,\%$$

| Tore | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Bayern (λ = 2,44) | 8,7 % | 21,3 % | **25,9 %** | 21,1 % | 12,9 % | 6,3 % | 2,6 % |
| Dortmund (λ = 1,21) | 29,8 % | **36,1 %** | 21,8 % | 8,8 % | 2,7 % | 0,6 % | 0,1 % |

**Warum Poisson?** Die Poisson-Verteilung beschreibt, wie oft ein seltenes Ereignis in einem festen Zeitraum eintritt. Ein Fußballspiel passt gut dazu: Ein Team hat in 90 Minuten viele Angriffe, aber nur wenige werden zu Toren. Die Treffer sind näherungsweise unabhängig voneinander, und es gibt nur ganze Torzahlen ab 0.

### 5. Von Torwahrscheinlichkeiten zu Sieg, Remis und Niederlage

Unter der Annahme, dass die Tore beider Teams unabhängig sind, ist die Wahrscheinlichkeit eines Endergebnisses das Produkt der beiden Einzelwahrscheinlichkeiten:

$$P(\text{2:1}) = P(\text{Bayern 2 Tore}) \times P(\text{Dortmund 1 Tor}) = 25{,}9\,\% \times 36{,}1\,\% \approx 9{,}4\,\%$$

Für alle Kombinationen von 0 bis 6 Toren entsteht so eine 7 × 7-**Ergebnis-Matrix**. Die Zeilen stehen für die Heimtore, die Spalten für die Auswärtstore:

```
              Dortmund 0   Dortmund 1   Dortmund 2   ...
Bayern 0         2,6 %        3,1 %        1,9 %
Bayern 1         6,3 %        7,7 %        4,6 %
Bayern 2         7,7 %        9,4 %        5,7 %
...
```

- **Heimsieg:** Summe aller Felder **unter** der Diagonale (Heimtore > Auswärtstore)
- **Remis:** Summe aller Felder **auf** der Diagonale (0:0, 1:1, 2:2 …)
- **Auswärtssieg:** Summe aller Felder **über** der Diagonale (Auswärtstore > Heimtore)
- **Wahrscheinlichstes Ergebnis:** das Feld mit dem größten Wert

Weil das Modell bei 6 Toren pro Team aufhört, ergibt die Matrix zusammen etwas weniger als 100 %, im Beispiel 98,7 %. Deshalb wird sie **normiert**: Jedes Feld wird durch die Gesamtsumme geteilt, sodass Heimsieg, Remis und Auswärtssieg genau 100 % ergeben.

In NumPy sind das nur wenige Zeilen:

```python
score_matrix = np.outer(home_goal_probs, away_goal_probs)
score_matrix = score_matrix / score_matrix.sum()

home_win = np.tril(score_matrix, k=-1).sum()   # unter der Diagonale
draw     = np.trace(score_matrix)              # Diagonale
away_win = np.triu(score_matrix, k=1).sum()    # über der Diagonale
```

## Installation und Start

Voraussetzung: Python 3.10 oder neuer.

```bash
git clone https://github.com/kawa077/bundesliga-predictor.git
cd bundesliga-predictor
python -m venv .venv
```

Virtuelle Umgebung aktivieren:

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Abhängigkeiten installieren und App starten:

```bash
pip install -r requirements.txt
python app.py
```

Danach im Browser öffnen: **http://127.0.0.1:5000**

`data.csv` ist bereits im Repository enthalten. Um die Daten neu herunterzuladen, führt man `python prepare_data.py` aus.

> Hinweis: `app.py` startet Flask im Debug-Modus. Der ist für die lokale Entwicklung gedacht und darf nicht auf einem öffentlich erreichbaren Server laufen.

## Grenzen des Modells

Das Modell ist bewusst einfach gehalten. Es ist ein statistisches Modell und **keine Garantie** für das tatsächliche Ergebnis. Es berücksichtigt unter anderem nicht:

- **Verletzungen, Sperren und Aufstellungen**
- **Formkurve:** Ein Spiel vom ersten Spieltag zählt genauso viel wie eines vom letzten.
- **Transfers** und Trainerwechsel
- **Teamspezifischen Heimvorteil:** Der Heimvorteil ist für alle Teams gleich groß.
- **Spielverlauf:** Die Tore beider Teams gelten als unabhängig. In Wirklichkeit greift ein zurückliegendes Team stärker an, und eine rote Karte verändert das ganze Spiel.
- **Unterschätzte Remis:** Einfache Poisson-Modelle sagen Unentschieden erfahrungsgemäß etwas zu selten voraus.

## Mögliche Erweiterungen

- Heim- und Auswärtsstärken getrennt berechnen
- Neuere Spiele stärker gewichten als ältere
- Mehrere Saisons einbeziehen
- Backtesting: Modell auf einer Saison berechnen und auf der nächsten testen
