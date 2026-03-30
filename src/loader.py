import pandas as pd
import os


SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls", ".json"]


def load_file(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Fichier introuvable : {filepath}")

    extension = os.path.splitext(filepath)[1].lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Format '{extension}' non supporté. "
            f"Formats acceptés : {', '.join(SUPPORTED_FORMATS)}"
        )

    print(f"[Loader] Chargement du fichier : {filepath}")

    if extension == ".csv":
        df = _load_csv(filepath)

    elif extension in (".xlsx", ".xls"):
        df = _load_excel(filepath)

    elif extension == ".json":
        df = _load_json(filepath)

    print(f"[Loader] {len(df)} lignes · {len(df.columns)} colonnes chargées.")
    return df


def _load_csv(filepath: str) -> pd.DataFrame:
    """Charge un CSV en détectant automatiquement le séparateur."""
    # Tentative avec virgule, puis point-virgule si ça échoue
    try:
        df = pd.read_csv(filepath, sep=",")
        # Si une seule colonne → mauvais séparateur, on retente
        if len(df.columns) == 1:
            df = pd.read_csv(filepath, sep=";")
    except Exception:
        df = pd.read_csv(filepath, sep=";")
    return df


def _load_excel(filepath: str) -> pd.DataFrame:
    return pd.read_excel(filepath, sheet_name=0)


def _load_json(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_json(filepath, orient="records")
    except Exception:
        df = pd.read_json(filepath)
    return df


def get_file_info(filepath: str) -> dict:
    stat = os.stat(filepath)
    return {
        "nom": os.path.basename(filepath),
        "format": os.path.splitext(filepath)[1].lower(),
        "taille_ko": round(stat.st_size / 1024, 2),
    }
