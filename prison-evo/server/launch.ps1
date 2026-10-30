$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
try {
  Write-Host 'HYLOR | Prison Evo - local demo' -ForegroundColor Magenta
  if (-not (Select-String -Path 'eula.txt' -Pattern '^eula=true' -Quiet)) {
    Write-Host 'Minecraft EULA: https://aka.ms/MinecraftEULA'
    $answer = Read-Host 'Have you read and accepted the Minecraft EULA? (Y/N)'
    if ($answer -notmatch '^[Yy]$') { Write-Host 'EULA was not accepted. Server not started.'; exit 0 }
    Set-Content -Encoding ascii -Path 'eula.txt' -Value 'eula=true'
  }
  $java = Get-ChildItem -Path '.runtime' -Filter java.exe -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
  if (-not $java) {
    if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64' -and $env:PROCESSOR_ARCHITEW6432 -ne 'AMD64') { throw 'Automatic Java install requires 64-bit Windows x64.' }
    Write-Host 'Downloading Java 25 (first start only)...'
    New-Item -ItemType Directory -Force -Path '.runtime' | Out-Null
    $archive = Join-Path $PSScriptRoot '.runtime\java.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://api.adoptium.net/v3/binary/latest/25/ga/windows/x64/jre/hotspot/normal/eclipse' -OutFile $archive
    Expand-Archive -Path $archive -DestinationPath '.runtime' -Force
    Remove-Item $archive
    $java = Get-ChildItem -Path '.runtime' -Filter java.exe -Recurse | Select-Object -First 1 -ExpandProperty FullName
  }
  if (-not $java) { throw 'Java 25 was not found after installation.' }
  Write-Host 'Starting server. Connect in Minecraft Java 26.3 to localhost.' -ForegroundColor Green
  & $java '-Xms1G' '-Xmx2G' '-jar' 'paper.jar' '--nogui'
  if ($LASTEXITCODE -ne 0) { Write-Host "Server exited with code $LASTEXITCODE" -ForegroundColor Red }
} catch { Write-Host "Start error: $($_.Exception.Message)" -ForegroundColor Red }
