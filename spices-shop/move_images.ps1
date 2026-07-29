$root = 'c:\Users\HP\Desktop\Backup\Desktop\websites\spices-shop'
$imagesDir = Join-Path $root 'images'
New-Item -ItemType Directory -Path $imagesDir -Force | Out-Null

Get-ChildItem -Path $root -File | Where-Object {
    $_.Extension -in '.jpeg', '.jpg', '.png'
} | ForEach-Object {
    $target = Join-Path $imagesDir $_.Name
    if (-not (Test-Path $target)) {
        Move-Item $_.FullName $target -Force
    }
}
