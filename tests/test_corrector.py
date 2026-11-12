"""
Tests para el módulo corrector (etapa 4).
Casos: TODO: identificador de los casos de prueba del documento TFG.
"""

from src.dominio.nota import Nota
from src.dominio.transcripción import Transcripción

# ─── Tests Unitarios ──────────────────────────────────────


class BaseReglas:
    def _crea_transcripción_y_aplica_regla(
        self, notas: list[Nota], regla
    ) -> tuple[Transcripción, Transcripción]:
        """Crea una transcripción a partir de la lista de notas,
        aplica la regla y devuelve la transcripción original y la corregida."""
        original = Transcripción(notas=notas, ruta_origen="irrelevante")
        corregida = regla.aplicar(original)
        return original, corregida

    def asserts_casos_especiales(self, regla_bajo_test):
        """TODO: identificador del caso de prueba:
        Transcripción vacía (0 notas) y transcripción con 1 sola nota.
        Ambas permanecen intactas tras aplicar cualquier regla"""
        # ----- Vacía ----- #
        _original, corregida = self._crea_transcripción_y_aplica_regla(
            notas=[], regla=regla_bajo_test
        )
        assert corregida.notas == []

        # ----- Transcripción de 1 nota ----- #
        _original, corregida = self._crea_transcripción_y_aplica_regla(
            notas=[Nota(64, 0.0, 1.0)], regla=regla_bajo_test
        )
        assert corregida.notas[0].offset == 1.0
        assert corregida.notas[0].uid_original == None


class TestEliminaciónSolapamientos(BaseReglas):
    """Tests para la regla ReglaEliminaciónSolapamientos."""

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
        self.asserts_casos_especiales(regla_eliminación_solapamientos)


