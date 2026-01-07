"""Main Application Module

Command-line interface for the Verification Coverage Analyzer
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.parser import CoverageReportParser, parse_coverage_report
from src.llm_integration import LLMTestGenerator, MockLLMGenerator
from src.prioritization import prioritize_suggestions
from src.coverage_prediction import CoverageClosurePredictor

# Initialize console with Windows-compatible settings
import os
if sys.platform == 'win32':
    # Set UTF-8 encoding for Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
console = Console(legacy_windows=False)


@click.command()
@click.argument('coverage_report', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for results (JSON)')
@click.option('--llm-provider', default='mock', type=click.Choice(['openai', 'anthropic', 'mock']),
              help='LLM provider to use')
@click.option('--llm-model', default='gpt-4', help='LLM model name')
@click.option('--max-suggestions', type=int, default=None,
              help='Maximum number of test suggestions to generate')
@click.option('--design-context', type=str, default=None,
              help='Additional context about the design/IP')
@click.option('--enable-prediction', is_flag=True,
              help='Enable coverage closure prediction (bonus feature)')
@click.option('--priority-weights', nargs=3, type=float, default=[0.5, 0.3, 0.2],
              help='Priority weights: coverage_impact difficulty dependency')
def main(
    coverage_report: str,
    output: Optional[str],
    llm_provider: str,
    llm_model: str,
    max_suggestions: Optional[int],
    design_context: Optional[str],
    enable_prediction: bool,
    priority_weights: tuple
):
    """Verification Coverage Analyzer with LLM Integration
    
    Analyzes functional coverage reports and generates prioritized test suggestions
    to close coverage gaps.
    """
    console.print(Panel.fit(
        "[bold blue]Verification Coverage Analyzer[/bold blue]\n"
        "AI-Assisted Functional Coverage Closure",
        border_style="blue"
    ))
    
    # Parse coverage report
    console.print(f"\n[cyan]Parsing coverage report:[/cyan] {coverage_report}")
    try:
        report = parse_coverage_report(coverage_report)
        console.print("[green]Parsing complete[/green]")
    except Exception as e:
        console.print(f"[red]Error parsing report:[/red] {e}")
        sys.exit(1)
    
    # Display coverage summary
    _display_coverage_summary(report)
    
    # Generate test suggestions
    console.print(f"\n[cyan]Generating test suggestions...[/cyan]")
    console.print(f"LLM Provider: {llm_provider}")
    
    try:
        if llm_provider == 'mock':
            generator = MockLLMGenerator()
        else:
            generator = LLMTestGenerator(provider=llm_provider, model=llm_model)
        
        console.print("[yellow]Generating suggestions...[/yellow]")
        suggestions = generator.generate_suggestions(
            uncovered_bins=report.uncovered_bins,
            design_name=report.design_name,
            design_context=design_context,
            max_suggestions=max_suggestions
        )
        console.print("[green]Suggestions generated[/green]")
        
        console.print(f"[green]Generated {len(suggestions)} test suggestions[/green]")
    
    except Exception as e:
        console.print(f"[red]Error generating suggestions:[/red] {e}")
        sys.exit(1)
    
    # Prioritize suggestions
    console.print(f"\n[cyan]Prioritizing test suggestions...[/cyan]")
    prioritized = prioritize_suggestions(
        suggestions,
        coverage_impact_weight=priority_weights[0],
        difficulty_weight=priority_weights[1],
        dependency_weight=priority_weights[2]
    )
    
    # Display prioritized suggestions
    _display_suggestions(prioritized)
    
    # Coverage prediction (optional)
    prediction = None
    if enable_prediction:
        console.print(f"\n[cyan]Predicting coverage closure...[/cyan]")
        predictor = CoverageClosurePredictor()
        console.print("[yellow]Calculating predictions...[/yellow]")
        prediction = predictor.predict(report, prioritized)
        console.print("[green]Predictions complete[/green]")
        
        _display_prediction(prediction)
    
    # Prepare output
    output_data = {
        'coverage_report': {
            'design_name': report.design_name,
            'overall_coverage': report.overall_coverage,
            'uncovered_bins_count': len(report.uncovered_bins),
            'uncovered_crosses_count': len(report.uncovered_crosses)
        },
        'test_suggestions': [
            {
                'uncovered_bin': s.uncovered_bin,
                'description': s.description,
                'test_outline': s.test_outline,
                'difficulty': s.difficulty.value,
                'dependencies': s.dependencies,
                'reasoning': s.reasoning,
                'estimated_time_hours': s.estimated_time_hours,
                'priority_score': s.priority_score
            }
            for s in prioritized
        ],
        'prediction': {
            'estimated_time_to_100_percent_hours': prediction.estimated_time_to_100_percent_hours,
            'likelihood_of_100_percent': prediction.likelihood_of_100_percent,
            'blocking_bins': prediction.blocking_bins,
            'predicted_final_coverage': prediction.predicted_final_coverage,
            'confidence_level': prediction.confidence_level
        } if prediction else None
    }
    
    # Save output
    if output:
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        console.print(f"\n[green]Results saved to:[/green] {output}")
    else:
        # Save to default location
        default_output = Path(coverage_report).stem + '_analysis.json'
        with open(default_output, 'w') as f:
            json.dump(output_data, f, indent=2)
        console.print(f"\n[green]Results saved to:[/green] {default_output}")


def _display_coverage_summary(report):
    """Display coverage summary table"""
    table = Table(title="Coverage Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Design Name", report.design_name)
    table.add_row("Overall Coverage", f"{report.overall_coverage:.2f}%")
    table.add_row("Covergroups", str(len(report.covergroups)))
    table.add_row("Uncovered Bins", str(len(report.uncovered_bins)))
    table.add_row("Uncovered Crosses", str(len(report.uncovered_crosses)))
    
    console.print(table)


def _display_suggestions(suggestions):
    """Display prioritized test suggestions"""
    table = Table(title="Prioritized Test Suggestions", show_header=True, header_style="bold magenta")
    table.add_column("Priority", style="cyan", justify="right")
    table.add_column("Coverpoint", style="yellow")
    table.add_column("Bin", style="yellow")
    table.add_column("Description", style="white", max_width=40)
    table.add_column("Difficulty", style="green")
    table.add_column("Time (hrs)", style="blue", justify="right")
    table.add_column("Score", style="magenta", justify="right")
    
    for idx, suggestion in enumerate(suggestions[:20], 1):  # Show top 20
        bin_info = suggestion.uncovered_bin
        difficulty_color = {
            'easy': 'green',
            'medium': 'yellow',
            'hard': 'red',
            'very_hard': 'bold red'
        }.get(suggestion.difficulty.value, 'white')
        
        table.add_row(
            str(idx),
            bin_info.get('coverpoint', 'N/A'),
            bin_info.get('bin', 'N/A'),
            suggestion.description[:40] + '...' if len(suggestion.description) > 40 else suggestion.description,
            f"[{difficulty_color}]{suggestion.difficulty.value}[/{difficulty_color}]",
            f"{suggestion.estimated_time_hours:.1f}",
            f"{suggestion.priority_score:.3f}"
        )
    
    console.print(table)
    
    if len(suggestions) > 20:
        console.print(f"\n[yellow]Showing top 20 of {len(suggestions)} suggestions[/yellow]")


def _display_prediction(prediction):
    """Display coverage closure prediction"""
    panel_content = f"""
