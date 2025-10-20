Param(
    [string]$DatabaseUrl = $env:DATABASE_URL
)

if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
    Write-Host "DATABASE_URL not set. Using default: $DatabaseUrl"
}

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt

$env:DATABASE_URL = $DatabaseUrl
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
