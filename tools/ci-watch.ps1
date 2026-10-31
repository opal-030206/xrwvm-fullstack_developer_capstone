param(
  [Parameter(Mandatory = $true)][string]$Token,
  [string]$Repo = "opal-030206/Capstone_carDealership",
  [string]$RunId = "41175397969"
)

$ErrorActionPreference = "Stop"
$headers = @{ Authorization = "Bearer $Token"; "User-Agent" = "capstone-ci-watch"; Accept = "application/vnd.github+json" }
$outDir = Join-Path $PSScriptRoot "..\submission\ci-logs"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

Write-Output "watching run $RunId in $Repo"
$run = $null
for ($i = 1; $i -le 120; $i++) {
  Start-Sleep -Seconds 15
  $run = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/actions/runs/$RunId" -Headers $headers
  Write-Output ("[{0}] status={1} conclusion={2}" -f $i, $run.status, $run.conclusion)
  if ($run.status -eq "completed") { break }
}

if ($run.status -ne "completed") {
  Write-Output "TIMEOUT waiting for run to complete"
  exit 2
}

$run | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 (Join-Path $outDir "run.json")

$jobs = (Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/actions/runs/$RunId/jobs" -Headers $headers).jobs
$summary = foreach ($j in $jobs) { [pscustomobject]@{ id = $j.id; name = $j.name; conclusion = $j.conclusion; started = $j.started_at; finished = $j.completed_at } }
$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding utf8 (Join-Path $outDir "jobs.json")

foreach ($j in $jobs) {
  $safe = ($j.name -replace "[^A-Za-z0-9]+", "-").Trim("-").ToLower()
  $path = Join-Path $outDir ("job-" + $safe + ".log")
  try {
    Invoke-WebRequest -Uri "https://api.github.com/repos/$Repo/actions/jobs/$($j.id)/logs" -Headers $headers -OutFile $path -UseBasicParsing
    Write-Output ("saved log for '{0}' -> {1}" -f $j.name, $path)
  }
  catch {
    Write-Output ("could not fetch log for '{0}': {1}" -f $j.name, $_.Exception.Message)
  }
}

Write-Output ("RUN_CONCLUSION=" + $run.conclusion)
Write-Output ("RUN_URL=" + $run.html_url)
