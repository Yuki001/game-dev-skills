[CmdletBinding()]
param(
    [switch]$Detailed
)

$ErrorActionPreference = 'Stop'

$candidates = [System.Collections.Generic.List[string]]::new()
$onPath = Get-Command magick -CommandType Application -ErrorAction SilentlyContinue
if ($onPath) {
    foreach ($command in $onPath) {
        $candidates.Add($command.Source)
    }
}

$roots = @(
    [Environment]::GetFolderPath('ProgramFiles'),
    [Environment]::GetFolderPath('ProgramFilesX86'),
    (Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'Programs')
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

foreach ($root in $roots) {
    Get-ChildItem -LiteralPath $root -Directory -Filter 'ImageMagick-*' -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending |
        ForEach-Object {
            $path = Join-Path $_.FullName 'magick.exe'
            if (Test-Path -LiteralPath $path) {
                $candidates.Add($path)
            }
        }
}

$resolved = $candidates |
    ForEach-Object { [IO.Path]::GetFullPath($_) } |
    Select-Object -Unique |
    Select-Object -First 1

if (-not $resolved) {
    throw 'ImageMagick 7 executable not found on PATH or in common Windows installation directories.'
}

if (-not $Detailed) {
    $resolved
    exit 0
}

$version = & $resolved -version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Found '$resolved', but 'magick -version' failed."
}

[pscustomobject]@{
    Path        = $resolved
    VersionText = ($version -join [Environment]::NewLine)
}
