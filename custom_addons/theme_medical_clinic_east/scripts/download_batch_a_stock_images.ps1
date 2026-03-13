$ErrorActionPreference = "Stop"

$moduleRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$assets = @(
    @{
        Path = "static/src/img/content/clinic/clinic-reception-01.jpg"
        Url = "https://images.pexels.com/photos/33812025/pexels-photo-33812025.jpeg?cs=srgb&dl=pexels-jinshu-pulpatta-2151876856-33812025.jpg&fm=jpg"
        Note = "Temporary reception image for About and Contact"
    },
    @{
        Path = "static/src/img/content/clinic/clinic-interior-01.jpg"
        Url = "https://images.pexels.com/photos/8459996/pexels-photo-8459996.jpeg?cs=srgb&dl=pexels-cristian-rojas-8459996.jpg&fm=jpg"
        Note = "Home trust section image"
    },
    @{
        Path = "static/src/img/content/clinic/clinic-exterior-01.jpg"
        Url = "https://images.pexels.com/photos/6473188/pexels-photo-6473188.jpeg?cs=srgb&dl=pexels-gene-wide-18396702-6473188.jpg&fm=jpg"
        Note = "Temporary exterior image for Contact"
    },
    @{
        Path = "static/src/img/content/team/doctor-amelia-hart.jpg"
        Url = "https://images.pexels.com/photos/7904457/pexels-photo-7904457.jpeg?cs=srgb&dl=pexels-anntarazevich-7904457.jpg&fm=jpg"
        Note = "Temporary homepage preview portrait"
    },
    @{
        Path = "static/src/img/content/team/doctor-priya-menon.jpg"
        Url = "https://images.pexels.com/photos/32254665/pexels-photo-32254665.jpeg?cs=srgb&dl=pexels-konrads-photo-32254665.jpg&fm=jpg"
        Note = "Temporary homepage preview portrait"
    },
    @{
        Path = "static/src/img/content/team/doctor-cameron-wells.jpg"
        Url = "https://images.pexels.com/photos/32254662/pexels-photo-32254662.jpeg?cs=srgb&dl=pexels-konrads-photo-32254662.jpg&fm=jpg"
        Note = "Temporary homepage preview portrait"
    }
)

Write-Host "Downloading Batch A stock images into $moduleRoot"
Write-Host "Note: the three team portraits are temporary placeholders only." -ForegroundColor Yellow

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
Get-ChildItem (Join-Path $moduleRoot "static/src/img/content") -Recurse -File |
    Where-Object { $_.Name -in @(
        "clinic-reception-01.jpg",
        "clinic-interior-01.jpg",
        "clinic-exterior-01.jpg",
        "doctor-amelia-hart.jpg",
        "doctor-priya-menon.jpg",
        "doctor-cameron-wells.jpg"
    ) } |
    Select-Object FullName, Length
