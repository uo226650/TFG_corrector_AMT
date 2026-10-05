from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.etapas.corrector.configuracion_correccion import ConfigCorrector


@dataclass(frozen=True)
class GlobalConfig:
    """Configuración global del sistema."""

    root_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent.parent
    )

    # Keys del YAML
    dir_audios: str = "data/audio"
    dir_ts_inicial: str = "data/ts_inicial"
    dir_ts_normalizada: str = "data/ts_normalizada"
    dir_ts_corregida: str = "data/ts_corregida"
    corrector: ConfigCorrector = field(default_factory=ConfigCorrector)

    @property
    def ruta_audios(self) -> Path:
        return self.root_dir / self.dir_audios

    @property
    def ruta_ts_inicial(self) -> Path:
        return self.root_dir / self.dir_ts_inicial

    @property
    def ruta_ts_normalizada(self) -> Path:
        return self.root_dir / self.dir_ts_normalizada

    @property
    def ruta_ts_corregida(self) -> Path:
        return self.root_dir / self.dir_ts_corregida


def cargar_config_yaml(ruta_yaml: Path, root_dir: Path) -> GlobalConfig:
    """Lee el archivo YAML y construye la configuración."""

    kwargs = {"root_dir": root_dir} if root_dir is not None else {}

    if ruta_yaml.exists():
        with open(ruta_yaml, "r", encoding="utf-8") as archivo:
            datos_config = yaml.safe_load(archivo) or {}

        # Sección global
        datos_pipeline = datos_config.get("pipeline", {})
        kwargs_pipeline = {k: v for k, v in datos_pipeline.items() if v is not None}
        kwargs.update(kwargs_pipeline)

        # Sección módulo corrector
        datos_corrector = datos_config.get("corrector", {})
        kwargs["corrector"] = ConfigCorrector(
            reglas_activas=datos_corrector.get("reglas_activas") or list()
        )

    return GlobalConfig(**kwargs)
