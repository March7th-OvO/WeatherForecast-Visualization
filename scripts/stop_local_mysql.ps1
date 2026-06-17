$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$localRoot = Join-Path $projectRoot ".mysql-local"
$pidFile = Join-Path $localRoot "mysqld-3307.pid"

if (Test-Path $pidFile) {
    $mysqlPid = Get-Content $pidFile | Select-Object -First 1
    $process = Get-Process -Id $mysqlPid -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $mysqlPid -Force
        Write-Output "Stopped local MySQL process $mysqlPid"
    }
    Remove-Item $pidFile -Force
} else {
    $connection = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
    if ($connection) {
        Stop-Process -Id $connection.OwningProcess -Force
        Write-Output "Stopped local MySQL process $($connection.OwningProcess)"
    } else {
        Write-Output "No local MySQL pid file found"
    }
}
