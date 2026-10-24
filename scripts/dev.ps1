param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('doctor', 'init', 'start', 'stop', 'nuke', 'logs', 'status', 'test-runtime')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $repoRoot

function Get-Setting([string]$Name, [string]$Default) {
    $value = [Environment]::GetEnvironmentVariable("QWEN_TASK_$Name")
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

$image = Get-Setting 'IMAGE' 'faster-qwen3-tts-studio:dev'
$container = Get-Setting 'CONTAINER' 'faster-qwen3-tts-studio'
$dataVolume = Get-Setting 'DATA_VOLUME' 'faster_qwen3_tts_studio_data'
$port = Get-Setting 'PORT' '7860'
$bindAddress = Get-Setting 'BIND_ADDRESS' '127.0.0.1'
$gpuDevice = Get-Setting 'GPU_DEVICE' '0'
$devMount = (Get-Setting 'DEV_MOUNT' '1') -eq '1'
$dryRun = (Get-Setting 'DRY_RUN' '0') -eq '1'
$ownerLabel = 'app.hangrylabs.project'
$owner = 'faster-qwen3-tts-studio'
foreach ($name in @($container, $dataVolume)) {
    if ($name -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$') { throw "Invalid Docker resource name: $name" }
}
if ($image -notmatch '^[a-zA-Z0-9][a-zA-Z0-9_./:@-]+$') { throw 'Invalid image reference.' }
if ($port -notmatch '^\d+$' -or [int]$port -lt 1 -or [int]$port -gt 65535) { throw 'PORT must be 1..65535.' }
if ($bindAddress -notmatch '^\d{1,3}(\.\d{1,3}){3}$') { throw 'BIND_ADDRESS must be an IPv4 address.' }
if ($gpuDevice -notmatch '^\d+$') { throw 'GPU_DEVICE must be one NVIDIA GPU index.' }

function Invoke-Docker([string[]]$DockerArgs) {
    & docker @DockerArgs
    if ($LASTEXITCODE -ne 0) { throw "Docker command failed ($LASTEXITCODE): $($DockerArgs[0])" }
}

function Invoke-Change([string[]]$DockerArgs) {
    if ($dryRun) {
        Write-Host ('DRY RUN: docker ' + (($DockerArgs | ForEach-Object { '"' + $_ + '"' }) -join ' '))
    } else {
        Invoke-Docker $DockerArgs
    }
}

function Get-OwnedResource([string]$Kind, [string]$Name) {
    # Distinguish an absent resource from a Docker error; do not suppress failures.
    if ($Kind -eq 'image') {
        $names = @(Invoke-Docker @('image', 'ls', '--format', '{{.Repository}}:{{.Tag}}'))
    } elseif ($Kind -eq 'container') {
        $names = @(Invoke-Docker @('container', 'ls', '--all', '--format', '{{.Names}}'))
    } else {
        $names = @(Invoke-Docker @('volume', 'ls', '--format', '{{.Name}}'))
    }
    if ($names -cnotcontains $Name) { return $null }
    $resource = @(Invoke-Docker @($Kind, 'inspect', $Name) | ConvertFrom-Json)[0]
    $labels = if ($Kind -eq 'volume') { $resource.Labels } else { $resource.Config.Labels }
    $label = if ($null -ne $labels) { $labels.PSObject.Properties[$ownerLabel] } else { $null }
    if ($null -eq $label -or $label.Value -ne $owner) {
        throw "Refusing to change $Kind '$Name': it is not labelled as this project's resource. Choose another name."
    }
    return $resource
}

function Initialize-Volume {
    if ($null -eq (Get-OwnedResource 'volume' $dataVolume)) {
        Invoke-Change @('volume', 'create', '--label', "$ownerLabel=$owner", $dataVolume)
    }
}

function Wait-ForStudio {
    $probeAddress = if ($bindAddress -eq '0.0.0.0') { '127.0.0.1' } else { $bindAddress }
    $deadline = [DateTime]::UtcNow.AddSeconds(45)
    while ([DateTime]::UtcNow -lt $deadline) {
        $running = (Invoke-Docker @('container', 'inspect', '--format', '{{.State.Running}}', $container) | Out-String).Trim()
        if ($running -ne 'true') {
            Invoke-Docker @('logs', '--tail', '40', $container)
            throw 'Studio exited during startup. Inspect task logs.'
        }
        try {
            $status = Invoke-RestMethod -Uri "http://${probeAddress}:$port/status" -TimeoutSec 2
            if ($status.default_backend -eq 'torch') { return }
        } catch {
            # Python imports and server startup can take a few seconds.
        }
        Start-Sleep -Seconds 1
    }
    throw 'Studio did not become ready within 45 seconds. Inspect task logs.'
}

$engine = (Invoke-Docker @('info', '--format', '{{.OSType}}') | Out-String).Trim()
if ($engine -ne 'linux') { throw 'Use Docker Desktop with Linux containers and NVIDIA GPU support.' }

switch ($Action) {
    'doctor' {
        Write-Host "PowerShell $($PSVersionTable.PSVersion)"
        & uv --version
        if ($LASTEXITCODE -ne 0) { throw 'uv is required.' }
        Invoke-Docker @('version', '--format', '{{.Server.Version}}')
        & nvidia-smi --query-gpu=index,name --format=csv,noheader
        if ($LASTEXITCODE -ne 0) { throw 'NVIDIA drivers are required.' }
    }
    'init' {
        $null = Get-OwnedResource 'image' $image
        Invoke-Change @('build', '--file', (Join-Path $repoRoot 'Dockerfile'), '--tag', $image, $repoRoot)
        Initialize-Volume
    }
    'start' {
        if ($null -eq (Get-OwnedResource 'image' $image)) { throw 'Development image is missing. Run task init first.' }
        $existing = Get-OwnedResource 'container' $container
        Initialize-Volume
        if ($null -ne $existing) { Invoke-Change @('container', 'rm', '--force', $container) }
        $runArgs = @('run', '--detach', '--name', $container, '--label', "$ownerLabel=$owner",
            '--publish', "${bindAddress}:${port}:7860", '--gpus', 'all',
            '--env', "CUDA_VISIBLE_DEVICES=$gpuDevice", '--mount', "type=volume,src=$dataVolume,dst=/app/persistent")
        if ($env:HF_TOKEN) { $runArgs += @('--env', 'HF_TOKEN') }
        if ($env:QWEN_STUDIO_ASR_URL) { $runArgs += @('--env', 'QWEN_STUDIO_ASR_URL') }
        if ($devMount) {
            $runArgs += @('--env', 'PYTHONPATH=/app/src')
            foreach ($folder in @('src')) {
                $source = Join-Path $repoRoot $folder
                $runArgs += @('--mount', "type=bind,src=$source,dst=/app/$folder,readonly")
            }
        }
        Invoke-Change ($runArgs + $image)
        if ($dryRun) { Write-Host "Planned UI/API: http://${bindAddress}:$port. No Docker resources changed." }
        else {
            Wait-ForStudio
            Write-Host "UI/API ready: http://${bindAddress}:$port (load a model in the UI)."
        }
    }
    'stop' {
        if ($null -ne (Get-OwnedResource 'container' $container)) {
            Invoke-Change @('container', 'stop', $container)
        } else { Write-Host 'Container is already absent.' }
    }
    'nuke' {
        # Check all ownership before changing any resource. Never prune globally.
        $oldContainer = Get-OwnedResource 'container' $container
        $oldImage = Get-OwnedResource 'image' $image
        $oldVolume = Get-OwnedResource 'volume' $dataVolume
        if ($null -ne $oldContainer) { Invoke-Change @('container', 'rm', '--force', $container) }
        if ($null -ne $oldImage) { Invoke-Change @('image', 'rm', $image) }
        if ($null -ne $oldVolume) { Invoke-Change @('volume', 'rm', $dataVolume) }
        if ($dryRun) { Write-Host 'Dry run complete. No Docker resources changed.' }
        else { Write-Host 'Project cleanup complete. Source files and other Docker projects are untouched.' }
    }
    'logs' {
        if ($null -eq (Get-OwnedResource 'container' $container)) { throw 'Container is missing. Run task start first.' }
        Invoke-Docker @('logs', '--follow', '--tail', '100', $container)
    }
    'status' {
        $current = Get-OwnedResource 'container' $container
        if ($null -eq $current) { Write-Host 'Container is absent.' }
        else { Write-Host "$container : $($current.State.Status)" }
    }
    'test-runtime' {
        if ($null -eq (Get-OwnedResource 'image' $image)) { throw 'Development image is missing. Run task init first.' }
        $testArgs = @('run', '--rm', '--entrypoint', 'sh', '--workdir', '/workspace',
            '--env', 'PYTHONDONTWRITEBYTECODE=1', '--env', 'PYTHONPATH=/workspace/src:/workspace')
        foreach ($item in @('src', 'tests', 'scripts', 'docs',
            'pyproject.toml', 'LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md')) {
            $source = Join-Path $repoRoot $item
            $testArgs += @('--mount', "type=bind,src=$source,dst=/workspace/$item,readonly")
        }
        Invoke-Change ($testArgs + @($image, '-lc',
            "python -m pip install --quiet --only-binary=:all: 'pytest>=8,<10' && python -m pytest -q -p no:cacheprovider --ignore=tests/test_e2e_parity.py tests"))
    }
}
