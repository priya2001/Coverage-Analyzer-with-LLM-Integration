"""Quick demo script for the Verification Coverage Analyzer"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main

if __name__ == '__main__':
    # Run with sample DMA controller report
    sample_report = Path(__file__).parent / 'sample_reports' / 'dma_controller_coverage.txt'
    
    if not sample_report.exists():
        print(f"Error: Sample report not found at {sample_report}")
        sys.exit(1)
    
    # Simulate command-line arguments
    sys.argv = [
        'demo.py',
        str(sample_report),
        '--llm-provider', 'mock',
        '--enable-prediction',
        '--max-suggestions', '5'
    ]
    
    main()
