import os
import librosa
from tqdm import tqdm

from config import *
from asr import ASRModel
from io_utils import load_quran_excel, get_surah
from audio_utils import convert_mp3_to_wav, export_segment, detect_silence, split_audio_2_chunks
from audio_utils import load_audio_once, cut_audio_from_loaded
from aligner import align_verses
from pydub import AudioSegment
from textgrid import TextGrid, IntervalTier

class QuranPipeline:
    def __init__(self):
        self.df = load_quran_excel(EXCEL_PATH)
        self.asr = ASRModel()

    def process_surah(self, surah_num):
        mp3_path = os.path.join(MP3_DIR, f"{surah_num:03d}.mp3")
        wav_path = os.path.join(WAV_DIR, f"{surah_num:03d}.wav")

        # check the file existance:
        if not os.path.exists(mp3_path):
            # print(f"Skipping Surah {surah_num:03d}.mp3 - Audio file not found.")
            return
            
        print(f"\nProcessing Surah {surah_num:03d}...")

        if not os.path.exists(wav_path):
            convert_mp3_to_wav(mp3_path, wav_path)

        # Get from Excel database sheet
        verses = get_surah(self.df, surah_num)

        # Get from Speech processing
        silences, file_duration_time = detect_silence(wav_path, top_db=35)  # your function

        # Get words using ASR to align with Sura verses
        if file_duration_time < CHUNK_TIME:
            words = self.asr.transcribe_with_timestamps(wav_path)
        else:
            words = []
            # Split the audio to chunks
            chunks = split_audio_2_chunks(silences)
            audio_data, sr = load_audio_once(wav_path)

            for i, (start, end) in enumerate(chunks):
                chunk_path = f"data/temp_chunks/chunk_{i}.wav"
                cut_audio_from_loaded(audio_data, sr, start, end, chunk_path)

                chunk_words = self.asr.transcribe_with_timestamps(chunk_path)

                for w in chunk_words:
                    w["start"] += start
                    w["end"] += start

                words.extend(chunk_words)

        aligned_verses = align_verses(words, verses, silences)

        self.export_results(surah_num, mp3_path, aligned_verses)

    def export_results(self, surah_num, mp3_path, aligned):
        audio = AudioSegment.from_mp3(mp3_path)
        duration = audio.duration_seconds

        tg = TextGrid(maxTime=duration)
        tier = IntervalTier(name="verses", maxTime=duration)

        for i, v in enumerate(aligned):
            fname = f"{surah_num:03d}{v['ayah']:03d}"

            wav_out = os.path.join(OUT_WAV_DIR, f"{fname}.wav")
            mp3_out = os.path.join(OUT_MP3_DIR, f"{fname}.mp3")

            export_segment(audio, v["start"], v["end"], wav_out, mp3_out)

            print(v["start"], v["end"], v["text"])

            if i == 0 and v["start"] > 0.2:
                tier.add(0, v["start"], "<Sil>")
                tier.add(v["start"], v["end"], v["text"]) 

            elif i == len(aligned)-1 and duration - v["end"] > 0.2:
                tier.add(v["start"], v["end"], v["text"])    
                tier.add(v["end"], duration, "<Sil>")

            else:
                tier.add(v["start"], v["end"], v["text"])    
                if v["end"] < aligned[i+1]["start"]:
                    tier.add(v["end"], aligned[i+1]["start"], "<Sil>")  

        tg.append(tier)
        tg.write(os.path.join(TEXTGRID_DIR, f"{surah_num:03d}.TextGrid"))