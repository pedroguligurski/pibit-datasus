# Instruções rápidas

Este repositório contém um sistema para processar os arquivos
fornecidos.

## Pré-requisitos

-   Python 3.8+ instalado

## Passos (do zero)

### 1. (Opcional) Crie e ative um ambiente virtual

**Windows (PowerShell):**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux (Terminal):**

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instale as dependências

**Windows:**

``` powershell
python -m pip install -r .\requirements.txt
```

**macOS / Linux:**

``` bash
python3 -m pip install -r requirements.txt
```

> Caso `pip3` não esteja disponível, utilize `pip`.

### 3. Execute o programa principal

**Windows:**

``` powershell
python .\src\main.py
```

**macOS / Linux:**

``` bash
python3 src/main.py
```

> Se o comando `python3` não existir no seu ambiente, utilize `python`.

------------------------------------------------------------------------

Pronto! O sistema será iniciado executando `src/main.py`.
