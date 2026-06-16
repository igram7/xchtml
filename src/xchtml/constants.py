"""Constants and configuration for xchtml report generation."""

# Test Status Colors & Icons
STATUS_COLORS = {
    "passed": {"badge": "text-green-700 bg-green-100", "border": "border-green-500", "icon": "✓", "color": "#10B981"},
    "failed": {"badge": "text-red-700 bg-red-100", "border": "border-red-500", "icon": "✗", "color": "#EF4444"},
    "skipped": {"badge": "text-yellow-700 bg-yellow-100", "border": "border-yellow-500", "icon": "⊘", "color": "#F59E0B"},
}

# Coverage Colors
COVERAGE_COLORS = {
    "high": {"bar": "#10B981", "text": "text-green-600"},     # >= 75%
    "medium": {"bar": "#F59E0B", "text": "text-amber-600"},    # 40-75%
    "low": {"bar": "#EF4444", "text": "text-red-600"},         # < 40%
}

# Tailwind CSS Classes
CSS_CLASSES = {
    "card": "bg-white rounded-2xl shadow-sm border border-gray-200",
    "input": "rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-500/30 focus:border-slate-500 transition-all",
    "button": "px-4 py-2.5 rounded-xl text-white text-sm font-medium transition-all",
}

# Fonts
FONT_LINKS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">"""

# CDN Resources
CDN_TAILWIND = "https://cdn.tailwindcss.com"
CDN_CHARTJS = "https://cdn.jsdelivr.net/npm/chart.js@latest"

# Default configuration
DEFAULT_OUTPUT_DIR = "reports"
DEFAULT_OUTPUT_FILE = "report.html"
SIDEBAR_WIDTH = "300px"
