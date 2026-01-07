"""Coverage Report Parser Module

This module parses text-based functional coverage reports and extracts
structured information including design name, coverage percentages, covergroups,
coverpoints, bins, hit counts, and coverage status.
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class CoverageStatus(Enum):
    """Coverage status enumeration"""
    COVERED = "covered"
    UNCOVERED = "uncovered"
    IGNORED = "ignored"


@dataclass
class Bin:
    """Represents a coverage bin"""
    name: str
    hit_count: int
    status: CoverageStatus
    goal: Optional[int] = None


@dataclass
class Coverpoint:
    """Represents a coverage coverpoint"""
    name: str
    bins: List[Bin]
    coverage_percentage: float
    total_bins: int
    covered_bins: int


@dataclass
class CrossCoverage:
    """Represents cross-coverage between coverpoints"""
    name: str
    coverpoints: List[str]
    bins: List[Bin]
    coverage_percentage: float
    total_bins: int
    covered_bins: int


@dataclass
class Covergroup:
    """Represents a coverage covergroup"""
    name: str
    coverpoints: List[Coverpoint]
    cross_coverage: List[CrossCoverage]
    coverage_percentage: float
    total_bins: int
    covered_bins: int


@dataclass
class CoverageReport:
    """Complete coverage report structure"""
    design_name: str
    overall_coverage: float
    covergroups: List[Covergroup]
    uncovered_bins: List[Dict[str, Any]]
    uncovered_crosses: List[Dict[str, Any]]


class CoverageReportParser:
    """Parser for functional coverage reports"""
    
    def __init__(self):
        self.design_name_pattern = re.compile(r'Design\s*:\s*(.+)', re.IGNORECASE)
        self.coverage_percentage_pattern = re.compile(r'(\d+\.?\d*)\s*%')
        self.covergroup_pattern = re.compile(r'Covergroup\s*:\s*(.+)', re.IGNORECASE)
        self.coverpoint_pattern = re.compile(r'Coverpoint\s*:\s*(.+)', re.IGNORECASE)
        self.bin_pattern = re.compile(r'Bin\s*:\s*(.+?)\s*-\s*Hits\s*:\s*(\d+)\s*-\s*Status\s*:\s*(\w+)', re.IGNORECASE)
        self.cross_pattern = re.compile(r'Cross\s*:\s*(.+?)\s*-\s*Coverage\s*:\s*(\d+\.?\d*)\s*%', re.IGNORECASE)
        
    def parse(self, report_text: str) -> CoverageReport:
        """Parse a coverage report text into structured data"""
        lines = report_text.split('\n')
        
        design_name = self._extract_design_name(lines)
        overall_coverage = self._extract_overall_coverage(lines)
        covergroups = self._extract_covergroups(lines)
        
        # Extract uncovered bins and crosses
        uncovered_bins = self._extract_uncovered_bins(covergroups)
        uncovered_crosses = self._extract_uncovered_crosses(covergroups)
        
        return CoverageReport(
            design_name=design_name,
            overall_coverage=overall_coverage,
            covergroups=covergroups,
            uncovered_bins=uncovered_bins,
            uncovered_crosses=uncovered_crosses
        )
    
    def _extract_design_name(self, lines: List[str]) -> str:
        """Extract design name from report"""
        for line in lines:
            match = self.design_name_pattern.search(line)
            if match:
                return match.group(1).strip()
        return "Unknown Design"
    
    def _extract_overall_coverage(self, lines: List[str]) -> float:
        """Extract overall coverage percentage"""
        for line in lines:
            if 'Overall Coverage' in line or 'Total Coverage' in line:
                match = self.coverage_percentage_pattern.search(line)
                if match:
                    return float(match.group(1))
        return 0.0
    
    def _extract_covergroups(self, lines: List[str]) -> List[Covergroup]:
        """Extract all covergroups from report"""
        covergroups = []
        current_covergroup = None
        current_coverpoint = None
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check for covergroup
            covergroup_match = self.covergroup_pattern.search(line)
            if covergroup_match:
                if current_covergroup:
                    covergroups.append(current_covergroup)
                current_covergroup = Covergroup(
                    name=covergroup_match.group(1).strip(),
                    coverpoints=[],
                    cross_coverage=[],
                    coverage_percentage=0.0,
                    total_bins=0,
                    covered_bins=0
                )
                current_coverpoint = None
            
            # Check for coverpoint
            coverpoint_match = self.coverpoint_pattern.search(line)
            if coverpoint_match and current_covergroup:
                if current_coverpoint:
                    current_covergroup.coverpoints.append(current_coverpoint)
                current_coverpoint = Coverpoint(
                    name=coverpoint_match.group(1).strip(),
                    bins=[],
                    coverage_percentage=0.0,
                    total_bins=0,
                    covered_bins=0
                )
            
            # Check for bin
            bin_match = self.bin_pattern.search(line)
            if bin_match and current_coverpoint:
                bin_name = bin_match.group(1).strip()
                hit_count = int(bin_match.group(2))
                status_str = bin_match.group(3).strip().lower()
                
                status = CoverageStatus.UNCOVERED
                if status_str == 'covered' or 'hit' in status_str:
                    status = CoverageStatus.COVERED
                elif 'ignore' in status_str:
                    status = CoverageStatus.IGNORED
                
                bin_obj = Bin(
                    name=bin_name,
                    hit_count=hit_count,
                    status=status
                )
                current_coverpoint.bins.append(bin_obj)
            
            # Check for cross coverage
            cross_match = self.cross_pattern.search(line)
            if cross_match and current_covergroup:
                cross_name = cross_match.group(1).strip()
                cross_coverage = float(cross_match.group(2))
                
                # Extract coverpoints from cross name (e.g., "cp1 x cp2")
                coverpoint_names = [cp.strip() for cp in cross_name.split('x')]
                
                # Find bins for this cross (simplified - in real parser, would parse actual cross bins)
                cross_bins = []
                i += 1
                while i < len(lines) and not self.covergroup_pattern.search(lines[i]) and not self.coverpoint_pattern.search(lines[i]):
                    bin_match = self.bin_pattern.search(lines[i])
                    if bin_match:
                        bin_name = bin_match.group(1).strip()
                        hit_count = int(bin_match.group(2))
                        status_str = bin_match.group(3).strip().lower()
                        
                        status = CoverageStatus.UNCOVERED
                        if 'cover' in status_str or 'hit' in status_str:
                            status = CoverageStatus.COVERED
                        elif 'ignore' in status_str:
                            status = CoverageStatus.IGNORED
                        
                        cross_bins.append(Bin(
                            name=bin_name,
                            hit_count=hit_count,
                            status=status
                        ))
                    i += 1
                i -= 1
                
                total_cross_bins = len(cross_bins)
                covered_cross_bins = sum(1 for b in cross_bins if b.status == CoverageStatus.COVERED)
                
                cross_coverage_obj = CrossCoverage(
                    name=cross_name,
                    coverpoints=coverpoint_names,
                    bins=cross_bins,
                    coverage_percentage=cross_coverage,
                    total_bins=total_cross_bins,
                    covered_bins=covered_cross_bins
                )
                current_covergroup.cross_coverage.append(cross_coverage_obj)
            
            # Update coverpoint statistics
            if current_coverpoint and i == len(lines) - 1:
                current_coverpoint.total_bins = len(current_coverpoint.bins)
                current_coverpoint.covered_bins = sum(1 for b in current_coverpoint.bins if b.status == CoverageStatus.COVERED)
                if current_coverpoint.total_bins > 0:
                    current_coverpoint.coverage_percentage = (current_coverpoint.covered_bins / current_coverpoint.total_bins) * 100
            
            i += 1
        
        # Add last coverpoint and covergroup
        if current_coverpoint and current_covergroup:
            current_coverpoint.total_bins = len(current_coverpoint.bins)
            current_coverpoint.covered_bins = sum(1 for b in current_coverpoint.bins if b.status == CoverageStatus.COVERED)
            if current_coverpoint.total_bins > 0:
                current_coverpoint.coverage_percentage = (current_coverpoint.covered_bins / current_coverpoint.total_bins) * 100
            current_covergroup.coverpoints.append(current_coverpoint)
        
        if current_covergroup:
            # Calculate covergroup statistics
            all_bins = []
            for cp in current_covergroup.coverpoints:
                all_bins.extend(cp.bins)
            for cross in current_covergroup.cross_coverage:
                all_bins.extend(cross.bins)
            
            current_covergroup.total_bins = len(all_bins)
            current_covergroup.covered_bins = sum(1 for b in all_bins if b.status == CoverageStatus.COVERED)
            if current_covergroup.total_bins > 0:
                current_covergroup.coverage_percentage = (current_covergroup.covered_bins / current_covergroup.total_bins) * 100
            
            covergroups.append(current_covergroup)
        
        return covergroups
    
    def _extract_uncovered_bins(self, covergroups: List[Covergroup]) -> List[Dict[str, Any]]:
        """Extract all uncovered bins with context"""
        uncovered = []
        for cg in covergroups:
            for cp in cg.coverpoints:
                for bin_obj in cp.bins:
                    if bin_obj.status == CoverageStatus.UNCOVERED:
                        uncovered.append({
                            'covergroup': cg.name,
                            'coverpoint': cp.name,
                            'bin': bin_obj.name,
                            'hit_count': bin_obj.hit_count,
                            'coverage_percentage': cp.coverage_percentage
                        })
        return uncovered
    
    def _extract_uncovered_crosses(self, covergroups: List[Covergroup]) -> List[Dict[str, Any]]:
        """Extract all uncovered cross-coverage combinations"""
        uncovered = []
        for cg in covergroups:
            for cross in cg.cross_coverage:
                for bin_obj in cross.bins:
                    if bin_obj.status == CoverageStatus.UNCOVERED:
                        uncovered.append({
                            'covergroup': cg.name,
                            'cross': cross.name,
                            'coverpoints': cross.coverpoints,
                            'bin': bin_obj.name,
                            'hit_count': bin_obj.hit_count,
                            'coverage_percentage': cross.coverage_percentage
                        })
        return uncovered
    
    def to_json(self, report: CoverageReport) -> str:
        """Convert coverage report to JSON string"""
        def convert_to_dict(obj):
            if isinstance(obj, CoverageStatus):
                return obj.value
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [convert_to_dict(item) for item in value]
                    elif isinstance(value, CoverageStatus):
                        result[key] = value.value
                    else:
                        result[key] = value
                return result
            return obj
        
        report_dict = convert_to_dict(report)
        return json.dumps(report_dict, indent=2)


def parse_coverage_report(file_path: str) -> CoverageReport:
    """Convenience function to parse a coverage report from file"""
    parser = CoverageReportParser()
    with open(file_path, 'r') as f:
        report_text = f.read()
    return parser.parse(report_text)
