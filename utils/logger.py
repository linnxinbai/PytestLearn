# utils/logger.py
import logging
import os
from datetime import datetime


def get_logger(name="api_test"):
    """
    实际工作中推荐：单文件日志 + 控制台输出，双 handler
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 避免重复添加 handler（pytest 多次导入时常见坑）
    if logger.handlers:
        return logger

    # 1. 控制台输出（INFO 级别以上）
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    fmt = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    console.setFormatter(fmt)
    logger.addHandler(console)

    # 2. 文件输出（DEBUG 级别以上，按日期命名）
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.now():%Y%m%d}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
