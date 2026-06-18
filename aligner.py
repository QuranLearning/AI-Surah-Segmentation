from difflib import SequenceMatcher
from config import MAX_WINDOW_WORDS

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_best_match(words, verse_text, start_idx):
    best_score = 0
    best_range = (start_idx, start_idx)

    for end_idx in range(start_idx + 1, min(len(words), start_idx + MAX_WINDOW_WORDS)):
        segment = " ".join(w["norm"] for w in words[start_idx:end_idx])
        score = similarity(segment, verse_text)

        if score > best_score:
            best_score = score
            best_range = (start_idx, end_idx)

    return best_range, best_score

def find_nearest_silence_before(silences, target_time, max_gap=5.0, forward_tolerance=0.2):
    """
    Find the silence that ends closest to (and before) target_time.
    
    Args:
        max_gap: maximum allowed seconds between silence end and target_time.
        forward_tolerance: if a silence starts within this many seconds AFTER
                           target_time, trust the ASR boundary and return None.
    Returns the silence end time, or None if not found / ASR is already accurate.
    """
    # If a silence starts just after target_time, ASR start is already correct
    for sil_start, sil_end in silences:
        if 0 <= sil_end - target_time <= forward_tolerance:
            return None  # trust ASR

    best_sil_end = None
    best_gap = float("inf")

    for sil_start, sil_end in silences:
        if sil_end <= target_time:
            gap = target_time - sil_end
            if gap < best_gap and gap <= max_gap:
                best_gap = gap
                best_sil_end = sil_end

    return best_sil_end


def find_nearest_silence_after(silences, target_time, max_gap=5.0, backword_tolerance=0.2):
    """
    Find the silence that starts closest to (and after) target_time.
    max_gap: maximum allowed seconds between target_time and silence start.
    Returns the silence start time, or None if not found.
    """

    # If a silence starts just after target_time, ASR start is already correct
    for sil_start, sil_end in silences:
        if 0 <= target_time - sil_start <= backword_tolerance:
            return None  # trust ASR
    
    best_sil_start = None
    best_gap = float("inf")

    for sil_start, sil_end in silences:
        if sil_start >= target_time:
            gap = sil_start - target_time
            if gap < best_gap and gap <= max_gap:
                best_gap = gap
                best_sil_start = sil_start

    return best_sil_start


def align_verses(words, verses, silences=None, max_gap=7.0, low_score_threshold=0.4):
    """
    Align verses to word timestamps from ASR, then tune boundaries using silences.

    Args:
        words: list of dicts with keys: norm, start, end
        verses: list of dicts with keys: norm_text, text, ayah_num
        silences: list of (sil_start, sil_end) tuples in seconds
        max_gap: max seconds to search for a silence boundary beyond ASR boundary
        low_score_threshold: flag verses below this similarity score as warnings
    """
    aligned = []
    idx = 0

    print(f"\n\nSiliences = {silences}")
    for verse in verses:
        (s, e), score = find_best_match(words, verse["norm_text"], idx)

        if score < low_score_threshold:
            print(f"WARNING: Low match score {score:.2f} for verse {verse['ayah_num']} — alignment may be wrong")

        asr_start = words[s]["start"]
        asr_end = words[e - 1]["end"]

        final_start = asr_start
        final_end = asr_end

        if silences:
            # Find nearest silence ending before or at asr_start
            sil_end_before = find_nearest_silence_before(silences, asr_start, max_gap=max_gap)
            if sil_end_before is not None:
                final_start = sil_end_before
            else:
                print(f"  Verse {verse['ayah_num']}: no silence found before start {asr_start:.2f}s within {max_gap}s — using ASR start")

            # Find nearest silence starting after or at asr_end
            sil_start_after = find_nearest_silence_after(silences, asr_end, max_gap=max_gap)
            if sil_start_after is not None:
                final_end = sil_start_after
            else:
                print(f"  Verse {verse['ayah_num']}: no silence found after end {asr_end:.2f}s within {max_gap}s — using ASR end")

        # Safety check: ensure no overlap with previous verse
        if aligned:
            prev_end = aligned[-1]["end"]
            if final_start < prev_end:
                print(f"  Verse {verse['ayah_num']}: start {final_start:.2f}s overlaps previous end {prev_end:.2f}s — clamping")
                final_start = prev_end

        print(f"Verse {verse['ayah_num']}: ASR[{asr_start:.2f} -> {asr_end:.2f}] | Final[{final_start:.2f} -> {final_end:.2f}] | score={score:.2f}")

        aligned.append({
            "ayah": verse["ayah_num"],
            "text": verse["text"],
            "start": final_start,
            "end": final_end,
            "score": score
        })

        idx = e

    return aligned