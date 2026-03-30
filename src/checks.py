import pandas as pd
import numpy as np
import re


# ---------------------------------------------------------------------------
# 1. DOUBLONS
# ---------------------------------------------------------------------------

def check_doublons(df: pd.DataFrame, colonnes_cles: list = None) -> dict:
    doublons = df.duplicated(subset=colonnes_cles, keep=False)
    nb = int(doublons.sum())

    if nb == 0:
        statut = "OK"
        details = "Aucun doublon détecté."
    elif nb / len(df) < 0.05:
        statut = "AVERTISSEMENT"
        details = f"{nb} ligne(s) dupliquée(s) ({nb/len(df)*100:.1f}% du fichier)."
    else:
        statut = "ERREUR"
        details = f"{nb} ligne(s) dupliquée(s) ({nb/len(df)*100:.1f}% du fichier) — taux critique."

    exemples = df[doublons].head(5).to_dict(orient="records") if nb > 0 else []

    return {
        "controle": "Doublons",
        "statut": statut,
        "details": details,
        "nb_lignes": nb,
        "exemples": exemples,
    }


# ---------------------------------------------------------------------------
# 2. VALEURS NULLES
# ---------------------------------------------------------------------------

def check_valeurs_nulles(df: pd.DataFrame, seuil_warning: float = 0.05,
                          seuil_erreur: float = 0.20) -> dict:
    nulls = df.isnull().sum()
    taux = (nulls / len(df)).round(4)
    colonnes_nulles = nulls[nulls > 0]

    if len(colonnes_nulles) == 0:
        statut = "OK"
        details = "Aucune valeur manquante détectée."
        nb = 0
    else:
        nb = int(nulls.sum())
        colonnes_critiques = taux[taux >= seuil_erreur].index.tolist()
        colonnes_warning   = taux[(taux >= seuil_warning) & (taux < seuil_erreur)].index.tolist()

        if colonnes_critiques:
            statut = "ERREUR"
            details = (
                f"{nb} valeur(s) manquante(s) au total. "
                f"Colonnes critiques (>{seuil_erreur*100:.0f}%) : {', '.join(colonnes_critiques)}."
            )
        else:
            statut = "AVERTISSEMENT"
            details = (
                f"{nb} valeur(s) manquante(s) au total. "
                f"Colonnes à surveiller : {', '.join(colonnes_warning)}."
            )

    detail_par_colonne = {
        col: {"nb_nulls": int(nulls[col]), "taux": f"{taux[col]*100:.1f}%"}
        for col in colonnes_nulles.index
    }

    return {
        "controle": "Valeurs nulles",
        "statut": statut,
        "details": details,
        "nb_lignes": nb,
        "exemples": detail_par_colonne,
    }


# ---------------------------------------------------------------------------
# 3. FORMATS
# ---------------------------------------------------------------------------

PATTERNS = {
    "email":      r"^[\w\.-]+@[\w\.-]+\.\w{2,}$",
    "telephone":  r"^(\+?\d[\d\s\-\.]{6,14}\d)$",
    "date_iso":   r"^\d{4}-\d{2}-\d{2}$",
    "code_postal_fr": r"^\d{5}$",
}


def check_format_colonne(df: pd.DataFrame, colonne: str, format_attendu: str) -> dict:
    if colonne not in df.columns:
        return {
            "controle": f"Format · {colonne}",
            "statut": "ERREUR",
            "details": f"Colonne '{colonne}' introuvable dans le fichier.",
            "nb_lignes": 0,
            "exemples": [],
        }

    pattern = PATTERNS.get(format_attendu, format_attendu)
    serie = df[colonne].dropna().astype(str)
    masque_invalide = ~serie.str.match(pattern)
    invalides = serie[masque_invalide]
    nb = len(invalides)

    if nb == 0:
        statut = "OK"
        details = f"Toutes les valeurs de '{colonne}' respectent le format '{format_attendu}'."
    elif nb / len(serie) < 0.1:
        statut = "AVERTISSEMENT"
        details = f"{nb} valeur(s) invalide(s) dans '{colonne}' (format attendu : {format_attendu})."
    else:
        statut = "ERREUR"
        details = f"{nb} valeur(s) invalide(s) dans '{colonne}' — format '{format_attendu}' non respecté."

    return {
        "controle": f"Format · {colonne}",
        "statut": statut,
        "details": details,
        "nb_lignes": nb,
        "exemples": invalides.head(5).tolist(),
    }


def check_formats(df: pd.DataFrame, regles: dict) -> list:
    return [check_format_colonne(df, col, fmt) for col, fmt in regles.items()]


