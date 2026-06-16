"""HTML building utilities for xchtml templates."""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from .constants import STATUS_COLORS, COVERAGE_COLORS, CSS_CLASSES, FONT_LINKS, CDN_TAILWIND, CDN_CHARTJS
from .utils import html_escape, format_duration, get_status_color, slug_from_name, get_coverage_colors


class StatusBadge:
    """Helper for rendering status badges."""
    
    @staticmethod
    def render(status: str) -> Dict[str, str]:
        """Get badge styling for a status."""
        return STATUS_COLORS.get(status, STATUS_COLORS["passed"])

    @staticmethod
    def html(status: str) -> str:
        """Render status badge HTML."""
        badge = StatusBadge.render(status)
        return f'<span class="inline-block px-3 py-1 rounded-full text-xs font-semibold {badge["badge"]}">{status.upper()}</span>'


class CoverageBadge:
    """Helper for rendering coverage badges."""
    
    @staticmethod
    def render(percent: float) -> Dict[str, str]:
        """Get coverage colors for a percentage."""
        bar, text = get_coverage_colors(percent)
        return {"bar": bar, "text": text}


class HtmlCard:
    """Helper for building card elements."""
    
    @staticmethod
    def metric(label: str, value: str, subtext: str, metric_type: str = "total") -> str:
        """Build a metric card."""
        return f"""<div class="metric-card {metric_type}">
                    <p class="text-xs text-slate-500 font-semibold uppercase tracking-wider mb-1">{label}</p>
                    <p class="text-3xl font-bold text-slate-800">{value}</p>
                    <p class="text-xs text-slate-400 mt-1">{subtext}</p>
                </div>"""
    
    @staticmethod
    def stat(label: str, value: str, color_class: str = "text-slate-700") -> str:
        """Build a stat display."""
        return f"""<div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div class="text-sm text-slate-500">{label}</div>
                    <div class="text-2xl font-bold {color_class}">{value}</div>
                </div>"""


class HtmlBase:
    """Base HTML template builder."""
    
    @staticmethod
    def doctype_and_head(title: str, extra_scripts: str = "") -> str:
        """Generate HTML head section."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {FONT_LINKS}
    <script src="{CDN_TAILWIND}"></script>
    <script src="{CDN_CHARTJS}"></script>
    {extra_scripts}
    <style>
        * {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
    </style>
</head>
<body class="bg-slate-50 text-gray-900 antialiased min-h-screen">"""
    
    @staticmethod
    def footer() -> str:
        """Generate footer."""
        return """    <footer class="mt-8 py-8 border-t border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-slate-500">Automated Test Report</div>
    </footer>
</body>
</html>"""
    
    @staticmethod
    def header(title: str, subtitle: str = "", extra_html: str = "") -> str:
        """Generate page header."""
        return f"""    <header class="text-white shadow-lg" style="background: linear-gradient(135deg, #0f172a 0%, #111827 50%, #000000 100%);">
        <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center">
                <div>
                    <p class="text-white/60 text-xs uppercase tracking-widest mb-1">Report</p>
                    <h1 class="text-2xl sm:text-3xl font-extrabold tracking-tight">{title}</h1>
                    {f'<p class="text-white/70 text-sm mt-1">{subtitle}</p>' if subtitle else ''}
                </div>
                {extra_html}
            </div>
        </div>
    </header>"""


class ErrorMessageBuilder:
    """Build error message displays."""
    
    @staticmethod
    def render(error_text: str, css_class: str = "bg-red-50 border border-red-200") -> str:
        """Render error message."""
        if not error_text:
            return ""
        escaped = html_escape(error_text)
        return f'<div class="mt-3 p-3 {css_class} rounded-lg text-xs font-mono whitespace-pre-wrap break-words overflow-x-auto">{escaped}</div>'


class ChartBuilder:
    """Build Chart.js configurations."""
    
    @staticmethod
    def doughnut_chart(chart_id: str, passed: int, failed: int, skipped: int) -> str:
        """Generate doughnut chart JavaScript."""
        return f"""
        new Chart(document.getElementById('{chart_id}').getContext('2d'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(['Passed', 'Failed', 'Skipped'])},
                datasets: [{{
                    data: {json.dumps([passed, failed, skipped])},
                    backgroundColor: ['#10B981', '#EF4444', '#F59E0B'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }}]
            }},
            options: {{
                responsive: true,
                cutout: '65%',
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ padding: 16, usePointStyle: true, pointStyle: 'circle' }} }}
                }}
            }}
        }});"""
