import os
import time
import shutil
import hashlib
import requests
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Create FastAPI app
app = FastAPI()

# Allow all origins for now (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder for generated videos
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# In-memory store of jobs
jobs = {}

# Some sample videos to mock different results
SAMPLE_VIDEOS = [
    "https://res.cloudinary.com/djontsvk9/video/upload/v1755258663/Peppo%20AI/Monica_-_Telugu_Song__COOLIE___Superstar_Rajinikanth___Sun_Pictures___Lokesh___Anirudh___Pooja_Hegde_r9g9i1.mp4",
    "https://res.cloudinary.com/djontsvk9/video/upload/v1755258662/Peppo%20AI/Golden_Sparrow_-_Video_Song___Dhanush___Priyanka_Mohan___Pavish___Anikha___GV_Prakash_NEEK_zbs7ba.mp4",
]


@app.post("/generate")
async def generate_video(prompt: str = Form(...), file: UploadFile = None):
    """
    Create a fake video generation job with unique output based on the prompt.
    """
    job_id = str(len(jobs) + 1)

    # Pick a sample video based on the prompt hash
    prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest(), 16)
    selected_url = SAMPLE_VIDEOS[prompt_hash % len(SAMPLE_VIDEOS)]

    # Download the chosen video to our VIDEO_DIR
    filename = f"{job_id}.mp4"
    video_path = os.path.join(VIDEO_DIR, filename)
    r = requests.get(selected_url, stream=True)
    with open(video_path, "wb") as f:
        shutil.copyfileobj(r.raw, f)

    # Store initial job info
    jobs[job_id] = {
        "status": "processing",
        "video_path": video_path,
        "progress": 0
    }

    # Simulate processing progress in a background-like way
    for i in range(1, 6):
        time.sleep(1)  # simulate work
        jobs[job_id]["progress"] = i * 20
    jobs[job_id]["status"] = "completed"

    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def check_status(job_id: str):
    """
    Check the status and progress of a job.
    """
    job = jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Job not found"}, status_code=404)
    return {
        "status": job["status"],
        "progress": job.get("progress", 0)
    }


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    """
    Download the completed generated video.
    """
    job = jobs.get(job_id)
    if not job or job["status"] != "completed":
        return JSONResponse({"error": "Job not ready"}, status_code=400)
    return FileResponse(job["video_path"], media_type="video/mp4", filename="generated.mp4")


@app.get("/")
async def root():
    return {"message": "Mock AI Video Generator API running"}
