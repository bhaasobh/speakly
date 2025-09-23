# main.py
from fastapi import FastAPI, UploadFile, File, Form, Request ,Body
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
from faster_whisper import WhisperModel
from starlette.concurrency import run_in_threadpool
from tempfile import NamedTemporaryFile
import os, httpx
from pydantic import BaseModel


STT_BASE = os.getenv("STT_BASE", "http://127.0.0.1:9001")  # change to GPU host later
STT_TIMEOUT = float(os.getenv("STT_TIMEOUT", "25"))

async def call_whisper_chunk(file_bytes: bytes, filename: str, session_id: str, start_ms: int):
    async with httpx.AsyncClient(timeout=STT_TIMEOUT) as client:
        files = {"file": (filename or "chunk.m4a", file_bytes, "application/octet-stream")}
        data = {"session_id": session_id, "start_ms": str(start_ms)}
        r = await client.post(f"{STT_BASE}/transcribe-chunk", data=data, files=files)
        r.raise_for_status()
        return r.json()
    
app = FastAPI(title="Speakly Backend", version="0.1.0")

@app.post("/stt/transcribe-chunk")
async def stt_transcribe_chunk(file: UploadFile = File(...), session_id: str = Form(""), start_ms: int = Form(0)):
    try:
        b = await file.read()
        return await call_whisper_chunk(b, file.filename, session_id, start_ms)
    except httpx.HTTPError as e:
        return {"ok": False, "error": f"whisper upstream: {e}"}



# CORS: allow local dev from Expo / emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}

UPLOAD_ROOT = Path("uploads")

class SessionPayload(BaseModel):
    title: str = "Untitled"

@app.post("/session/create")
def create_session(payload: SessionPayload = Body(...)):
    """
    Generate a session folder where clips will be stored.
    Returns: { session_id }
    """
    sid = str(uuid.uuid4())[:8]
    (UPLOAD_ROOT / sid).mkdir(parents=True, exist_ok=True)
    return {"session_id": sid, "title": payload.title}


@app.post("/upload")
async def upload(session_id: str = Form(...), file: UploadFile = File(...)):
    """
    Save uploaded file under uploads/<session_id>/<filename>
    """
    dest_dir = (UPLOAD_ROOT / session_id)
    dest_dir.mkdir(parents=True, exist_ok=True)  # auto-create to avoid "invalid session_id"

    dest = dest_dir / file.filename
    data = await file.read()
    dest.write_bytes(data)

    return {"ok": True, "saved": str(dest), "size": len(data)}

# Optional: debug what the server actually receives
@app.post("/debug-upload")
async def debug_upload(request: Request):
    form = await request.form()
    keys = list(form.keys())
    types = {k: type(form[k]).__name__ for k in keys}
    filenames = {k: getattr(form[k], "filename", None) for k in keys}
    return {
        "content_type": request.headers.get("content-type"),
        "keys": keys,
        "types": types,
        "filenames": filenames,
    }