[bold]Coverage Closure Prediction[/bold]

Estimated Time to 100% Coverage: [cyan]{prediction.estimated_time_to_100_percent_hours:.1f} hours[/cyan]
Likelihood of Achieving 100%: [cyan]{prediction.likelihood_of_100_percent * 100:.1f}%[/cyan]
Predicted Final Coverage: [cyan]{prediction.predicted_final_coverage:.2f}%[/cyan]
Confidence Level: [cyan]{prediction.confidence_level.upper()}[/cyan]

Blocking Bins: [yellow]{len(prediction.blocking_bins)}[/yellow]
"""
    
    console.print(Panel(panel_content, title="Prediction Results", border_style="green"))
    
    if prediction.blocking_bins:
        table = Table(title="Blocking Bins", show_header=True, header_style="bold red")
        table.add_column("Coverpoint", style="yellow")
        table.add_column("Bin", style="yellow")
        table.add_column("Reason", style="white")
        table.add_column("Severity", style="red")
        
        for bin_info in prediction.blocking_bins[:10]:  # Show top 10
            table.add_row(
                bin_info.get('coverpoint', 'N/A'),
                bin_info.get('bin', 'N/A'),
                bin_info.get('reason', 'N/A'),
                bin_info.get('severity', 'N/A')
            )
        
        console.print(table)


if __name__ == '__main__':
    main()
