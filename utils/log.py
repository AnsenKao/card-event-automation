import logging
from datetime import datetime
import os

# 建立 log 檔案儲存資料夾（例如 logs/）
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 啟動時固定 timestamp
RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOG_DIR, f"submit_{RUN_TIMESTAMP}.log")

def setup_logger(name=__name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # 加入 level 與訊息內容
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
