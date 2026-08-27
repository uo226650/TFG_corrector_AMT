from dataclasses import dataclass, field
import uuid
from itertools import count

_id = count(1)


# TODO: Faltan validaciones (offset > onset, pitch dentro de rango de valores, ...)
@dataclass
class Nota:
    """Docstring: Objeto que representa un evento de nota."""

    pitch: int  # formato MIDI
    onset: float
    offset: float
    duración: float
    fuente: str = "BasicPitch"  # Default
    confianza: float = None
    observaciones: str = None
    identificador: int = field(
        default_factory=lambda: next(_id)
    )  # ID para trazabilidad
    uid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])  # ID único, técnico
    uid_original: str | None = None  # Apunta a la nota original si esta es corregida
