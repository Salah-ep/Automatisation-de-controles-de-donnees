import os
import json
from datetime import datetime


# ---------------------------------------------------------------------------
# Couleurs par statut
# ---------------------------------------------------------------------------

COULEURS = {
    "OK":            {"bg": "#e8f5e9", "texte": "#2e7d32", "badge": "#43a047"},
    "AVERTISSEMENT": {"bg": "#fff8e1", "texte": "#f57f17", "badge": "#fbc02d"},
    "ERREUR":        {"bg": "#ffebee", "texte": "#b71c1c", "badge": "#e53935"},
}

COULEURS_GRADE = {
    "A": "#2e7d32",
    "B": "#1565c0",
    "C": "#f57f17",
    "D": "#e65100",
    "F": "#b71c1c",
}


# ---------------------------------------------------------------------------
# Composants HTML
# ---------------------------------------------------------------------------

def _badge(statut: str) -> str:
    c = COULEURS.get(statut, COULEURS["OK"])
    icone = {"OK": "✔", "AVERTISSEMENT": "⚠", "ERREUR": "✖"}.get(statut, "?")
    return (
        f'<span style="background:{c["badge"]};color:#fff;'
        f'padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">'
        f'{icone} {statut}</span>'
    )


def _barre_score(score: float, couleur: str = "#1565c0") -> str:
    return (
        f'<div style="background:#e0e0e0;border-radius:6px;height:10px;margin:6px 0;">'
        f'<div style="width:{score}%;background:{couleur};height:10px;border-radius:6px;'
        f'transition:width .4s;"></div></div>'
    )


def _carte_controle(item: dict) -> str:
    c = COULEURS.get(item["statut"], COULEURS["OK"])
    return f"""
    <div style="border-left:4px solid {c['badge']};background:{c['bg']};
                padding:14px 18px;border-radius:0 8px 8px 0;margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-weight:600;color:#212121;">{item['controle']}</span>
        <div style="display:flex;align-items:center;gap:12px;">
          <span style="font-size:13px;color:#555;">{item['score']}/100</span>
          {_badge(item['statut'])}
        </div>
      </div>
      {_barre_score(item['score'], c['badge'])}
      <p style="margin:6px 0 0;font-size:13px;color:{c['texte']};">{item['details']}</p>
    </div>"""


def _section_resume(score_data: dict, info_fichier: dict) -> str:
    grade = score_data["grade"]
    couleur_grade = COULEURS_GRADE.get(grade, "#555")
    score = score_data["score_global"]

    couleur_barre = (
        "#43a047" if score >= 75 else
        "#fbc02d" if score >= 50 else
        "#e53935"
    )

    return f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px;">

      <div style="background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 6px rgba(0,0,0,.08);">
        <p style="margin:0 0 4px;font-size:13px;color:#888;">Score global</p>
        <div style="display:flex;align-items:baseline;gap:10px;">
          <span style="font-size:48px;font-weight:700;color:{couleur_barre};">{score}</span>
          <span style="font-size:20px;color:#aaa;">/100</span>
          <span style="font-size:32px;font-weight:700;color:{couleur_grade};margin-left:8px;">
            {grade}
          </span>
        </div>
        {_barre_score(score, couleur_barre)}
        <p style="margin:8px 0 0;font-size:14px;color:#555;">
          {score_data['mention']} — {score_data['interpretation']}
        </p>
      </div>

      <div style="background:#fff;border-radius:12px;padding:24px;box-shadow:0 1px 6px rgba(0,0,0,.08);">
        <p style="margin:0 0 12px;font-size:13px;color:#888;">Résumé des contrôles</p>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
          <div style="text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#43a047;">{score_data['nb_ok']}</div>
            <div style="font-size:12px;color:#888;">OK</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#fbc02d;">{score_data['nb_avertissements']}</div>
            <div style="font-size:12px;color:#888;">Avertissements</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:28px;font-weight:700;color:#e53935;">{score_data['nb_erreurs']}</div>
            <div style="font-size:12px;color:#888;">Erreurs</div>
          </div>
        </div>
        <hr style="margin:16px 0;border:none;border-top:1px solid #eee;">
        <p style="margin:0;font-size:13px;color:#555;">
          📄 <strong>{info_fichier.get('nom','—')}</strong><br>
          Format : {info_fichier.get('format','—').upper().strip('.')} &nbsp;·&nbsp;
          Taille : {info_fichier.get('taille_ko','—')} Ko
        </p>
      </div>
    </div>"""


# ---------------------------------------------------------------------------
# Rapport complet
# ---------------------------------------------------------------------------

def generer_rapport(
    score_data: dict,
    info_fichier: dict,
    output_dir: str = "reports",
    nom_fichier: str = None,
) -> str:
    os.makedirs(output_dir, exist_ok=True)

    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    if nom_fichier is None:
        nom_fichier = f"rapport_qualite_{horodatage}.html"

    chemin = os.path.join(output_dir, nom_fichier)

    cartes = "\n".join(_carte_controle(item) for item in score_data["detail"])
    resume = _section_resume(score_data, info_fichier)
    date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Rapport qualité — {info_fichier.get('nom','fichier')}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f5f5f5;
      color: #212121;
      margin: 0;
      padding: 0;
    }}
    header {{
      background: #1565c0;
      color: #fff;
      padding: 24px 40px;
    }}
    header h1 {{ margin: 0 0 4px; font-size: 22px; font-weight: 600; }}
    header p  {{ margin: 0; font-size: 13px; opacity: .8; }}
    main {{
      max-width: 900px;
      margin: 32px auto;
      padding: 0 20px;
    }}
    section {{
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 6px rgba(0,0,0,.08);
      margin-bottom: 24px;
    }}
    h2 {{
      margin: 0 0 20px;
      font-size: 16px;
      font-weight: 600;
      color: #1565c0;
      border-bottom: 2px solid #e3f2fd;
      padding-bottom: 8px;
    }}
    footer {{
      text-align: center;
      padding: 24px;
      font-size: 12px;
      color: #aaa;
    }}
  </style>
</head>
<body>

<header>
  <h1>Rapport de qualité des données</h1>
  <p>Généré le {date_str} &nbsp;·&nbsp; Fichier : {info_fichier.get('nom','—')}</p>
</header>

<main>

  {resume}

  <section>
    <h2>Détail des contrôles</h2>
    {cartes if cartes else '<p style="color:#888;">Aucun contrôle enregistré.</p>'}
  </section>

</main>

<footer>
  Data Quality Checker &nbsp;·&nbsp; Généré automatiquement par le pipeline Python
</footer>

</body>
</html>"""

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Reporter] Rapport généré : {chemin}")
    return chemin
