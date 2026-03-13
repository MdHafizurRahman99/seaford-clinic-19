$ErrorActionPreference = "Stop"

$moduleRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$assets = @(
    @{
        Path = "static/src/img/content/services/service-skin-check-01.jpg"
        Url = "https://images.pexels.com/photos/7446661/pexels-photo-7446661.jpeg?auto=compress&cs=tinysrgb&w=1600"
        Note = "Skin check consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-weight-management-01.jpg"
        Url = "https://images.pexels.com/photos/15319020/pexels-photo-15319020.jpeg?auto=compress&cs=tinysrgb&w=1600"
        Note = "Weight management consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-health-wellness-01.jpg"
        Url = "https://images.pexels.com/photos/7578808/pexels-photo-7578808.jpeg?auto=compress&cs=tinysrgb&w=1600"
        Note = "Health and wellness consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-immunisations-01.jpg"
        Url = "https://images.pexels.com/photos/8413291/pexels-photo-8413291.jpeg?auto=compress&cs=tinysrgb&w=1600"
        Note = "Immunisation support image"
    }
)

Write-Host "Downloading the next service-page images into $moduleRoot"

foreach ($asset in $assets) {
    $destination = Join-Path $moduleRoot $asset.Path
    $directory = Split-Path $destination -Parent

    if (-not (Test-Path $directory)) {
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
    }

    Write-Host "Downloading $($asset.Path)"
    Invoke-WebRequest -Uri $asset.Url -OutFile $destination -UseBasicParsing
}

Write-Host ""
Write-Host "Downloaded files:" -ForegroundColor Green
Get-ChildItem (Join-Path $moduleRoot "static/src/img/content/services") -Recurse -File |
    Where-Object { $_.Name -in @(
        "service-skin-check-01.jpg",
        "service-weight-management-01.jpg",
        "service-health-wellness-01.jpg",
        "service-immunisations-01.jpg"
    ) } |
    Select-Object FullName, Length
