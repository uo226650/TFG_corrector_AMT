"""
Tests para el Adaptador AMT (etapa 2).
Casos: TODO: identificador de los casos de prueba del documento TFG.
"""

from unittest.mock import patch

import pytest

from src.etapas.adaptador_amt import (
    DEFAULT_ADAPTADOR_AMT,
    REGISTRO_ADAPTADORES,
    AdaptadorBasicPitch,
    AdaptadorNoEncontradoError,
    _obtener_adaptador_amt,
    transcribir_audio,
)

# ─── Tests Unitarios ──────────────────────────────────────


class TestObtenerAdaptadorAmt:
    def test_nombre_válido_retorna_adaptador(self):
        """TODO: identificador del caso de prueba:
        'basicpitch' retorna instancia de AdaptadorBasicPitch."""

        adaptador = _obtener_adaptador_amt("basicpitch")
        assert isinstance(adaptador, AdaptadorBasicPitch)

    def test_nombre_mayúsculas_retorna_adaptador(self):
        """TODO: identificador del caso de prueba:
        El nombre se convierte a minúsculas."""

        adaptador = _obtener_adaptador_amt("BasicPitch")
        assert isinstance(adaptador, AdaptadorBasicPitch)
        assert adaptador.nombre == AdaptadorBasicPitch.nombre

    def test_nombre_inexistente_lanza_error(self):
        """TODO: identificador del caso de prueba:
        Nombre no registrado lanza AdaptadorNoEncontradoError."""

        with pytest.raises(AdaptadorNoEncontradoError) as exc_info:
            _obtener_adaptador_amt("adaptador_inexistente")
        assert "adaptador_inexistente" in str(exc_info.value)
        assert "basicpitch" in str(exc_info.value)  # Adaptadores válidos


class TestRegistroAdaptadores:
    def test_registro_no_está_vacío(self):
        """TODO: identificador del caso de prueba:
        El registro tiene al menos un adaptador."""

        assert len(REGISTRO_ADAPTADORES) >= 1

    def test_registro_contiene_default(self):
        """TODO: identificador del caso de prueba:
        El adaptador por defecto está registrado."""

        assert DEFAULT_ADAPTADOR_AMT in REGISTRO_ADAPTADORES

    def test_default_es_basicpitch(self):
        """El default es 'basicpitch'."""

        assert DEFAULT_ADAPTADOR_AMT == "basicpitch"

    def test_adaptador_basicpitch_tiene_método_transcribir(self):
        """TODO: identificador del caso de prueba:
        AdaptadorBasicPitch tiene método transcribir."""

        assert hasattr(AdaptadorBasicPitch, "transcribir")
        assert callable(AdaptadorBasicPitch.transcribir)

    def test_adaptador_basicpitch_tiene_método_csv_a_ts(self):
        """TODO: identificador del caso de prueba:
        AdaptadorBasicPitch tiene método csv_a_ts."""

        assert hasattr(AdaptadorBasicPitch, "csv_a_ts")
        assert callable(AdaptadorBasicPitch.csv_a_notas)


# ─── Tests de Componente: transcribir_audio ───────────────────────────────────


class TestTranscribirAudio:
    """Flujo de transcripción automática (con mocks)."""

    @patch("src.etapas.adaptador_amt.predict_and_save")
    def test_transcribir_invoca_predict_and_save_retorna_ruta_csv(
        self, mock_predict_and_save, tmp_path
    ):

        audio = tmp_path / "test.wav"
        audio.touch()
        adaptador = AdaptadorBasicPitch()

        # Simula la creación del csv
        def side_effect(*args, **kwargs):
            salida = kwargs["output_directory"]
            stem = kwargs["audio_path_list"][0].stem
            (salida / f"{stem}_{adaptador.nombre}.csv").touch()

        mock_predict_and_save.side_effect = side_effect

        ruta_salida = tmp_path / "out"
        ruta_salida.mkdir()

        ruta_csv = adaptador.transcribir(audio, ruta_salida)

        mock_predict_and_save.assert_called_once()
        kwargs = mock_predict_and_save.call_args.kwargs
        assert kwargs.get("save_notes") is True
        assert ruta_csv.exists()
        assert ruta_csv.name == "test_basic_pitch.csv"

    @patch("src.etapas.adaptador_amt.predict_and_save")
    def test_transcribir_error_externo_lanza_warning(
        self, mock_predict_and_save, tmp_path, caplog
    ):
        audio = tmp_path / "test.wav"
        audio.touch()
        adaptador = AdaptadorBasicPitch()

        mock_predict_and_save.side_effect = RuntimeError("BasicPitch ERROR")

        # Genera el csv para evitar FileNotFoundError
        ruta_salida = tmp_path / "out"
        ruta_salida.mkdir()
        (ruta_salida / "test_basic_pitch.csv").touch()

        adaptador.transcribir(audio, ruta_salida)

        assert "WARNING" in caplog.text
        assert caplog.records[0].name == "src.etapas.adaptador_amt"

    @patch("src.etapas.adaptador_amt.predict_and_save")
    def test_transcribir_adaptador_no_encontrado_usa_default(
        self, mock_predict_and_save, tmp_path, caplog
    ):
        """TODO: identificador del caso de prueba:
        Adaptador inexistente loguea CRITICAL y usa default."""

        audio_path = tmp_path / "test.wav"
        audio_path.write_bytes(b"fake audio")

        mock_predict_and_save.return_value = None

        _ruta, adaptador_usado = transcribir_audio(audio_path, "motor_inexistente")

        # Verifica que log CRITICAL se genera con el error del adaptador no encontrado
        assert "no encontrado" in caplog.text
        assert "CRITICAL" in caplog.text
        assert caplog.records[0].name == "src.etapas.adaptador_amt"
        assert DEFAULT_ADAPTADOR_AMT in caplog.text
        assert (
            adaptador_usado.nombre == REGISTRO_ADAPTADORES[DEFAULT_ADAPTADOR_AMT].nombre
        )

    def test_transcribir_csv_no_generado_produce_system_exit(self, audio_corrupto):
        """TODO: identificador del caso de prueba:
        Si BasicPitch no genera CSV, se produce sys.exit(1)."""

        with pytest.raises(SystemExit) as exc_info:
            transcribir_audio(audio_corrupto, "basicpitch")
        assert exc_info.value.code == 1
