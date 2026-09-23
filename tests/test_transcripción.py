"""
Tests para el modelo de dominio: Transcripción.
Casos: TODO
"""  # noqa: N999

from src.dominio.transcripción import Transcripción


class TestTranscripción:
    """Creación de Transcripción."""

    def test_transcripción_con_eventos(self, notas_escala):
        """TODO: identificador del caso de prueba:
        Transcripción con lista de notas."""
        ts = Transcripción(notas=notas_escala, ruta_origen="irrelevante")
        assert len(ts.notas) == 7
        assert ts.notas[0].pitch == 60
        assert ts.notas[4].pitch == 67

    def test_transcripción_vacía(self):
        """TODO: identificador del caso de prueba:
        Transcripción con lista vacía es válida."""
        ts = Transcripción(notas=[], ruta_origen="irrelevante")
        assert len(ts.notas) == 0
        assert ts.num_notas == 0
        assert ts.duración_sonora == 0.0
        assert ts.pitch_max == 0
        assert ts.pitch_min == 0
        assert ts.inicio == 0.0
        assert ts.fin == 0.0
        assert ts.duración_toma == 0
        assert not ts.tiene_solapamientos()
