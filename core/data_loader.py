"""
core/data_loader.py
───────────────────
Data gateway for the RoadMind-X Strategist AI.

Architecture Rule:
    NO other module opens the JSON files directly.
    All data access goes through the functions in this module.

Responsibilities:
    - Load and validate ai_context.json
    - Load and validate causality_graph.json
    - Provide typed convenience extractors
    - Cache results to avoid re-reading on every Streamlit rerun
    - Raise descriptive errors so the UI can show helpful messages
"""

import json
import streamlit as st
from pathlib import Path
from typing import Any

from config.settings import (
    AI_CONTEXT_PATH,
    CAUSALITY_GRAPH_PATH,
    CACHE_TTL_SECONDS,
)


# ── Private Helpers ───────────────────────────────────────────────────────────

def _read_json(path: Path) -> dict:
    """
    Read and parse a JSON file from disk.

    Raises FileNotFoundError with a human-readable message if missing.
    Raises ValueError with context if JSON is malformed.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {path}\n"
            f"Make sure '{path.name}' is inside the 'data/' directory."
        )

    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse '{path.name}'. "
            f"The file contains invalid JSON.\nDetail: {exc}"
        ) from exc


def _validate_ai_context(data: dict) -> None:
    """
    Validate that ai_context.json has all required top-level keys.
    Raises ValueError listing every missing key at once.
    """
    required_keys = {"system_status", "hotspots"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(
            f"ai_context.json is missing required keys: {sorted(missing)}"
        )

    required_status_keys = {"overall_city_health_score", "active_alerts", "last_updated"}
    status = data.get("system_status", {})
    missing_status = required_status_keys - status.keys()
    if missing_status:
        raise ValueError(
            f"ai_context.json → system_status is missing keys: {sorted(missing_status)}"
        )


def _validate_causality_graph(data: dict) -> None:
    """
    Validate that causality_graph.json has nodes and links arrays.
    Raises ValueError listing every missing key at once.
    """
    required_keys = {"nodes", "links"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(
            f"causality_graph.json is missing required keys: {sorted(missing)}"
        )

    if not isinstance(data["nodes"], list):
        raise ValueError("causality_graph.json → 'nodes' must be a list.")
    if not isinstance(data["links"], list):
        raise ValueError("causality_graph.json → 'links' must be a list.")


# ── Public Loaders (Streamlit-cached) ─────────────────────────────────────────

@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_ai_context() -> dict[str, Any]:
    """
    Load, validate, and cache ai_context.json.

    Returns the full parsed dictionary.
    Cached for CACHE_TTL_SECONDS (default 5 minutes).

    Usage:
        from core.data_loader import load_ai_context
        ctx = load_ai_context()
    """
    data = _read_json(AI_CONTEXT_PATH)
    _validate_ai_context(data)
    return data


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_causality_graph() -> dict[str, Any]:
    """
    Load, validate, and cache causality_graph.json.

    Returns the full parsed dictionary with 'nodes' and 'links' arrays.
    Cached for CACHE_TTL_SECONDS (default 5 minutes).

    Usage:
        from core.data_loader import load_causality_graph
        graph = load_causality_graph()
    """
    data = _read_json(CAUSALITY_GRAPH_PATH)
    _validate_causality_graph(data)
    return data


# ── Convenience Extractors ────────────────────────────────────────────────────

def get_system_status() -> dict[str, Any]:
    """
    Return the system_status block from ai_context.json.

    Returns:
        {
            "overall_city_health_score": int,
            "active_alerts": int,
            "last_updated": str (ISO 8601)
        }
    """
    return load_ai_context()["system_status"]


def get_hotspots() -> list[dict[str, Any]]:
    """
    Return the list of hotspot objects from ai_context.json.

    Each hotspot contains:
        location, current_issue, severity, violation_increase_percentage,
        root_cause_analysis, digital_twin_simulations
    """
    return load_ai_context()["hotspots"]


def get_severity_counts() -> dict[str, int]:
    """
    Count hotspots by severity level.

    Returns:
        {"Critical": 1, "High": 1, "Medium": 1, "Low": 0}

    Used by: forecast charts, sidebar summary badge.
    """
    counts: dict[str, int] = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for h in get_hotspots():
        sev = h.get("severity", "Low")
        if sev in counts:
            counts[sev] += 1
        else:
            counts[sev] = 1
    return counts


def get_graph_nodes() -> list[dict[str, Any]]:
    """
    Return the list of node objects from causality_graph.json.

    Each node contains: {"id": str, "group": str}
    """
    return load_causality_graph()["nodes"]


def get_graph_links() -> list[dict[str, Any]]:
    """
    Return the list of link/edge objects from causality_graph.json.

    Each link contains: {"source": str, "target": str, "weight": int}
    """
    return load_causality_graph()["links"]


def get_context_summary_for_prompt() -> str:
    """
    Serialize the full ai_context.json as a formatted JSON string.
    Used by prompt_builder.py to inject live city data into the LLM prompt.

    Returns a pretty-printed JSON string.
    """
    return json.dumps(load_ai_context(), indent=2)


def get_graph_summary_for_prompt() -> str:
    """
    Serialize the full causality_graph.json as a formatted JSON string.
    Used by prompt_builder.py to inject causal graph data into the LLM prompt.

    Returns a pretty-printed JSON string.
    """
    return json.dumps(load_causality_graph(), indent=2)
