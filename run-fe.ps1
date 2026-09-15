$ErrorActionPreference = "SilentlyContinue"
$log = "$PSScriptRoot\.freebuff\preview-7c5b1513-c8f0-452c-83c3-161e55cb3718.log"
$logErr = "$log.err"
$npmCmd = "npm.cmd"
$workDir = "$PSScriptRoot\frontend"

$psOut = @()
$psOut += "→ starting frontend dev server (npm run dev) in $workDir on port 5174"
$psOut += "  stdout -> $log"
$psOut += "  stderr -> $logErr"

$proc = Start-Process -FilePath $npmCmd `
    -ArgumentList "run", "dev" `
    -WorkingDirectory $workDir `
    -RedirectStandardOutput $log `
    -RedirectStandardError $logErr `
    -WindowStyle Hidden `
    -PassThru

$pid = $proc.Id
$psOut += "  PID $pid"
$psOut += "  waiting for port 5174..."

for ($i = 0; $i -lt 30; $i++) {
    $code = curl.exe -s -o $null -w "%{http_code}" "http://localhost:5174" 2>$null
    $psOut += "    attempt $($i+1): $code"
    if ($code -match "^(200|300|400|401|403|404)$") {
        $psOut += "  frontend responded $code after $($i+1) attempts"
        break
    }
    Start-Sleep -Seconds 1
}

if ($code -notmatch "^(200|300|400|401|403|404)$") {
    $psOut += "  frontend did not respond after 30s"
    $psOut += "  log tail:"
    Get-Content $log -Tail 20 | ForEach-Object { $psOut += $_ }
    $proc | Stop-Process -ErrorAction SilentlyContinue
    exit -1
}

$psOut | ForEach-Object { Write-Host $_ }
Write-Host "  exiting with PID $pid"
exit $pid
