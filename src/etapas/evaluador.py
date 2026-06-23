"""
Calcula métricas.
Compara la transcripción inicial con una referencia manual.
Compara la transcripción corregida con una referencia manual.
"""

import logging

# Crea logger para el módulo evaluador
logger = logging.getLogger(__name__)


def _cargar_referencia_manual():
    logger.info("Cargando referencia manual")


def evaluar_transcripciones():
    _cargar_referencia_manual()
    logger.info("Evaluando las transcripciones")
