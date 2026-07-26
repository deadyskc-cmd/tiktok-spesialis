# Setup Windows Task Scheduler untuk generate & upload video harian otomatis
# Jalankan sebagai Administrator: right-click -> Run with PowerShell

$TaskName = "FreeFaceless KisahNyata"
$ScriptPath = Join-Path $PSScriptRoot "run_daily.ps1"
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

# Peak hours untuk YouTube Shorts Indonesia (bisa disesuaikan)
$Triggers = @(
    New-ScheduledTaskTrigger -Daily -At 09:00  # pagi
    New-ScheduledTaskTrigger -Daily -At 12:00  # jam makan siang
    New-ScheduledTaskTrigger -Daily -At 15:00  # sore
    New-ScheduledTaskTrigger -Daily -At 19:00  # jam prime time malam
)

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Empat trigger: 1 video tiap jam 09:00, 12:00, 15:00, 19:00
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers -Settings $Settings -RunLevel Highest -Force

Write-Host "`nTask '$TaskName' berhasil dibuat!" -ForegroundColor Green
Write-Host "Jadwal: 09:00, 12:00, 15:00, 19:00 setiap hari -> 4 video/hari" -ForegroundColor Cyan
Write-Host "`nCek di Task Scheduler: taskschd.msc" -ForegroundColor Yellow
