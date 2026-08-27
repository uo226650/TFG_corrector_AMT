import argparse
import logging
from pathlib import Path
import sys

from logger_config import setup_logging
from src.etapas.gestor_entrada.excepciones_entrada import AudioValidationError
from src.etapas.gestor_entrada.gestor_entrada import cargar_audio
from src.etapas.adaptador_AMT import (
    transcribir_audio,
    DEFAULT_AMT_ADAPTER,
    REGISTRO_ADAPTADORES,
)
from src.etapas.conversor_simbólico import convertir_formato
from src.etapas.corrector import corregir_transcripción
from src.etapas.evaluador import evaluar_transcripciones
from src.etapas.generador_informes import generar_informe

setup_logging()
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):

    if args.audio is None:
        parser.error("-- se requiere el argumento 'audio'")
    ruta_audio = args.audio

    # TODO: control manual del comando que viene (si no viene ninguno se ejecuta la pipeline entera)
    flujo_completo(ruta_audio, args.amt)


def flujo_completo(ruta_audio: Path, adaptador_amt_nombre: str):

    logger.info("[PIPELINE] Iniciando canalización para el archivo %s", ruta_audio)

    # Etapa 1: Carga y validación del archivo de audio
    try:
        audio, sr = cargar_audio(Path(ruta_audio))
    except AudioValidationError as e:
        logger.critical("[PIPELINE] %s", e)
        sys.exit(1)  # Salida controlada, no se puede continuar con la canalización

    # Etapa 2: Transcripción del audio con herramienta externa
    ts_inicial_ruta, adaptador_ts = transcribir_audio(
        Path(ruta_audio), adaptador_amt_nombre
    )

    # Etapa 3: Conversión a formato interno
    ts_normalizada = convertir_formato(ts_inicial_ruta, adaptador_ts)

    # Etapa 4: Corrección de la transcripción inicial
    ts_corregida = corregir_transcripción()

    # Etapa 5: Generación de métricas
    evaluar_transcripciones()

    # Etapa 6: Generación de informes
    generar_informe()

    logger.info("[PIPELINE] Canalización completada sin paradas")


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Canalización de transcripción de audio y su corrección. \nUsa --run (ejecución de principio a fin) --transcribir o --evaluar"
    )
    grupo = parser.add_mutually_exclusive_group()  # (required=True)

    # Comandos
    grupo.add_argument(
        "--transcribir", action="store_true", help="Solo transcribir audio"
    )
    grupo.add_argument("--evaluar", action="store_true", help="Solo evaluar csv")
    grupo.add_argument("--run", action="store_true", help="Pipeline completa")

    # Args
    parser.add_argument("audio", type=Path, nargs="?", help="Archivo de audio")
    parser.add_argument(
        "--amt",
        default=DEFAULT_AMT_ADAPTER,
        choices=REGISTRO_ADAPTADORES.keys(),
        help="Selección del motor AMT",
    )
    parser.add_argument(
        "--csv", type=Path, nargs="?", help="CSV de referencia o a evaluar"
    )

    return parser


if __name__ == "__main__":
    parser = _make_parser()
    args = parser.parse_args()
    main(args)
