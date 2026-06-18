import pandas as pd
from text_utils import normalize_arabic

def load_quran_excel(path):
    df = pd.read_excel(path)
    return df

def get_surah(df, surah_num):
    sdf = df[df["Sura number"] == surah_num]

    return [
        {
            "ayah_num": row["Aya number"],
            "text": row["Aya text"],
            "norm_text": normalize_arabic(row["Aya text"])
        }
        for _, row in sdf.iterrows()
    ]