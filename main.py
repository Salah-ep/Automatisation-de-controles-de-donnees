import argparse
import sys
import os

# Ajout du dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from loader   import load_file, get_file_info
from checks   import run_all_checks
from scorer   import calculer_score, afficher_resume
from reporter import generer_rapport


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pipeline de contrôle qualité des données"
    )
    parser.add_argument(
        "--fichier", "-f",
        required=True,
        help="Chemin vers le fichier à analyser (CSV, Excel, JSON)"
    )
    parser.add_argument(
        "--methode", "-m",
        default="iqr",
        choices=["iqr", "zscore"],
        help="Méthode de détection des outliers : iqr (défaut) ou zscore"
    )
    parser.add_argument(
        "--output", "-o",
        default="reports",
        help="Dossier de sortie pour le rapport HTML (défaut : reports/)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("\n" + "=" * 50)
    print("  DATA QUALITY CHECKER")
    print("=" * 50)
    df = load_file(args.fichier)
    info = get_file_info(args.fichier)
    config = {
        "methode_outliers": args.methode,
    }
    resultats = run_all_checks(df, config)
    score_data = calculer_score(resultats, nb_lignes_total=len(df))
    afficher_resume(score_data)
    chemin_rapport = generer_rapport(score_data, info, output_dir=args.output)
    print(f"\n  Rapport disponible : {chemin_rapport}\n")


if __name__ == "__main__":
    main()
