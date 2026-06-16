"""Utility functions for xchtml report generation."""

import re
from typing import Optional, Dict, List, Any


def html_escape(text: str) -> str:
    """Escape HTML special characters in text."""
    return (
        str(text)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable 'Xm Ys' string."""
    try:
        total = float(seconds)
    except (TypeError, ValueError):
        return "0s"
    if total < 0:
        total = 0
    mins = int(total // 60)
    secs = total % 60
    if mins > 0:
        return f"{mins}m {secs:.1f}s"
    else:
        return f"{secs:.1f}s"


def slug_from_name(name: str) -> str:
    """Convert a name to a URL-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def get_status_color(status: str) -> str:
    """Get the color code for a test status."""
    status_map = {
        "passed": "#10B981",
        "failed": "#EF4444",
        "skipped": "#F59E0B",
    }
    return status_map.get(status.lower(), "#94A3B8")


def normalize_status(status: Optional[str]) -> str:
    """Normalize test status to standard form."""
    if not status:
        return "unknown"
    s = str(status).strip().lower()
    status_map = {
        "success": "passed",
        "passed": "passed",
        "failure": "failed",
        "failed": "failed",
        "skipped": "skipped",
    }
    return status_map.get(s, s)


def normalize_requirements(requirements: Any) -> List[str]:
    """Normalize requirements from various formats to a list of strings."""
    if requirements is None:
        return []
    if isinstance(requirements, str):
        r = requirements.strip()
        if not r or r.upper() in ('SRS_ID', 'SRS-ID', 'SRSID'):
            return []
        return [r]
    
    normalized = []
    if isinstance(requirements, dict) and '_value' in requirements:
        return normalize_requirements(requirements['_value'])
    
    if isinstance(requirements, list):
        for req in requirements:
            if isinstance(req, dict) and '_value' in req:
                req = req['_value']
            if isinstance(req, str) and req.strip():
                r = req.strip()
                if r.upper() not in ('SRS_ID', 'SRS-ID', 'SRSID'):
                    normalized.append(r)
    
    return normalized


def get_coverage_colors(percent: float) -> tuple:
    """Get bar and text colors for a coverage percentage."""
    if percent >= 75:
        return "#10B981", "text-green-600"
    if percent >= 40:
        return "#F59E0B", "text-amber-600"
    return "#EF4444", "text-red-600"


def calculate_pass_rate(passed: int, total: int) -> float:
    """Calculate pass rate percentage."""
    if total <= 0:
        return 0.0
    return round((passed / total) * 100, 1)
