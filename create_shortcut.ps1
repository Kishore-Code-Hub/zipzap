$WshShell = New-Object -comObject WScript.Shell
$TargetFolder = $PWD.Path
$ShortcutPath = Join-Path $TargetFolder "ZipZap.lnk"
$ExePath = Join-Path $TargetFolder "ZipZap.exe"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $ExePath
$Shortcut.WorkingDirectory = $TargetFolder
$Shortcut.Save()

Write-Host "Shortcut created at $ShortcutPath"
