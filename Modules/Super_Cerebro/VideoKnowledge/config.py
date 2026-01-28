# ==================== CONFIGURATION ====================
import logging

API_BASE = "http://localhost:8000"
DEFAULT_INTERVAL = 5  # seconds between frames
DEFAULT_OUTPUT = r"c:\Users\user\Desktop\ONIV24\Modules\Super_Cerebro\estudos_temporario"
DEFAULT_LANGUAGE = "pt"
WHISPER_MODEL = "medium"

# Timeouts and Retries
MAX_RETRIES = 3
INITIAL_TIMEOUT = 60  # seconds
RETRY_BACKOFF = 2  # exponential multiplier
HEALTH_CHECK_TIMEOUT = 10

# Batch sizes
BATCH_SIZE = 5
RATE_LIMIT_DELAY = 0.3  # seconds between batches

# Logging Configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s │ %(levelname)-7s │ %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()
