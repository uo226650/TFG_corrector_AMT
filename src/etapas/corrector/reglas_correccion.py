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
        nombre: Identifica cada regla por su nombre único.
    """

    nombre: str

    def aplicar(self, transcripción: Transcripción) -> Transcripción: ...


class ReglaEliminaciónSolapamientos:
    """Elimina solapamiento entre notas."""

    nombre = "eliminación_solapamientos"

    def __init__(self, config: dict):
        pass

    # TODO: registrar el número de ediciones en almacenamiento permanente
    def aplicar(self, transcripción: Transcripción) -> Transcripción:
        """
        Aplica la regla de eliminación de solapamientos:
            - Comprueba si la transcripción contiene solapamientos:
                - si no tiene, devuelve la transcripción sin alterarla.
                - si tiene, procede a recorrer la lista de notas para resolver los solapamientos.
            - Recorta el offset de las notas que solapan con la siguiente.
            - Anota el número de notas que han sido corregidas.
            - Crea una nueva transcripción que contiene la lista de notas originales y corregidas.
        Args:
            transcripción: transcripción a corregir.

        Returns:
            transcripción_sin_solapamientos: Transcripción que contiene el mismo número de notas que la original, con el offset recortado en aquellas notas que solapaban con la siguiente.
        """
        if not transcripción.tiene_solapamientos():
            logger.info(
                "[%s] Total corregidas: 0/%d",
                self.nombre,
                len(transcripción.notas),
            )
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
                    "[CORRECTOR] Nota %d corregida (%s) -> nueva Nota (%s): \n- offset %.3f -> %.3f (solapaba con nota %d onset %.3f)",
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


class ReglaFusiónPorProximidad:
    """Fusiona notas consecutivas del mismo pitch si la distancia entre ellas < umbral."""

    nombre = "fusión_proximidad"

    def __init__(self, config: dict):
        self.max_gap = float(config.get("max_gap", 0.05))  # default

    # TODO: registrar el número de ediciones en almacenamiento permanente
    def aplicar(self, transcripción: Transcripción) -> Transcripción:
        """
        Aplica la regla de fusión de notas por proximidad:
            - Comprueba si la transcripción contiene notas:
                - si está vacía no hace nada y termina.
                - si tiene notas, procede a recorrer la lista de notas para identificar los candidatos a la fusión.
            - Calcula el espacio temporal entre cada par de notas consecutivas (entre el final de la nota actual y el inicio de la siguiente).
            - Comprueba si ambas notas tienen el mismo pitch y si el espacio entre ellas es menor que el umbral configurado.
            - Fusiona las notas que cumplen el criterio comprobado en el paso anterior:
                - modifica el final de la nota actual (offset) para que abarque hasta el final (offset) de la siguiente.
            - Anota el número de notas que han sido corregidas.
            - Crea una nueva transcripción que contiene la lista de notas originales y corregidas.
        Args:
            transcripción: transcripción a corregir.

        Returns:
            transcripción_fusionada: Transcripción que contiene el mismo o menor número de notas que la original, resultante de fusionar notas con el mismo pitch y espacio < umbral.
        """
        if transcripción.num_notas == 0:
            return transcripción

        nueva_transcripción_notas = []
        num_corregidas = 0

        actual = replace(transcripción.notas[0])
        uid_base = actual.uid  # para trazabilidad en fusiones múltiples

        for i in range(1, len(transcripción.notas)):
            siguiente = transcripción.notas[i]

            gap = round(
                siguiente.onset - actual.offset, 5
            )  # evitar errores de precisión del float

            # Criterio para la fusión
            if siguiente.pitch == actual.pitch and gap <= self.max_gap:
                nuevo_offset = siguiente.offset  # se asume que no hay solapamientos, que ya se ha aplicado la regla eliminación de solapamientos

                if actual.offset != nuevo_offset:
                    offset_antiguo = actual.offset
                    actual = Nota(
                        pitch=actual.pitch,
                        onset=actual.onset,
                        offset=nuevo_offset,
                        fuente=actual.fuente,
                        confianza=actual.confianza,
                        observaciones=actual.observaciones,
                        identificador=actual.identificador,
                        uid_original=uid_base,
                    )

                    num_corregidas += 1

                    logger.info(
                        "[CORRECTOR] Nota %d corregida (%s) -> nueva Nota (%s): \n- offset %.3f -> %.3f (se ha fusionado con nota %d onset %.3f)",
                        actual.identificador,
                        actual.uid_original,
                        actual.uid,
                        offset_antiguo,
                        nuevo_offset,
                        siguiente.identificador,
                        siguiente.onset,
                    )

            else:
                nueva_transcripción_notas.append(actual)
                actual = replace(siguiente)
                uid_base = actual.uid

        nueva_transcripción_notas.append(actual)

        logger.info(
            "[%s] Total corregidas: %d/%d (umbral = %f)",
            self.nombre,
            num_corregidas,
            len(transcripción.notas),
            self.max_gap,
        )
        return replace(transcripción, notas=nueva_transcripción_notas)
