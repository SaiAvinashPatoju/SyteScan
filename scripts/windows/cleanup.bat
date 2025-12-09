@echo off
REM ==================================
REM SyteScan Cleanup Script
REM ==================================
REM Purpose: Remove build artifacts and caches
REM Usage: Run from project root directory
REM ==================================

echo Cleaning SyteScan project...
echo.

echo Removing Python bytecode...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

echo Removing pytest cache...
for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"

echo Removing Next.js build cache...
if exist .next rd /s /q .next

echo Removing node_modules cache...
if exist node_modules\.cache rd /s /q node_modules\.cache

echo Removing coverage reports...
if exist coverage rd /s /q coverage
if exist htmlcov rd /s /q htmlcov

echo.
echo ================================
echo Cleanup complete!
echo ================================
