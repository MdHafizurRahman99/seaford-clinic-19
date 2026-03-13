$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$moduleRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$contentRoot = Join-Path $moduleRoot "static/src/img/content"

function Get-JpegCodec {
    return [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() |
        Where-Object { $_.MimeType -eq "image/jpeg" } |
        Select-Object -First 1
}

function Apply-ExifOrientation {
    param(
        [System.Drawing.Image]$Image
    )

    $orientationId = 0x0112
    if (-not ($Image.PropertyIdList -contains $orientationId)) {
        return
    }

    $property = $Image.GetPropertyItem($orientationId)
    $orientation = $property.Value[0]

    switch ($orientation) {
        2 { $Image.RotateFlip([System.Drawing.RotateFlipType]::RotateNoneFlipX) }
        3 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone) }
        4 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipX) }
        5 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipX) }
        6 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone) }
        7 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipX) }
        8 { $Image.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipNone) }
        default { }
    }

    try {
        $Image.RemovePropertyItem($orientationId)
    } catch {
    }
}

function Get-TargetWidth {
    param(
        [string]$FullName
    )

    if ($FullName -like "*\static\src\img\content\team\*") {
        return 900
    }

    return 1600
}

function Save-Jpeg {
    param(
        [System.Drawing.Image]$Image,
        [string]$Path,
        [int]$Quality
    )

    $encoder = Get-JpegCodec
    $encoderParams = New-Object System.Drawing.Imaging.EncoderParameters(1)
    $encoderParams.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter(
        [System.Drawing.Imaging.Encoder]::Quality,
        [long]$Quality
    )

    $tempPath = "$Path.optimized.jpg"
    if (Test-Path $tempPath) {
        Remove-Item -Path $tempPath -Force
    }

    $Image.Save($tempPath, $encoder, $encoderParams)

    $keepOriginal = $false
    if (Test-Path $Path) {
        $originalSize = (Get-Item $Path).Length
        $tempSize = (Get-Item $tempPath).Length
        if ($tempSize -ge $originalSize) {
            $keepOriginal = $true
        }
    }

    if ($keepOriginal) {
        Remove-Item -Path $tempPath -Force
        return $false
    }

    if (Test-Path $Path) {
        Remove-Item -Path $Path -Force
    }

    Move-Item -Path $tempPath -Destination $Path
    return $true
}

function Optimize-Jpeg {
    param(
        [System.IO.FileInfo]$File
    )

    $quality = 82
    $targetWidth = Get-TargetWidth -FullName $File.FullName
    $beforeBytes = $File.Length

    $bytes = [System.IO.File]::ReadAllBytes($File.FullName)
    $stream = New-Object System.IO.MemoryStream(, $bytes)
    $loadedImage = [System.Drawing.Image]::FromStream($stream)
    $image = New-Object System.Drawing.Bitmap($loadedImage)

    $loadedImage.Dispose()
    $stream.Dispose()

    try {
        Apply-ExifOrientation -Image $image

        $currentWidth = $image.Width
        $currentHeight = $image.Height

        if ($currentWidth -le $targetWidth) {
            Save-Jpeg -Image $image -Path $File.FullName -Quality $quality
        } else {
            $targetHeight = [int][math]::Round(($currentHeight * $targetWidth) / $currentWidth)
            $bitmap = New-Object System.Drawing.Bitmap($targetWidth, $targetHeight)
            try {
                $bitmap.SetResolution($image.HorizontalResolution, $image.VerticalResolution)
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
                try {
                    $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
                    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
                    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
                    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
                    $graphics.DrawImage($image, 0, 0, $targetWidth, $targetHeight)
                } finally {
                    $graphics.Dispose()
                }

                Save-Jpeg -Image $bitmap -Path $File.FullName -Quality $quality
            } finally {
                $bitmap.Dispose()
            }
        }
    } finally {
        $image.Dispose()
    }

    $afterBytes = (Get-Item $File.FullName).Length

    [pscustomobject]@{
        File = $File.FullName
        BeforeKB = [math]::Round($beforeBytes / 1KB, 1)
        AfterKB = [math]::Round($afterBytes / 1KB, 1)
        SavedKB = [math]::Round(($beforeBytes - $afterBytes) / 1KB, 1)
        TargetWidth = $targetWidth
    }
}

$targets = Get-ChildItem $contentRoot -Recurse -File |
    Where-Object {
        $_.Extension -match '^\.(jpg|jpeg)$' -and
        (
            $_.FullName -like "*\static\src\img\content\clinic\*" -or
            $_.FullName -like "*\static\src\img\content\services\*" -or
            $_.FullName -like "*\static\src\img\content\team\*"
        )
    }

if (-not $targets) {
    Write-Host "No JPEG images found to optimize."
    exit 0
}

$results = foreach ($file in $targets) {
    Optimize-Jpeg -File $file
}

$beforeTotal = ($results | Measure-Object -Property BeforeKB -Sum).Sum
$afterTotal = ($results | Measure-Object -Property AfterKB -Sum).Sum
$savedTotal = ($results | Measure-Object -Property SavedKB -Sum).Sum

Write-Host "Optimized images:" -ForegroundColor Green
$results | Sort-Object SavedKB -Descending | Format-Table File, BeforeKB, AfterKB, SavedKB, TargetWidth -AutoSize

Write-Host ""
Write-Host ("Total before: {0} KB" -f [math]::Round($beforeTotal, 1))
Write-Host ("Total after:  {0} KB" -f [math]::Round($afterTotal, 1))
Write-Host ("Saved:        {0} KB" -f [math]::Round($savedTotal, 1)) -ForegroundColor Yellow
