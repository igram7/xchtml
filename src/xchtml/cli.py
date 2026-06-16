"""Command-line interface for xchtml.

Usage examples:
    xchtml generate                                # auto-detect from DerivedData
    xchtml generate MyTests.xcresult               # specific bundle
    xchtml generate MyTests.xcresult -o ./output   # custom output dir
    xchtml --version                               # show version
"""

import argparse
import os
import sys
from typing import Optional

from xchtml import __version__
from xchtml.core import (
    find_latest_xcresult_in_derived_data,
    resolve_manual_xcresult,
    load_xcresult_test_results,
    load_database_test_results,
    enrich_categories_with_database_metadata,
    load_coverage_data,
    load_test_summary,
    get_wall_clock_duration,
    get_top_insights,
    generate_html_report,
)
from xchtml.parsers import parse_xcresulttool_results, get_device_info_from_db


def _as_dict_metrics_and_categories(metrics, categories):
    """Normalizes parser output into plain dictionaries for report generation."""
    if hasattr(metrics, "to_dict"):
        metrics = metrics.to_dict()

    normalized_categories = {}
    for suite_name, tests in (categories or {}).items():
        normalized_tests = []
        for test in tests:
            if hasattr(test, "to_dict"):
                normalized_tests.append(test.to_dict())
            elif isinstance(test, dict):
                normalized_tests.append(test)
        normalized_categories[suite_name] = normalized_tests

    return metrics, normalized_categories


def _build_parser() -> argparse.ArgumentParser:
    """Builds the top-level argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="xchtml",
        description="Generate beautiful HTML reports from Xcode .xcresult bundles",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"xchtml {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── generate ──────────────────────────────────────────────────────────
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate an HTML report from an .xcresult bundle",
        description="Generate an HTML report from an .xcresult bundle",
    )
    gen_parser.add_argument(
        "xcresult",
        nargs="?",
        default=None,
        help="Path to .xcresult bundle (omit to auto-detect from DerivedData)",
    )
    gen_parser.add_argument(
        "-o",
        "--output",
        default="reports",
        help="Output directory for the generated report (default: reports)",
    )

    return parser


def _cmd_generate(args: argparse.Namespace) -> None:
    """Handles the 'generate' subcommand."""

    # Resolve the xcresult bundle path.
    if args.xcresult:
        # Direct path provided
        bundle_path = resolve_manual_xcresult(args.xcresult)
        if not bundle_path:
            print(f"Error: Could not resolve xcresult bundle from input: {args.xcresult}")
            sys.exit(1)
    else:
        # Auto-detect from DerivedData
        bundle_path = find_latest_xcresult_in_derived_data()
        if not bundle_path:
            print("Error: No .xcresult bundle found in Xcode DerivedData.")
            print("Tip: provide the path directly: xchtml generate <path>.xcresult")
            sys.exit(1)

    mode_label = "manual" if args.xcresult else "auto"
    print(f"Loading test results from xcresult bundle ({mode_label} mode): {bundle_path}")

    xcdata = load_xcresult_test_results(bundle_path)
    if not xcdata:
        print("Error: Failed to read test results from xcresult bundle.")
        sys.exit(1)

    metrics, categories = parse_xcresulttool_results(xcdata)
    metrics, categories = _as_dict_metrics_and_categories(metrics, categories)

    db_path = os.path.join(bundle_path, "database.sqlite3")
    if os.path.exists(db_path):
        db_results = load_database_test_results(db_path)
        if db_results:
            bundle_dir = os.path.dirname(db_path)
            categories = enrich_categories_with_database_metadata(categories, db_results, bundle_dir)

    if metrics is None or categories is None or not categories:
        print("Error: No test categories found in the xcresult bundle.")
        sys.exit(1)

    # Extract coverage and device info when available
    coverage = load_coverage_data(bundle_path)
    device_info = get_device_info_from_db(db_path).to_dict() if os.path.exists(db_path) else {}

    # Read the test-results summary once; it feeds both the wall-clock duration
    # and the Top Insights section.
    test_summary = load_test_summary(bundle_path)

    # Wall-clock run duration (matches Xcode's "Ran for ...") overrides the
    # summed per-test duration for the overall report figure.
    wall_duration = get_wall_clock_duration(test_summary)
    if wall_duration is not None:
        metrics['wall_duration'] = wall_duration

    # Top Insights (mirrors Xcode's Top Insights section in the result bundle)
    metrics['top_insights'] = get_top_insights(test_summary)

    # Generate the HTML report and per-category pages
    generate_html_report(
        metrics,
        categories,
        "report.html",
        coverage=coverage,
        device_info=device_info,
        output_dir=args.output,
    )

    print(f"Summary: {metrics['passed']} passed, {metrics['failed']} failed, "
          f"{metrics['skipped']} skipped out of {metrics['total']} tests")


def main() -> None:
    """Entry point for the xchtml CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate":
        _cmd_generate(args)


if __name__ == "__main__":
    main()
