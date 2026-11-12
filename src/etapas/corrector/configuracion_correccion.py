from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConfigCorrector:
    """Configuración para el corrector cargada desde YAML"""

    reglas_activas: list[str] = field(default_factory=list)
    umbrales: dict = field(default_factory=dict)

    def __post_init__(self):

        if not isinstance(self.reglas_activas, list):
            object.__setattr__(
                self,
                "reglas_activas",
                list(self.reglas_activas) if self.reglas_activas else [],
            )

        if not isinstance(self.umbrales, dict):
            object.__setattr__(self, "umbrales", {})
