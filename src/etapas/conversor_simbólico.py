"""
Transforma la salida de la herramienta AMT a un modelo común.
"""

import os
import logging
import csv
from pathlib import Path
from dataclasses import fields, asdict

from src.dominio.transcripción import Transcripción
from src.etapas.adaptador_AMT import AdaptadorAMT

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
    ts_normalizada = adaptador.csv_a_ts(ts_inicial_ruta)

    # Ordena eventos
    notas_ordenadas = sorted(ts_normalizada.eventos, key=lambda n: (n.onset, n.pitch))

    # Reasigna identificadores
    for idx, nota in enumerate(notas_ordenadas):
        nota.identificador = idx + 1

    ts_normalizada.eventos = notas_ordenadas

    # Directorio para guardar la salida
    ts_dirname = f"data/ts_normalizada/{adaptador.nombre}"
    os.makedirs(ts_dirname, exist_ok=True)
    ts_normalizada_ruta = f"{ts_dirname}/{ts_inicial_ruta.name}"

    # Exporta a csv
    columnas = _exportar_trancripción_csv(ts_normalizada, ts_normalizada_ruta)

    # Registra datos de la etapa
    _extraer_características(ts_normalizada, columnas, ts_normalizada_ruta)


def _extraer_características(
    ts: Transcripción, columnas: list[str], ts_normalizada_ruta: Path
):
    notas = ts.eventos
    total = len(notas)
    duración_total = sum(n.offset - n.onset for n in notas) if total else 0.0
    pitch_min = min((n.pitch for n in notas), default=0)
    pitch_max = max((n.pitch for n in notas), default=0)
    inicio = min(n.onset for n in notas) if total else 0.0
    fin = max(n.offset for n in notas) if total else 0.0
    duración_toma = fin - inicio
    # TODO: WARNING si duración_sonora (suma de todas las duraciones de las notas) > duración_toma (total de sonoridad desde que empieza primera nota hasta que acaba la última)

    logger.info(
        "[CONVERSOR] Exportación completada -> %s\n"
        " - Notas totales: %s \n"
        " - Atributos por nota: %s\n"
        " - Rango temporal: %.2fs - %.2fs (longitud: %.2fs)| Duración sonora: %.2fs\n"
        " - Rango de pitch: %s - %s MIDI\n",
        ts_normalizada_ruta,
        total,
        ", ".join(columnas),
        inicio,
        fin,
        duración_toma,
        duración_total,
        pitch_min,
        pitch_max,
    )


def _exportar_trancripción_csv(ts: Transcripción, ruta_salida: Path):
    """
    Exporta una Transcripción (en formato interno) a CSV.
        - Una fila por cada Nota
    """
    # TODO: exceptions
    # Exporta a csv
    columnas = [f.name for f in fields(ts.eventos[0])]
    with open(ruta_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()

        for nota in ts.eventos:
            writer.writerow(asdict(nota))
        return columnas
