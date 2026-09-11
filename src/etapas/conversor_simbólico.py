"""
Etapa 3. Conversor Simbólico
Transforma la salida de la herramienta AMT a un modelo común.
"""  # noqa: N999

import csv
import logging
import os
from dataclasses import asdict, fields
from pathlib import Path

from src.dominio.nota import Nota
from src.dominio.transcripción import Transcripción
from src.etapas.adaptador_amt import AdaptadorAMT

# Crea logger para el conversor simbólico
logger = logging.getLogger(__name__)


def convertir_formato(ts_inicial_ruta: Path, adaptador: AdaptadorAMT) -> Transcripción:
    """
    Normaliza una transcripción bruta al formato interno:
        - Ordena eventos por onset, si dos eventos tienen el mismo onset ordena por pitch
        - Reasigna identificadores secuenciales
        - Exporta artefacto intermedio a csv para permitir el análisis y revisión manual
    Args:
        ts_inicial: ruta de la transcripción (csv) bruta a procesar
        adaptador: Nombre de la herramienta AMT que proporciona ts_inicial

    Returns:
        ts_normalizada: Transcripción normalizada al formato interno
    """

    logger.info("[CONVERSOR] Conviertiendo tabla %s a formato interno", ts_inicial_ruta)
    # Normaliza a formato interno
    notas_inicial = adaptador.csv_a_notas(ts_inicial_ruta)

    if not notas_inicial:
        logger.warning("[CONVERSOR] %s contiene 0 notas válidas", ts_inicial_ruta)

    # Ordena eventos
    notas_ordenadas = sorted(notas_inicial, key=lambda n: (n.onset, n.pitch))

    # Reasigna identificadores
    for idx, nota in enumerate(notas_ordenadas):
        nota.identificador = idx + 1

    # Genera estructura interna
    ts_normalizada = Transcripción(notas=notas_ordenadas, ruta_origen=ts_inicial_ruta)

    # Directorio para guardar la salida
    ts_dirname = f"data/ts_normalizada/{adaptador.nombre}"
    os.makedirs(ts_dirname, exist_ok=True)
    ts_normalizada_ruta = f"{ts_dirname}/{ts_inicial_ruta.name}"

    # Exporta a csv
    columnas = _exportar_trancripción_csv(ts_normalizada, ts_normalizada_ruta)

    # Registra datos de la etapa
    logger.info(
        "[CONVERSOR] Exportación completada -> %s\n"
        " - Notas totales: %s \n"
        " - Atributos por nota: %s\n"
        " - Rango temporal: %.2fs - %.2fs (longitud: %.2fs)| Duración sonora: %.2fs\n"
        " - Rango de pitch: %s - %s MIDI\n",
        ts_normalizada_ruta,
        ts_normalizada.num_notas,
        ", ".join(columnas),
        ts_normalizada.inicio,
        ts_normalizada.fin,
        ts_normalizada.duración_toma,
        ts_normalizada.duración_sonora,
        ts_normalizada.pitch_min,
        ts_normalizada.pitch_max,
    )


def _exportar_trancripción_csv(ts: Transcripción, ruta_salida: Path):
    """
    Exporta una Transcripción (en formato interno) a CSV.
        - Una fila por cada Nota
    """
    if not ts.notas:
        logger.warning("[CONVERSOR] Exportando transcripción vacía: %s", ruta_salida)
        columnas = [f.name for f in fields(Nota)]
        with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
        return columnas

    columnas = [f.name for f in fields(ts.notas[0])]
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()

        for nota in ts.notas:
            writer.writerow(asdict(nota))
    return columnas
