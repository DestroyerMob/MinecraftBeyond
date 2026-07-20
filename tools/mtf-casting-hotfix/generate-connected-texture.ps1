Add-Type -AssemblyName System.Drawing

$hotfixRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$basePath = Join-Path $hotfixRoot 'source-assets\foundry_glass.png'
$connectedPath = Join-Path $hotfixRoot 'source-assets\foundry_glass_connected_2x2.png'
$outputPath = Join-Path $hotfixRoot 'resources\assets\mobstoolforging\textures\block\foundry_glass_connected.png'

$base = [System.Drawing.Bitmap]::FromFile($basePath)
$connected = [System.Drawing.Bitmap]::FromFile($connectedPath)
$atlas = [System.Drawing.Bitmap]::new(80, 16, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($atlas)
$graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half

try {
    if ($base.Width -ne 16 -or $base.Height -ne 16) {
        throw "Expected a 16x16 base texture, found $($base.Width)x$($base.Height)."
    }
    if ($connected.Width -ne 32 -or $connected.Height -ne 32) {
        throw "Expected a 32x32 connected texture, found $($connected.Width)x$($connected.Height)."
    }

    # Fusion pieced layout, left to right:
    # 0 isolated, 1 center, 2 vertical, 3 horizontal, 4 cross.
    $graphics.DrawImage($base, [System.Drawing.Rectangle]::new(0, 0, 16, 16), 0, 0, 16, 16, [System.Drawing.GraphicsUnit]::Pixel)
    $graphics.DrawImage($connected, [System.Drawing.Rectangle]::new(16, 0, 16, 16), 0, 0, 16, 16, [System.Drawing.GraphicsUnit]::Pixel)
    $graphics.DrawImage($connected, [System.Drawing.Rectangle]::new(32, 0, 16, 16), 16, 0, 16, 16, [System.Drawing.GraphicsUnit]::Pixel)
    $graphics.DrawImage($connected, [System.Drawing.Rectangle]::new(48, 0, 16, 16), 0, 16, 16, 16, [System.Drawing.GraphicsUnit]::Pixel)
    $graphics.DrawImage($connected, [System.Drawing.Rectangle]::new(64, 0, 16, 16), 16, 16, 16, 16, [System.Drawing.GraphicsUnit]::Pixel)

    $atlas.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
} finally {
    $graphics.Dispose()
    $atlas.Dispose()
    $connected.Dispose()
    $base.Dispose()
}
