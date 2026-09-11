from dataclasses import dataclass, field
from pathlib import Path

from src.dominio.nota import Nota


@dataclass(frozen=True)
class Transcripción:
    """Transcripción de una melodía monofónica.
    Consiste en una secuencia de eventos de nota

    Attributes:
        ruta_origen: Apunta al archivo que contiene la transcripción inicial.
        notas: Lista de Notas que componen la transcripción actual.
        num_notas: Número total de notas en esta transcripción.
        duración_sonora: Suma de todas las duraciones de las notas.
        pitch_min: Altura mínima detectada en la secuencia.
        pitch_max: Altura máxima detectada en la secuencia.
        inicio: Instante en que comienza el primer sonido.
        fin: Instante en que finaliza el último sonido.
        duración_toma: Total de sonoridad desde que empieza primera nota hasta que acaba la última.
    """

    ruta_origen: Path
    notas: list[Nota]
    num_notas: int = field(init=False)
    duración_sonora: float = field(init=False)
    pitch_min: int = field(init=False)
    pitch_max: int = field(init=False)
    inicio: float = field(init=False)
    fin: float = field(init=False)
    duración_toma: float = field(init=False)

    def __post_init__(self):
        # Calcula atributos derivados
        object.__setattr__(self, "num_notas", len(self.notas))
        object.__setattr__(
            self,
            "duración_sonora",
            sum(n.offset - n.onset for n in self.notas) if self.num_notas else 0.0,
        )
        object.__setattr__(
            self, "pitch_min", min((n.pitch for n in self.notas), default=0)
        )
        object.__setattr__(
            self, "pitch_max", max((n.pitch for n in self.notas), default=0)
        )
        object.__setattr__(
            self, "inicio", min(n.onset for n in self.notas) if self.num_notas else 0.0
        )
        object.__setattr__(
            self, "fin", max(n.offset for n in self.notas) if self.num_notas else 0.0
        )
        object.__setattr__(self, "duración_toma", self.fin - self.inicio)
