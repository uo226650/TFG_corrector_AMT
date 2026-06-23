"""
Encapsula la herramienta externa AMT.
Solicita y proporciona la transcripción inicial de un audio vocal monofónico.
"""

import logging

# Crea logger para el adaptador AMT externo
logger = logging.getLogger(__name__)


def transcribir_audio():
    logger.info("Transcribiendo con AMT externa")
