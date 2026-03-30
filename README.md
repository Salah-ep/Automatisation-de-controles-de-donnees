# Data Quality Checker

Pipeline Python d'automatisation des contrôles qualité sur des fichiers de données.
Produit un score de qualité (0–100) et un rapport HTML auto-généré.

---

## Contexte du projet

Dans de nombreuses équipes data, les contrôles qualité sont effectués manuellement :
vérification visuelle des fichiers Excel, détection ad hoc des doublons, corrections
au cas par cas. Ce projet automatise ces tâches répétitives et fournit un rapport
structuré, reproductible et partageable.

---

## Fonctionnalités

| Contrôle | Description |
|---|---|
| Doublons | Détection de lignes dupliquées sur tout ou partie des colonnes |
| Valeurs nulles | Taux de nulls par colonne, seuils d'alerte configurables |
| Formats | Validation par regex : email, téléphone, date ISO, code postal |
| Outliers | Méthode IQR ou Z-score sur toutes les colonnes numériques |
| Cohérence métier | Règles personnalisées exprimées en expressions pandas |

---

## Structure du projet

```
Automatisation-de-controles-de-donnees/
│
├── data/
│   ├── sample_clean.csv       # Jeu de données sans anomalie
│   └── sample_dirty.csv       # Jeu de données avec erreurs volontaires
│
├── src/
│   ├── loader.py              # Chargement CSV / Excel / JSON
│   ├── checks.py              # Tous les contrôles qualité
│   ├── scorer.py              # Score de 0 à 100 + grade A–F
│   └── reporter.py            # Génération du rapport HTML
│
├── reports/                   # Rapports générés (ignorés par git)
├── main.py                    # Point d'entrée CLI
├── requirements.txt           # Dépendances Python
└── README.md
```

---

## Installation

```bash
# Cloner le projet
git clone https://github.com/Salah-ep/Automatisation-de-controles-de-donnees.git
cd Automatisation-de-controles-de-donnees

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## Utilisation

### Commande de base

```bash
python main.py --fichier data/sample_dirty.csv
```

### Options disponibles

```bash
python main.py --fichier <chemin> [--methode iqr|zscore] [--output <dossier>]
```

| Option | Description | Défaut |
|---|---|---|
| `--fichier` | Chemin vers le fichier à analyser | — (obligatoire) |
| `--methode` | Méthode de détection outliers : `iqr` ou `zscore` | `iqr` |
| `--output` | Dossier de sortie du rapport HTML | `reports/` |

### Exemples

```bash
# Fichier CSV avec méthode Z-score
python main.py --fichier data/sample_dirty.csv --methode zscore

# Fichier Excel, rapport dans un dossier personnalisé
python main.py --fichier data/mon_fichier.xlsx --output resultats/

# Fichier JSON
python main.py --fichier data/export.json
```

---

## Personnaliser les contrôles

Dans `main.py`, la variable `config` permet d'adapter les contrôles à ton fichier :

```python
config = {
    # Colonnes servant de clés pour la détection de doublons
    "colonnes_cles": ["id"],

    # Contrôles de format (clé = colonne, valeur = format attendu)
    "regles_formats": {
        "email":       "email",
        "code_postal": "code_postal_fr",
        "date_naissance": "date_iso",
    },

    # Règles métier personnalisées
    "regles_coherence": [
        {"nom": "Age valide",   "condition": "age >= 0 and age <= 120"},
        {"nom": "Prix positif", "condition": "prix > 0"},
        {"nom": "Stock cohérent", "condition": "stock_reel <= stock_max"},
    ],

    # Méthode de détection des outliers
    "methode_outliers": "iqr",
}
```

---

## Exemple de sortie console

```
==================================================
  DATA QUALITY CHECKER
==================================================
[Loader] Chargement du fichier : data/sample_dirty.csv
[Loader] 15 lignes · 8 colonnes chargées.
[Checks] Lancement des contrôles qualité...
[Checks] 3 contrôle(s) effectué(s).
[Scorer] Score global : 61.4/100  →  Grade C (Moyen)

==================================================
  SCORE QUALITÉ : 61.4/100  |  Grade C  |  Moyen
  Corrections recommandées avant utilisation.
==================================================
  ✔  OK            : 0
  ⚠  Avertissements: 1
  ✖  Erreurs       : 2
--------------------------------------------------
  ✖  [ 45.2/100]  Doublons
          2 ligne(s) dupliquée(s) (13.3% du fichier) — taux critique.
  ✖  [ 58.8/100]  Valeurs nulles
          5 valeur(s) manquante(s). Colonnes critiques : email, code_postal.
  ⚠  [ 80.3/100]  Outliers
          1 valeur(s) aberrante(s) détectée(s) (méthode : IQR).
==================================================

  Rapport disponible : reports/rapport_qualite_20260330_143022.html
```

---

## Score et grades

| Grade | Score | Signification |
|---|---|---|
| A | ≥ 90 | Excellent — données prêtes à l'emploi |
| B | ≥ 75 | Bon — quelques points à surveiller |
| C | ≥ 55 | Moyen — corrections recommandées |
| D | ≥ 35 | Insuffisant — nettoyage prioritaire |
| F | < 35 | Critique — données non fiables |

Le score est **pondéré** : les doublons et la cohérence métier ont un poids plus élevé
que les contrôles de format, car ils impactent directement l'intégrité des données.

---

## Dépendances

```
pandas>=2.0
numpy>=1.24
openpyxl>=3.1
```

---

## Compétences démontrées

- **Python** : programmation modulaire, gestion d'erreurs, argparse
- **Pandas / NumPy** : manipulation de DataFrames, statistiques descriptives
- **Qualité de données** : définition et implémentation de KPIs qualité
- **Reporting** : génération de rapports HTML auto-contenus
- **Bonnes pratiques** : interface uniforme, configuration externalisée, documentation

---

## Auteur

Salah Eddine El Boukili — Élève ingénieur ISIMA, spécialité SIAD  
[salaheddine00elboukili@gmail.com](mailto:salaheddine00elboukili@gmail.com)
