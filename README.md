# Suivi Nutrition & Forme

Dashboard personnel de suivi nutrition, entraînement et forme pour athlète d'endurance. Développé avec Streamlit et SQLite.

## Fonctionnalités

### 🍽️ Nutrition
- Saisie des repas par type (petit-déjeuner, déjeuner, dîner, collation) et heure
- Calcul automatique des macros (glucides, protéines, lipides) et calories
- Bilan journalier avec objectifs personnalisés et balance énergétique (TDEE)
- Bibliothèque d'aliments favoris personnalisable
- Import d'aliments par photo (OCR via EasyOCR) et fichiers nutrition
- Suppression de repas par groupe

### 🏃 Entraînement
- Import de fichiers `.fit` (Garmin, etc.) avec analyse des zones de fréquence cardiaque
- Visualisation des zones FC avec bandes colorées et plages bpm
- Saisie manuelle des séances (sport, durée, distance, dénivelé, puissance)
- Calcul automatique des calories brûlées

### 🫀 Forme (morning routine)
- Suivi quotidien des métriques Kubios HRV : Readiness %, RMSSD, PNS index, SNS index, FC repos
- Heure de la prise de mesure HRV
- Suivi du poids et du sommeil (durée + qualité)
- Résumé visuel du jour avec code couleur (optimal / modéré / faible)
- Tendances historiques sur tous les indicateurs (graphiques interactifs)

### 📈 Performance
- Score de ressenti du soir (fatigue, satiété)
- Historique du poids avec moyenne mobile 7 jours
- Graphiques de tendance nutrition

## Installation

```bash
# Cloner le projet
git clone <url-du-repo>
cd Suivi-Nutrition

# Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`.

## Dépendances principales

| Package | Usage |
|---|---|
| `streamlit` | Interface web |
| `pandas` | Manipulation des données |
| `plotly` | Graphiques interactifs |
| `numpy` | Calculs numériques |
| `fitparse` | Lecture des fichiers .fit |
| `easyocr` | OCR pour import photo (optionnel) |
| `Pillow` | Traitement des images |

> **Note** : `easyocr` télécharge un modèle (~100 Mo) au premier lancement. Si vous ne souhaitez pas l'utiliser, l'application fonctionne sans (la fonctionnalité OCR sera simplement désactivée).

## Structure

```
Suivi-Nutrition/
├── app.py              # Application principale
├── requirements.txt    # Dépendances Python
└── sports_nutrition.db # Base de données SQLite (créée au premier lancement, non versionnée)
```

La base de données est créée automatiquement au premier lancement. Elle contient vos données personnelles et n'est pas versionnée (voir `.gitignore`).

## Profil utilisateur

Au premier lancement, configurez votre profil dans la barre latérale :
- Poids, taille, âge, sexe
- TDEE de base (dépense énergétique au repos)

Ces paramètres servent au calcul de la balance énergétique journalière.
