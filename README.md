# Verification Coverage Analyzer with LLM Integration

An intelligent, AI-assisted system to automate and accelerate functional coverage closure in chip verification. This tool combines structured data parsing with Large Language Model (LLM)–based reasoning to generate prioritized test suggestions for uncovered coverage bins.

## Features

- **Coverage Report Parser**: Parses text-based functional coverage reports and extracts structured information (covergroups, coverpoints, bins, hit counts, coverage status)
- **LLM-Based Test Suggestion Generator**: Uses LLMs (OpenAI GPT-4, Anthropic Claude, or mock mode) to generate actionable test scenarios for uncovered bins
- **Prioritization Algorithm**: Ranks test suggestions based on coverage impact, difficulty, and dependencies
- **Coverage Closure Prediction** (Bonus): Estimates time to full coverage, predicts likelihood of achieving 100% coverage, and identifies blocking bins

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) For LLM integration, set up API keys:
   - Create a `.env` file in the project root
   - Add your API key(s):
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     # OR
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```

## Usage

### Basic Usage

Analyze a coverage report and generate test suggestions:

```bash
python -m src.main sample_reports/dma_controller_coverage.txt
```

### Advanced Options

```bash
python -m src.main sample_reports/dma_controller_coverage.txt \
    --output results.json \
    --llm-provider openai \
    --llm-model gpt-4 \
    --max-suggestions 10 \
    --design-context "DMA controller with 4 channels, supports memory-to-memory and peripheral transfers" \
    --enable-prediction \
    --priority-weights 0.5 0.3 0.2
```

### Command-Line Options

- `coverage_report`: Path to the coverage report file (required)
- `--output, -o`: Output file path for JSON results (default: `{report_name}_analysis.json`)
- `--llm-provider`: LLM provider to use (`openai`, `anthropic`, or `mock`) (default: `mock`)
- `--llm-model`: LLM model name (default: `gpt-4`)
- `--max-suggestions`: Maximum number of test suggestions to generate (default: all)
- `--design-context`: Additional context about the design/IP
- `--enable-prediction`: Enable coverage closure prediction (bonus feature)
- `--priority-weights`: Priority weights for coverage_impact difficulty dependency (default: 0.5 0.3 0.2)

### Mock Mode (No API Key Required)

By default, the tool runs in mock mode, which generates sample test suggestions without requiring LLM API access. This is useful for testing and demonstration purposes.

## Coverage Report Format

The parser expects coverage reports in the following format:

```
Design: <Design Name>
Overall Coverage: <percentage>%

Covergroup: <covergroup_name>
Coverage: <percentage>%

Coverpoint: <coverpoint_name>
Coverage: <percentage>%
Bin: <bin_name> - Hits: <count> - Status: <Covered|Uncovered|Ignored>
...

Cross: <cross_name>
Coverage: <percentage>%
Bin: <bin_name> - Hits: <count> - Status: <Covered|Uncovered|Ignored>
...
```

See `sample_reports/` directory for example coverage reports.

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "coverage_report": {
    "design_name": "...",
    "overall_coverage": 72.5,
    "uncovered_bins_count": 15,
    "uncovered_crosses_count": 8
  },
  "test_suggestions": [
    {
      "uncovered_bin": {...},
      "description": "...",
      "test_outline": ["step1", "step2", ...],
      "difficulty": "medium",
      "dependencies": [...],
      "reasoning": "...",
      "estimated_time_hours": 4.0,
      "priority_score": 0.85
    },
    ...
  ],
  "prediction": {
    "estimated_time_to_100_percent_hours": 120.0,
    "likelihood_of_100_percent": 0.75,
    "blocking_bins": [...],
    "predicted_final_coverage": 95.0,
    "confidence_level": "medium"
  }
}
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── parser.py              # Coverage report parser
│   ├── llm_integration.py      # LLM test suggestion generator
│   ├── prioritization.py       # Prioritization algorithm
│   ├── coverage_prediction.py  # Coverage closure prediction (bonus)
│   └── main.py                 # CLI interface
├── sample_reports/
│   ├── dma_controller_coverage.txt
│   └── uart_coverage.txt
├── requirements.txt
├── README.md
└── DESIGN.md
```

## Example Output

When running the tool, you'll see:

1. **Coverage Summary**: Overview of the coverage report
2. **Prioritized Test Suggestions**: Table showing top suggestions ranked by priority score
3. **Coverage Prediction** (if enabled): Estimates and blocking bin analysis

## Sample Runs

### Example 1: DMA Controller Analysis

```bash
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction
```

### Example 2: UART Controller with OpenAI

```bash
python -m src.main sample_reports/uart_coverage.txt \
    --llm-provider openai \
    --llm-model gpt-4 \
    --max-suggestions 5 \
    --design-context "UART controller with configurable baud rates and parity"
```

## Prioritization Formula

Test suggestions are prioritized using the following formula:

```
priority_score = (coverage_impact_weight × coverage_impact) +
                 (difficulty_weight × inverse_difficulty) +
                 (dependency_weight × dependency_score)
```

Where:
- **Coverage Impact**: Higher for bins in coverpoints with lower coverage
- **Inverse Difficulty**: Easier tests get higher scores (Easy=1.0, Medium=0.7, Hard=0.4, Very Hard=0.2)
- **Dependency Score**: Fewer dependencies = higher score (1.0 / (1 + num_dependencies))

## Limitations and Future Improvements

See `DESIGN.md` for detailed discussion of scalability, limitations, and future improvements.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure you're running from the project root:
```bash
python -m src.main <coverage_report>
```

### LLM API Errors

- Verify your API key is set correctly in `.env`
- Check your API quota/credits
- Use `--llm-provider mock` for testing without API access

### Parser Errors

- Ensure your coverage report follows the expected format
- Check that the report file is readable and properly formatted

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

This is a demonstration project. For production use, consider:
- Enhanced error handling
- Support for additional coverage report formats
- Integration with verification frameworks
- Web-based UI
- Historical coverage tracking
