<#
.SYNOPSIS
    Parkir Camera Service - Installer v3
.DESCRIPTION
    Install/update/uninstall RTSP camera service.
    Supports: snapshot (JPEG) + video recording (AVI).
#>

param([switch]$Install,[switch]$Update,[switch]$Uninstall,[switch]$Status,[switch]$Silent,[int]$Port=5050,[string]$RtspUrl="rtsp://admin:akatsuki86@192.168.1.81:554/Streaming/Channels/102",[string]$FotoDir="Z:\Foto_Masuk",[string]$VideoDir="Z:\Video_Keluar")

$ErrorActionPreference = "Continue"
$script:PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServiceDir = $script:PSScriptRoot
. (Join-Path $ServiceDir "..\parkir-installer\shared.ps1")

$ServiceName = "ParkirVideoRecorder"; $DisplayName = "Parkir Camera Service"

function Do-Status { try { $s=Get-Service $ServiceName -ErrorAction Stop; Write-Host "  ${DisplayName}: $($s.Status)" -ForegroundColor $(if($s.Status-eq"Running"){"Green"}else{"Red"}) } catch { Write-Host "  ${DisplayName}: BELUM TERINSTALL" -ForegroundColor DarkGray } }
function Do-Uninstall { wStep "Uninstall ${DisplayName}..."; try { $s=Get-Service $ServiceName -ErrorAction SilentlyContinue; if($s){if($s.Status-eq"Running"){Stop-Service $ServiceName -Force};& $script:NssmExe remove $ServiceName confirm 2>&1|Out-Null;wOK "Service removed"} } catch { wErr "Gagal: $_" } }
function Do-Update { wStep "Update ${DisplayName}..."; if(Test-Path (Join-Path $ServiceDir ".git")){Push-Location $ServiceDir;git pull 2>&1|Out-Null;Pop-Location;wOK "Git pull OK"};$pip=Join-Path $ServiceDir "venv\Scripts\pip.exe";if(Test-Path $pip){& $pip install -r (Join-Path $ServiceDir "requirements.txt") --quiet 2>&1|Out-Null};try{Restart-Service $ServiceName -Force;wOK "Restarted"}catch{Start-Service $ServiceName -ErrorAction SilentlyContinue} }

function Do-Install {
    wStep "Install ${DisplayName}..."

    if (-not $Silent) {
        Write-Host ""; Write-Host "Konfigurasi Camera Service:" -ForegroundColor Yellow
        $p=Read-Host "  Port [${Port}]"; if($p){$Port=[int]$p}
        $r=Read-Host "  RTSP URL [default]"; if($r){$RtspUrl=$r}
        Write-Host "  Output folder:" -ForegroundColor DarkGray
        $f=Read-Host "    Foto (snapshot) [${FotoDir}]"; if($f){$FotoDir=$f}
        $v=Read-Host "    Video (recording) [${VideoDir}]"; if($v){$VideoDir=$v}
    }

    $cfg = Join-Path $ServiceDir "config.yaml"
    $content = @"
server:
  port: ${Port}
  host: 127.0.0.1
camera:
  rtsp_url: ${RtspUrl}
  fps: 25
  width: 1280
  height: 720
  buffer_seconds: 10
paths:
  foto_dir: ${FotoDir}
  output_dir: ${VideoDir}
"@
    [System.IO.File]::WriteAllText($cfg, $content, (New-Object System.Text.UTF8Encoding($false)))
    wOK "config.yaml dibuat"

    $venvPath = Join-Path $ServiceDir "venv"; if(-not(Test-Path $venvPath)){python -m venv $venvPath 2>&1|Out-Null;wOK "venv dibuat"}
    $pip=Join-Path $venvPath "Scripts\pip.exe"; if(Test-Path (Join-Path $ServiceDir "requirements.txt")){wStep "Install deps..."; & $pip install -r (Join-Path $ServiceDir "requirements.txt") 2>&1|Out-Null;wOK "Dependencies OK"}
    $logDir=Join-Path $ServiceDir "logs"; if(-not(Test-Path $logDir)){New-Item -ItemType Directory -Path $logDir -Force|Out-Null}

    wStep "Register NSSM service..."
    $py=Join-Path $venvPath "Scripts\python.exe"; $main=Join-Path $ServiceDir "src\recording_service.py"
    Register-Service $ServiceName $py "`"$main`"" $DisplayName "Camera service: snapshot + video recording" (Join-Path $logDir "service.log") (Join-Path $logDir "error.log") $ServiceDir
    wOK "Service registered"

    if(Start-ServiceSafe $ServiceName){wOK "RUNNING - http://localhost:${Port}/status"}else{wWarn "Cek log"}

    Write-Host ""; Write-Host "  Endpoints:" -ForegroundColor Cyan
    Write-Host "    Snapshot : GET /snapshot?notrans=..." -ForegroundColor White
    Write-Host "    Record   : GET /start?notrans=... /stop?notrans=..." -ForegroundColor White
    Write-Host "    Status   : GET /status" -ForegroundColor White
}

if($Uninstall){Do-Uninstall}elseif($Update){Do-Update}elseif($Status){Do-Status|Out-Null}else{Do-Install}
