from auth import BasicAuth
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_auth_flow(port: int = 9000):
    """Test the Basic.tech OAuth2 authentication flow"""
    logger.info(f"Starting OAuth2 authentication test on port {port}")
    
    # Initialize the auth handler
    auth = BasicAuth(port=port)
    
    # Start the authentication flow
    # This will open your browser and start a local server
    auth.start_auth_flow()
    
    # After successful authentication, you should see the token
    token = auth.get_token()
    if token:
        logger.info("Authentication successful!")
        logger.info(f"Access token: {token}")
    else:
        logger.error("Failed to obtain access token")

if __name__ == "__main__":
    test_auth_flow(port=9000) 