$ErrorActionPreference = "Stop"

$moduleRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$assets = @(
    @{
        Path = "static/src/img/content/services/service-mens-health-01.jpg"
        Url = "https://images.pexels.com/photos/5215016/pexels-photo-5215016.jpeg?cs=srgb&dl=pexels-shkrabaanthony-5215016.jpg&fm=jpg"
        Note = "Men's health consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-pregnancy-breastfeeding-01.jpg"
        Url = "https://images.pexels.com/photos/7491270/pexels-photo-7491270.jpeg?cs=srgb&dl=pexels-mart-production-7491270.jpg&fm=jpg"
        Note = "Pregnancy and breastfeeding support image"
    },
    @{
        Path = "static/src/img/content/services/service-antenatal-care-01.jpg"
        Url = "https://images.pexels.com/photos/7089329/pexels-photo-7089329.jpeg?cs=srgb&dl=pexels-mart-production-7089329.jpg&fm=jpg"
        Note = "Antenatal consultation support image"
    },
    @{
        Path = "static/src/img/content/services/service-older-age-care-01.jpg"
        Url = "https://images.pexels.com/photos/11030158/pexels-photo-11030158.jpeg?cs=srgb&dl=pexels-towfiqu-barbhuiya-3440682-11030158.jpg&fm=jpg"
        Note = "Older age care support image"
    }
)

Write-Host "Downloading additional service-page images into $moduleRoot"

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
        "service-mens-health-01.jpg",
        "service-pregnancy-breastfeeding-01.jpg",
        "service-antenatal-care-01.jpg",
        "service-older-age-care-01.jpg"
    ) } |
    Select-Object FullName, Length
