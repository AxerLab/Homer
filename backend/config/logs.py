import logging
import sys
import colorlog
from dotenv import load_dotenv
import os

load_dotenv()

# Create the logger
logger = logging.getLogger("my-app")
log_level = os.getenv("LOGGING", "INFO").upper()
if log_level == "DEBUG":
    logger.setLevel(logging.DEBUG)
elif log_level == "INFO":
    logger.setLevel(logging.INFO)
elif log_level == "WARNING":
    logger.setLevel(logging.WARNING)
elif log_level == "ERROR":
    logger.setLevel(logging.ERROR)

# ===== Terminal Pretty (Colored) Logs =====
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s[%(levelname)s]%(reset)s %(message)s",
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(color_formatter)


# ===== Add Handlers to Logger =====
logger.addHandler(console_handler)

# ===== Test Logs =====
# logger.debug("Debug message")
# logger.info("User login", extra={"user": {"name": "alice"}})
# logger.warning("Disk space low")
# logger.error("Something went wrong")
