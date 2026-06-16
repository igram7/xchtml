"""Data models for xchtml test results."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    status: str
    duration: float
    srs_id: str
    error: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    category_description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status,
            "duration": self.duration,
            "srs_id": self.srs_id,
            "error": self.error,
            "description": self.description,
            "requirements": self.requirements,
            "category_description": self.category_description,
        }


@dataclass
class TestMetrics:
    """Aggregated test metrics."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: float = 0.0
    wall_duration: Optional[float] = None
    top_insights: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "duration": self.duration,
            "wall_duration": self.wall_duration,
            "top_insights": self.top_insights,
        }

    def get_pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.total <= 0:
            return 0.0
        return round((self.passed / self.total) * 100, 1)


@dataclass
class DeviceInfo:
    """Device/simulator information."""
    name: str = ""
    model: str = ""
    os_version: str = ""
    os_version_build: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "model": self.model,
            "os_version": self.os_version,
            "os_version_build": self.os_version_build,
        }

    def is_empty(self) -> bool:
        """Check if device info is empty."""
        return not any(self.to_dict().values())


@dataclass
class CoverageFile:
    """Code coverage for a single file."""
    path: str
    covered: int
    executable: int
    percent: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "covered": self.covered,
            "executable": self.executable,
            "percent": self.percent,
        }


@dataclass
class CoverageSummary:
    """Overall code coverage metrics."""
    covered_lines: int = 0
    executable_lines: int = 0
    percent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "covered_lines": self.covered_lines,
            "executable_lines": self.executable_lines,
            "percent": self.percent,
        }
