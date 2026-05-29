# Tesis

Metodología para descubrir expresiones analíticas de sistemas de ecuaciones no lineales usando regresión simbólica con PySR.

## Requisitos

- Python 3.12 o superior
- Julia 1.10 o superior (para PySR)
- Git (opcional, para clonar el repo)

## Instalación

### 1) Clonar y entrar al proyecto

```bash
git clone <URL_DEL_REPO>
cd Tesis
```

### 2) Crear y activar entorno virtual

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

Windows CMD:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r src/requirements.txt
```

### 3) Instalar Julia

1. Instalar Julia desde su instalador oficial.
2. Verificar que el comando julia quede en PATH:

```bash
julia --version
```

## Ejecutar

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python src/main.py
```
