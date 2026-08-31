"""
Tests de componente para el gestor de entrada (etapa 1).
Casos: TODO: identificador de los casos de prueba del documento TFG.
"""

import pytest
from pathlib import Path
import numpy as np
import logging

from src.etapas.gestor_entrada.gestor_entrada import cargar_audio
from src.etapas.gestor_entrada.excepciones_entrada import (
    AudioNotFoundError,
    AudioFormatError,
    AudioDurationError,
    AudioSilentError,
)


class TestCargarAudio:
    """Tests para gestor_entrada.cargar_audio()."""

    ERROR_LOG_COUNT = 1  # Número de entradas en el log cuando la etapa ha dado error
    VALIDO_LOG_COUNT = (
        2  # Número de entradas en el log cuando la etapa ha finalizado con éxito
    )

    def test_audio_formatos_admitidos(self, audio_formatos_soportados):
        """TODO: identificador del caso de prueba:
        Audio válido devuelve info y registra dos entradas de log."""

        audio, sr = cargar_audio(audio_formatos_soportados)
        assert isinstance(audio, np.ndarray)
        self._assert_log(self.VALIDO_LOG_COUNT)

    def test_audio_formato_m4a_renombrado(self, audio_m4a_renombrado):
        """TODO: identificador del caso de prueba:
        Audio válido en formato m4a devuelve info y registra dos entradas de log."""

        audio, sr = cargar_audio(audio_m4a_renombrado)
        assert isinstance(audio, np.ndarray)
        self._assert_log(self.VALIDO_LOG_COUNT)

    def test_audio_inexistente(self):
        """TODO: identificador del caso de prueba:
        Archivo no encontrado lanza excepción y registra una entrada de log."""

        ruta = Path("no_existe.wav")

        self._assert_carga_falla_y_log(AudioNotFoundError, ruta)

    def test_archivo_no_audio(self, archivo_no_audio):
        """TODO: identificador del caso de prueba:
        Audio no encontrado (archivo de texto) lanza excepción y registra una entrada de log."""

        self._assert_carga_falla_y_log(AudioFormatError, archivo_no_audio)

    def test_audio_no_soportado(self, audio_formatos_no_soportados):
        """TODO: identificador del caso de prueba:
        Audio en formato no soportado lanza excepción y registra una entrada de log."""

        self._assert_carga_falla_y_log(AudioFormatError, audio_formatos_no_soportados)

    def test_audio_corrupto(self, audio_corrupto):
        """TODO: identificador del caso de prueba:
        Audio corrupto (texto como wav) lanza excepción y registra una entrada de log."""

        self._assert_carga_falla_y_log(AudioFormatError, audio_corrupto)

    def test_audio_demasiado_largo(self, audio_largo):
        """TODO: identificador del caso de prueba:
        Audio de 240s (> 120s default) lanza excepción y registra una entrada de log."""

        self._assert_carga_falla_y_log(AudioDurationError, audio_largo)

    def test_audio_demasiado_corto(self, audio_corto):
        """TODO: identificador del caso de prueba:
        Audio de 0.25s (< 0.5s default) lanza excepción y registra una entrada de log."""
        self._assert_carga_falla_y_log(AudioDurationError, audio_corto)

    def test_audio_silencioso(self, audio_silencioso):
        """TODO: identificador del caso de prueba:
        Audio completamente silencioso lanza excepción y registra una entrada de log."""
        self._assert_carga_falla_y_log(AudioSilentError, audio_silencioso)

    @pytest.fixture(autouse=True)  # Ejecuta antes de cada test
    def _setup_caplog(self, caplog):
        caplog.set_level(logging.INFO)
        self.caplog = caplog

    def _assert_log(self, log_count: int):  # Refactorizado código común
        MENSAJE_ESPERADO = "[GESTOR ENTRADA] Cargando archivo"
        assert len(self.caplog.records) == log_count
        assert MENSAJE_ESPERADO in self.caplog.text
        assert self.caplog.records[0].name == "src.etapas.gestor_entrada.gestor_entrada"

    def _assert_carga_falla_y_log(self, tipo_excepción: Exception, ruta: Path):
        """Helper común a tests de error.
        Carga un audio que falla, lanza excepción y registra una entrada de log"""
        with pytest.raises(tipo_excepción):
            cargar_audio(ruta)

        self._assert_log(self.ERROR_LOG_COUNT)
