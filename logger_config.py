import os
import sys
import logging
from datetime import datetime
from contextlib import redirect_stderr, redirect_stdout, contextmanager
from io import StringIO


def setup_logging():

    # Carpeta para logs y formato de nombre
    log_dirname = "logs"
    os.makedirs(log_dirname, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    log_filename = f"{log_dirname}/{timestamp}.log"

    main_logger = logging.getLogger()
    # main_logger.setLevel(logging.DEBUG)
    main_logger.setLevel(logging.INFO)
    if main_logger.hasHandlers():
        main_logger.handlers.clear()  # Evitar duplicados

    # Formato para archivos de log
    formato_log = logging.Formatter(
        "%(asctime)s - [%(levelname)s]- %(name)s: %(message)s"
    )
    log_handler = logging.FileHandler(log_filename, encoding="utf-8")
    log_handler.setFormatter(formato_log)
    main_logger.addHandler(log_handler)

    # Formato para consola
    formato_consola = logging.Formatter("[%(levelname)s] %(message)s")
    consola_handler = logging.StreamHandler(sys.stdout)
    consola_handler.setFormatter(formato_consola)
    main_logger.addHandler(consola_handler)


@contextmanager
def capturar_prints(logger: logging.Logger, tool: str):
    """
    Captura prints de librerías externas para añadir al log de la aplicación.

    Args:
        logger: objeto Logger que recoge los prints
        tool: etiqueta para indicar el origen del print (ayuda a filtrar logs)

    Use:
        >>> with capturar_prints(amt_logger, "[basic-pitch]"):
        >>>     predict_and_save(...)

    Output example:
        2026-06-28 05:23:18,273 - [INFO]- src.etapas.adaptador_AMT: [basic-pitch] Creating note events...
    """
    buf = StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        yield
    for line in buf.getvalue().splitlines():
        if line.strip():
            logger.info("%s %s", tool, line)
