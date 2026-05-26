#!/usr/bin/env python3
"""
统一日志配置模块
"""

import logging
import sys
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器（仅终端输出时使用）"""

    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m",
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logging(
    level="INFO",
    log_file=None,
    log_dir=None,
    use_colors=True,
    name=None,
):
    """
    统一日志配置函数

    参数：
        level: 日志级别
        log_file: 日志文件名，指定则同时写入文件
        log_dir: 日志目录，未指定时使用 data/logs/
        use_colors: 是否使用彩色输出
        name: logger 名称，未指定时使用根 logger
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    if use_colors and sys.stdout.isatty():
        formatter = ColoredFormatter(log_format, datefmt=date_format)
    else:
        formatter = logging.Formatter(log_format, datefmt=date_format)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        if log_dir:
            log_path = Path(log_dir)
        else:
            from app.utils.paths import Paths

            log_path = Paths.data() / "logs"

        log_path.mkdir(parents=True, exist_ok=True)
        log_file_path = log_path / log_file

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(
            logging.Formatter(log_format, datefmt=date_format)
        )
        logger.addHandler(file_handler)

    return logger


def setup_production_logging():
    """生产环境日志配置"""
    return setup_logging(level="INFO", log_file="app.log", use_colors=False)


def setup_debug_logging():
    """调试环境日志配置"""
    return setup_logging(level="DEBUG", log_file="debug.log")


def setup_training_logging():
    """训练脚本日志配置"""
    return setup_logging(level="INFO", log_file="training.log")
