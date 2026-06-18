from difflib import SequenceMatcher
from config import MAX_WINDOW_WORDS

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_best_match(words, verse_text, start_idx):
    best_score = 0
    best_range = (start_idx, start_idx)

    for end_idx in range(start_idx+1, min(len(words), start_idx+MAX_WINDOW_WORDS)):
        segment = " ".join(w["norm"] for w in words[start_idx:end_idx])
        score = similarity(segment, verse_text)

        if score > best_score:
            best_score = score
            best_range = (start_idx, end_idx)

    return best_range, best_score

def align_verses(words, verses, silences=None):
    aligned = []
    idx = 0

    for sil_start, sil_end in silences:
        print(f"sil_start ={sil_start}, sil_end = {sil_end}")

    for verse in verses:
        (s, e), score = find_best_match(words, verse["norm_text"], idx)

        start = words[s]["start"]
        end = words[e-1]["end"]
        # init the expected silience
        prev_sil_end, next_sil_start = start, end

        # see some logs:
        if idx <= 50:
            print(f"verse text = {verse['norm_text']}, start = {start}, end = {end}")

        # Optional silence adjustment
        if silences:
            for _, sil_end in silences:
                if sil_end <= start:
                    if  start - sil_end < 3:
                        prev_sil_end = sil_end
                else:
                    break
            start = prev_sil_end


            for sil_start, _ in silences:
                if sil_start >= end:      
                    if sil_start - end < 3:
                        next_sil_start = sil_start
                        break
            end = next_sil_start



            # for sil_start, _ in silences:
            #     if sil_start - end > 0 and end - sil_start < 2.5:          # TODO: check the threshold value
            #         end = sil_start
            #         break

            # for _, sil_end in silences:
            #     if sil_end - start > 0 and sil_end - start < 2.5:          # TODO: check the threshold value
            #         start = sil_end
            #         break

        # see some logs:
        if idx <= 50:
            print(f"verse text = {verse['norm_text']}, start = {start}, mod_end = {end}")

        aligned.append({
            "ayah": verse["ayah_num"],
            "text": verse["text"],
            "start": start,
            "end": end,
            "score": score
        })

        idx = e

    return aligned