from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class VideoBase(BaseModel):
    """Base model for video data"""
    prompt: str
    description: str
    content: str
    metadata: Dict[str, Any]

class VideoCreate(VideoBase):
    """Model for creating a new video"""
    pass

class VideoResponse(VideoBase):
    """Model for video response including the ID"""
    id: str

class PromptBase(BaseModel):
    """Base model for prompt data"""
    topic: str
    output: str
    top_text: str
    bottom_text: str
    metadata: Dict[str, Any] = Field(default_factory=lambda: {
        "generated_at": datetime.now().isoformat(),
        "model": "llama3.2:1b"
    })

class PromptCreate(PromptBase):
    """Model for creating a new prompt"""
    pass

class PromptResponse(PromptBase):
    """Model for prompt response including the ID"""
    id: str 