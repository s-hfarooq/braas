import torch
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from typing import Optional
import uuid
import requests
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import tempfile

app = FastAPI(title="Video Generation API")

class GenerationRequest(BaseModel):
    prompt: str
    num_inference_steps: Optional[int] = 10
    output_format: Optional[str] = "mp4"
    num_frames: Optional[int] = 16
    model_name: Optional[str] = "mistral"  # Ollama model to use
    add_audio: Optional[bool] = True  # Control whether to add TTS audio to the video

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

def generate_script(prompt: str, model_name: str = "mistral") -> str:
    """
    Generate a script using Ollama based on the video content and prompt
    """
    try:
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   "model": model_name,
                                   "prompt": f"Write a short, engaging script for a video about: {prompt}. Keep it concise and natural, around 2-3 sentences. Only have narration and no audio descriptions of events. The text should only have things that should be spoken.",
                                   "stream": False
                               })
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating script: {str(e)}")

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
        filename = f"output/video_{uuid.uuid4()}.{request.output_format}"
        
        # Export video
        video_path = export_to_video(video_frames, filename)
        
        if request.add_audio:
            # Generate script using Ollama
            script = generate_script(request.prompt, model_name=request.model_name)
            
            # Add audio to video
            final_video_path = add_audio_to_video(video_path, script)
        else:
            final_video_path = video_path
            script = ''
        
        return {
            "status": "success",
            "message": "Video generated successfully" + (" with audio" if request.add_audio else ""),
            "file_path": final_video_path,
            "script": script,
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

def add_audio_to_video(video_path, script_text):
    """Add TTS audio to the video"""
    if not script_text or not isinstance(script_text, str):
        print(script_text)
        raise ValueError("Invalid script text for TTS")
        
    # Generate audio from script
    tts = gTTS(text=script_text.strip(), lang='en')
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
        tts.save(temp_audio.name)
        
        # Load video and audio
        video = VideoFileClip(video_path)
        audio = AudioFileClip(temp_audio.name)
        
        # If audio is longer than video, loop the video
        if audio.duration > video.duration:
            # Calculate how many times we need to loop the video
            loop_count = int(np.ceil(audio.duration / video.duration))
            # Create a list of video clips to concatenate
            video_clips = [video] * loop_count
            # Concatenate the video clips
            final_video = concatenate_videoclips(video_clips)
        else:
            final_video = video
            
        # Add audio to video
        final_video = final_video.set_audio(audio)
        
        # Generate output path
        output_path = video_path.replace('.mp4', '_with_audio.mp4')
        
        # Write final video
        final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        # Clean up
        video.close()
        audio.close()
        if audio.duration > video.duration:
            final_video.close()
        os.unlink(temp_audio.name)
        
        return output_path

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
