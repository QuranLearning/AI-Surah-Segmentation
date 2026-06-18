import os

BASE_DIR = os.path.dirname(__file__)

DATA_DIR = os.path.join(BASE_DIR, "data")

MP3_DIR = os.path.join(DATA_DIR, "mp3")
WAV_DIR = os.path.join(DATA_DIR, "wav")

OUT_WAV_DIR = os.path.join(DATA_DIR, "output_wav")
OUT_MP3_DIR = os.path.join(DATA_DIR, "output_mp3")
TEXTGRID_DIR = os.path.join(DATA_DIR, "textgrid")

EXCEL_PATH = os.path.join(DATA_DIR, "Quran_text_db.xlsx")

SAMPLE_RATE = 16000
MAX_WINDOW_WORDS = 50
SIM_THRESHOLD = 0.6

CHUNK_TIME = 40     # in sec.