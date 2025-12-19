import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Central configuration for x-generator."""

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TWITTERAPI_IO_KEY = os.getenv("TWITTERAPI_IO_KEY")

    # X OAuth2 credentials
    X_CLIENT_ID = os.getenv("X_CLIENT_ID")
    X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
    X_REDIRECT_URI = os.getenv("X_REDIRECT_URI", "http://localhost:8000/auth/x/callback")

    # Model Configuration
    BLOG_MODEL = os.getenv("BLOG_MODEL", "claude-3-5-sonnet-20241022")
    SOCIAL_MODEL = os.getenv("SOCIAL_MODEL", "gpt-4-turbo")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # RAG Configuration
    CHROMA_DB_PATH = "./chroma_db"
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    RETRIEVAL_K = 3
    STYLE_EXAMPLES_K = 2

    # Generation parameters
    BLOG_MAX_TOKENS = 2000
    TWEET_MAX_TOKENS = 280
    BLOG_TEMPERATURE = 0.7
    SOCIAL_TEMPERATURE = 0.8

    # Tweet format weights (70/20/10 engagement strategy)
    POST_FORMAT_WEIGHTS = {
        "short": 70,
        "thread": 20,
        "long": 10
    }

    # Format-specific token limits
    SHORT_MAX_TOKENS = 100
    THREAD_MAX_TOKENS = 2000
    LONG_MAX_TOKENS = 2000

    # Scheduler Configuration
    SCHEDULE_ENABLED = os.getenv("SCHEDULE_ENABLED", "true").lower() == "true"
    SCHEDULE_INTERVALS = [int(x) for x in os.getenv("SCHEDULE_INTERVALS", "45,60,90,120").split(",")]
    SCHEDULE_BLACKOUT_START = os.getenv("SCHEDULE_BLACKOUT_START", "23:00")
    SCHEDULE_BLACKOUT_END = os.getenv("SCHEDULE_BLACKOUT_END", "05:00")
    SCHEDULE_TIMEZONE = os.getenv("SCHEDULE_TIMEZONE", "America/New_York")

    # Data paths
    DATA_RAW_DIR = "./data/raw"
    STYLE_EXAMPLES_DIR = "./data/style_examples"
    PROCESSED_DIR = "./data/processed"

    # Stoic virtues
    VIRTUES = ["wisdom", "courage", "justice", "temperance", "general"]

    @staticmethod
    def validate():
        """Validate that required API keys are configured."""
        required_keys = [Config.ANTHROPIC_API_KEY, Config.OPENAI_API_KEY]
        missing = [key for key in required_keys if not key]

        if missing:
            raise ValueError(
                "Missing required API keys. "
                "Please set ANTHROPIC_API_KEY and OPENAI_API_KEY in .env"
            )
