
# Evaluación y corrección automática de transcripciones melódicas de canto monofónico
### Autor
Rocío Cenador Martínez

## Descripción
Evaluación y corrección automática de transcripciones melódicas de canto monofónico.

## Instalación
Este proyecto usa [uv] para dependencias

Requiere Python 3.10

```
git clone https://github.com/uo226650/TFG_corrector_AMT.git
cd vocal_amt_corrector
uv sync
```
## Uso

#### Command Line Tool

Interfaz por línea de comandos. Para transcribir, corregir y evaluar una transcripción de un audio `<ruta-archivo-audio>` :

```
uv run python main.py  <ruta-archivo-audio>
```

Ejemplo: 
```
uv run python main.py audios/melodía.mp3
```
Opcionalmente se podrán incluir las siguientes flags para ejecutar etapas específicas de la pipeline por separado:

- [future release] `--transcribir` para ejecutar únicamente la transcripción de un audio.
- [future release] `--evaluar` para ejecutar únicamente el evaluador.
-  `--run` para especificar que deseas ejecutar la pipeline completa (comportamiento por defecto si no se incluye ningún comando).

Para más ayuda:

```bash
main.py --help
```