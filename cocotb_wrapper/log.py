import os
import logging
logging.basicConfig()


logging.root.setLevel(level=logging.WARNING)
log_level = os.environ.get("TB_LOG_LEVEL")
if log_level != None: 
    log_level = log_level.upper()
    if log_level in logging._nameToLevel:
        logging.root.setLevel(level=logging._nameToLevel[log_level])
