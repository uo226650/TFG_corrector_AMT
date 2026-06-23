class AudioValidationError(Exception):
    """Excepción base para todos los tipos de errores relativos a la validación del audio de entrada"""

    pass


class AudioNotFoundError(AudioValidationError):
    pass


class AudioFormatError(AudioValidationError):
    pass


class AudioDurationError(AudioValidationError):
    pass


class AudioSilentError(AudioValidationError):
    pass
