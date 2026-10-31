param(
  [Parameter(Mandatory = $true)][string]$Out,
  [Parameter(Mandatory = $true)][string]$ExpectTitle
)

# Captures a Chrome window (browser chrome + address bar included) to a PNG.
#
# The page under test sets a unique marker in document.title, so this script
# can find exactly the right window even when several Chrome windows are open.
# It raises that window, verifies it is really in front, then grabs the screen
# region it occupies. PrintWindow is tried first because it works even when the
# window is occluded; a screen grab is the fallback.
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class WinCap {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint flags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool attach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
  [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int maxCount);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr context);
}
"@

# Without this, Windows reports logical (scaled) window sizes and PrintWindow
# returns a downscaled frame, which makes the address bar blurry.
try {
  [void][WinCap]::SetProcessDpiAwarenessContext([IntPtr]-4)   # PER_MONITOR_AWARE_V2
} catch {
  [void][WinCap]::SetProcessDPIAware()
}

function Get-Title([IntPtr]$handle) {
  $length = [WinCap]::GetWindowTextLength($handle)
  if ($length -le 0) { return "" }
  $builder = New-Object System.Text.StringBuilder ($length + 1)
  [void][WinCap]::GetWindowText($handle, $builder, $builder.Capacity)
  return $builder.ToString()
}

function Count-Colors([System.Drawing.Bitmap]$bmp) {
  $colors = New-Object 'System.Collections.Generic.HashSet[int]'
  for ($px = 0; $px -lt $bmp.Width; $px += 9) {
    for ($py = 0; $py -lt $bmp.Height; $py += 9) {
      [void]$colors.Add($bmp.GetPixel($px, $py).ToArgb())
    }
  }
  return $colors.Count
}

function Force-Foreground([IntPtr]$handle) {
  if ([WinCap]::IsIconic($handle)) { [void][WinCap]::ShowWindow($handle, 9) }  # SW_RESTORE

  $foreground = [WinCap]::GetForegroundWindow()
  $foregroundPid = 0
  $foregroundThread = [WinCap]::GetWindowThreadProcessId($foreground, [ref]$foregroundPid)
  $targetPid = 0
  $targetThread = [WinCap]::GetWindowThreadProcessId($handle, [ref]$targetPid)

  if ($foregroundThread -ne $targetThread) {
    [void][WinCap]::AttachThreadInput($foregroundThread, $targetThread, $true)
    [void][WinCap]::BringWindowToTop($handle)
    [void][WinCap]::SetForegroundWindow($handle)
    [void][WinCap]::AttachThreadInput($foregroundThread, $targetThread, $false)
  } else {
    [void][WinCap]::BringWindowToTop($handle)
    [void][WinCap]::SetForegroundWindow($handle)
  }

  # Windows blocks SetForegroundWindow unless the caller "just received input".
  if ([WinCap]::GetForegroundWindow() -ne $handle) {
    [void][WinCap]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)   # ALT down
    [void][WinCap]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)   # ALT up
    [void][WinCap]::SetForegroundWindow($handle)
  }
}

$hwnd = [IntPtr]::Zero
$title = ""
for ($attempt = 1; $attempt -le 20; $attempt++) {
  foreach ($candidate in (Get-Process chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 })) {
    $candidateTitle = Get-Title $candidate.MainWindowHandle
    if ($candidateTitle.IndexOf($ExpectTitle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
      $hwnd = $candidate.MainWindowHandle
      $title = $candidateTitle
      break
    }
  }
  if ($hwnd -ne [IntPtr]::Zero) { break }
  Start-Sleep -Milliseconds 400
}

if ($hwnd -eq [IntPtr]::Zero) {
  Write-Error "No Chrome window titled like '$ExpectTitle'."
  exit 1
}

$rect = New-Object WinCap+RECT
[void][WinCap]::GetWindowRect($hwnd, [ref]$rect)
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
if ($width -le 100 -or $height -le 100) {
  Write-Error "Chrome window has no usable size ($width x $height)."
  exit 1
}

# --- 1st choice: PrintWindow (independent of z-order) ------------------------
$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$hdc = $graphics.GetHdc()
$printed = [WinCap]::PrintWindow($hwnd, $hdc, 2)   # PW_RENDERFULLCONTENT
$graphics.ReleaseHdc($hdc)
$graphics.Dispose()
$mode = "printwindow"
$unique = Count-Colors $bitmap

# --- 2nd choice: raise the window and copy its pixels off the screen ---------
if (-not $printed -or $unique -lt 40) {
  $bitmap.Dispose()
  $mode = "screengrab"

  for ($attempt = 1; $attempt -le 6; $attempt++) {
    Force-Foreground $hwnd
    Start-Sleep -Milliseconds 450
    if ([WinCap]::GetForegroundWindow() -eq $hwnd) { break }
    Start-Sleep -Milliseconds 250
  }

  $vs = [System.Windows.Forms.SystemInformation]::VirtualScreen
  $x = [Math]::Max($rect.Left, $vs.X)
  $y = [Math]::Max($rect.Top, $vs.Y)
  $w = [Math]::Min($width, $vs.Right - $x)
  $h = [Math]::Min($height, $vs.Bottom - $y)

  $bitmap = New-Object System.Drawing.Bitmap $w, $h
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $graphics.CopyFromScreen($x, $y, 0, 0, $bitmap.Size)
  $graphics.Dispose()
  $unique = Count-Colors $bitmap
  $width = $w
  $height = $h
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Out) | Out-Null
$bitmap.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bitmap.Dispose()

$front = [WinCap]::GetForegroundWindow() -eq $hwnd
Write-Output ("captured {0} {1}x{2} uniqueColors={3} mode={4} front={5} title='{6}'" -f $Out, $width, $height, $unique, $mode, $front, $title)
