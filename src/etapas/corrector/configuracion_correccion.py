from dataclasses import dataclass


@dataclass
class ConfigCorrector:
    """Configuración para el corrector cargada desde YAML"""

    reglas_activas: list[str]
