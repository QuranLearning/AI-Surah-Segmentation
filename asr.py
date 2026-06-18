import torch
import nemo.collections.asr as nemo_asr
from text_utils import normalize_arabic

MODEL_NAME = "nvidia/stt_ar_fastconformer_hybrid_large_pcd_v1.0"

class ASRModel:
    def __init__(self):
        self.model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel\
            .from_pretrained(model_name=MODEL_NAME)
        self.model.eval()

    def transcribe_with_timestamps(self, audio_path):
        with torch.no_grad():
            hyp = self.model.transcribe(
                [audio_path],
                timestamps=True,
                return_hypotheses=True
            )

        ctc_hyp = hyp[1][0] if isinstance(hyp, tuple) else hyp[0]

        words = []
        for w in ctc_hyp.timestamp['word']:
            words.append({
                "word": w["word"],
                "norm": normalize_arabic(w["word"]),
                "start": w["start"],
                "end": w["end"]
            })

        return words