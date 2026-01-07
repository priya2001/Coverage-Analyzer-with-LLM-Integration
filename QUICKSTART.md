# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **(Optional) Set up LLM API keys:**
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_key_here
     # OR
     ANTHROPIC_API_KEY=your_key_here
     ```

## Running the Tool

### Basic Usage (Mock Mode - No API Key Required)

```bash
python -m src.main sample_reports/dma_controller_coverage.txt
```

### With Real LLM (Requires API Key)

```bash
python -m src.main sample_reports/dma_controller_coverage.txt --llm-provider openai --llm-model gpt-4
```

### With Coverage Prediction

```bash
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction
```

### Full Example

```bash
python -m src.main sample_reports/dma_controller_coverage.txt \
    --output my_results.json \
    --llm-provider mock \
    --max-suggestions 10 \
    --design-context "DMA controller with 4 channels" \
    --enable-prediction \
    --priority-weights 0.5 0.3 0.2
```

## Expected Output

The tool will:
1. Parse the coverage report
2. Display a coverage summary table
3. Generate test suggestions (using LLM or mock)
4. Prioritize suggestions by score
5. Display prioritized suggestions table
6. (Optional) Show coverage closure predictions
7. Save results to JSON file

## Troubleshooting

**Import errors:**
- Make sure you're running from the project root directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Module not found:**
- Use `python -m src.main` instead of `python src/main.py`

**LLM API errors:**
- Check your API key is set in `.env`
- Verify your API quota/credits
- Use `--llm-provider mock` for testing without API

## Sample Reports

Two sample coverage reports are included:
- `sample_reports/dma_controller_coverage.txt` - DMA Controller (72.5% coverage)
- `sample_reports/uart_coverage.txt` - UART Controller (58.2% coverage)

Try both to see different coverage scenarios!
