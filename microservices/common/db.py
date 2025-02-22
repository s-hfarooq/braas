from typing import Dict, Any, Tuple, List
import requests
from fastapi import HTTPException
import os
import json
from pathlib import Path
from .models import (
    PromptCreate, PromptResponse, PromptData, PromptBase,
    VideoCreate, VideoResponse, VideoData, VideoBase
)
import logging

logger = logging.getLogger(__name__)

class BasicDB:
    @staticmethod
    def _load_credentials() -> Tuple[str, str, str]:
        """
        Load Basic.tech credentials from secrets.json or environment variables.
        Returns a tuple of (project_id, api_key, jwt).
        
        Raises:
            RuntimeError: If credentials cannot be loaded or are invalid
        """
        # First try environment variables
        project_id = os.getenv("BASIC_PROJECT_ID")
        api_key = os.getenv("BASIC_API_KEY")
        jwt = os.getenv("BASIC_JWT")
        
        # If environment variables are not set, try secrets.json
        if not project_id or not api_key or not jwt:
            try:
                secrets_path = Path("/app/secrets.json")
                with open(secrets_path) as f:
                    secrets = json.load(f)
                    project_id = secrets.get("basic_project_id", "").split('/')[-1]
                    api_key = secrets.get("basic_api_key")
                    jwt = secrets.get("basic_jwt")
            except (FileNotFoundError, json.JSONDecodeError, AttributeError) as e:
                raise RuntimeError(f"Failed to load secrets.json and no environment variables set: {str(e)}")

        if not project_id or not api_key or not jwt:
            raise RuntimeError("Missing required Basic.tech credentials")
            
        return project_id, api_key, jwt

    def __init__(self):
        # Load credentials using the helper function
        self.project_id, self.api_key, self.jwt = self._load_credentials()
        self.base_url = f"https://api.basic.tech/account/{self.project_id}/db"
        self.headers = {
            "Authorization": f"Bearer {self.jwt}",
            "Content-Type": "application/json"
        }

    async def store_prompt(self, prompt_data: PromptCreate) -> PromptBase:
        """Store a prompt in the Basic.tech database."""
        url = f"{self.base_url}/prompts"
        payload = {"value": prompt_data.model_dump()}
        
        try:
            logger.info(f"Sending request to Basic.tech API with payload: {json.dumps(payload, indent=2)}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"Raw Basic.tech API Response: {json.dumps(response_json, indent=2)}")
            
            # Try to parse the response and log each step
            try:
                prompt_response = PromptResponse(**response_json)
                logger.info(f"Parsed PromptResponse: {prompt_response.model_dump_json(indent=2)}")
                prompt_data = prompt_response.data
                logger.info(f"Parsed PromptData: {prompt_data.model_dump_json(indent=2)}")
                prompt_value = prompt_data.value
                logger.info(f"Parsed PromptBase: {prompt_value.model_dump_json(indent=2)}")
                return prompt_value
            except Exception as e:
                logger.error(f"Error during response parsing: {str(e)}")
                logger.error(f"Response structure: {type(response_json)}")
                if isinstance(response_json, dict):
                    logger.error(f"Response keys: {list(response_json.keys())}")
                raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error Response: {e.response.text if hasattr(e, 'response') else str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to store prompt in database: {str(e)}")
        except Exception as e:
            logger.error(f"Validation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

    async def store_video(self, video_data: VideoCreate) -> VideoBase:
        """Store a video in the Basic.tech database."""
        url = f"{self.base_url}/video"
        payload = {"value": video_data.model_dump()}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            response_json = response.json()
            logger.info(f"Basic.tech API Response: {json.dumps(response_json, indent=2)}")
            return VideoResponse(**response_json).data.value
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error Response: {e.response.text if hasattr(e, 'response') else str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to store video in database: {str(e)}")
        except Exception as e:
            logger.error(f"Validation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

    async def get_prompts(self, limit: int = 10) -> List[PromptBase]:
        """Retrieve prompts from the Basic.tech database."""
        url = f"{self.base_url}/prompts"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Basic.tech API Response: {json.dumps(data, indent=2)}")
            
            # Check if data is a list
            if not isinstance(data, list):
                logger.error(f"Expected list response, got {type(data)}")
                raise ValueError(f"Unexpected response format: {data}")
            
            prompts = []
            for item in data:
                try:
                    # Ensure item is a dictionary
                    if not isinstance(item, dict):
                        logger.warning(f"Skipping non-dict item: {item}")
                        continue
                        
                    # Create PromptResponse object
                    prompt_response = PromptResponse(data=PromptData(
                        id=item.get("id", ""),
                        value=PromptBase(
                            topic=item["data"]["value"]["topic"],
                            output=item["data"]["value"]["output"],
                            top_text=item["data"]["value"]["top_text"],
                            bottom_text=item["data"]["value"]["bottom_text"],
                            metadata=item["data"]["value"].get("metadata", {})
                        )
                    ))
                    prompts.append(prompt_response.data.value)
                except KeyError as ke:
                    logger.error(f"Missing required field in item: {ke}")
                    logger.debug(f"Problem item: {json.dumps(item, indent=2)}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing item: {str(e)}")
                    logger.debug(f"Problem item: {json.dumps(item, indent=2)}")
                    continue
            
            return prompts
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error Response: {e.response.text if hasattr(e, 'response') else str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve prompts from database: {str(e)}")
        except Exception as e:
            logger.error(f"Validation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

    async def get_videos(self, limit: int = 10) -> List[VideoBase]:
        """Retrieve videos from the Basic.tech database."""
        url = f"{self.base_url}/video"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Basic.tech API Response: {json.dumps(data, indent=2)}")
            return [VideoResponse(**item).data.value for item in data]
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error Response: {e.response.text if hasattr(e, 'response') else str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve videos from database: {str(e)}")
        except Exception as e:
            logger.error(f"Validation Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

# Create a singleton instance
db = BasicDB() 