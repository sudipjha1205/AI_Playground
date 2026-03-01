"""
Centralized logging configuration for AI Playground.
"""
import logging
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Configure and return a named logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            fmt='[%(asctime)s] %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level)
    return logger


def get_logger(name: str) -> logging.Logger:
    return setup_logger(name)
