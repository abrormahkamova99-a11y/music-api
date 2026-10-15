import os
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/info")
def get_info(url: str):
    ydl_opts = {
        'noplaylist': True, 
        'quiet': True,
        'username': 'oauth2',
        'password': '',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail")
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/download")
def download_audio(url: str, background_tasks: BackgroundTasks):
    file_id = str(uuid.uuid4())
    output_template = f"/tmp/{file_id}.%(ext)s"
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'username': 'oauth2',
        'password': '',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get('title', 'music')
        background_tasks.add_task(remove_file, filename)
        return FileResponse(path=filename, media_type="audio/mp4", filename=f"{title}.m4a")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
