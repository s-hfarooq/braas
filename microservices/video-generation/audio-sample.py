import torch
from TTS.api import TTS

# Get device
device = "mps"

print("init")
# Init TTS with the target model name
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to(device)

print("run")
# Run TTS
tts.tts_to_file(text="This is a test.", file_path="./sample.mp3")
