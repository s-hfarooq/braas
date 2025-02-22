# from diffusers import DiffusionPipeline

# pipe = DiffusionPipeline.from_pretrained("rhymes-ai/Allegro")
# pipe = pipe.to("mps")
# pipe.enable_attention_slicing()

# prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
# image = pipe(prompt).images[0]
# print(type(image))

# from diffusers import DiffusionPipeline

# pipe = DiffusionPipeline.from_pretrained("ali-vilab/text-to-video-ms-1.7b")
# pipe = pipe.to("mps")
# pipe.enable_attention_slicing()

# prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
# image = pipe(prompt).images[0]
# image.show()  # This will display the image in your default image viewer




import torch
from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video
import numpy as np
from PIL import Image

pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b", torch_dtype=torch.float16, variant="fp16")
pipe = pipe.to("mps")
# pipe.enable_attention_slicing()
# pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
# pipe.enable_model_cpu_offload()

prompt = "Spiderman is surfing"
video_frames = pipe(prompt, num_inference_steps=10).frames[0]

print(video_frames)

# video_frames = pipe(prompt, num_inference_steps=25).frames
# video_frames = [np.array(frame) for frame in video_frames[0]]
video_path = export_to_video(video_frames)
print(video_path)


