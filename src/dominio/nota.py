import uuid
from dataclasses import dataclass, field
from itertools import count

_contador = count(1)
MIDI_límite_inferior = 0
MIDI_límite_superior = 127


@dataclass
class Nota:
    """Evento de nota musical. Representa una nota detectada por un modelo de AMT.
    Attributes:
        pitch: Altura tonal en formato MIDI (0-127).
        onset: Instante de inicio en segundos.
        offset: Instante de finalización en segundos. Debe ser > onset.
        duración: Duración en segundos.
        fuente: Modelo que originó la nota.
        confianza: Probabilidad o certeza [0.0, 1.0]. Opcional.
        observaciones: Anotación manual. Opcional.
        identificador: Identificador numérico incremental para trazabilidad del csv.
        uid: Identificador único de 8 caracteres hex.
        uid_original: Si es nota originada por corrección, apunta al uid de la nota original.
    """

    pitch: int  # formato MIDI
    onset: float
    offset: float
    duración: float = field(init=False)
    fuente: str = "BasicPitch"  # Default
    confianza: float | None = None
    observaciones: str | None = None
    identificador: int = field(
        default_factory=lambda: next(_contador)
    )  # ID para trazabilidad
    uid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])  # ID único, técnico
    uid_original: str | None = None  # Apunta a la nota original si esta es corregida

    def __post_init__(self):
        # Validaciones para el objeto Nota
        # TODO: offset < duración audio
        errores = []
        if not (MIDI_límite_inferior <= self.pitch <= MIDI_límite_superior):
            errores.append(f"pitch ({self.pitch}) fuera de rango MIDI [0-127]")
        if not (0 <= self.onset):
            errores.append(f"onset ({self.onset}) debe ser >= 0")
        if not (0 < self.offset):
            errores.append(f"offset ({self.offset}) debe ser > 0")
        if self.offset <= self.onset:
            errores.append(f"offset ({self.offset}) debe ser > onset ({self.onset})")
        if self.confianza is not None and not (0.0 <= self.confianza <= 1.0):
            errores.append(f"confianza {self.confianza} fuera de rango [0, 1]")

        if errores:
            raise NotaValidationError("\n- " + "\n- ".join(errores))

        # Calcular atributos derivados
        object.__setattr__(self, "duración", self.offset - self.onset)


class NotaValidationError(ValueError):
    """Se lanza cuando algún atributo de la Nota no pasa la validación"""
