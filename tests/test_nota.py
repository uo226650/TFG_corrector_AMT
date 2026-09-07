"""
Tests para el modelo de dominio: Nota.
Casos: TODO
"""

import pytest
from src.dominio.nota import Nota, NotaValidationError


class TestNota:
    """Creación y validación de Nota."""

    def test_creación_nota_válida_todos_los_campos(self):
        """TODO: identificador del caso de prueba:
        Nota con todos los campos explícitos."""
        nota = Nota(
            pitch=60,
            onset=0.0,
            offset=0.5,
            fuente="BasicPitch",
            confianza=0.9,
            observaciones="test",
            identificador=1,
            uid=2,
            uid_original="1a2b3c4d",
        )
        assert nota.pitch == 60
        assert nota.onset == 0.0
        assert nota.offset == 0.5
        assert nota.fuente == "BasicPitch"
        assert nota.confianza == 0.9
        assert nota.observaciones == "test"
        assert nota.identificador == 1
        assert nota.uid == 2
        assert nota.uid_original == "1a2b3c4d"

    def test_creación_nota_valores_por_defecto(self):
        """TODO: identificador del caso de prueba:
        Nota con valores default (fuente, confianza, observaciones, identificador, uid, uid_original)."""
        nota = Nota(
            pitch=62,
            onset=0.5,
            offset=1.0,
        )
        assert nota.fuente == "BasicPitch"
        assert nota.confianza is None
        assert nota.observaciones is None
        assert isinstance(nota.identificador, int)
        assert nota.identificador == 1
        assert isinstance(nota.uid, str)
        assert len(nota.uid) == 8
        assert nota.uid_original is None

    def test_nota_pitch_límite_inferior_midi(self):
        """TODO: identificador del caso de prueba:
        Pitch 0 (C1) es válido."""
        nota = Nota(0, 0.0, 0.5)
        assert nota.pitch == 0

    def test_nota_pitch_límite_superior_midi(self):
        """TODO: identificador del caso de prueba:
        Pitch 127 (G9) es válido."""
        nota = Nota(127, 0.0, 0.5)
        assert nota.pitch == 127

    def test_nota_pitch_fuera_de_rango_lanza_excepción(self):
        """TODO: identificador del caso de prueba:
        Pitch 128 no es válido."""
        with pytest.raises(NotaValidationError) as exc_info:
            Nota(128, 0.0, 0.5)
        assert "fuera de rango MIDI" in str(exc_info.value)

    def test_nota_pitch_negativo_lanza_excepción(self):
        """TODO: identificador del caso de prueba:
        Pitch -1 (negativo) no es válido."""
        with pytest.raises(NotaValidationError) as exc_info:
            Nota(-1, 0.0, 0.5)
        assert "fuera de rango MIDI" in str(exc_info.value)

    def test_nota_offset_menor_que_onset_lanza_excepción(self):
        """TODO: identificador del caso de prueba:
        offset < onset lanza error de validación de nota."""

        with pytest.raises(NotaValidationError) as exc_info:
            Nota(60, 1.0, 0.5)
        assert "debe ser > onset" in str(exc_info.value)

    def test_nota_confianza_límite_inferior(self):
        """TODO: identificador del caso de prueba:
        Confianza 0.0 es válida (nota detectada pero sin certeza)."""
        nota = Nota(60, 0.0, 0.5, confianza=0.0)
        assert nota.confianza == 0.0

    def test_nota_confianza_límite_superior(self):
        """TODO: identificador del caso de prueba:
        Confianza 1.0 es válida (certeza total)."""
        nota = Nota(60, 0.0, 0.5, confianza=1.0)
        assert nota.confianza == 1.0
