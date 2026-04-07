@echo off
setlocal

set "ROOT=%~dp0"
set "DOCS=%ROOT%docs"
set "TEX=UNYTS_User_Manual.tex"
set "OUTDIR=%ROOT%build\latex-manual"
set "PDF_ROOT=%ROOT%UNYTS_User_Manual.pdf"

if not exist "%DOCS%\%TEX%" (
    echo ERROR: Could not find "%DOCS%\%TEX%"
    exit /b 1
)

if not exist "%OUTDIR%" mkdir "%OUTDIR%"

pushd "%DOCS%" || exit /b 1

echo Compiling pass 1...
xelatex -interaction=nonstopmode -halt-on-error -output-directory="%OUTDIR%" "%TEX%"
if errorlevel 1 (
    popd
    echo ERROR: XeLaTeX failed on pass 1.
    exit /b 1
)

echo Compiling pass 2...
xelatex -interaction=nonstopmode -halt-on-error -output-directory="%OUTDIR%" "%TEX%"
if errorlevel 1 (
    popd
    echo ERROR: XeLaTeX failed on pass 2.
    exit /b 1
)

popd

copy /Y "%OUTDIR%\UNYTS_User_Manual.pdf" "%PDF_ROOT%" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy PDF to project root.
    exit /b 1
)

echo Done: "%PDF_ROOT%"
exit /b 0
