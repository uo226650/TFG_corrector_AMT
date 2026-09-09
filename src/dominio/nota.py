import uuid
from dataclasses import dataclass, field
from itertools import count

_contador = count(1)
MIDI_límite_inferior = 0
MIDI_límite_superior = 127


@dataclass
class Nota:
    """Docstring: Objeto que representa un evento de nota."""

    pitch: int  # formato MIDI
    onset: float
    offset: float
    duración: float = field(init=False)
    fuente: str = "BasicPitch"  # Default
    confianza: float = None
    observaciones: str = None
    identificador: int = field(
        default_factory=lambda: next(_contador)
    )  # ID para trazabilidad
    uid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])  # ID único, técnico
    uid_original: str | None = None  # Apunta a la nota original si esta es corregida

    def __post_init__(self):

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
    pass
