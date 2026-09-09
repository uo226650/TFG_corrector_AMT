"""
Motor que aplica reglas de corrección sobre la transcripción inicial.
"""
#########################_____CUMPLIR _____##################################################
#### 2.2.1. RTrazabilidad. Se almacenan: transcripción inicial, transcripción corregida
#### y las transcripciones resultantes tras aplicar cada una de las reglas de corrección

import logging

# Crea logger para el módulo corrector
logger = logging.getLogger(__name__)


def corregir_transcripción():
    logger.info("[CORRECTOR] Corrigiendo transcripción inicial")
