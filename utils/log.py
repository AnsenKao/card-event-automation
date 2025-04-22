# utils/logging.py
import logging

LOG_FILE = "submit.log"

def setup_logger(name=__name__) -> logging.Logger:
    logger = logging.getLogger(name)

    # 避免重複加 handler（常見陷阱）
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
