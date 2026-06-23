# Full public data sync wrapper
$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$python = Join-Path $projectRoot "townenv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  $python = Join-Path $projectRoot "com.pulse\.venv\Scripts\python.exe"
}
if (-not (Test-Path $python)) {
  $python = "python"
}
$env:PYTHONUNBUFFERED = "1"
& $python (Join-Path $projectRoot "com.pulse\scripts\run_full_sync.py")
