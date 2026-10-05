"""
Etapa 4. Módulo corrector.
Motor que aplica reglas de corrección sobre la transcripción inicial.
"""
#########################_____CUMPLIR _____##################################################
#### 2.2.1. RTrazabilidad. Se almacenan: transcripción inicial, transcripción corregida
#### y las transcripciones resultantes tras aplicar cada una de las reglas de corrección

import logging
import os

from src.config import GlobalConfig
from src.dominio.transcripción import Transcripción
from src.etapas.corrector.configuracion_correccion import ConfigCorrector
from src.etapas.corrector.reglas_correccion import (
    ReglaEliminaciónSolapamientos,
    ReglaFusiónNotasCortas,
)

# Crea logger para el módulo corrector
logger = logging.getLogger(__name__)


REGISTRO_REGLAS = {
    "eliminación_solapamientos": ReglaEliminaciónSolapamientos(),
    "fusión_notas_cortas": ReglaFusiónNotasCortas(),
    # "otra_regla": ReglaOtra(),
}


def corregir_transcripción(
    ts_normalizada: Transcripción, config: GlobalConfig
) -> Transcripción:
    """
    Aplica reglas de corrección a una transcripción:
        - Aplica únicamente reglas activas
        - Aplica reglas activas secuencialmente

    """
    config_corrector = config.corrector
    reglas_activas = config_corrector.reglas_activas

    logger.info("[CORRECTOR] Corrigiendo transcripción inicial")
    logger.info("[CORRECTOR] Aplicando %d reglas", len(reglas_activas))

    ts_actual = ts_normalizada
    for nombre_regla in reglas_activas:
        regla = REGISTRO_REGLAS[nombre_regla]
        ts_actual = regla.aplicar(ts_actual)
        logger.info("[CORRECTOR] Regla '%s' aplicada", nombre_regla)
        # Directorio para guardar la salida
        ts_dirname = f"data/ts_corregida/{nombre_regla}"
        os.makedirs(ts_dirname, exist_ok=True)
        ts_regla_ruta = f"{ts_dirname}/{ts_actual.ruta_origen.name}"
        # Exportar transcripción intermedia
        ts_actual.exportar_a_csv(ts_regla_ruta)

    # TODO: fuera del for, guardar transcripción corregida ts_actual (la resultante de aplicar todas las reglas activas)
    return ts_actual
