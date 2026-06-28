"""
Encapsula la herramienta externa AMT.

Solicita y proporciona la transcripción inicial de un audio vocal monofónico.
"""

import os
import logging

from pathlib import Path
from logger_config import capturar_prints
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

# Crea logger para el adaptador AMT externo
logger = logging.getLogger(__name__)


def transcribir_audio(ruta: Path):
    logger.info("Transcribiendo con AMT externa")

    # Directorio para guardar la salida
    ts_dirname = "ts_originales"
    os.makedirs(f"data/{ts_dirname}", exist_ok=True)

    with capturar_prints(logger, "[basic-pitch]"):
        predict_and_save(
            audio_path_list=[ruta],
            output_directory=f"data/{ts_dirname}/",
            save_midi=False,
            sonify_midi=False,
            save_model_outputs=True,
            save_notes=True,
            model_or_model_path=ICASSP_2022_MODEL_PATH,
        )
