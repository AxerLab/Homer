import logging
import sys
from ecs_logging import StdlibFormatter
import colorlog

# Create the logger
logger = logging.getLogger("my-app")
logger.setLevel(logging.DEBUG)

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

# ===== ECS JSON Logs (for ELK/APM) =====
ecs_handler = logging.FileHandler("ecs-logs.json")
ecs_handler.setLevel(logging.INFO)
ecs_handler.setFormatter(StdlibFormatter())

# ===== Add Handlers to Logger =====
logger.addHandler(console_handler)
logger.addHandler(ecs_handler)

# ===== Test Logs =====
# logger.debug("Debug message")
# logger.info("User login", extra={"user": {"name": "alice"}})
# logger.warning("Disk space low")
# logger.error("Something went wrong")
