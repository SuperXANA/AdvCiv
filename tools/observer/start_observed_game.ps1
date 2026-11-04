#requires -Version 4.0
<#
.SYNOPSIS
Explicitly launch an existing Civ4 or AutoIT executable with observer opt-in.
.DESCRIPTION
Run on the Windows runtime VM in its interactive game session. The selected
executable, and any children it launches normally, inherit the observer settings.
An already-running game does not inherit them. This script does not install a
DLL, create a tunnel, drive gameplay, or prove observation. JSON output records
only launch and optional exit evidence for the selected process.
.EXAMPLE
.\start_observed_game.ps1 -EnableObservation -ExecutablePath 'C:\Games\Beyond the Sword\Civ4BeyondSword.exe' -ArgumentLine 'mod="MLP Civilization is Magic"' -ResultPath '.\launch-result.json'
.EXAMPLE
.\start_observed_game.ps1 -EnableObservation -ExecutablePath 'C:\Tools\AutoIt3.exe' -ArgumentLine '"C:\Local Scripts\PlayCiv4.au3"' -WaitForExit -WaitTimeoutSeconds 600
#>
[CmdletBinding()]
param(
    [switch]$EnableObservation,
    [string]$ExecutablePath = '',
    [string]$WorkingDirectory = '',
    [string]$ArgumentLine = '',
    [int]$Port = 37631,
    [int]$Queue = 16,
    [int]$RetryMilliseconds = 500,
    [int]$TimeoutMilliseconds = 500,
    [string]$ResultPath = '',
    [switch]$WaitForExit,
    [int]$WaitTimeoutSeconds = 300
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$startedAt = [DateTime]::UtcNow
$result = [ordered]@{
    schema = 'advciv-observer-launch/v1'
    evidence = 'selected_windows_process_only'
    civ4_runtime_validated = $false
    started_utc = $startedAt.ToString('o')
    completed_utc = $null
    checks = @()
}
$exitCode = 2
$process = $null
$launchAttempted = $false
$stage = 'launch_prerequisites'

try {
    if (-not $EnableObservation) {
        throw 'Explicit -EnableObservation is required; no process was started.'
    }
    if ($env:OS -ne 'Windows_NT') {
        throw 'Run this launcher on the Windows runtime VM.'
    }
    if ($Port -lt 1 -or $Port -gt 65535 -or
        $Queue -lt 1 -or $Queue -gt 64 -or
        $RetryMilliseconds -lt 50 -or $RetryMilliseconds -gt 30000 -or
        $TimeoutMilliseconds -lt 50 -or $TimeoutMilliseconds -gt 5000 -or
        $WaitTimeoutSeconds -lt 1 -or $WaitTimeoutSeconds -gt 86400) {
        throw 'Observer settings or wait timeout are outside the supported ranges.'
    }
    if ([String]::IsNullOrWhiteSpace($ExecutablePath) -or
        -not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) {
        throw 'ExecutablePath must name an existing local executable.'
    }
    $resolvedExecutable = (Resolve-Path -LiteralPath $ExecutablePath).ProviderPath
    if ([IO.Path]::GetExtension($resolvedExecutable) -ine '.exe') {
        throw 'ExecutablePath must be an .exe; pass an AutoIT script through ArgumentLine.'
    }
    if ([String]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $WorkingDirectory = [IO.Path]::GetDirectoryName($resolvedExecutable)
    }
    if (-not (Test-Path -LiteralPath $WorkingDirectory -PathType Container)) {
        throw 'WorkingDirectory must name an existing directory.'
    }
    $resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).ProviderPath

    # Check the evidence destination before launching. CreateNew below also
    # protects prior evidence if another writer races this existence check.
    $resolvedResultPath = $null
    if (-not [String]::IsNullOrWhiteSpace($ResultPath)) {
        $resolvedResultPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ResultPath)
        if (Test-Path -LiteralPath $resolvedResultPath) {
            throw 'ResultPath already exists; choose a new evidence filename.'
        }
        if (-not (Test-Path -LiteralPath ([IO.Path]::GetDirectoryName($resolvedResultPath)) -PathType Container)) {
            throw 'The ResultPath parent directory must already exist.'
        }
    }

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $resolvedExecutable
    $startInfo.WorkingDirectory = $resolvedWorkingDirectory
    # ArgumentLine uses the executable's normal Windows command-line quoting.
    # No command shell or Invoke-Expression evaluates this string.
    $startInfo.Arguments = $ArgumentLine
    $startInfo.UseShellExecute = $false
    $startInfo.EnvironmentVariables['CV_OBSERVER_ENABLE'] = '1'
    $startInfo.EnvironmentVariables['CV_OBSERVER_PORT'] = [String]$Port
    $startInfo.EnvironmentVariables['CV_OBSERVER_QUEUE'] = [String]$Queue
    $startInfo.EnvironmentVariables['CV_OBSERVER_RETRY_MS'] = [String]$RetryMilliseconds
    $startInfo.EnvironmentVariables['CV_OBSERVER_TIMEOUT_MS'] = [String]$TimeoutMilliseconds
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $startInfo
    $stage = 'process_launch'
    $launchAttempted = $true
    if (-not $process.Start()) {
        throw 'The selected executable did not create a process.'
    }
    $result.checks += [ordered]@{
        name = 'process_launch'
        status = 'passed'
        reason = 'Selected process started with child-only observer environment.'
        process_id = $process.Id
        observer_port = $Port
        observer_queue = $Queue
        observer_retry_ms = $RetryMilliseconds
        observer_timeout_ms = $TimeoutMilliseconds
    }
    $exitCode = 0

    $stage = 'selected_process_exit'
    if ($WaitForExit) {
        $timer = [Diagnostics.Stopwatch]::StartNew()
        # Poll so an interrupted console can release this wrapper promptly.
        while (-not $process.WaitForExit(200)) {
            if ($timer.Elapsed.TotalSeconds -ge $WaitTimeoutSeconds) { break }
        }
        $timer.Stop()
        if ($process.HasExited) {
            $result.checks += [ordered]@{
                name = 'selected_process_exit'
                status = $(if ($process.ExitCode -eq 0) { 'passed' } else { 'failed' })
                reason = 'Exit observed for the selected executable; an AutoIT wrapper may outlive or precede Civ4.'
                process_exit_code = $process.ExitCode
                elapsed_seconds = $timer.Elapsed.TotalSeconds
            }
            if ($process.ExitCode -ne 0) { $exitCode = 1 }
        } else {
            $result.checks += [ordered]@{
                name = 'selected_process_exit'
                status = 'not_run'
                reason = 'Wait deadline expired; the selected process was left running.'
                elapsed_seconds = $timer.Elapsed.TotalSeconds
            }
            $exitCode = 2
        }
    } else {
        $result.checks += [ordered]@{
            name = 'selected_process_exit'
            status = 'not_run'
            reason = 'WaitForExit was not requested.'
        }
    }
} catch {
    $result.checks += [ordered]@{
        name = $stage
        status = $(if ($launchAttempted) { 'failed' } else { 'not_run' })
        reason = $_.Exception.Message
    }
    $exitCode = $(if ($launchAttempted) { 1 } else { 2 })
} finally {
    # Disposing the Process object releases this wrapper's handle; it never
    # terminates the launched application. The parent environment is unchanged.
    if ($null -ne $process) { $process.Dispose() }
}

$result.completed_utc = [DateTime]::UtcNow.ToString('o')
$result.exit_code = $exitCode
$json = $result | ConvertTo-Json -Depth 6
if (-not [String]::IsNullOrWhiteSpace($ResultPath)) {
    try {
        # Compute again so prerequisite failures can still produce a report.
        $reportPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ResultPath)
        $reportBytes = (New-Object Text.UTF8Encoding($false)).GetBytes($json + [Environment]::NewLine)
        $reportFile = [IO.File]::Open($reportPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        try { $reportFile.Write($reportBytes, 0, $reportBytes.Length) }
        finally { $reportFile.Dispose() }
    } catch {
        [Console]::Error.WriteLine('Could not create ResultPath; JSON evidence follows on stdout. Prior files were preserved.')
        $exitCode = 2
        $result.checks += [ordered]@{
            name = 'result_file_write'
            status = 'not_run'
            reason = 'ResultPath could not be created; read stdout for evidence.'
        }
        $result.exit_code = $exitCode
        $json = $result | ConvertTo-Json -Depth 6
    }
}
Write-Output $json
exit $exitCode
