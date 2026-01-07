# Example PowerShell script to run the Verification Coverage Analyzer on Windows

# Set UTF-8 encoding for Windows
$env:PYTHONIOENCODING = 'utf-8'

# Run with DMA controller sample report
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction --max-suggestions 5

# Wait for user input
Read-Host "Press Enter to exit"
