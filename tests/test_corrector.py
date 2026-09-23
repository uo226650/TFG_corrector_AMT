"""
Tests para el módulo corrector (etapa 4).
Casos: TODO: identificador de los casos de prueba del documento TFG.
"""

from src.dominio.nota import Nota
from src.dominio.transcripción import Transcripción

# ─── Tests Unitarios ──────────────────────────────────────


class TestEliminaciónSolapamientos:
    """Tests para la regla ReglaEliminaciónSolapamientos"""

    def test_no_hay_solapamiento(self, regla_eliminación_solapamientos):
        """TODO: identificador del caso de prueba:
        Dos notas que no se solapan permanecen inalteradas tras aplicar la regla de eliminación de solapamientos."""
        notas = [Nota(64, onset=0.0, offset=1.0), Nota(64, onset=1.0, offset=2.0)]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas, regla_eliminación_solapamientos
        )
        assert not corregida.tiene_solapamientos()
        assert original.notas[0].offset == 1.0

    def test_solapamiento_se_corrige(self, regla_eliminación_solapamientos):
        """TODO: identificador del caso de prueba:
        Dos notas se solapan originalmente. Tras aplicar la regla de corrección de solapamientos
        la primera nota se recorta para igualar su offset al instante de inicio de la segunda."""
        notas = [Nota(64, onset=0.0, offset=1.5), Nota(64, onset=1.0, offset=2.0)]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas, regla_eliminación_solapamientos
        )
        assert original.tiene_solapamientos()
        assert not corregida.tiene_solapamientos()

        assert corregida.notas[0].offset == 1.0
        assert corregida.notas[1].offset == 2.0
        assert original.notas[0].offset == 1.5  # intacta
        assert corregida.notas[0].uid_original == notas[0].uid

    def test_varios_solapes_se_corrigen(self, regla_eliminación_solapamientos):
        """TODO: identificador del caso de prueba:
        Transcripción con más de un caso de solapamiento
        resuelve todos ellos tras aplicar la regla de eliminación de solapamientos."""
        notas = [
            Nota(64, onset=0.0, offset=1.2),
            Nota(64, onset=1.0, offset=2.2),
            Nota(64, onset=2.0, offset=3.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas, regla_eliminación_solapamientos
        )

        assert original.tiene_solapamientos()
        assert not corregida.tiene_solapamientos()

        assert corregida.notas[0].offset == 1.0
        assert corregida.notas[1].offset == 2.0
        assert (
            original.notas[0].offset == 1.2
        )  # intacta (no se modifica la transcripción original)
        assert (
            corregida.notas[0].uid_original == notas[0].uid
        )  # corregida apunta a uid original
        assert corregida.notas[0].uid != notas[0].uid  # corregida tiene nuevo uid
        assert (
            corregida.notas[1].uid_original == notas[1].uid
        )  # corregida apunta a uid original
        assert corregida.notas[1].uid != notas[1].uid  # corregida tiene nuevo uid
        assert corregida.notas[2].uid == notas[2].uid  # es la misma, no corregida

    def test_casos_especiales(self, regla_eliminación_solapamientos):
        """TODO: identificador del caso de prueba:
        Transcripción vacía (0 notas) y transcripción con 1 sola nota.
        Ambas permanecen intactas tras aplicar regla de eliminación de solapamientos"""
        # ----- Vacía ----- #
        _original, corregida = self._crea_transcripción_y_aplica_regla(
            notas=[], regla=regla_eliminación_solapamientos
        )
        assert corregida.notas == []

        # ----- Transcripción de 1 nota ----- #
        _original, corregida = self._crea_transcripción_y_aplica_regla(
            notas=[Nota(64, 0.0, 1.0)], regla=regla_eliminación_solapamientos
        )
        assert corregida.notas[0].offset == 1.0

    def _crea_transcripción_y_aplica_regla(
        self, notas: list[Nota], regla
    ) -> tuple[Transcripción, Transcripción]:
        """Crea una transcripción a partir de la lista de notas,
        aplica la regla y devuelve la transcripción original y la corregida."""
        original = Transcripción(notas=notas, ruta_origen="irrelevante")
        corregida = regla.aplicar(original)
        return original, corregida
