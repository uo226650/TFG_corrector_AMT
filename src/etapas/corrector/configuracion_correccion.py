from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConfigCorrector:
    """Configuración para el corrector cargada desde YAML"""

    reglas_activas: list[str] = field(default_factory=list)
