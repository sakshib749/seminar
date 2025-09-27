param(
    [string]$url = "https://www.example.com",
    [switch]$Verbose,
    [switch]$NoCalibrate,
    [string]$Model = ""
)

# Activate venv (no error if not present)
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    . .\.venv\Scripts\Activate.ps1
}

$cmd = "python predict.py $url"
if ($Verbose) { $cmd += " --verbose" }
if ($NoCalibrate) { $cmd += " --no-calibrate" }
if ($Model -ne "") { $cmd += " --model $Model" }

Write-Host "Running: $cmd"
Invoke-Expression $cmd
