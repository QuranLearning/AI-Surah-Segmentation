import librosa
import soundfile as sf
from pydub import AudioSegment
from config import SAMPLE_RATE
import numpy as np

def convert_mp3_to_wav(mp3_path, wav_path):
    y, _ = librosa.load(mp3_path, sr=SAMPLE_RATE, mono=True)
    sf.write(wav_path, y, SAMPLE_RATE)

def export_segment(audio, start, end, wav_path, mp3_path):
    seg = audio[int(start*1000):int(end*1000)]

    seg.set_frame_rate(SAMPLE_RATE).set_channels(1)\
        .export(wav_path, format="wav")

    seg.export(mp3_path, format="mp3")

def detect_silence(audio_path, top_db=None, min_silence_len=0.4):
    audio, sr = librosa.load(audio_path, sr=None)

    # Estimate noise floor and set top_db dynamically
    if top_db is None:
        # Use the bottom 10% of RMS frames as noise floor estimate
        rms = librosa.feature.rms(y=audio)[0]
        noise_floor_db = librosa.amplitude_to_db(np.percentile(rms, 10))
        peak_db = librosa.amplitude_to_db(np.max(np.abs(audio)))
        dynamic_range = peak_db - noise_floor_db
        # Use 60-70% of dynamic range as threshold
        top_db = dynamic_range * 0.65
        print(f"Auto top_db = {top_db:.1f} dB  (dynamic range = {dynamic_range:.1f} dB)")

    non_silent_intervals = librosa.effects.split(audio, top_db=top_db)
    
    duration_samples = len(audio)
    silences = []
    
    # 2. Check for silence at the very beginning
    if non_silent_intervals[0][0] > 0:
        silences.append((0.0, non_silent_intervals[0][0]/sr))
        
    # 3. Check for gaps between active segments (internal silence)
    for i in range(len(non_silent_intervals) - 1):
        start_silence = non_silent_intervals[i][1]
        end_silence = non_silent_intervals[i+1][0]
        if end_silence - start_silence > min_silence_len*sr:
            silences.append((start_silence/sr, end_silence/sr))
            
    # 4. Check for silence at the very end
    if non_silent_intervals[-1][1] < duration_samples:
        silences.append((non_silent_intervals[-1][1]/sr, duration_samples/sr))
        
    return silences, duration_samples/sr

def detect_silence_gemi(audio_path, top_db=35, min_silence_len=0.4):
    # CALL YOUR EXISTING FUNCTION HERE

    # 1. Get intervals of non-silent (active) audio
    # intervals is an array of [start_sample, end_sample]
    audio, sr = librosa.load(audio_path, sr=None)
    non_silent_intervals = librosa.effects.split(audio, top_db=top_db)
    
    duration_samples = len(audio)
    silences = []
    
    # 2. Check for silence at the very beginning
    if non_silent_intervals[0][0] > 0:
        silences.append((0.0, non_silent_intervals[0][0]/sr))
        
    # 3. Check for gaps between active segments (internal silence)
    for i in range(len(non_silent_intervals) - 1):
        start_silence = non_silent_intervals[i][1]
        end_silence = non_silent_intervals[i+1][0]
        if end_silence - start_silence > min_silence_len*sr:
            silences.append((start_silence/sr, end_silence/sr))
            
    # 4. Check for silence at the very end
    if non_silent_intervals[-1][1] < duration_samples:
        silences.append((non_silent_intervals[-1][1]/sr, duration_samples/sr))
        
    return silences, duration_samples/sr

def split_audio_2_chunks(silences, max_len=60):
    chunks = []
    current_start = 0

    for sil_start, _ in silences:
        if sil_start - current_start > max_len:
            chunks.append((current_start, sil_start))
            current_start = sil_start

    chunks.append((current_start, None))  # last chunk
    return chunks

def load_audio_once(wav_path):
    data, sr = sf.read(wav_path)
    return data, sr


def cut_audio_from_loaded(audio_data, sr, start, end, out_path):
    """
    audio_data: numpy array (full audio)
    sr: sample rate (16000)
    start, end: in seconds
    out_path: output wav file
    """

    total_duration = len(audio_data) / sr

    # Handle edge cases
    start = max(0, start)
    end = total_duration if end is None else min(end, total_duration)

    if start >= end:
        raise ValueError(f"Invalid segment: start={start}, end={end}")

    start_sample = int(start * sr)
    end_sample = int(end * sr)

    segment = audio_data[start_sample:end_sample]

    sf.write(out_path, segment, sr)

    return out_path
