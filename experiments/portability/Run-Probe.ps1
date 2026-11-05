param([Parameter(Mandatory=$true)][string]$ModelDirectory)
$ErrorActionPreference = "Stop"
$Models = (Resolve-Path -LiteralPath $ModelDirectory).Path
$Result = Join-Path $PSScriptRoot ("results/windows-x64-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
Push-Location $PSScriptRoot
try {
    foreach ($Name in @("dsp_tests", "pipeline_tests", "api_tests")) {
        & (Join-Path $PSScriptRoot "bin/$Name.exe")
        if ($LASTEXITCODE -ne 0) { throw "$Name failed: $LASTEXITCODE" }
    }
    & py -3 verify_probe.py self-test
    if ($LASTEXITCODE -ne 0) { throw "Verifier controls failed" }
    & py -3 verify_probe.py run bin/pipeline_cli.exe $Models $Result
    if ($LASTEXITCODE -ne 0) { throw "Windows export contracts failed; inspect $Result/report.json" }
    & py -3 verify_probe.py compare reference-mac-arm64 $Result "$Result/comparison.json"
    if ($LASTEXITCODE -ne 0) { throw "Numerical divergence; inspect $Result/comparison.json" }
    Write-Output "Synthetic Windows probe PASS: $Result"
    Write-Output "This does not validate the GUI, devices, sandbox, long projects or listening quality."
} finally {
    Pop-Location
}
