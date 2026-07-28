"""
Configuración centralizada del sistema de logging.

Todos los módulos del proyecto deben obtener el logger
mediante la función get_logger().
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Crea (o recupera) un logger con un formato uniforme.

    Parameters
    ----------
    name : str
        Nombre del módulo que solicita el logger.

    Returns
    -------
    logging.Logger
        Logger configurado.
    """

    logger = logging.getLogger(name)

    # Evita agregar múltiples handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.propagate = False

    return logger