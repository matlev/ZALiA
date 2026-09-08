param(
    [string]$PythonExecutable,
    [switch]$NoOpen
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$generator = Join-Path $PSScriptRoot 'generate_asset_catalog.py'
$pythonArgs = @()

if (-not $PythonExecutable) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if (Test-Path -LiteralPath $bundledPython) {
        $PythonExecutable = $bundledPython
    } elseif (Get-Command py.exe -ErrorAction SilentlyContinue) {
        $PythonExecutable = (Get-Command py.exe).Source
        $pythonArgs = @('-3')
    } elseif (Get-Command python.exe -ErrorAction SilentlyContinue) {
        $PythonExecutable = (Get-Command python.exe).Source
    } else {
        throw 'Python 3.9+ is required. Pass -PythonExecutable with its executable path.'
    }
}
& $PythonExecutable @pythonArgs $generator --root $repoRoot
if ($LASTEXITCODE -ne 0) { throw 'Catalog generation failed. The previous catalog was not opened.' }
$catalogPath = Join-Path $repoRoot 'dev/generated/asset-catalog/index.html'
if (-not $NoOpen) { Start-Process -FilePath $catalogPath -WindowStyle Hidden }
