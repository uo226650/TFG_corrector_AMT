import logging
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from .excepciones_entrada import (
    AudioDurationError,
    AudioFormatError,
    AudioNotFoundError,
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

    Returns:
        Tupla (audio, sr). Audio es un ndarray y sr la frecuencia de muestreo real tras la carga.
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


def _get_audio_info(ruta: Path) -> sf._SoundFileInfo:
    """
    Obtiene metadatos del audio sin cargar el contenido completo.

    Utiliza soundfile para leer solo la cabecera.

    Args:
        ruta: Ruta al archivo de audio.

    Returns:
        Objeto SoundFileInfo.

    Raises:
        AudioFormatError: si el formato no es reconocido por libsndfile (ej. .txt renombrado a .wav)
        o no es soportado por la canalización (ej. .aiff soportado por libsndfile pero no por el sistema).

    """
    try:
        info = sf.info(ruta)
    except RuntimeError as e:
        raise AudioFormatError(f"Formato incorrecto o corrupto: {e} - {ruta}") from e

    if info.format not in FORMATOS_SOPORTADOS:
        raise AudioFormatError(f"Formato de audio {info.format} no soportado")
    return info


def _validar_duración(info: sf._SoundFileInfo, max_seg: float, min_seg: float):
    """
    Valida que la duración del audio esté dentro del rango permitido.

    Args:
        info: Metadatos del audio.
        max_seg: Duración máxima permitida en segundos.
        mix_seg: Duración mínima permitida en segundos.

    Raises:
        AudioDurationError: si info.duration está fuera del rango [min_seg, max_seg].

    """
    if info.duration > max_seg:
        raise AudioDurationError(
            f"Duración {info.duration:.1f}s > máximo {max_seg}s - {info.name}"
        )
    if info.duration < min_seg:
        raise AudioDurationError(
            f"Duración {info.duration:.2f}s < mínimo {min_seg}s - {info.name}"
        )


def _cargar_contenido(ruta: Path, sr: int) -> tuple[np.ndarray, int]:
    """
    Decodifica el contenido del audio.

    Args:
        ruta: Ruta al archivo de audio.
        sr: Frecuencia de muestreo para el resampleo.

    Returns:
        Tupla (audio, sr). Audio es un ndarray y sr la frecuencia de muestreo real tras la carga.

    Raises:
        AudioFormatError: si librosa falla al decodificar el archivo.

    """
    try:
        audio, sr = librosa.load(ruta, sr=sr, mono=True)
        return audio, sr
    except Exception as e:
        raise AudioFormatError(f"Error decodificando audio: {e} - {ruta}") from e


def _validar_no_silencio(audio: np.ndarray, umbral: float):
    """
    Valida si el audio contiene señal útil y no es solo silencio.

    Utiliza librosa para calcular el volumen/energía promedio del audio (Root Mean Square).
    Rango[0-1]: 0.0 = silencio total, 1.0 = audio al máximo

    Args:
        audio: np.ndarray que contiene la señal de audio.
        umbral: volumen mínimo para considerar no silencio.

    Raises:
        AudioSilentError: si el volumen está por debajo del mínimo indicado por el umbral.

    """
    rms = librosa.feature.rms(y=audio).mean()
    if rms < umbral:
        raise AudioSilentError(f"Audio silencioso: RMS={rms:.5f} < {umbral}")
