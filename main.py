import logging
from pipeline import QuranPipeline

logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

pipeline = QuranPipeline()

for surah in range(1, 115):
    # try:
    logging.info(f"Processing Surah {surah}")
    pipeline.process_surah(surah)
    # except Exception as e:
    #     logging.error(f"Error in Surah {surah}: {e}")