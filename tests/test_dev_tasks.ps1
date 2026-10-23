# Exercise lifecycle safety without calling Docker or changing host resources.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$devScript = Join-Path $PSScriptRoot '../scripts/dev.ps1'
$global:mockChanges = [Collections.Generic.List[object]]::new()
$global:mockPresent = $true
$global:mockForeignVolume = $false
$global:mockDaemonFailure = $false
$global:mockBuildFailure = $false
$global:mockRunning = 'true'

function global:docker {
    $call = @($args)
    $global:LASTEXITCODE = 0
    if ($call[0] -eq 'info') {
        if ($global:mockDaemonFailure) { $global:LASTEXITCODE = 1; return }
        return 'linux'
    }
    if ($call.Count -gt 1 -and $call[1] -eq 'ls') {
        if (!$global:mockPresent) { return }
        switch ($call[0]) {
            'image' { return 'faster-qwen3-tts-studio:dev' }
            'container' { return 'faster-qwen3-tts-studio' }
            'volume' { return 'faster_qwen3_tts_studio_data' }
        }
    }
    if ($call.Count -gt 1 -and $call[1] -eq 'inspect') {
        if ($call -contains '--format') { return $global:mockRunning }
        $labelValue = if ($call[0] -eq 'volume' -and $global:mockForeignVolume) { 'other-project' } else { 'faster-qwen3-tts-studio' }
        $labels = @{ 'app.hangrylabs.project' = $labelValue }
        return ConvertTo-Json -Depth 4 -InputObject @(@{ Config = @{ Labels = $labels }; Labels = $labels; State = @{ Status = 'running' } })
    }
    $global:mockChanges.Add($call)
    if ($call[0] -eq 'build' -and $global:mockBuildFailure) { $global:LASTEXITCODE = 1 }
}

function global:Invoke-RestMethod {
    return @{ default_backend = 'torch' }
}

function Assert-True([bool]$Condition, [string]$Message) {
    if (!$Condition) { throw $Message }
}

function Assert-Fails([string]$Action, [string]$Message) {
    $caught = $false
    try { & $devScript $Action | Out-Null } catch {
        $caught = $true
        Assert-True ($_.Exception.Message -like "*$Message*") "Unexpected failure: $_"
    }
    Assert-True $caught "Expected $Action to fail."
}

$savedSettings = @{}
foreach ($key in @('IMAGE', 'CONTAINER', 'DATA_VOLUME', 'PORT', 'BIND_ADDRESS', 'GPU_DEVICE', 'DEV_MOUNT', 'DRY_RUN')) {
    $name = "QWEN_TASK_$key"
    $savedSettings[$name] = [Environment]::GetEnvironmentVariable($name)
    [Environment]::SetEnvironmentVariable($name, $null)
}
try {
    & $devScript start | Out-Null
    $run = $global:mockChanges[$global:mockChanges.Count - 1]
    Assert-True ($run[0] -eq 'run') 'Start must create a container.'
    Assert-True ($run -contains '127.0.0.1:7860:7860') 'Start must bind locally by default.'
    Assert-True ($run -contains 'CUDA_VISIBLE_DEVICES=0') 'Start must select the configured NVIDIA GPU.'
    Assert-True ($run -contains 'type=volume,src=faster_qwen3_tts_studio_data,dst=/app/persistent') 'Start must persist product data.'
    Assert-True (@($run | Where-Object { $_ -like 'type=bind,*readonly' }).Count -eq 2) 'Source mounts must remain separate native arguments and read-only.'
    $global:mockChanges.Clear()

    & $devScript test-runtime | Out-Null
    $runtime = $global:mockChanges[0]
    Assert-True ($runtime -notcontains '--gpus') 'CPU unit tests must not reserve a GPU.'
    Assert-True (@($runtime | Where-Object { $_ -like '*--ignore=tests/test_e2e_parity.py*' }).Count -eq 1) 'Runtime unit tests must exclude model parity downloads.'
    Assert-True (@($runtime | Where-Object { $_ -like '*src=*' -and $_ -notlike '*,readonly' }).Count -eq 0) 'Test source mounts must be read-only.'
    $global:mockChanges.Clear()

    $global:mockRunning = 'false'
    Assert-Fails start 'Demo exited during startup'
    $global:mockRunning = 'true'
    $global:mockChanges.Clear()

    & $devScript nuke | Out-Null
    Assert-True ($global:mockChanges.Count -eq 3) 'Nuke must change exactly three named resources.'
    Assert-True (($global:mockChanges[0] -join ' ') -eq 'container rm --force faster-qwen3-tts-studio') 'Wrong container cleanup.'
    Assert-True (($global:mockChanges[1] -join ' ') -eq 'image rm faster-qwen3-tts-studio:dev') 'Image removal must not force-delete shared images.'
    Assert-True (($global:mockChanges[2] -join ' ') -eq 'volume rm faster_qwen3_tts_studio_data') 'Wrong volume cleanup.'
    $global:mockChanges.Clear()

    $global:mockForeignVolume = $true
    Assert-Fails nuke 'not labelled'
    Assert-True ($global:mockChanges.Count -eq 0) 'Ownership checks must finish before any removal.'
    $global:mockForeignVolume = $false

    $env:QWEN_TASK_DRY_RUN = '1'
    & $devScript nuke | Out-Null
    Assert-True ($global:mockChanges.Count -eq 0) 'Dry run must not change Docker resources.'
    $env:QWEN_TASK_DRY_RUN = '0'

    $global:mockPresent = $false
    & $devScript stop | Out-Null
    & $devScript nuke | Out-Null
    Assert-True ($global:mockChanges.Count -eq 0) 'Absent resources must be harmless.'

    $global:mockBuildFailure = $true
    Assert-Fails init 'Docker command failed'
    Assert-True ($global:mockChanges.Count -eq 1) 'A failed build must abort before volume creation.'
    $global:mockChanges.Clear()
    $global:mockBuildFailure = $false

    $global:mockDaemonFailure = $true
    Assert-Fails nuke 'Docker command failed'
    Assert-True ($global:mockChanges.Count -eq 0) 'Docker failures must not be treated as absent resources.'
    Write-Host 'PASS: 9 task lifecycle scenarios; no real Docker commands executed.'
} finally {
    foreach ($name in $savedSettings.Keys) { [Environment]::SetEnvironmentVariable($name, $savedSettings[$name]) }
    Remove-Item Function:/docker
    Remove-Item Function:/Invoke-RestMethod
}
