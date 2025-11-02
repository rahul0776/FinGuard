# Build Lambda Layer for ML dependencies
$layerDir = "$PSScriptRoot\..\layers\ml"
$pythonDir = "$layerDir\python"

# Create directory structure
New-Item -ItemType Directory -Force -Path $pythonDir | Out-Null

# Install dependencies to python/ directory
pip install -r "$layerDir\requirements.txt" -t $pythonDir

Write-Host "Layer built successfully at: $pythonDir"



