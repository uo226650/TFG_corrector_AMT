import logging
from dataclasses import replace
from typing import Protocol

from src.dominio.nota import Nota
from src.dominio.transcripción import Transcripción

# Crea logger para las reglas
logger = logging.getLogger(__name__)


class ReglaCorreción(Protocol):
    """Define la interfaz que deben implementar las reglas de corrección.

    Attributes:
        nombre: Identifica cada regla por su nombre único
    """

    nombre: str

    def aplicar(self, transcripción: Transcripción) -> Transcripción: ...


class ReglaEliminaciónSolapamientos:
    """Elimina solapamiento entre notas"""

    nombre = "eliminación_solapamientos"

    # TODO: registrar el número de ediciones en almacenamiento permanente
    def aplicar(self, transcripción: Transcripción) -> Transcripción:
        """
        Aplica la regla de eliminación de solapamientos:
            - Comprueba si la transcripción contiene solapamientos:
                - si no tiene, devuelve la transcripción sin alterarla
                - si tiene, procede a recorrer la lista de notas para resolver los solapamientos
            - Recorta el offset de las notas que solapan con la siguiente
            - Anota el número de notas que han sido corregidas
            - Crea una nueva transcripción que contiene la lista de notas originales y corregidas
        Args:
            transcripción: transcripción a corregir

        Returns:
            transcripción_sin_solapamientos: Transcripción que contiene el mismo número de notas que la original, con el offset recortado en aquellas notas que solapaban con la siguiente.
        """
        if not transcripción.tiene_solapamientos():
            return transcripción

        nueva_transcripción_notas = []
        num_corregidas = 0
        for i in range(len(transcripción.notas) - 1):
            actual = transcripción.notas[i]
            siguiente = transcripción.notas[i + 1]
            nuevo_offset = min(actual.offset, siguiente.onset)
            if actual.offset != nuevo_offset:
                nueva = Nota(
                    pitch=actual.pitch,
                    onset=actual.onset,
                    offset=nuevo_offset,
                    fuente=actual.fuente,
                    confianza=actual.confianza,
                    observaciones=actual.observaciones,
                    identificador=actual.identificador,
                    uid_original=actual.uid,
                )
                nueva_transcripción_notas.append(nueva)
                num_corregidas += 1

                logger.info(
                    "Nota %d corregida (%s) -> nueva Nota (%s): \n- offset %.3f -> %.3f (solapaba con nota %d onset %.3f)",
                    actual.identificador,
                    actual.uid,
                    nueva.uid,
                    actual.offset,
                    nuevo_offset,
                    siguiente.identificador,
                    siguiente.onset,
                )
            else:
                nueva_transcripción_notas.append(actual)
        nueva_transcripción_notas.append(transcripción.notas[-1])

        logger.info(
            "[%s] Total corregidas: %d/%d",
            self.nombre,
            num_corregidas,
            len(transcripción.notas),
        )
        return replace(transcripción, notas=nueva_transcripción_notas)


class ReglaFusiónNotasCortas:
    """Fusiona notas consecutivas del mismo pitch si distancia < umbral"""

    nombre = "fusión_notas_cortas"

    def aplicar(self, transcripción: Transcripción) -> Transcripción:
        # TODO
        ...
