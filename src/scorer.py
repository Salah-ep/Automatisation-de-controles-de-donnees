import pandas as pd


# ---------------------------------------------------------------------------
# Poids des statuts (pénalités de base)
# ---------------------------------------------------------------------------

PENALITE_BASE = {
    "OK":            0.0,
    "AVERTISSEMENT": 0.15,
    "ERREUR":        0.40,
}

POIDS_CONTROLES = {
    "Doublons":      1.5,   # Critique pour l'intégrité
    "Valeurs nulles": 1.2,
    "Outliers":      1.0,
    "Format":        1.0,
    "Cohérence":     1.3,
}

GRADES = [
    (90, "A", "Excellent",     "Données fiables, prêtes à l'emploi."),
    (75, "B", "Bon",           "Quelques points à surveiller, utilisable."),
    (55, "C", "Moyen",         "Corrections recommandées avant utilisation."),
    (35, "D", "Insuffisant",   "Problèmes significatifs, à nettoyer en priorité."),
    (0,  "F", "Critique",      "Données non fiables, intervention requise."),
]


# ---------------------------------------------------------------------------
# Score par contrôle
# ---------------------------------------------------------------------------

def _score_controle(resultat: dict, nb_lignes_total: int) -> float:
    statut = resultat.get("statut", "OK")
    nb_lignes = resultat.get("nb_lignes", 0)

    penalite_base = PENALITE_BASE.get(statut, 0.0)

    if nb_lignes_total > 0 and statut != "OK":
        taux = min(nb_lignes / nb_lignes_total, 1.0)
        penalite = penalite_base * (1 + taux)
    else:
        penalite = penalite_base

    score = max(0.0, 1.0 - penalite)
    return round(score, 4)


def _get_poids(nom_controle: str) -> float:
    for cle, poids in POIDS_CONTROLES.items():
        if cle.lower() in nom_controle.lower():
            return poids
    return 1.0


# ---------------------------------------------------------------------------
# Score global
# ---------------------------------------------------------------------------

def calculer_score(resultats: list, nb_lignes_total: int) -> dict:
    if not resultats:
        return _score_vide()

    detail = []
    score_pondere = 0.0
    poids_total = 0.0

    nb_ok = nb_avert = nb_err = 0

    for res in resultats:
        score = _score_controle(res, nb_lignes_total)
        poids = _get_poids(res["controle"])

        score_pondere += score * poids
        poids_total   += poids

        statut = res["statut"]
        if statut == "OK":
            nb_ok += 1
        elif statut == "AVERTISSEMENT":
            nb_avert += 1
        else:
            nb_err += 1

        detail.append({
            "controle": res["controle"],
            "statut":   statut,
            "score":    round(score * 100, 1),
            "details":  res["details"],
        })

    score_global = round((score_pondere / poids_total) * 100, 1) if poids_total > 0 else 100.0

    grade, mention, interpretation = _attribuer_grade(score_global)

    print(f"[Scorer] Score global : {score_global}/100  →  Grade {grade} ({mention})")

    return {
        "score_global":      score_global,
        "grade":             grade,
        "mention":           mention,
        "interpretation":    interpretation,
        "detail":            detail,
        "nb_ok":             nb_ok,
        "nb_avertissements": nb_avert,
        "nb_erreurs":        nb_err,
    }


def _attribuer_grade(score: float) -> tuple:
    """Retourne (grade, mention, interpretation) selon le score."""
    for seuil, grade, mention, interpretation in GRADES:
        if score >= seuil:
            return grade, mention, interpretation
    return "F", "Critique", "Données non fiables."


def _score_vide() -> dict:
    return {
        "score_global":      100.0,
        "grade":             "A",
        "mention":           "Excellent",
        "interpretation":    "Aucun contrôle effectué.",
        "detail":            [],
        "nb_ok":             0,
        "nb_avertissements": 0,
        "nb_erreurs":        0,
    }


# ---------------------------------------------------------------------------
# Résumé console lisible
# ---------------------------------------------------------------------------

def afficher_resume(score_data: dict) -> None:
    print("\n" + "=" * 50)
    print(f"  SCORE QUALITÉ : {score_data['score_global']}/100  |  Grade {score_data['grade']}  |  {score_data['mention']}")
    print(f"  {score_data['interpretation']}")
    print("=" * 50)
    print(f"  ✔  OK            : {score_data['nb_ok']}")
    print(f"  ⚠  Avertissements: {score_data['nb_avertissements']}")
    print(f"  ✖  Erreurs       : {score_data['nb_erreurs']}")
    print("-" * 50)
    for item in score_data["detail"]:
        icone = {"OK": "✔", "AVERTISSEMENT": "⚠", "ERREUR": "✖"}.get(item["statut"], "?")
        print(f"  {icone}  [{item['score']:5.1f}/100]  {item['controle']}")
        print(f"          {item['details']}")
    print("=" * 50 + "\n")
