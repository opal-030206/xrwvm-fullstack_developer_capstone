param(
  [Parameter(Mandatory = $true)][string]$WindowPath,
  [Parameter(Mandatory = $true)][string]$PagePath
)

# Objective check that a window capture really contains the page content.
#
# Both images are reduced to a coarse grayscale grid. The page grid is then
# slid down the window grid; if the window capture contains the page, a strong
# match appears at the offset occupied by the browser chrome (address bar).
Add-Type -AssemblyName System.Drawing

function Get-Grid([string]$path, [int]$step) {
  $bmp = [System.Drawing.Bitmap]::FromFile((Resolve-Path $path))
  $w = [int]($bmp.Width / $step)
  $h = [int]($bmp.Height / $step)
  $values = New-Object 'double[]' ($w * $h)
  for ($gx = 0; $gx -lt $w; $gx++) {
    for ($gy = 0; $gy -lt $h; $gy++) {
      $c = $bmp.GetPixel($gx * $step, $gy * $step)
      $values[($gy * $w) + $gx] = ($c.R * 0.299 + $c.G * 0.587 + $c.B * 0.114)
    }
  }
  $info = @{ Width = $w; Height = $h; Pixels = $bmp.Width; PixelH = $bmp.Height }
  $bmp.Dispose()
  return @{ Values = $values; Meta = $info }
}

$winGrid = Get-Grid $WindowPath 8
$pageGrid = Get-Grid $PagePath 8

$cols = [Math]::Min(160, [Math]::Min($winGrid.Meta.Width, $pageGrid.Meta.Width))
$maxOffset = [Math]::Min(40, $winGrid.Meta.Height - 10)
$bestOffset = 0
$bestDiff = 1e9
$baseDiff = 0.0

for ($offset = 0; $offset -le $maxOffset; $offset++) {
  $rows = [Math]::Min($pageGrid.Meta.Height, $winGrid.Meta.Height - $offset)
  if ($rows -lt 20) { continue }
  $sum = 0.0
  $n = 0
  for ($gx = 0; $gx -lt $cols; $gx += 2) {
    for ($gy = 0; $gy -lt $rows; $gy += 2) {
      $winIndex = (($gy + $offset) * $winGrid.Meta.Width) + $gx
      $pageIndex = ($gy * $pageGrid.Meta.Width) + $gx
      $sum += [Math]::Abs($winGrid.Values[$winIndex] - $pageGrid.Values[$pageIndex])
      $n++
    }
  }
  $mean = $sum / $n
  if ($offset -eq 0) { $baseDiff = $mean }
  if ($mean -lt $bestDiff) {
    $bestDiff = $mean
    $bestOffset = $offset
  }
}

Write-Output ("window={0}x{1} page={2}x{3}" -f $winGrid.Meta.Pixels, $winGrid.Meta.PixelH, $pageGrid.Meta.Pixels, $pageGrid.Meta.PixelH)
Write-Output ("bestOffsetPx={0} meanAbsDiff={1}  (offset0 diff={2})" -f ($bestOffset * 8), [Math]::Round($bestDiff, 2), [Math]::Round($baseDiff, 2))

if ($bestDiff -lt ($baseDiff * 0.6) -and $bestOffset * 8 -ge 40 -and $bestOffset * 8 -le 160) {
  Write-Output "VERDICT: window capture contains the page below $($bestOffset * 8)px of browser chrome"
  exit 0
}
Write-Output "VERDICT: could not confirm page content in window capture"
exit 2
