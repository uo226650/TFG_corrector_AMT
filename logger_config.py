import os
import sys
import logging
from datetime import datetime


def setup_logging():

    # Carpeta para logs y formato de nombre
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    log_filename = f"logs/{timestamp}.log"

    main_logger = logging.getLogger()
    # main_logger.setLevel(logging.DEBUG)
    main_logger.setLevel(logging.INFO)

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
