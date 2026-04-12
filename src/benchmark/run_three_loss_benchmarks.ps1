$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $RepoRoot

if (Get-Command py -ErrorAction SilentlyContinue) {
    py -3 src/benchmark/run_three_loss_benchmarks.py
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python src/benchmark/run_three_loss_benchmarks.py
} else {
    throw "No se encontró py ni python en PATH."
}
