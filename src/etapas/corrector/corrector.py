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
from src.etapas.corrector.reglas_correccion import (
    ReglaEliminaciónSolapamientos,
    ReglaFusiónPorProximidad,
)

# Crea logger para el módulo corrector
logger = logging.getLogger(__name__)


REGISTRO_REGLAS = {
    "eliminación_solapamientos": ReglaEliminaciónSolapamientos,
    "fusión_proximidad": ReglaFusiónPorProximidad,
    # "otra_regla": ReglaOtra,
}


def corregir_transcripción(
    ts_normalizada: Transcripción, config: GlobalConfig
) -> Transcripción:
    """
    Aplica reglas de corrección a una transcripción:
        - Aplica únicamente reglas activas.
        - Aplica reglas activas secuencialmente.
        - Exporta la transcripción intermedia resultante de aplicar cada regla activa.

    Args:
        ts_normalizada: transcripción en formato interno propuesta para corrección.
        config: configuración del sistema para esta ejecución.

    Returns:
        ts_actual: Transcripción corregida resultante de aplicar todas las reglas activas.

    Raises:
        ReglaNoEncontradaError: Si el nombre no está registrado en REGISTRO_REGLAS.
    """
    config_corrector = config.corrector
    reglas_activas = config_corrector.reglas_activas
    umbrales = config_corrector.umbrales

    logger.info("[CORRECTOR] Corrigiendo transcripción inicial")
    logger.info("[CORRECTOR] Aplicando %d reglas", len(reglas_activas))

    ts_actual = ts_normalizada
    for nombre_regla in reglas_activas:
        try:
            if nombre_regla not in REGISTRO_REGLAS:
                raise ReglaNoEncontradaError(
                    f"La regla '{nombre_regla}' indicada en el YAML no está registrada en el sistema."
                )

            regla_clase = REGISTRO_REGLAS[nombre_regla]
            regla_config = umbrales.get(nombre_regla) or {}
            regla = regla_clase(regla_config)  # Instancia la clase con su cofiguración

            logger.info("[CORRECTOR] Aplicando regla '%s'", nombre_regla)
            ts_actual = regla.aplicar(ts_actual)
            logger.info("[CORRECTOR] Regla '%s' aplicada", nombre_regla)

            # Directorio para guardar la salida
            ts_dirname = config.ruta_ts_corregida / nombre_regla
            os.makedirs(ts_dirname, exist_ok=True)
            ts_regla_ruta = ts_dirname / ts_actual.ruta_origen.name
            # Exportar transcripción intermedia
            ts_actual.exportar_a_csv(ts_regla_ruta)
            logger.info(
                "[CORRECTOR] Exportada transcripción (%s) resultante de aplicar la regla '%s'",
                ts_regla_ruta,
                nombre_regla,
            )
        except ReglaNoEncontradaError as e:
            logger.error(
                "[CORRECTOR] %s Se omitirá esta regla.\nReglas válidas disponibles: %s",
                e,
                list(REGISTRO_REGLAS.keys()),
            )

    # TODO: fuera del for, guardar transcripción corregida ts_actual (la resultante de aplicar todas las reglas activas)
    return ts_actual


class ReglaNoEncontradaError(Exception):
    """Se lanza cuando el nombre de la regla no está registrado."""
