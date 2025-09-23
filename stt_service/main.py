from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from tempfile import NamedTemporaryFile
from pathlib import Path
import os

app = FastAPI(title="Speakly STT")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
DEVICE     = os.getenv("WHISPER_DEVICE", "cpu")     # or "cuda"
COMPUTE    = os.getenv("WHISPER_COMPUTE", "int8")   # or "float16" for GPU
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE)

@app.get("/health")
def health(): return {"ok": True, "model": MODEL_SIZE, "device": DEVICE, "compute": COMPUTE}

@app.post("/transcribe-chunk")
async def transcribe_chunk(file: UploadFile = File(...), session_id: str = Form(""), start_ms: int = Form(0)):
    suffix = Path(file.filename or "chunk").suffix or ".m4a"
    tmp = NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(await file.read()); tmp.close()
        segs, info = model.transcribe(tmp.name, language=None, vad_filter=True, beam_size=1, condition_on_previous_text=False)
        out = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs]
        lang = (info.language or "auto").lower()
        if lang.startswith("heb"): lang = "he"
        if lang.startswith("ara"): lang = "ar"
        return {"ok": True, "session_id": session_id, "lang": lang, "start_ms": start_ms, "segments": out}
    finally:
        try: os.remove(tmp.name)
        except: pass
