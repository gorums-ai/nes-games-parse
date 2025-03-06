# Basic script with simple quotes
Write-Host "Starting script"

$fileCount = 0
$renamedCount = 0
$allFiles = @()
$renamedFiles = @()

# Process files
Get-ChildItem -Filter "*.zip" | ForEach-Object {
    $fileCount++
    
    # Get name
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    
    # Convert case
    $newName = ($baseName -split " " | ForEach-Object { 
        (Get-Culture).TextInfo.ToTitleCase($_) 
    }) -join " "
    
    # Add extension
    $newName = $newName + $_.Extension
    
    # Store file info
    $fileInfo = [PSCustomObject]@{
        OriginalName = $_.Name
        NewName = $newName
        NeedsRename = (-not ([string]::Equals($_.Name, $newName, [StringComparison]::Ordinal)))
    }
    $allFiles += $fileInfo
    
    # Rename if different (case-sensitive comparison)
    if (-not ([string]::Equals($_.Name, $newName, [StringComparison]::Ordinal))) {
        Write-Host "Renaming: $($_.Name) -> $newName"
        Rename-Item -Path $_.FullName -NewName $newName
        $renamedCount++
        $renamedFiles += $fileInfo
    } else {
        Write-Host "Skipped: $($_.Name)"
    }
}

# Print summary
Write-Host "`n===== SUMMARY ====="
Write-Host "Total files found: $fileCount"
Write-Host "Files renamed: $renamedCount"

if ($fileCount -gt 0) {
    Write-Host "`nALL FILES FOUND:"
    $allFiles | Format-Table -Property OriginalName, NewName, NeedsRename
    
    if ($renamedCount -gt 0) {
        Write-Host "`nFILES RENAMED:"
        $renamedFiles | Format-Table -Property OriginalName, NewName
    }
}

Write-Host "Script completed"
