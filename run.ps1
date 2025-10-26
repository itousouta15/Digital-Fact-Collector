# run.ps1 — 一鍵建立 venv、安裝相依並執行 quote_collector.py
# Usage: 在專案根目錄執行本腳本（PowerShell）

$ErrorActionPreference = 'Stop'

Write-Host "== Digital-Fact-Collector: run.ps1 ==" -ForegroundColor Cyan

# 找出可用的 python
$pythonCmd = $null
$pyCmd = (Get-Command py -ErrorAction SilentlyContinue)
if ($pyCmd) {
    # 使用 py launcher 優先指定 py -3（若可用）
    $pythonCmd = "py -3"
    Write-Host "Using launcher: py -3" -ForegroundColor Green
} else {
    $python = (Get-Command python -ErrorAction SilentlyContinue)
    if ($python) {
        $pythonCmd = $python.Source
        Write-Host "Using python: $pythonCmd" -ForegroundColor Green
    }
}

if (-not $pythonCmd) {
    Write-Host "No python found in PATH. Please install Python from https://python.org/downloads/ and try again." -ForegroundColor Red
    exit 1
}

# 建立或重新建立 venv（使用目前找到的 python，確保 venv 與該 python 一致）
Write-Host "Creating/updating virtual environment .venv using: $pythonCmd" -ForegroundColor Yellow
try {
    & $pythonCmd -m venv .venv --clear
} catch {
    # 若 venv module 不可用，嘗試不用 --clear
    & $pythonCmd -m venv .venv
}

# 決定 venv 中的 python 路徑：嘗試常見位置，若找不到就在 .venv 下遞迴尋找 python 可執行檔
$venvPython = $null
$candidates = @(
    ".\\.venv\\Scripts\\python.exe",
    ".\\.venv\\bin\\python.exe",
    ".\\.venv\\Scripts\\python3.exe",
    ".\\.venv\\bin\\python3.exe"
)
foreach ($c in $candidates) {
    if (Test-Path $c) { $venvPython = $c; break }
}

if (-not $venvPython) {
    # 嘗試遞迴搜尋任何 python*.exe
    $found = Get-ChildItem -Path ".\.venv" -Filter "python*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $venvPython = $found.FullName }
}

if (-not $venvPython) {
    Write-Host "Could not find python executable inside .venv. The venv creation may have failed or files are not accessible." -ForegroundColor Red
    exit 1
}

Write-Host "Using venv python: $venvPython" -ForegroundColor Green

# 安裝相依（若有 requirements.txt）
if (Test-Path "requirements.txt") {
    Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Yellow
    & $venvPython -m pip install --upgrade pip setuptools wheel
    & $venvPython -m pip install -r requirements.txt
} else {
    Write-Host "No requirements.txt found — skipping pip install." -ForegroundColor Yellow
}

# 執行主腳本
Write-Host "Running quote_collector.py..." -ForegroundColor Cyan
& $venvPython .\quote_collector.py

Write-Host "Done." -ForegroundColor Cyan
