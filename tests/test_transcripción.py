"""
Tests para el modelo de dominio: Transcripción.
Casos: TODO
"""  # noqa: N999

import csv
from dataclasses import fields
from pathlib import Path

import pytest

from src.dominio.nota import Nota
from src.dominio.transcripción import TranscripcionVacíaError, Transcripción


class TestTranscripción:
    """Creación de Transcripción."""

    def test_transcripción_con_eventos(self, notas_escala):
        """TODO: identificador del caso de prueba:
        Transcripción con lista de notas."""
        ruta = Path("irrelevante")
        ts = Transcripción(notas=notas_escala, ruta_origen=ruta)
        assert ts.notas == notas_escala
        assert len(ts.notas) == 7
        assert ts.notas[0].pitch == 60
        assert ts.notas[4].pitch == 67
        assert ts.ruta_origen == ruta

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

    def test_campos_calculados(self, notas_escala):
        """TODO: identificador del caso de prueba:
        Transcripción calcula los atributos derivados: pitch_min, pitch_max, inicio, fin, duración_toma y duración_sonora."""
        ts = Transcripción(notas=notas_escala, ruta_origen=Path("irrelevante"))

        assert ts.pitch_min == 60
        assert ts.pitch_max == 71
        assert ts.inicio == 0.0
        assert ts.fin == 4.0
        assert ts.duración_toma == 4.0
        assert ts.duración_sonora == 3.5  # 7 notas * 0.5s = 3.5s


class TestTranscripciónMétodos:
    """Comportamiento de Transcripción."""

    def test_escala_secuencial_no_tiene_solapamientos(self, notas_escala):
        """TODO: identificador del caso de prueba:
        Una lista de notas donde cada una empieza cuando acaba
        la anterior (o después) debe retornar False."""
        ts = Transcripción(notas=notas_escala, ruta_origen=Path("irrelevante"))

        assert ts.tiene_solapamientos() is False

    def test_offset_supera_siguiente_onset_tiene_solapamientos(self):
        """TODO: identificador del caso de prueba:
        Si el offset de una nota supera el onset de la siguiente nota,
        debe retornar True."""
        nota_1 = Nota(pitch=60, onset=0.0, offset=1.0, fuente="BasicPitch")
        nota_2 = Nota(pitch=64, onset=0.8, offset=1.5, fuente="BasicPitch")

        ts = Transcripción(notas=[nota_1, nota_2], ruta_origen=Path("irrelevante"))

        assert ts.tiene_solapamientos() is True

    def test_exportar_a_csv_lanza_excepcion_si_esta_vacia(self, tmp_path):
        """TODO: identificador del caso de prueba:
        Intentar exportar una transcripción sin notas debe lanzar
        la excepción TranscripcionVacíaError."""
        ts = Transcripción(notas=[], ruta_origen=tmp_path / "vacia.csv")
        ruta_salida = tmp_path / "falla_y_no_se_crea.csv"

        with pytest.raises(TranscripcionVacíaError):
            ts.exportar_a_csv(ruta_salida)

        assert not ruta_salida.exists()

    def test_exportar_a_csv_escribe_archivo_correctamente(self, notas_escala, tmp_path):
        """TODO: identificador del caso de prueba:
        Exportar transcripción no vacía debe generar un CSV con
        los valores serializados por columnas que corresponden a los campos de la dataclass Nota."""
        ts = Transcripción(notas=notas_escala, ruta_origen=tmp_path / "escala.csv")
        ruta_salida = tmp_path / "escala_normalizada.csv"

        columnas = ts.exportar_a_csv(ruta_salida)

        columnas_esperadas = [f.name for f in fields(Nota)]
        assert columnas == columnas_esperadas  # Devuelve las columnas correctas

        assert ruta_salida.exists()  # Crea el archivo
        assert ruta_salida.is_file()

        with open(ruta_salida, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            assert reader.fieldnames == columnas_esperadas

            filas = list(reader)

        assert len(filas) == len(
            ts.notas
        )  # Contiene tantas filas como notas tiene la transcripción

        primera_fila = filas[0]
        primera_nota = ts.notas[0]

        assert int(primera_fila["pitch"]) == primera_nota.pitch
        assert float(primera_fila["onset"]) == primera_nota.onset  # OJO: precisión...
        assert float(primera_fila["offset"]) == primera_nota.offset
        assert primera_fila["fuente"] == primera_nota.fuente
