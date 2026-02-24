@echo off
REM Build the C++ chaos_crypto extension module
REM Requires: Visual Studio Build Tools with C++ workload, pybind11
REM
REM Uses uv for dependency management.
REM Then run this script: build_cpp.bat

echo ==========================================
echo  Building C++ chaos_crypto_cpp extension
echo ==========================================

REM Ensure dependencies are synced
uv sync

uv run python -c "import pybind11; print('pybind11 OK:', pybind11.__version__)"
uv run python -c "import setuptools; print('setuptools OK:', setuptools.__version__)"

uv run python setup.py build_ext --inplace

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] C++ extension built successfully!
    echo The module is now available as: cyo.chaos_crypto_cpp
) else (
    echo.
    echo [ERROR] Build failed. Please ensure you have:
    echo   1. Visual Studio Build Tools with C++ workload installed
    echo   2. pybind11 installed (in pyproject.toml dependencies)
    echo   3. Python development headers available
)
