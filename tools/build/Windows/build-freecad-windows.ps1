#Requires -Version 5.1
<#
.SYNOPSIS
  Download LibPack, configure CMake, and build FreeCAD on Windows (LibPack + MSVC).

.DESCRIPTION
  Run from an elevated PowerShell ("Run as administrator") the first time you install
  Visual Studio Build Tools. Typical total compile time: 1–3+ hours.

  Prerequisites (install if missing):
    - Git
    - CMake (e.g. winget install Kitware.CMake)
    - Visual Studio 2022 Build Tools or VS Community with "Desktop development with C++"
    - 7-Zip (for LibPack .7z), e.g. winget install 7zip.7zip

  Usage (from repo root):
    pwsh -ExecutionPolicy Bypass -File tools\build\Windows\build-freecad-windows.ps1

  Optional environment variables:
    $env:FREECAD_LIBPACK_DIR = path to an existing LibPack (skips download)
    $env:CMAKE_GENERATOR = "Visual Studio 17 2022" (default)
#>
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $RepoRoot

function Find-CMake {
    $candidates = @(
        "cmake"
        "${env:ProgramFiles}\CMake\bin\cmake.exe"
        "${env:ProgramFiles(x86)}\Microsoft Visual Studio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
        "${env:ProgramFiles}\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
    )
    foreach ($c in $candidates) {
        if ($c -eq "cmake") {
            $cmd = Get-Command cmake -ErrorAction SilentlyContinue
            if ($cmd) { return $cmd.Source }
        } elseif (Test-Path $c) { return $c }
    }
    return $null
}

function Find-7z {
    $p = "${env:ProgramFiles}\7-Zip\7z.exe"
    if (Test-Path $p) { return $p }
    $p = "${env:ProgramFiles(x86)}\7-Zip\7z.exe"
    if (Test-Path $p) { return $p }
    return $null
}

Write-Host "Repository: $RepoRoot"

# --- Submodules (requires a Git clone with .git, not a ZIP download) ---
if (Test-Path (Join-Path $RepoRoot ".git")) {
    & git -C $RepoRoot submodule update --init --recursive
    if ($LASTEXITCODE -ne 0) { throw "git submodule failed" }
} else {
    Write-Warning "No .git folder: skip submodules. For a full build, clone the repo with Git (git clone --recurse-submodules https://github.com/FreeCAD/FreeCAD.git) or unpack submodules manually."
}

# --- LibPack (same URL as .github/workflows/actions/windows/getLibpack) ---
$LibPackUrl = "https://github.com/FreeCAD/FreeCAD-LibPack/releases/download/3.1.1.3/LibPack-1.1.0-v3.1.1.3-Release.7z"
$LibPackInnerName = "LibPack-1.1.0-v3.1.1.3-Release"
$LibPackRoot = Join-Path $RepoRoot "tools\build\Windows\LibPack"

if ($env:FREECAD_LIBPACK_DIR) {
    $LibPackDir = $env:FREECAD_LIBPACK_DIR
    Write-Host "Using FREECAD_LIBPACK_DIR=$LibPackDir"
} else {
    $SevenZip = Find-7z
    if (-not $SevenZip) {
        throw "7-Zip not found. Install from https://www.7-zip.org/ or: winget install 7zip.7zip"
    }
    New-Item -ItemType Directory -Force -Path $LibPackRoot | Out-Null
    $Archive = Join-Path $LibPackRoot "libpack.7z"
    if (-not (Test-Path (Join-Path $LibPackRoot $LibPackInnerName))) {
        Write-Host "Downloading LibPack..."
        Invoke-WebRequest -Uri $LibPackUrl -OutFile $Archive -UseBasicParsing
        Write-Host "Extracting LibPack (large)..."
        & $SevenZip x $Archive "-o$LibPackRoot\temp" -y | Out-Null
        $inner = Join-Path $LibPackRoot "temp\$LibPackInnerName"
        if (-not (Test-Path $inner)) {
            throw "Unexpected LibPack layout under temp; check extracted folder name."
        }
        Move-Item -Path $inner -Destination (Join-Path $LibPackRoot $LibPackInnerName)
        Remove-Item -Recurse -Force (Join-Path $LibPackRoot "temp")
        Remove-Item -Force $Archive -ErrorAction SilentlyContinue
    }
    $LibPackDir = Join-Path $LibPackRoot $LibPackInnerName
}

$qsvg = Join-Path $LibPackDir "plugins\imageformats\qsvg.dll"
if (-not (Test-Path $qsvg)) {
    throw "Invalid FREECAD_LIBPACK_DIR: missing plugins\imageformats\qsvg.dll in $LibPackDir"
}

# --- CMake ---
$cmake = Find-CMake
if (-not $cmake) {
    throw "CMake not found. Install: winget install Kitware.CMake (then re-open PowerShell)."
}
Write-Host "Using CMake: $cmake"
& $cmake --version

$BuildDir = Join-Path $RepoRoot "build\release"
$Generator = if ($env:CMAKE_GENERATOR) { $env:CMAKE_GENERATOR } else { "Visual Studio 17 2022" }

$configureArgs = @(
    "-B", $BuildDir
    "-S", $RepoRoot
    "--preset", "release"
    "-G", $Generator
    "-A", "x64"
    "-DCMAKE_VS_NO_COMPILE_BATCHING=ON"
    "-DCMAKE_BUILD_TYPE=Release"
    "-DFREECAD_USE_PCH=OFF"
    "-DFREECAD_RELEASE_PDB=OFF"
    "-DFREECAD_LIBPACK_DIR=$LibPackDir"
    "-DFREECAD_COPY_DEPEND_DIRS_TO_BUILD=ON"
    "-DFREECAD_COPY_LIBPACK_BIN_TO_BUILD=ON"
    "-DFREECAD_COPY_PLUGINS_BIN_TO_BUILD=ON"
)

Write-Host "Configuring..."
& $cmake @configureArgs
if ($LASTEXITCODE -ne 0) { throw "CMake configure failed" }

Write-Host "Building (Release). This may take 1–3+ hours..."
& $cmake --build $BuildDir --config Release --parallel
if ($LASTEXITCODE -ne 0) { throw "Build failed" }

$exe = Join-Path $BuildDir "bin\FreeCAD.exe"
Write-Host ""
Write-Host "Done. If successful, run:"
Write-Host "  $exe"
Write-Host ""
