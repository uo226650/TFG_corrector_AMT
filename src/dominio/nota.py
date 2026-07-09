from dataclasses import dataclass


# TODO: Faltan validaciones (offset > onset, pitch dentro de rango de valores, ...)
@dataclass
class Nota:
    """Docstring: Objeto que representa un evento de nota."""

    identificador: int
    pitch: int
    onset: float
    offset: float
    duración: float
    fuente: str = "BasicPitch"  # Default
    confianza: float = None
    observaciones: str = None
