import uuid
from dataclasses import asdict, dataclass, field

from src.config import GlobalConfig


@dataclass
class EjecucionExperimental:
    """
    Almacena la configuración de entrada, las ediciones y las métricas asociadas a una ejecución."""

    config: GlobalConfig = field(default_factory=GlobalConfig)
    uuid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    ediciones_corrector: dict = field(default_factory=dict)  # Etapa 4. Corrector
    metricas_evaluacion: dict = field(default_factory=dict)  # Etapa 5. Evaluador
    # TODO. sustituir diccionario metricas_evaluacion por objeto MetricasEvaluación (metricas inicial, corregida y mejora)

    def obtener_datos_ejecucion(self) -> dict:
        """Estructura para guardar en JSON."""
        return {
            "id": self.uuid,
            "configuracion_corrector": asdict(self.config.corrector),  # TODO: revisar
            "ediciones": self.ediciones_corrector,
            "metricas": self.metricas_evaluacion,
        }
