"""
Configuration settings for the simple patent search.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the simple patent search."""
    
    # API Keys
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-4.1"
    OPENAI_TIMEOUT: int = 3600
    
    # Patent Search Settings
    MAX_PATENTS: int = 20
    SIMILARITY_THRESHOLD: float = 0.8
    
    # Web Scraping Settings
    REQUEST_TIMEOUT: int = 15
    REQUEST_DELAY: int = 2
    MAX_RETRIES: int = 3
    
    # Output Settings
    RESULTS_DIR: str = "results"
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    @classmethod
    def get_output_path(cls, compound: str) -> str:
        """Get output file path for a specific compound."""
        import os
        # Create safe filename from compound name
        safe_name = "".join(c for c in compound if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Create results directory if it doesn't exist
        compound_dir = os.path.join(cls.RESULTS_DIR, safe_name)
        os.makedirs(compound_dir, exist_ok=True)
        
        return os.path.join(compound_dir, "verified_patents.json")
