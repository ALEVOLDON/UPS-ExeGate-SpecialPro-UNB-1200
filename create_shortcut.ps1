# Creates a desktop shortcut that works after moving the project folder.
# Run from the project directory:  powershell -ExecutionPolicy Bypass -File .\create_shortcut.ps1

$ErrorActionPreference = "Stop"

$WorkDir = $PSScriptRoot
if (-not $WorkDir) {
    $WorkDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}

$AppScriptPath = Join-Path $WorkDir "desktop_app.py"
if (-not (Test-Path $AppScriptPath)) {
    Write-Error "desktop_app.py not found in: $WorkDir"
}

function Find-Pythonw {
    # 1) pythonw on PATH
    $cmd = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source) { return @{ Exe = $cmd.Source; Args = "`"$AppScriptPath`"" } }

    # 2) Windows py launcher (windowless: -3w)
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py -and $py.Source) { return @{ Exe = $py.Source; Args = "-3w `"$AppScriptPath`"" } }

    # 3) Common install locations
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\pythonw.exe",
        "$env:ProgramFiles\Python313\pythonw.exe",
        "$env:ProgramFiles\Python312\pythonw.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return @{ Exe = $c; Args = "`"$AppScriptPath`"" } }
    }
    return $null
}

$pyInfo = Find-Pythonw
if (-not $pyInfo) {
    Write-Error "Could not find pythonw/py. Install Python 3 and re-run this script."
}

$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "ExeGate UPS Monitor.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $pyInfo.Exe
$Shortcut.Arguments = $pyInfo.Args
$Shortcut.WorkingDirectory = $WorkDir
$Shortcut.Description = "ExeGate UNB-1200 UPS Monitoring Application"
$Shortcut.IconLocation = "$($pyInfo.Exe),0"
$Shortcut.Save()

Write-Host "Desktop shortcut created:"
Write-Host "  $ShortcutPath"
Write-Host "  Target : $($pyInfo.Exe) $($pyInfo.Args)"
Write-Host "  WorkDir: $WorkDir"
