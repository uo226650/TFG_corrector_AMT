"""
Encapsula la herramienta externa AMT.

Solicita y proporciona la transcripción inicial de un audio vocal monofónico.
"""

import os
import sys
import logging
import csv

from pathlib import Path
from typing import Protocol

from logger_config import capturar_prints
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
from src.dominio.transcripción import Transcripción, Nota

DEFAULT_AMT_ADAPTER = "basicpitch"

# Crea logger para el adaptador AMT externo
logger = logging.getLogger(__name__)


# Strategy Interface
class AdaptadorAMT(Protocol):
    nombre: str

    # Strategy
    def transcribir(self, ruta_audio: Path, ruta_salida: Path) -> Transcripción: ...
    # Adapter
    def csv_a_ts(self, ruta_csv: Path) -> Transcripción: ...


class AdaptadorBasicPitch:
    nombre = "basic_pitch"

    def transcribir(self, ruta_audio: Path, ruta_salida: Path) -> Path:
        try:
            with capturar_prints(logger, f"[{self.nombre}]"):
                predict_and_save(
                    audio_path_list=[ruta_audio],
                    output_directory=ruta_salida,
                    save_midi=False,  # Cambiar a True (Requisito sistema: RTranscripciónInicial)
                    sonify_midi=False,
                    save_model_outputs=False,  # Para guardar el .npz
                    save_notes=True,  # Para guardar el .csv
                    model_or_model_path=ICASSP_2022_MODEL_PATH,
                )
        except Exception as e:
            logger.error("[ADAPTADOR_AMT] %s ha lanzado: %s", self.nombre, e)

        # Carga la ruta del csv generado
        stem = ruta_audio.stem
        ruta_csv = ruta_salida / f"{stem}_{self.nombre}.csv"

        # Verifica que existe
        if not ruta_csv.exists():
            raise FileNotFoundError(
                f"Basic Pitch no generó el csv: {ruta_csv}"
            )  # para test usar predict_save con save_notes=False

        return ruta_csv

    def csv_a_ts(self, ruta_csv: Path) -> Transcripción:

        with open(ruta_csv, newline="", encoding="utf-8") as ts_inicial:
            notas = []
            reader = csv.reader(ts_inicial)
            next(reader)
            for row in reader:
                start_time = float(row[0])
                end_time = float(row[1])
                pitch_midi = int(row[2])
                notas.append(
                    Nota(
                        pitch=pitch_midi,
                        onset=start_time,
                        offset=end_time,
                        duración=end_time - start_time,
                        fuente=self.nombre,
                    )
                )
        return Transcripción(eventos=notas)


# class AdaptadorOtroAMT:
#     nombre = "otroAMT"

#     def transcribir(self, ruta_audio: Path, ruta_salida: Path) -> Transcripción:
#         { lógica del nuevo AMT }


REGISTRO_ADAPTADORES = {
    "basicpitch": AdaptadorBasicPitch()
    # "nuevoAMT": AdaptadorOtroAMT(),
}


class AdaptadorNoEncontradoError(Exception):
    """Se lanza cuando el nombre del adaptador no está registrado"""

    pass


def _obtener_adaptador_amt(nombre: str) -> AdaptadorAMT:  # Factory
    """
    Raises:
        AdaptadorNoEncontradoError: Si el nombre no está registrado
    """
    try:
        adaptador = REGISTRO_ADAPTADORES[nombre.lower()]
    except KeyError:
        adaptadores_validos = ",".join(REGISTRO_ADAPTADORES.keys())
        raise AdaptadorNoEncontradoError(
            f"[ADAPTADOR_AMT] Adaptador '{nombre}' no encontrado. Válidos: {adaptadores_validos}"
        )

    return adaptador


def transcribir_audio(ruta_archivo: Path, adaptador: str):
    """
    Transcribe el archivo de entrada:

        - Verifica la existencia del adaptador AMT. En caso de no encontrar el adaptador solicitado utiliza el adaptador por defecto.
        - Solicita la transcripción automática

    Args:
        ruta: Ruta al archivo de audio.
        adaptador: Nombre de la herramienta AMT a utilizar

    Returns:
        ts_inicial: Transcripción automática inicial cruda
        adaptador_amt: Nombre de la herramienta AMT que ha proporcionado esa transcripción ts_incial
    """
    logger.info("[ADAPTADOR_AMT] Transcribiendo con AMT externa")

    try:
        adaptador_amt = _obtener_adaptador_amt(adaptador)
    except AdaptadorNoEncontradoError as e:
        logger.critical(e)
        adaptador_amt = REGISTRO_ADAPTADORES[DEFAULT_AMT_ADAPTER]  # default
        logger.info(
            "[ADAPTADOR_AMT] Ejecutando adaptador por defecto: %s",
            adaptador_amt.nombre,
        )

    # Directorio para guardar la salida
    ts_dirname = f"data/ts_inicial/{adaptador_amt.nombre}"
    os.makedirs(ts_dirname, exist_ok=True)

    try:
        ts_inicial_ruta = adaptador_amt.transcribir(
            ruta_archivo, Path(ts_dirname)
        )  # Método. No detecta estáticamente la falta de argumentos
        return ts_inicial_ruta, adaptador_amt
    except FileNotFoundError as e:
        logger.critical("[ADAPTADOR_AMT] %s.", e)
        logger.critical("Detenido el proceso de transcripción")
        sys.exit(1)
