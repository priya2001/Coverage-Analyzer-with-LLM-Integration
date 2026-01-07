@echo off
REM Example batch script to run the Verification Coverage Analyzer on Windows

REM Set UTF-8 encoding for Windows
set PYTHONIOENCODING=utf-8

REM Run with DMA controller sample report
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction --max-suggestions 5

pause
