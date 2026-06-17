$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$mysqlRoot = "E:\Mysql\MySQL Server 8.0"
$mysqlBin = Join-Path $mysqlRoot "bin\mysqld.exe"
$mysqlCli = Join-Path $mysqlRoot "bin\mysql.exe"
$localRoot = Join-Path $projectRoot ".mysql-local"
$dataDir = Join-Path $localRoot "data"
$pidFile = Join-Path $localRoot "mysqld-3307.pid"
$port = 3307

New-Item -ItemType Directory -Force $localRoot | Out-Null

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Force $dataDir | Out-Null
}

$isInitialized = Test-Path (Join-Path $dataDir "mysql")
if (-not $isInitialized) {
    & $mysqlBin "--initialize-insecure" "--basedir=$mysqlRoot" "--datadir=$dataDir"
}

$existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($existing) {
    Set-Content -Path $pidFile -Value $existing.OwningProcess
    Write-Output "Local MySQL already listening on port $port"
    exit 0
}

$proc = Start-Process -FilePath $mysqlBin -ArgumentList @(
    "`"--basedir=$mysqlRoot`"",
    "`"--datadir=$dataDir`"",
    "--port=$port",
    "--bind-address=127.0.0.1",
    "--mysqlx=0"
) -WindowStyle Hidden -PassThru

Start-Sleep -Seconds 5

& $mysqlCli -h 127.0.0.1 -P $port -u root -e "SELECT 1 AS ok;" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Local MySQL did not start correctly on port $port"
}

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Set-Content -Path $pidFile -Value $listener.OwningProcess
}

& $mysqlCli -h 127.0.0.1 -P $port -u root -e "CREATE USER IF NOT EXISTS 'weatherapp'@'127.0.0.1' IDENTIFIED BY 'weatherapp123'; GRANT ALL PRIVILEGES ON *.* TO 'weatherapp'@'127.0.0.1'; FLUSH PRIVILEGES;"

Write-Output "Local MySQL started on 127.0.0.1:$port"