class TestFusiónPorProximidad(BaseReglas):
    """Tests para la regla ReglaFusiónPorProximidad."""

    def test_notas_consecutivas_mismo_pitch_no_se_fusionan(
        self, regla_fusión_proximidad
    ):
        """TODO: identificador del caso de prueba:
        Dos notas consecutivas del mismo pitch no se fusionan por no cumplir criterio de umbral temporal tras aplicar la regla de fusión por proximidad."""
        notas_incumplen_criterio_umbral = [
            Nota(64, onset=0.0, offset=1.0),
            Nota(64, onset=1.06, offset=2.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas_incumplen_criterio_umbral, regla_fusión_proximidad
        )
        assert original.notas[0].offset == 1.0
        assert corregida.notas[0].offset == 1.0
        assert original.notas[0].onset == 0.0
        assert corregida.notas[0].onset == 0.0
        assert original.notas[1].offset == 2.0
        assert corregida.notas[1].offset == 2.0
        assert original.notas[1].onset == 1.06
        assert corregida.notas[1].onset == 1.06

    def test_notas_consecutivas_distinto_pitch_no_se_fusionan(
        self, regla_fusión_proximidad
    ):
        """TODO: identificador del caso de prueba:
        Dos notas consecutivas de distinto pitch que cumplen el criterio de umbral temporal no se fusionan tras aplicar la regla de fusión por proximidad."""
        notas_incumplen_criterio_pitch = [
            Nota(64, onset=0.0, offset=1.0),
            Nota(65, onset=1.01, offset=2.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas_incumplen_criterio_pitch, regla_fusión_proximidad
        )
        assert original.notas[0].offset == 1.0
        assert corregida.notas[0].offset == 1.0
        assert original.notas[0].onset == 0.0
        assert corregida.notas[0].onset == 0.0
        assert original.notas[1].offset == 2.0
        assert corregida.notas[1].offset == 2.0
        assert original.notas[1].onset == 1.01
        assert corregida.notas[1].onset == 1.01

    def test_notas_consecutivas_se_fusionan(self, regla_fusión_proximidad):
        """TODO: identificador del caso de prueba:
        Dos notas consecutivas del mismo pitch se fusionan por cumplir criterio de umbral tras aplicar la regla de fusión por proximidad."""
        notas_cumplen_criterio = [
            Nota(64, onset=0.0, offset=1.0),
            Nota(64, onset=1.03, offset=2.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas_cumplen_criterio, regla_fusión_proximidad
        )

        assert len(corregida.notas) == 1
        # Fusión
        assert corregida.notas[0].onset == 0.0
        assert corregida.notas[0].offset == 2.0  # fusionada
        assert corregida.notas[0].uid_original == original.notas[0].uid

        # Original no cambia
        assert original.notas[0].onset == 0.0
        assert original.notas[0].offset == 1.0
        assert original.notas[1].onset == 1.03
        assert original.notas[1].offset == 2.0

    def test_varias_fusiones_no_consecutivas_se_resuelven(
        self, regla_fusión_proximidad
    ):
        """TODO: identificador del caso de prueba:
        Transcripción con más de un caso de fusión de notas resuelve todos ellos tras aplicar la regla."""
        notas = [
            Nota(64, onset=0.0, offset=1.0),
            Nota(64, onset=1.03, offset=2.0),
            Nota(60, onset=2.0, offset=3.0),
            Nota(64, onset=3.0, offset=4.0),
            Nota(64, onset=4.01, offset=5.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas, regla_fusión_proximidad
        )

        # Comprobar que han ocurrido dos fusiones
        assert len(original.notas) == 5
        assert len(corregida.notas) == 3

        # Primera fusión
        assert corregida.notas[0].offset == 2.0  # fusionada
        assert corregida.notas[1].offset == 3.0

        # Corregida tiene nuevo uid y apunta a uid original
        assert corregida.notas[0].uid_original == original.notas[0].uid
        assert corregida.notas[0].uid != original.notas[0].uid

        # No corregida mantiene su uid y no apunta a un uid_original
        assert corregida.notas[1].uid == original.notas[2].uid
        assert corregida.notas[1].uid_original == None

        # Segunda fusión
        assert corregida.notas[2].offset == 5.0  # fusionada
        assert corregida.notas[2].uid_original == original.notas[3].uid

        # Originales intactas
        assert original.notas[0].offset == 1.0
        assert original.notas[1].offset == 2.0
        assert original.notas[2].offset == 3.0
        assert original.notas[3].offset == 4.0
        assert original.notas[4].offset == 5.0

    def test_varias_fusiones_consecutivas_se_resuelven(self, regla_fusión_proximidad):
        """TODO: identificador del caso de prueba:
        Transcripción con fusión múltiple de notas la resuelve tras aplicar la regla."""
        notas = [
            Nota(64, onset=0.0, offset=1.0),
            Nota(64, onset=1.03, offset=2.0),
            Nota(64, onset=2.04, offset=3.0),
            Nota(64, onset=3.05, offset=4.0),
            Nota(60, onset=4.0, offset=5.0),
        ]
        original, corregida = self._crea_transcripción_y_aplica_regla(
            notas, regla_fusión_proximidad
        )

        # Comprobar que han ocurrido tres fusiones
        assert len(original.notas) == 5
        assert len(corregida.notas) == 2

        # Fusión múltiple: fusionadas notas con índices 0,1,2 y 3
        assert corregida.notas[0].offset == 4.0
        assert corregida.notas[1].offset == 5.0

        # Corregida tiene nuevo uid y apunta al uid original
        assert corregida.notas[0].uid != original.notas[0].uid
        assert corregida.notas[0].uid_original == original.notas[0].uid

        # No corregida mantiene su uid y no apunta a un uid_original
        assert corregida.notas[1].uid == original.notas[4].uid
        assert corregida.notas[1].uid_original == None

        # Originales intactas
        assert original.notas[0].offset == 1.0
        assert original.notas[1].offset == 2.0
        assert original.notas[2].offset == 3.0
        assert original.notas[3].offset == 4.0
        assert original.notas[4].offset == 5.0

    def test_casos_especiales(self, regla_fusión_proximidad):
        """TODO: identificador del caso de prueba:
        Transcripción vacía (0 notas) y transcripción con 1 sola nota.
        Ambas permanecen intactas tras aplicar regla de fusión por proximidad"""
        self.asserts_casos_especiales(regla_fusión_proximidad)
