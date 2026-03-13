$ErrorActionPreference = "Stop"

$moduleRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$assets = @(
    @{
        Path = "static/src/img/content/services/service-womens-health-01.jpg"
        Url = "https://images.pexels.com/photos/3992806/pexels-photo-3992806.jpeg?cs=srgb&dl=pexels-cdc-library-3992806.jpg&fm=jpg"
        Note = "Women's health consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-child-health-01.jpg"
        Url = "https://images.pexels.com/photos/7653322/pexels-photo-7653322.jpeg?cs=srgb&dl=pexels-pavel-danilyuk-7653322.jpg&fm=jpg"
        Note = "Child health consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-telehealth-01.jpg"
        Url = "https://images.pexels.com/photos/8376198/pexels-photo-8376198.jpeg?cs=srgb&dl=pexels-tima-miroshnichenko-8376198.jpg&fm=jpg"
        Note = "Telehealth consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-exercise-physiology-01.jpg"
        Url = "https://images.pexels.com/photos/20860617/pexels-photo-20860617.jpeg?cs=srgb&dl=pexels-funkcines-terapijos-centras-927573878-20860617.jpg&fm=jpg"
        Note = "Exercise physiology support image"
    }
)

Write-Host "Downloading service-page images into $moduleRoot"

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
        "service-womens-health-01.jpg",
        "service-child-health-01.jpg",
        "service-telehealth-01.jpg",
        "service-exercise-physiology-01.jpg"
    ) } |
    Select-Object FullName, Length
