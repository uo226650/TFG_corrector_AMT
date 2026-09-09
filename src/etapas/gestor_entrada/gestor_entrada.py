"""
Etapa 1. Gestor de entrada.
Valida que los archivos de audio de entrada presentan
un formato soportado por los siguientes subsistemas de la canalización
"""

import logging
from pathlib import Path

import numpy as np

from .validadores_entrada import validar_entrada

# Crea logger para el gestor de entrada
logger = logging.getLogger(__name__)


def cargar_audio(ruta: Path) -> tuple[np.ndarray, int]:
    logger.info("[GESTOR ENTRADA] Cargando archivo %s", ruta)
    audio, sr = validar_entrada(ruta)
    logger.info("[GESTOR ENTRADA] Cargado con éxito: %s", ruta)
    return audio, sr
