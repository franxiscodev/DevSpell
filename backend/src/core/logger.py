"""
Sistema de logging estructurado para DevSpell.
"""
import logging
import sys
from typing import Any


def setup_logger(name: str = "devspell") -> logging.Logger:
    """
    Configura y retorna un logger.

    Args:
        name: Nombre del logger

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Handler para consola
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# Logger global
logger = setup_logger()
