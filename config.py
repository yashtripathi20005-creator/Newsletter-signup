import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Mailchimp configuration
    MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
    MAILCHIMP_AUDIENCE_ID = os.getenv('MAILCHIMP_AUDIENCE_ID')
    MAILCHIMP_SERVER_PREFIX = os.getenv('MAILCHIMP_SERVER_PREFIX')
    
    # Validate required configuration
    @classmethod
    def validate_config(cls):
        """Check if all required environment variables are set."""
        required_vars = [
            'MAILCHIMP_API_KEY',
            'MAILCHIMP_AUDIENCE_ID',
            'MAILCHIMP_SERVER_PREFIX'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please create a .env file based on .env.example"
            )
