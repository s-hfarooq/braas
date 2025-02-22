from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import requests
import logging
from urllib.parse import urlencode
import webbrowser
from typing import Optional
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicAuth:
    def __init__(self, port: int = 9000):
        self.client_id = "a9cf1e85-1cb1-461e-9c04-fcb5e0908369"
        self.port = port
        self.redirect_uri = f"http://localhost:{port}/callback"
        self.auth_url = "https://api.basic.tech/auth/authorize"
        self.token_url = "https://api.basic.tech/auth/token"
        self.scope = "read write"
        
        # Initialize FastAPI app for handling callback
        self.app = FastAPI()
        self.setup_routes()
        self.access_token: Optional[str] = None
        
    def setup_routes(self):
        @self.app.get("/login")
        async def login():
            """Initiate the OAuth2 flow by redirecting to Basic.tech's auth page"""
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': self.scope
            }
            auth_url = f"{self.auth_url}?{urlencode(params)}"
            logger.info(f"Redirecting to auth URL: {auth_url}")
            return RedirectResponse(auth_url)
            
        @self.app.get("/callback")
        async def callback(code: str):
            """Handle the OAuth2 callback and exchange code for token"""
            logger.info("Received callback with authorization code")
            try:
                # Exchange the authorization code for an access token
                token_data = {
                    'client_id': self.client_id,
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': self.redirect_uri
                }
                
                response = requests.post(self.token_url, data=token_data)
                response.raise_for_status()
                
                token_info = response.json()
                self.access_token = token_info['access_token']
                logger.info("Successfully obtained access token")
                
                return {"message": "Authentication successful!", "token": self.access_token}
                
            except Exception as e:
                logger.error(f"Error exchanging code for token: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    def start_auth_flow(self):
        """Start the authentication flow by opening the browser"""
        auth_url = f"http://localhost:{self.port}/login"
        logger.info(f"Opening browser for authentication at port {self.port}...")
        webbrowser.open(auth_url)
        
        # Start the FastAPI server
        uvicorn.run(self.app, host="localhost", port=self.port)

    def get_token(self) -> Optional[str]:
        """Get the current access token"""
        return self.access_token

if __name__ == "__main__":
    # Example usage
    auth = BasicAuth(port=9000)
    auth.start_auth_flow() 