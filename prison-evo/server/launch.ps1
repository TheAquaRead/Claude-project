$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-Location $PSScriptRoot

function Test-JavaRuntime([string]$JavaPath) {
  if (-not $JavaPath -or -not (Test-Path -LiteralPath $JavaPath -PathType Leaf)) { return $false }
  $bin = Split-Path -Parent $JavaPath
  foreach ($required in @('java.dll', 'jli.dll', 'server\jvm.dll')) {
    if (-not (Test-Path -LiteralPath (Join-Path $bin $required) -PathType Leaf)) { return $false }
  }
  try {
    $proc = Start-Process -FilePath $JavaPath -ArgumentList '-version' -Wait -PassThru -NoNewWindow
    return ($proc.ExitCode -eq 0)
  } catch { return $false }
}

try {
  Write-Host 'HYLOR | Prison Evo - local demo' -ForegroundColor Magenta
  if (-not (Select-String -Path 'eula.txt' -Pattern '^eula=true' -Quiet)) {
    Write-Host 'Minecraft EULA: https://aka.ms/MinecraftEULA'
    $answer = Read-Host 'Have you read and accepted the Minecraft EULA? (Y/N)'
    if ($answer -notmatch '^[Yy]$') { Write-Host 'EULA was not accepted. Server not started.'; exit 0 }
    Set-Content -Encoding ascii -Path 'eula.txt' -Value 'eula=true'
  }
  if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64' -and $env:PROCESSOR_ARCHITEW6432 -ne 'AMD64') { throw 'Automatic Java installation requires 64-bit Windows x64.' }
  # The public folder normally has an ASCII-only path even when the user's profile
  # or extracted server directory contains non-Latin characters.
  $runtimeRoot = Join-Path $env:PUBLIC 'HylorPrisonEvo\Java25'
  New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
  $java = $null
  $candidates = Get-ChildItem -LiteralPath $runtimeRoot -Filter java.exe -Recurse -File -ErrorAction SilentlyContinue
  foreach ($candidate in $candidates) {
    if (Test-JavaRuntime $candidate.FullName) { $java = $candidate.FullName; break }
  }
  if (-not $java) {
    Write-Host 'Downloading a complete Java 25 runtime. This is needed once...' -ForegroundColor Cyan
    $stage = Join-Path $runtimeRoot ('install-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    $archive = Join-Path $stage 'java.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://api.adoptium.net/v3/binary/latest/25/ga/windows/x64/jre/hotspot/normal/eclipse' -OutFile $archive
    Expand-Archive -LiteralPath $archive -DestinationPath $stage -Force
    $candidates = Get-ChildItem -LiteralPath $stage -Filter java.exe -Recurse -File
    foreach ($candidate in $candidates) {
      if (Test-JavaRuntime $candidate.FullName) { $java = $candidate.FullName; break }
    }
    if (-not $java) { throw 'The downloaded Java installation is incomplete or could not run. Check antivirus quarantine and retry.' }
    Remove-Item -LiteralPath $archive -ErrorAction SilentlyContinue
  }
  Write-Host 'Starting server. Connect in Minecraft Java 26.3 to localhost.' -ForegroundColor Green
  & $java '-Xms1G' '-Xmx2G' '-jar' 'paper.jar' '--nogui'
  if ($LASTEXITCODE -ne 0) { Write-Host "Server exited with code $LASTEXITCODE" -ForegroundColor Red }
} catch { Write-Host "Start error: $($_.Exception.Message)" -ForegroundColor Red }
