# How to Run the Verification Coverage Analyzer

## Step 1: Install Dependencies

First, make sure you have Python 3.8+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

This will install:
- `openai` - For OpenAI GPT models
- `anthropic` - For Anthropic Claude models
- `click` - For CLI interface
- `rich` - For beautiful console output
- `python-dotenv` - For environment variable management
- `pydantic` - For data validation

## Step 2: (Optional) Set Up API Keys

If you want to use real LLM providers (OpenAI or Anthropic), create a `.env` file:

```bash
# Copy the example file
copy .env.example .env
```

Then edit `.env` and add your API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Note:** You can skip this step if you want to use mock mode (no API key needed).

## Step 3: (Windows Only) Set UTF-8 Encoding

On Windows, set the encoding environment variable before running:

**PowerShell:**
```powershell
$env:PYTHONIOENCODING='utf-8'
```

**Command Prompt:**
```cmd
set PYTHONIOENCODING=utf-8
```

**Note:** This is automatically handled in the code, but you may need to set it manually in some environments.

## Step 4: Run the Tool

### Option A: Basic Run (Mock Mode - No API Key)

```bash
python -m src.main sample_reports/dma_controller_coverage.txt
```

This will:
- Parse the coverage report
- Generate mock test suggestions (no API calls)
- Prioritize suggestions
- Display results in the console
- Save results to `dma_controller_coverage_analysis.json`

### Option B: With Coverage Prediction

```bash
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction
```

### Option C: With Real LLM (Requires API Key)

```bash
python -m src.main sample_reports/dma_controller_coverage.txt --llm-provider openai --llm-model gpt-4
```

### Option D: Full Customization

```bash
python -m src.main sample_reports/dma_controller_coverage.txt ^
    --output my_results.json ^
    --llm-provider mock ^
    --max-suggestions 10 ^
    --design-context "DMA controller with 4 channels" ^
    --enable-prediction ^
    --priority-weights 0.5 0.3 0.2
```

**Note:** On Windows PowerShell, use backticks (`) instead of `^` for line continuation:
```powershell
python -m src.main sample_reports/dma_controller_coverage.txt `
    --output my_results.json `
    --enable-prediction
```

## Available Sample Reports

You can use either of these sample reports:

1. **DMA Controller** (72.5% coverage):
   ```bash
   python -m src.main sample_reports/dma_controller_coverage.txt
   ```

2. **UART Controller** (58.2% coverage):
   ```bash
   python -m src.main sample_reports/uart_coverage.txt
   ```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `coverage_report` | Path to coverage report file (required) | - |
| `--output, -o` | Output JSON file path | `{report_name}_analysis.json` |
| `--llm-provider` | LLM provider: `openai`, `anthropic`, or `mock` | `mock` |
| `--llm-model` | Model name (e.g., `gpt-4`, `claude-3-opus`) | `gpt-4` |
| `--max-suggestions` | Maximum number of suggestions | All uncovered bins |
| `--design-context` | Additional design context | None |
| `--enable-prediction` | Enable coverage closure prediction | Disabled |
| `--priority-weights` | Weights: coverage difficulty dependency | `0.5 0.3 0.2` |

## Expected Output

When you run the tool, you'll see:

1. **Coverage Summary Table** - Shows design name, overall coverage, uncovered bins count
2. **Test Suggestions Table** - Prioritized list of test suggestions with:
   - Priority rank
   - Coverpoint and bin name
   - Test description
   - Difficulty level
   - Estimated time
   - Priority score
3. **Coverage Prediction** (if enabled) - Shows:
   - Estimated time to 100% coverage
   - Likelihood of achieving 100%
   - Blocking bins
   - Predicted final coverage

4. **JSON Output File** - Detailed results saved to JSON file

## Troubleshooting

### "ModuleNotFoundError: No module named 'rich'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "No module named 'src'"
**Solution:** Make sure you're in the project root directory and use:
```bash
python -m src.main sample_reports/dma_controller_coverage.txt
```

### "OPENAI_API_KEY not found"
**Solution:** Either:
- Add your API key to `.env` file, OR
- Use mock mode: `--llm-provider mock`

### "FileNotFoundError: sample_reports/dma_controller_coverage.txt"
**Solution:** Make sure you're running from the project root directory where `sample_reports/` folder exists.

### UnicodeEncodeError on Windows
**Solution:** Set UTF-8 encoding:
```powershell
$env:PYTHONIOENCODING='utf-8'
python -m src.main sample_reports/dma_controller_coverage.txt
```

## Quick Test

To quickly verify everything works:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with mock mode (no API key needed)
python -m src.main sample_reports/dma_controller_coverage.txt --enable-prediction
```

You should see colorful output with tables showing coverage analysis and test suggestions!
