"""
Fixtures globales para todos los tests del proyecto.
Genera archivos de audio de forma programática, garantizando reproducibilidad.
"""

import pytest
import numpy as np
import soundfile as sf
from enum import Enum
from src.etapas.gestor_entrada.validadores_entrada import (
    FORMATOS_SOPORTADOS,
    SR,
    MIN_DURACION,
    MAX_DURACION,
)

FORMATOS_GENERABLES = [f for f in FORMATOS_SOPORTADOS if f != "M4A"]


class TipoAudio(Enum):
    VALIDO = "valido"
    CORTO = "corto"
    LARGO = "largo"
    SILENCIOSO = "silencioso"


def _factory_audio_duración(tipo: TipoAudio):
    """Genera audio con tono 440Hz, frecuencia de muestreo 22050Hz
    y duración variable (determinada por argumento)."""
    duraciones = {
        TipoAudio.VALIDO: (MIN_DURACION + MAX_DURACION) / 2,
        TipoAudio.CORTO: MIN_DURACION / 2,
        TipoAudio.LARGO: MAX_DURACION * 2,
        TipoAudio.SILENCIOSO: (MIN_DURACION + MAX_DURACION) / 2,
    }

    audio_duración = duraciones[tipo]
    num_muestras = int(SR * audio_duración)

    if tipo == TipoAudio.VALIDO:
        t = np.linspace(0, audio_duración, num_muestras, endpoint=False)
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
    elif tipo == TipoAudio.CORTO or tipo == TipoAudio.SILENCIOSO:
        audio = np.zeros(num_muestras)
    elif tipo == TipoAudio.LARGO:
        audio = np.random.randn(num_muestras) * 0.1

    return audio.astype(np.float32)


def _factory_audio_formato(tmp_path, audio, formato: str, nombre: str):
    """Escribe archivos de audio en distintos formatos"""
    path = tmp_path / f"{nombre}.{formato}"
    try:
        sf.write(path, audio, SR, format=formato.upper())
    except RuntimeError as e:
        pytest.skip(f"Formato {formato} no soportado: {e}")
    return path


######### ────────── Fixtures de Audio ────────── #############

#############################################
###     Fixtures de Audio VALIDO         ####
#############################################


# ── Audio en distintos FORMATOS, duración VÁLIDA ──#
@pytest.fixture(scope="session", params=FORMATOS_GENERABLES)
def audio_formatos_soportados(request, tmp_path_factory):
    """Audio con tono 440Hz, frecuencia de muestreo 22050Hz
    y duración 2 seg y formato soportado"""
    tmp = tmp_path_factory.mktemp("formatos")
    audio = _factory_audio_duración(TipoAudio.VALIDO)
    return _factory_audio_formato(tmp, audio, request.param, "valido")


@pytest.fixture
def audio_m4a_renombrado(tmp_path):
    """El sistema soporta m4a pero soundfile no puede crearlo (solo lee, no escribe).
    Para test se crea un wav renombrado a m4a con el fin de no añadir nuevas dependencias"""

    path = tmp_path / "testRenombrado.m4a"
    audio = _factory_audio_duración(TipoAudio.VALIDO)
    try:
        sf.write(path, audio, SR, format="WAV")
    except RuntimeError as e:
        pytest.skip(f"Formato no soportado: {e}")
    return path


#############################################
###     Fixtures de Audio ERROR          ####
#############################################


# ── ERROR de Audio en distintos FORMATOS, duración VÁLIDA ──#
@pytest.fixture(scope="session", params=["aiff", "voc", "avr"])
def audio_formatos_no_soportados(request, tmp_path_factory):
    tmp = tmp_path_factory.mktemp("formatos")
    audio = _factory_audio_duración(TipoAudio.VALIDO)
    return _factory_audio_formato(tmp, audio, request.param, "valido")


# ── ERROR de DURACIÓN del Audio, formato VÁLIDO ──#
@pytest.fixture
def audio_corto(tmp_path_factory):
    """WAV de 0.1s (por debajo del mínimo de 0.5s)."""
    tmp = tmp_path_factory.mktemp("audio")
    audio = _factory_audio_duración(TipoAudio.CORTO)
    return _factory_audio_formato(tmp, audio, "wav", "corto")


@pytest.fixture
def audio_largo(tmp_path_factory):
    """WAV de 180s (supera límite por defecto de 120s)."""
    tmp = tmp_path_factory.mktemp("audio")
    audio = _factory_audio_duración(TipoAudio.LARGO)
    return _factory_audio_formato(tmp, audio, "wav", "largo")


# ── ERROR de CONTENIDO del Audio, formato y duración VÁLIDOS ──#
@pytest.fixture
def audio_silencioso(tmp_path_factory):
    """WAV de 2s completamente silencioso (amplitud 0)."""
    tmp = tmp_path_factory.mktemp("audio")
    audio = _factory_audio_duración(TipoAudio.SILENCIOSO)
    return _factory_audio_formato(tmp, audio, "wav", "silencioso")


@pytest.fixture
def audio_corrupto(tmp_path):
    """Archivo con extensión .wav pero contenido de texto."""
    ruta = tmp_path / "test_corrupto.wav"
    ruta.write_text("esto no es un audio wav")
    return ruta


@pytest.fixture
def archivo_no_audio(tmp_path):
    """Archivo de texto plano."""
    ruta = tmp_path / "texto.txt"
    ruta.write_text("contenido de texto")
    return ruta
