Param(
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [switch]$NoCompose
)

Write-Host "[smoke] starting wrapper"

if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql+psycopg://user:sintetica@localhost:5432/girardot"
    Write-Host "[smoke] DATABASE_URL not provided. Using default: $DatabaseUrl"
}

# Optional: bring up DB using docker compose if not disabled
if (-not $NoCompose) {
    try {
        Write-Host "[smoke] ensuring docker compose db is up"
        docker compose up -d db | Out-Null
    } catch {
        Write-Warning "[smoke] docker compose not available or failed. Continuing assuming DB is up..."
    }
}

# Ensure venv exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -U pip | Out-Null
if (Test-Path ".\constraints.txt") {
    pip install -r requirements.txt -c constraints.txt | Out-Null
} else {
    pip install -r requirements.txt | Out-Null
}

$env:DATABASE_URL = $DatabaseUrl

# Apply migrations
Write-Host "[smoke] applying migrations"
python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Error "[smoke] alembic upgrade failed"
    exit 1
}

# Run smoke python helper
Write-Host "[smoke] running smoke flow"
python .\scripts\smoke.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "[smoke] smoke flow failed"
    exit 1
}

Write-Host "[smoke] done"
