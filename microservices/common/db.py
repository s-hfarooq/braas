from typing import Dict, Any, Tuple
import requests
from fastapi import HTTPException
import os
import json
from pathlib import Path

class BasicDB:
    @staticmethod
    def _load_credentials() -> Tuple[str, str]:
        """
        Load Basic.tech credentials from secrets.json or environment variables.
        Returns a tuple of (project_id, api_key).
        
        Raises:
            RuntimeError: If credentials cannot be loaded or are invalid
        """
        # First try environment variables
        project_id = os.getenv("BASIC_PROJECT_ID")
        api_key = os.getenv("BASIC_API_KEY")
        
        # If environment variables are not set, try secrets.json
        if not project_id or not api_key:
            try:
                secrets_path = Path("/app/secrets.json")
                with open(secrets_path) as f:
                    secrets = json.load(f)
                    project_id = secrets.get("basic_project_id", "").split('/')[-1]
                    api_key = secrets.get("basic_api_key")
            except (FileNotFoundError, json.JSONDecodeError, AttributeError) as e:
                raise RuntimeError(f"Failed to load secrets.json and no environment variables set: {str(e)}")

        if not project_id or not api_key:
            raise RuntimeError("Missing required Basic.tech credentials")
            
        return project_id, api_key

    def __init__(self):
        # Load credentials using the helper function
        self.project_id, self.api_key = self._load_credentials()
        self.base_url = f"https://api.basic.tech/account/{self.project_id}/db"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def store_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a prompt in the Basic.tech database."""
        url = f"{self.base_url}/prompts"
        payload = {"value": prompt_data}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to store prompt in database: {str(e)}")

    async def store_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a video in the Basic.tech database."""
        url = f"{self.base_url}/video"
        payload = {"value": video_data}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to store video in database: {str(e)}")

    async def get_prompts(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Retrieve prompts from the Basic.tech database."""
        url = f"{self.base_url}/prompts"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve prompts from database: {str(e)}")

    async def get_videos(self, limit: int = 10) -> list[Dict[str, Any]]:
        """Retrieve videos from the Basic.tech database."""
        url = f"{self.base_url}/video"
        params = {"limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve videos from database: {str(e)}")

# Create a singleton instance
db = BasicDB() 