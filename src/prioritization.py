"""Prioritization Algorithm Module

This module implements the prioritization algorithm that ranks test suggestions
based on coverage impact, difficulty, and dependencies.
"""

from typing import List
from src.llm_integration import TestSuggestion, DifficultyLevel


class Prioritizer:
    """Prioritizes test suggestions based on multiple factors"""
    
    def __init__(
        self,
        coverage_impact_weight: float = 0.5,
        difficulty_weight: float = 0.3,
        dependency_weight: float = 0.2
    ):
        """
        Initialize prioritizer with weights
        
        Args:
            coverage_impact_weight: Weight for coverage impact (0-1)
            difficulty_weight: Weight for inverse difficulty (0-1)
            dependency_weight: Weight for dependency score (0-1)
        """
        self.coverage_impact_weight = coverage_impact_weight
        self.difficulty_weight = difficulty_weight
        self.dependency_weight = dependency_weight
        
        # Normalize weights
        total_weight = coverage_impact_weight + difficulty_weight + dependency_weight
        if total_weight > 0:
            self.coverage_impact_weight /= total_weight
            self.difficulty_weight /= total_weight
            self.dependency_weight /= total_weight
    
    def prioritize(self, suggestions: List[TestSuggestion]) -> List[TestSuggestion]:
        """
        Prioritize test suggestions and return sorted list
        
        Args:
            suggestions: List of test suggestions to prioritize
        
        Returns:
            Sorted list of test suggestions by priority score (highest first)
        """
        # Calculate priority scores
        for suggestion in suggestions:
            suggestion.priority_score = self._calculate_priority_score(suggestion)
        
        # Sort by priority score (descending)
        sorted_suggestions = sorted(
            suggestions,
            key=lambda s: s.priority_score,
            reverse=True
        )
        
        return sorted_suggestions
    
    def _calculate_priority_score(self, suggestion: TestSuggestion) -> float:
        """
        Calculate priority score for a test suggestion
        
        Formula: 
        priority_score = (coverage_impact_weight * coverage_impact) +
                        (difficulty_weight * inverse_difficulty) +
                        (dependency_weight * dependency_score)
        
        Args:
            suggestion: Test suggestion to score
        
        Returns:
            Priority score (0-1, higher is better)
        """
        # Coverage impact: based on how much coverage this bin contributes
        coverage_impact = self._calculate_coverage_impact(suggestion)
        
        # Inverse difficulty: easier tests get higher scores
        inverse_difficulty = self._calculate_inverse_difficulty(suggestion)
        
        # Dependency score: fewer dependencies = higher score
        dependency_score = self._calculate_dependency_score(suggestion)
        
        # Calculate weighted score
        priority_score = (
            self.coverage_impact_weight * coverage_impact +
            self.difficulty_weight * inverse_difficulty +
            self.dependency_weight * dependency_score
        )
        
        return priority_score
    
    def _calculate_coverage_impact(self, suggestion: TestSuggestion) -> float:
        """
        Calculate coverage impact score
        
        Higher impact if:
        - Bin is in a coverpoint with low coverage
        - Bin is part of cross-coverage
        - Bin represents a critical functionality
        
        Returns:
            Coverage impact score (0-1)
        """
        bin_info = suggestion.uncovered_bin
        
        # Base score from coverpoint coverage (lower coverage = higher impact)
        coverpoint_coverage = bin_info.get('coverage_percentage', 0) / 100.0
        impact = 1.0 - coverpoint_coverage  # Invert: lower coverage = higher impact
        
        # Boost for cross-coverage bins
        if 'cross' in bin_info or 'coverpoints' in bin_info:
            impact = min(1.0, impact * 1.2)
        
        # Normalize to 0-1 range
        return min(1.0, max(0.0, impact))
    
    def _calculate_inverse_difficulty(self, suggestion: TestSuggestion) -> float:
        """
        Calculate inverse difficulty score
        
        Easier tests get higher scores:
        - Easy: 1.0
        - Medium: 0.7
        - Hard: 0.4
        - Very Hard: 0.2
        
        Returns:
            Inverse difficulty score (0-1)
        """
        difficulty_map = {
            DifficultyLevel.EASY: 1.0,
            DifficultyLevel.MEDIUM: 0.7,
            DifficultyLevel.HARD: 0.4,
            DifficultyLevel.VERY_HARD: 0.2
        }
        
        return difficulty_map.get(suggestion.difficulty, 0.5)
    
    def _calculate_dependency_score(self, suggestion: TestSuggestion) -> float:
        """
        Calculate dependency score
        
        Fewer dependencies = higher score
        Score = 1.0 / (1 + num_dependencies)
        
        Returns:
            Dependency score (0-1)
        """
        num_dependencies = len(suggestion.dependencies)
        return 1.0 / (1.0 + num_dependencies)


def prioritize_suggestions(
    suggestions: List[TestSuggestion],
    coverage_impact_weight: float = 0.5,
    difficulty_weight: float = 0.3,
    dependency_weight: float = 0.2
) -> List[TestSuggestion]:
    """
    Convenience function to prioritize test suggestions
    
    Args:
        suggestions: List of test suggestions
        coverage_impact_weight: Weight for coverage impact
        difficulty_weight: Weight for inverse difficulty
        dependency_weight: Weight for dependency score
    
    Returns:
        Sorted list of prioritized suggestions
    """
    prioritizer = Prioritizer(
        coverage_impact_weight=coverage_impact_weight,
        difficulty_weight=difficulty_weight,
        dependency_weight=dependency_weight
    )
    return prioritizer.prioritize(suggestions)
