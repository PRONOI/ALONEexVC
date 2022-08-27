__version__ = "0.1"
# >>> patch : F.11.22

import time
import logging


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGS = logging.getLogger(__name__)