# ---------------------------------------------------------------------------
# 4. VALEURS ABERRANTES (OUTLIERS)
# ---------------------------------------------------------------------------

def check_outliers(df: pd.DataFrame, colonnes: list = None,
                   methode: str = "iqr") -> dict:
    cols_numeriques = df.select_dtypes(include=[np.number]).columns.tolist()
    if colonnes:
        cols_numeriques = [c for c in colonnes if c in cols_numeriques]

    if not cols_numeriques:
        return {
            "controle": "Outliers",
            "statut": "OK",
            "details": "Aucune colonne numérique à analyser.",
            "nb_lignes": 0,
            "exemples": {},
        }

    resultats = {}
    total_outliers = 0

    for col in cols_numeriques:
        serie = df[col].dropna()

        if methode == "iqr":
            Q1 = serie.quantile(0.25)
            Q3 = serie.quantile(0.75)
            IQR = Q3 - Q1
            borne_basse = Q1 - 1.5 * IQR
            borne_haute = Q3 + 1.5 * IQR
            masque = (serie < borne_basse) | (serie > borne_haute)

        elif methode == "zscore":
            z = (serie - serie.mean()) / serie.std()
            masque = z.abs() > 3

        else:
            raise ValueError(f"Méthode '{methode}' non reconnue. Utilisez 'iqr' ou 'zscore'.")

        outliers = serie[masque]
        nb = len(outliers)
        total_outliers += nb

        if nb > 0:
            resultats[col] = {
                "nb_outliers": nb,
                "valeurs": outliers.head(5).tolist(),
                "min": float(serie.min()),
                "max": float(serie.max()),
            }

    if total_outliers == 0:
        statut = "OK"
        details = f"Aucun outlier détecté (méthode : {methode.upper()})."
    elif total_outliers < 10:
        statut = "AVERTISSEMENT"
        details = f"{total_outliers} valeur(s) aberrante(s) détectée(s) (méthode : {methode.upper()})."
    else:
        statut = "ERREUR"
        details = f"{total_outliers} valeur(s) aberrante(s) — volume important (méthode : {methode.upper()})."

    return {
        "controle": "Outliers",
        "statut": statut,
        "details": details,
        "nb_lignes": total_outliers,
        "exemples": resultats,
    }


# ---------------------------------------------------------------------------
# 5. COHÉRENCE ENTRE COLONNES
# ---------------------------------------------------------------------------

def check_coherence(df: pd.DataFrame, regles: list) -> list:
    resultats = []
    for regle in regles:
        try:
            masque_invalide = ~df.eval(regle["condition"])
            nb = int(masque_invalide.sum())

            if nb == 0:
                statut, details = "OK", f"Règle '{regle['nom']}' respectée sur toutes les lignes."
            else:
                statut = "ERREUR" if nb / len(df) > 0.05 else "AVERTISSEMENT"
                details = f"{nb} ligne(s) violent la règle '{regle['nom']}'."

            resultats.append({
                "controle": f"Cohérence · {regle['nom']}",
                "statut": statut,
                "details": details,
                "nb_lignes": nb,
                "exemples": df[masque_invalide].head(5).to_dict(orient="records"),
            })
        except Exception as e:
            resultats.append({
                "controle": f"Cohérence · {regle['nom']}",
                "statut": "ERREUR",
                "details": f"Impossible d'évaluer la règle : {e}",
                "nb_lignes": 0,
                "exemples": [],
            })

    return resultats


# ---------------------------------------------------------------------------
# FONCTION PRINCIPALE : lancer tous les contrôles
# ---------------------------------------------------------------------------

def run_all_checks(df: pd.DataFrame, config: dict = None) -> list:
    config = config or {}
    resultats = []

    print("[Checks] Lancement des contrôles qualité...")

    # 1. Doublons
    resultats.append(check_doublons(df, config.get("colonnes_cles")))

    # 2. Valeurs nulles
    resultats.append(check_valeurs_nulles(df))

    # 3. Outliers
    resultats.append(check_outliers(df, methode=config.get("methode_outliers", "iqr")))

    # 4. Formats (si configurés)
    if config.get("regles_formats"):
        resultats.extend(check_formats(df, config["regles_formats"]))

    # 5. Cohérence métier (si configurée)
    if config.get("regles_coherence"):
        resultats.extend(check_coherence(df, config["regles_coherence"]))

    print(f"[Checks] {len(resultats)} contrôle(s) effectué(s).")
    return resultats
