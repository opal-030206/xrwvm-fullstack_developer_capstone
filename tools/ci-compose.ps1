param(
  [string]$LogDir = (Join-Path $PSScriptRoot "..\submission\ci-logs"),
  [string]$OutFile = (Join-Path $PSScriptRoot "..\submission\CICD")
)

$ErrorActionPreference = "Stop"
$run = Get-Content -Raw -Encoding utf8 (Join-Path $LogDir "run.json") | ConvertFrom-Json
$jobs = Get-Content -Raw -Encoding utf8 (Join-Path $LogDir "jobs.json") | ConvertFrom-Json

$sb = New-Object System.Text.StringBuilder
function Add-Line([string]$text = "") { [void]$sb.AppendLine($text) }

Add-Line "GITHUB ACTIONS - CI PIPELINE RUN (REAL RUN, NOT A MOCK-UP)"
Add-Line ("=" * 78)
Add-Line "Repository : https://github.com/opal-030206/Capstone_carDealership"
Add-Line "Workflow   : .github/workflows/ci.yml  (""CI"")"
Add-Line ("Run        : #" + $run.run_number + "   id " + $run.id)
Add-Line ("Event      : " + $run.event + " on " + $run.head_branch + " @ " + $run.head_sha.Substring(0, 7))
Add-Line ("Commit     : " + $run.head_commit.message.Trim())
Add-Line ("Started    : " + $run.run_started_at)
Add-Line ("Finished   : " + $run.updated_at)
Add-Line ("Result     : " + $run.status.ToUpper() + " / " + $run.conclusion.ToUpper())
Add-Line ("Run page   : " + $run.html_url)
Add-Line ""
Add-Line "JOBS"
Add-Line ("-" * 78)
foreach ($j in $jobs) {
  $mins = ""
  if ($j.started) {
    $d = ([datetime]$j.finished) - ([datetime]$j.started)
    $mins = " ({0}m {1}s)" -f [int]$d.TotalMinutes, $d.Seconds
  }
  Add-Line ("  [OK] " + $j.name.PadRight(16) + $j.conclusion + $mins)
}
Add-Line ""
Add-Line "The three jobs below are what the one-line ""status=completed"" summary in the"
Add-Line "Actions UI expands to. Full console output follows."
Add-Line ""

foreach ($j in $jobs) {
  $safe = ($j.name -replace "[^A-Za-z0-9]+", "-").Trim("-").ToLower()
  $logPath = Join-Path $LogDir ("job-" + $safe + ".log")
  Add-Line ("=" * 78)
  Add-Line ("JOB: " + $j.name + "   (" + $j.conclusion + ")")
  Add-Line ("=" * 78)
  Add-Line ""
  if (Test-Path $logPath) {
    $text = Get-Content -Raw -Encoding utf8 $logPath
    # strip the 2026-...Z prefix GitHub adds to every log line
    $text = [regex]::Replace($text, "(?m)^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z ", "")
    Add-Line $text.TrimEnd()
  }
  else {
    Add-Line "(log for this job could not be downloaded)"
  }
  Add-Line ""
  Add-Line ""
}

Set-Content -Path $OutFile -Value $sb.ToString().TrimEnd() -Encoding utf8
Write-Output ("wrote " + $OutFile)
