import torch
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import Optional
import uuid

app = FastAPI(title="Video Generation API")

class GenerationRequest(BaseModel):
    prompt: str
    num_inference_steps: Optional[int] = 10
    output_format: Optional[str] = "mp4"
    num_frames: Optional[int] = 16

# Determine the best available device
def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

# Initialize the pipeline
device = get_device()
print(f"Using device: {device}")

pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
pipe = pipe.to(device)

if device == "cuda":
    pipe.enable_model_cpu_offload()
    pipe.enable_vae_slicing()

# Create output directory if it doesn't exist
os.makedirs("output", exist_ok=True)

@app.post("/generate")
async def generate_video(request: GenerationRequest):
    try:
        # Generate video frames
        video_frames = pipe(
            prompt=request.prompt,
            num_inference_steps=request.num_inference_steps,
            num_frames=request.num_frames
        ).frames[0]

        # Generate unique filename
        print(video_frames)
        filename = f"output/video_{uuid.uuid4()}.{request.output_format}"
        
        # Export video
        video_path = export_to_video(video_frames, filename)
        
        return {
            "status": "success",
            "message": "Video generated successfully",
            "file_path": video_path,
            "details": {
                "prompt": request.prompt,
                "num_inference_steps": request.num_inference_steps,
                "num_frames": request.num_frames,
                "device_used": device
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
