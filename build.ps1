$ErrorActionPreference = "Stop"

$python = ".\.venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Python virtual environment not found at $python"
}

& $python -m PyInstaller --clean --onefile --name dx-sub .\main.py
