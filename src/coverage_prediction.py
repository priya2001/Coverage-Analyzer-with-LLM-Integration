"""Coverage Closure Prediction Module (Optional Bonus Component)

This module predicts coverage closure metrics including:
- Time to reach full coverage
- Likelihood of achieving 100% coverage
- Identification of potentially blocking bins
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from src.parser import CoverageReport
from src.llm_integration import TestSuggestion, DifficultyLevel


@dataclass
class CoveragePrediction:
    """Coverage closure prediction results"""
    estimated_time_to_100_percent_hours: float
    likelihood_of_100_percent: float  # 0-1
    blocking_bins: List[Dict[str, Any]]
    predicted_final_coverage: float  # Predicted maximum achievable coverage
    confidence_level: str  # "high", "medium", "low"


class CoverageClosurePredictor:
    """Predicts coverage closure metrics"""
    
    def __init__(self):
        """Initialize coverage closure predictor"""
        pass
    
    def predict(
        self,
        coverage_report: CoverageReport,
        test_suggestions: List[TestSuggestion],
        historical_data: Optional[Dict] = None
    ) -> CoveragePrediction:
        """
        Predict coverage closure metrics
        
        Args:
            coverage_report: Current coverage report
            test_suggestions: Generated test suggestions
            historical_data: Optional historical coverage closure data
        
        Returns:
            CoveragePrediction object with predictions
        """
        # Calculate estimated time to 100% coverage
        estimated_time = self._estimate_time_to_full_coverage(test_suggestions)
        
        # Predict likelihood of achieving 100% coverage
        likelihood = self._predict_100_percent_likelihood(
            coverage_report,
            test_suggestions
        )
        
        # Identify blocking bins
        blocking_bins = self._identify_blocking_bins(
            coverage_report,
            test_suggestions
        )
        
        # Predict final achievable coverage
        predicted_final_coverage = self._predict_final_coverage(
            coverage_report,
            test_suggestions,
            blocking_bins
        )
        
        # Determine confidence level
        confidence = self._determine_confidence(
            coverage_report,
            test_suggestions,
            blocking_bins
        )
        
        return CoveragePrediction(
            estimated_time_to_100_percent_hours=estimated_time,
            likelihood_of_100_percent=likelihood,
            blocking_bins=blocking_bins,
            predicted_final_coverage=predicted_final_coverage,
            confidence_level=confidence
        )
    
    def _estimate_time_to_full_coverage(
        self,
        test_suggestions: List[TestSuggestion]
    ) -> float:
        """
        Estimate time to reach 100% coverage based on test suggestions
        
        Assumes all suggestions are implemented and successful
        """
        if not test_suggestions:
            return 0.0
        
        # Sum up estimated time from all suggestions
        total_time = sum(s.estimated_time_hours for s in test_suggestions)
        
        # Add overhead factor (20% for integration, debugging, etc.)
        overhead_factor = 1.2
        
        return total_time * overhead_factor
    
    def _predict_100_percent_likelihood(
        self,
        coverage_report: CoverageReport,
        test_suggestions: List[TestSuggestion]
    ) -> float:
        """
        Predict likelihood of achieving 100% coverage
        
        Factors considered:
        - Number of uncovered bins vs suggestions
        - Difficulty distribution of suggestions
        - Presence of blocking bins
        """
        uncovered_bins_count = len(coverage_report.uncovered_bins)
        uncovered_crosses_count = len(coverage_report.uncovered_crosses)
        total_uncovered = uncovered_bins_count + uncovered_crosses_count
        
        if total_uncovered == 0:
            return 1.0
        
        if len(test_suggestions) == 0:
            return 0.0
        
        # Base likelihood: ratio of suggestions to uncovered items
        suggestion_ratio = min(1.0, len(test_suggestions) / total_uncovered)
        
        # Adjust based on difficulty distribution
        difficulty_penalty = self._calculate_difficulty_penalty(test_suggestions)
        
        # Adjust based on current coverage (higher current coverage = higher likelihood)
        current_coverage_factor = coverage_report.overall_coverage / 100.0
        
        # Combine factors
        likelihood = suggestion_ratio * (1.0 - difficulty_penalty) * (0.5 + 0.5 * current_coverage_factor)
        
        return min(1.0, max(0.0, likelihood))
    
    def _calculate_difficulty_penalty(self, suggestions: List[TestSuggestion]) -> float:
        """Calculate penalty based on test difficulty"""
        if not suggestions:
            return 0.0
        
        difficulty_weights = {
            DifficultyLevel.EASY: 0.1,
            DifficultyLevel.MEDIUM: 0.3,
            DifficultyLevel.HARD: 0.6,
            DifficultyLevel.VERY_HARD: 0.9
        }
        
        total_penalty = sum(
            difficulty_weights.get(s.difficulty, 0.5)
            for s in suggestions
        )
        
        return total_penalty / len(suggestions)
    
    def _identify_blocking_bins(
        self,
        coverage_report: CoverageReport,
        test_suggestions: List[TestSuggestion]
    ) -> List[Dict[str, Any]]:
        """
        Identify potentially blocking bins that may be impossible to cover
        
        A bin is considered blocking if:
        - It has very hard difficulty
        - It has many dependencies
        - No test suggestion exists for it
        - It's been uncovered for a long time (if historical data available)
        """
        blocking_bins = []
        
        # Check uncovered bins without suggestions
        uncovered_bin_names = {
            bin_info.get('bin', '') for bin_info in coverage_report.uncovered_bins
        }
        
        suggested_bin_names = {
            s.uncovered_bin.get('bin', '') for s in test_suggestions
        }
        
        unsuggested_bins = uncovered_bin_names - suggested_bin_names
        
        for bin_info in coverage_report.uncovered_bins:
            bin_name = bin_info.get('bin', '')
            
            # Check if bin has no suggestion
            if bin_name in unsuggested_bins:
                blocking_bins.append({
                    **bin_info,
                    'reason': 'No test suggestion generated',
                    'severity': 'medium'
                })
            
            # Check for very hard suggestions with many dependencies
            for suggestion in test_suggestions:
                if suggestion.uncovered_bin.get('bin') == bin_name:
                    if (suggestion.difficulty == DifficultyLevel.VERY_HARD and
                        len(suggestion.dependencies) >= 3):
                        blocking_bins.append({
                            **bin_info,
                            'reason': 'Very hard test with multiple dependencies',
                            'severity': 'high'
                        })
                    break
        
        return blocking_bins
    
    def _predict_final_coverage(
        self,
        coverage_report: CoverageReport,
        test_suggestions: List[TestSuggestion],
        blocking_bins: List[Dict]
    ) -> float:
        """
        Predict final achievable coverage percentage
        
        Accounts for blocking bins that may never be covered
        """
        current_coverage = coverage_report.overall_coverage
        
        # Calculate potential coverage gain from suggestions
        total_uncovered_bins = len(coverage_report.uncovered_bins) + len(coverage_report.uncovered_crosses)
        
        if total_uncovered_bins == 0:
            return 100.0
        
        # Estimate bins that can be covered
        coverable_bins = total_uncovered_bins - len(blocking_bins)
        
        # Assume each bin contributes equally to coverage
        # This is a simplification - in reality, bins may have different weights
        coverage_per_bin = (100.0 - current_coverage) / total_uncovered_bins
        
        predicted_gain = coverable_bins * coverage_per_bin
        
        predicted_final = min(100.0, current_coverage + predicted_gain)
        
        return predicted_final
    
    def _determine_confidence(
        self,
        coverage_report: CoverageReport,
        test_suggestions: List[TestSuggestion],
        blocking_bins: List[Dict]
    ) -> str:
        """
        Determine confidence level of predictions
        
        High: Many suggestions, few blocking bins, high current coverage
        Medium: Moderate suggestions, some blocking bins
        Low: Few suggestions, many blocking bins, low current coverage
        """
        uncovered_count = len(coverage_report.uncovered_bins) + len(coverage_report.uncovered_crosses)
        
        if uncovered_count == 0:
            return "high"
        
        suggestion_ratio = len(test_suggestions) / uncovered_count if uncovered_count > 0 else 0
        blocking_ratio = len(blocking_bins) / uncovered_count if uncovered_count > 0 else 0
        
        if (suggestion_ratio >= 0.8 and blocking_ratio <= 0.1 and 
            coverage_report.overall_coverage >= 80):
            return "high"
        elif (suggestion_ratio >= 0.5 and blocking_ratio <= 0.3):
            return "medium"
        else:
            return "low"
