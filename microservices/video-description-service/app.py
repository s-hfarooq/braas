from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ollama import chat
from ollama import ChatResponse
import uvicorn
from typing import Dict, Any, Optional, Tuple, Literal
import json
import datetime
import os
from pathlib import Path
import logging
from common.db import db
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Video Description Generator",
    description="A service that generates video descriptions based on keywords",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Base Models
class VideoBase(BaseModel):
    prompt: str
    description: str
    content: str
    metadata: Dict[str, Any]

class VideoCreate(VideoBase):
    pass

class Video(VideoBase):
    id: str

class PromptBase(BaseModel):
    topic: str
    output: str
    top_text: str
    bottom_text: str
    metadata: Dict[str, Any]

class PromptCreate(PromptBase):
    pass

class Prompt(PromptBase):
    id: str

# Request Models
class GenerateRequest(BaseModel):
    topic: str

class GenerateResponse(BaseModel):
    result: str

SYSTEM_PROMPT = """
You are tasked with describing what is happening in a video based on a given keyword. When given a keyword, you should describe a typical video that would be found when searching for that keyword on social media platforms.

Here is the keyword:
<video_topic>
{{VIDEO_TOPIC}}
</video_topic>

To create the video description:
1. Consider what type of video content is commonly associated with this keyword
2. Describe the main visual elements and actions that would typically appear in such a video
3. Mention any key characters or subjects that are commonly featured
4. Describe the sequence of events in chronological order
5. Include relevant details about the setting or environment
6. Keep the description between 2-4 sentences long
7. Generate appropriate meme text that would appear at the top and bottom of the video

Your output should be in the following JSON format:

<output_format>
{
    "videoDescription": "Your scene-by-scene description goes here",
    "topText": "Text that would appear at the top of the video",
    "bottomText": "Text that would appear at the bottom of the video"
}
</output_format>

Focus on describing what would be actually visible and happening in the video, as if you were explaining the scene to someone who cannot see it. The top and bottom text should follow common meme formats and humor styles associated with the keyword. Write your final output in the JSON format specified above, ensuring it is properly formatted. Omit tags in your response. Output ONLY the JSON.
"""

@app.post("/generate", response_model=GenerateResponse)
async def generate_description(request: GenerateRequest):
    logger.info(f"Generating description for topic: {request.topic}")
    try:
        # Replace the placeholder in the system prompt
        formatted_prompt = SYSTEM_PROMPT.replace("{{VIDEO_TOPIC}}", request.topic)
        
        # Get response from Ollama
        response = chat(model='llama3.2:3b', messages=[
            {
                'role': 'system',
                'content': formatted_prompt,
            },
            {
                'role': 'user',
                'content': request.topic,
            },
        ])
        
        # Print response for debugging
        print("Ollama Response:", response)
        response_content = response["message"]["content"]
        print(json.dumps(response_content, indent=4))
    
            
        content = json.loads(response_content)
        
        # Create prompt data
        prompt_data = {
            "topic": request.topic,
            "output": content["videoDescription"],
            "top_text": content["topText"],
            "bottom_text": content["bottomText"],
            "metadata": {
                "generated_at": str(datetime.datetime.now()),
                "model": "llama3.2:1b"
            }
        }
        
        # Store in database using the common db module
        logger.info(f"Storing prompt in database: {prompt_data}")
        await db.store_prompt(prompt_data)
        
        return GenerateResponse(result=json.dumps(content))
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", str(e))
        print("Response Content:", response_content)
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        print("General Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000) 