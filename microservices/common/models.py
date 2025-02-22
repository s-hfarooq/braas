from pydantic import BaseModel, Field
from typing import Dict, Any, Generic, TypeVar
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

class VideoData(BaseModel):
    """Model for video data including the ID"""
    id: str
    value: VideoBase

class VideoResponse(BaseModel):
    """Model for Basic.tech API response containing video data"""
    data: VideoData

class PromptBase(BaseModel):
    """Base model for prompt data"""
    topic: str
    output: str
    top_text: str
    bottom_text: str
    metadata: Dict[str, Any] = Field(default_factory=lambda: {
        "generated_at": datetime.now().isoformat(),
        "model": "llama3.2:3b"
    })

class PromptCreate(PromptBase):
    """Model for creating a new prompt"""
    pass

class PromptData(BaseModel):
    """Model for prompt data including the ID"""
    id: str
    value: PromptBase

class PromptResponse(BaseModel):
    """Model for Basic.tech API response containing prompt data"""
    data: PromptData 