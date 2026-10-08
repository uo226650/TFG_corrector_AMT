"""
Tests para el conversor simbólico (etapa 3).
Casos: TODO: identificador de los casos de prueba del documento TFG.
"""

import copy
import csv
from unittest.mock import MagicMock

from src.config import GlobalConfig
from src.dominio.nota import Nota
from src.dominio.transcripción import Transcripción
from src.etapas.conversor_simbólico import convertir_formato


class TestConvertirFormato:
    """Flujo de conversión a formato interno."""

    def test_convertir_formato_ordena_y_asigna_ids(self, notas_escala, tmp_path):
        config_test = GlobalConfig(root_dir=tmp_path)

        ts_inicial_ruta = config_test.ruta_ts_inicial / "escala.csv"
        ts_inicial_ruta.parent.mkdir(parents=True, exist_ok=True)
        ts_inicial_ruta.touch()

        notas_input = copy.deepcopy(notas_escala)
        # Nueva nota pitch 59 tiene que ir antes que pitch 64 en onset 1.0
        nota_desempate = Nota(
            pitch=59, onset=1.0, offset=1.5, fuente="BasicPitch", confianza=0.95
        )
        notas_input.append(nota_desempate)
        notas_input.reverse()  # Desordena

        mock_adaptador = MagicMock()  # TODO: cambiar a decorador por consistencia?
        mock_adaptador.nombre = "BasicPitch"
        mock_adaptador.csv_a_notas.return_value = notas_input

        ts_normalizada = convertir_formato(
            ts_inicial_ruta, mock_adaptador, config=config_test
        )

        assert len(ts_normalizada.notas) == 8
        notas_esperadas_pitch = [60, 62, 59, 64, 65, 67, 69, 71]
        assert [nota.pitch for nota in ts_normalizada.notas] == notas_esperadas_pitch

        for idx, nota in enumerate(ts_normalizada.notas):
            assert nota.identificador == idx + 1

        ruta_salida = config_test.ruta_ts_normalizada / "BasicPitch" / "escala.csv"
        assert ruta_salida.exists()
        assert ruta_salida.is_file()

        with open(ruta_salida, mode="r", encoding="utf-8") as f:
            lector_csv = csv.reader(f)
            cabecera = next(lector_csv)
            filas = list(lector_csv)

        assert len(filas) == 8

        idx_id = cabecera.index("identificador")
        ids_en_csv = [fila[idx_id] for fila in filas]

        assert ids_en_csv == ["1", "2", "3", "4", "5", "6", "7", "8"]

    def test_convertir_formato_transcripcion_vacia_informa(self, tmp_path, caplog):
        config_test = GlobalConfig(root_dir=tmp_path)

        ts_inicial_ruta = config_test.ruta_ts_inicial / "vacia.csv"
        ts_inicial_ruta.parent.mkdir(parents=True, exist_ok=True)
        ts_inicial_ruta.touch()

        mock_adaptador = MagicMock()
        mock_adaptador.nombre = "BasicPitch"
        mock_adaptador.csv_a_notas.return_value = []

        with caplog.at_level("INFO"):
            resultado = convertir_formato(
                ts_inicial_ruta, mock_adaptador, config=config_test
            )

        assert isinstance(resultado, Transcripción)
        assert len(resultado.notas) == 0

        ruta_salida = config_test.ruta_ts_normalizada / "BasicPitch"
        assert ruta_salida.exists()
        assert ruta_salida.is_dir()

        logs = caplog.text
        assert "[CONVERSOR] Exportando transcripción vacía:" in logs
        assert "[CONVERSOR] Exportación completada ->" in logs
        assert "Notas totales: 0" in logs
