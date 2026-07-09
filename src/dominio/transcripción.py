from dataclasses import dataclass
from typing import List
from src.dominio.nota import Nota


@dataclass
class Transcripción:
    """Docstring: Objeto que representa la totalidad de una transcripción de una melodía monofónica.
    Consiste en una secuencia de eventos de nota"""

    eventos: List[Nota]
