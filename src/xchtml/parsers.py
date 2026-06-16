"""Data parsing functions for xchtml."""

import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any

from .models import TestMetrics, TestCase, DeviceInfo, CoverageFile


def parse_duration(node: Dict[str, Any]) -> float:
    """Extract duration from a test node."""
    duration = node.get("durationInSeconds")
    if isinstance(duration, (int, float)):
        return float(duration)

    duration_str = node.get("duration")
    if isinstance(duration_str, str):
        try:
            seconds = 0.0
            if "m" in duration_str:
                parts = duration_str.split()
                for part in parts:
                    if part.endswith('m'):
                        seconds += float(part[:-1]) * 60
                    elif part.endswith('s'):
                        seconds += float(part[:-1])
            elif duration_str.endswith('s'):
                seconds += float(duration_str[:-1])
            return seconds
        except Exception:
            return 0.0

    return 0.0


def extract_metadata_from_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata from a test node."""
    if not isinstance(node, dict):
        return {}

    metadata = {}

    if isinstance(node.get('metadata'), dict):
        metadata = node['metadata']
        if metadata:
            return metadata

    attachments = node.get('attachments')
    if isinstance(attachments, dict) and '_values' in attachments:
        attachments = attachments['_values']

    if isinstance(attachments, list):
        for attachment in attachments:
            if not isinstance(attachment, dict):
                continue
            real_name = str(attachment.get('name', '')).lower()
            uri = str(attachment.get('uniformTypeIdentifier', '')).lower()
            if 'test metadata' in real_name or 'json' in uri or str(attachment.get('filenameOverride', '')).lower().endswith('.json'):
                payload = attachment.get('payload') or attachment.get('content') or attachment.get('string') or attachment.get('data')
                if isinstance(payload, dict):
                    return payload
                if isinstance(payload, str):
                    try:
                        return json.loads(payload)
                    except Exception:
                        pass

    for value in node.values():
        if isinstance(value, dict):
            metadata = extract_metadata_from_node(value)
            if metadata:
                return metadata
        elif isinstance(value, list):
            for item in value:
                metadata = extract_metadata_from_node(item)
                if metadata:
                    return metadata

    return {}


def parse_srs_id_from_metadata(metadata: Dict[str, Any], default_id: str) -> str:
    """Extract SRS ID from test metadata."""
    if not isinstance(metadata, dict):
        return default_id

    # Prefer explicit SRS fields
    for key in ('srs_id', 'SRS_ID', 'srsId'):
        val = metadata.get(key)
        if isinstance(val, str):
            v = val.strip()
            if v and v.upper() not in ('SRS_ID', 'SRS-ID', 'SRSID'):
                return v

    # Inspect requirements for SRS identifiers
    from .utils import normalize_requirements
    requirements = normalize_requirements(metadata.get('requirements'))
    candidates = []
    for req in requirements:
        if not isinstance(req, str):
            continue
        r = req.strip()
        if not r:
            continue
        ru = r.upper()
        if ru in ('SRS_ID', 'SRS-ID', 'SRSID'):
            continue
        # Prefer identifiers with digits or dashes
        if any(ch.isdigit() for ch in r) or '-' in r:
            return r
        candidates.append(r)

    # Fallback to candidates starting with SRS/REQ
    for c in candidates:
        cu = c.upper()
        if cu.startswith('SRS') or cu.startswith('REQ'):
            return c

    return default_id


def parse_xcresulttool_results(data: Dict[str, Any]) -> tuple:
    """Parse xcresulttool JSON output into metrics and categories."""
    metrics = TestMetrics()
    categories: Dict[str, List[TestCase]] = {}
    test_id_counter: Dict[str, int] = {}

    def walk(node: Dict[str, Any], current_suite: Optional[str] = None):
        """Recursively walk test node hierarchy."""
        if not isinstance(node, dict):
            return

        node_type = node.get("nodeType", "")
        
        if node_type == "Test Case":
            suite_name = current_suite or node.get("name", "General Tests")
            if suite_name not in categories:
                categories[suite_name] = []
                test_id_counter[suite_name] = 1

            status = node.get("result", "unknown")
            duration = parse_duration(node)
            default_srs_id = f"SRS-{suite_name.replace(' ', '')}-{test_id_counter[suite_name]}"
            metadata = extract_metadata_from_node(node)
            srs_id = parse_srs_id_from_metadata(metadata, default_srs_id)

            from .utils import normalize_requirements, normalize_status
            requirements = normalize_requirements(metadata.get("requirements"))
            description = metadata.get("description", "") if isinstance(metadata, dict) else ""
            cat_desc = metadata.get("category_description", "") if isinstance(metadata, dict) else ""
            test_id_counter[suite_name] += 1

            # Extract failure messages from child nodes
            failure_messages = []
            for child in node.get("children", []) or []:
                if isinstance(child, dict) and child.get("nodeType") == "Failure Message":
                    msg = str(child.get("name", "")).strip()
                    if msg:
                        failure_messages.append(msg)
            error_text = node.get("failureSummary", "") or "\n".join(failure_messages)

            test_case = TestCase(
                name=node.get("name", "Unknown Test"),
                status=normalize_status(status),
                duration=round(duration, 3),
                srs_id=srs_id,
                error=error_text,
                description=description,
                requirements=requirements,
                category_description=cat_desc,
            )
            categories[suite_name].append(test_case)

            # Update metrics
            if test_case.status == "passed":
                metrics.passed += 1
            elif test_case.status == "failed":
                metrics.failed += 1
            elif test_case.status == "skipped":
                metrics.skipped += 1
            metrics.duration += duration
            return

        next_suite = current_suite
        if node_type in ("Test Suite", "Unit test bundle", "UI test bundle", "Test Plan"):
            next_suite = node.get("name", current_suite)

        for child in node.get("children", []):
            walk(child, next_suite)

    for test_node in data.get("testNodes", []):
        walk(test_node, None)

    metrics.total = metrics.passed + metrics.failed + metrics.skipped
    metrics.duration = round(metrics.duration, 2)

    return metrics, categories


def get_device_info_from_db(db_path: str) -> DeviceInfo:
    """Extract device information from xcresult database."""
    if not db_path or not Path(db_path).exists():
        return DeviceInfo()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT device_fk FROM RunDestinations LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return DeviceInfo()

        device_fk = row[0]
        cursor.execute(
            "SELECT name, modelName, operatingSystemVersion, operatingSystemVersionWithBuildNumber FROM Devices WHERE rowid=?",
            (device_fk,)
        )
        d = cursor.fetchone()
        conn.close()
        
        if not d:
            return DeviceInfo()

        return DeviceInfo(
            name=d[0] or "",
            model=d[1] or "",
            os_version=d[2] or "",
            os_version_build=d[3] or "",
        )
    except Exception:
        return DeviceInfo()
