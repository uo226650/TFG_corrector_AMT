# TODO: validar que el audio es monofónico?

import logging
from pathlib import Path
import soundfile as sf
import librosa
import numpy as np
from .excepciones_entrada import (
    AudioNotFoundError,
    AudioFormatError,
    AudioDurationError,
    AudioSilentError,
)

logger = logging.getLogger(__name__)

FORMATOS_SOPORTADOS = {
    "WAV",
    "FLAC",
    "MP3",
    "OGG",
    "M4A",
}  # Requisito funcional -> 1.1.1.1. RCargarAudio
SR = 22050
MIN_DURACION = 0.5  # segundos
MAX_DURACION = 120  # segundos


def validar_entrada(
    ruta: Path,
    max_duración: float = MAX_DURACION,
    min_duración: float = MIN_DURACION,
    sr_objetivo: int = SR,
    rms_umbral: float = 0.01,
) -> tuple[np.ndarray, int]:
    """
    Valida el archivo de entrada

    Verifica la existencia del archivo, comprueba que contenga audio válido
    y rechaza pistas vacías o que superen los 2 minutos de duración (valor por defecto, parametrizable).

    Args:
        ruta: Ruta al archivo de audio.
        max_duración: Límite de la duración máxima del audio admitida para el procesamiento
        min_duración: Valor mínimo para validar que no se trata de un audio vacío
        sr_objetivo: Sample rate esperado. Para AMT con BasicPitch es 22050Hz. En caso de ser otro resamplea (Input audio maybe be of any sample rate, however, all audio will be resampled to 22050 Hz before processing.)
        rms_umbral: Root Mean Square es el volumen/energía promedio del audio. Rango[0-1]: 0.0 = silencio total, 1.0 = audio al máximo
    """

    logger.debug("[ETAPA 1] Validando header: %s", ruta)

    _validar_archivo_existe(ruta)
    info = _get_audio_info(ruta)
    _validar_duración(info, max_seg=max_duración, min_seg=min_duración)

    logger.debug(
        "[ETAPA 1] Header OK: %.1fs, %dHz -> %dHz, %dch - %s",
        info.duration,
        info.samplerate,
        sr_objetivo,
        info.channels,
        ruta,
    )

    logger.debug("[ETAPA 1] Validando contenido: %s", info.name)
    audio, sr = _cargar_contenido(ruta, sr_objetivo)
    _validar_no_silencio(audio, umbral=rms_umbral)

    logger.debug("[ETAPA 1] Contenido OK: %.1fs", info.duration)
    return audio, sr


def _validar_archivo_existe(ruta: Path):
    if not ruta.is_file():
        raise AudioNotFoundError(f"Archivo no válido o no existe: {ruta}")


# HEADER, sin necesidad de cargar el audio completo
def _get_audio_info(ruta: Path) -> sf._SoundFileInfo:
    try:
        info = sf.info(ruta)
    except (
        RuntimeError
    ) as e:  # Formato no reconocido por libsndfile. Ej. txt renombrado a wav
        raise AudioFormatError(f"Formato incorrecto o corrupto: {e} - {ruta}") from e

    if info.format not in FORMATOS_SOPORTADOS:
        # Formato soportado por libsndfile pero no por mi sistema, Ej. audio.aiff
        raise AudioFormatError(f"Formato de audio {info.format} no soportado")
    return info


def _validar_duración(info: sf._SoundFileInfo, max_seg: float, min_seg: float):
    if info.duration > max_seg:
        raise AudioDurationError(
            f"Duración {info.duration:.1f}s > máximo {max_seg}s - {info.name}"
        )
    if info.duration < min_seg:
        raise AudioDurationError(
            f"Duración {info.duration:.2f}s < mínimo {min_seg}s - {info.name}"
        )


def _cargar_contenido(ruta: Path, sr: int) -> tuple[np.ndarray, int]:
    try:
        audio, sr = librosa.load(ruta, sr=sr, mono=True)
        return audio, sr
    except Exception as e:
        raise AudioFormatError(f"Error decodificando audio: {e} - {ruta}") from e


def _validar_no_silencio(y: np.ndarray, umbral: float):
    rms = librosa.feature.rms(y=y).mean()
    if rms < umbral:
        raise AudioSilentError(f"Audio silencioso: RMS={rms:.5f} < {umbral}")
