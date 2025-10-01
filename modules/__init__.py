# Module initialization file
"""
Sales Compensation Dashboard - New Architecture

This package provides:
- Type-safe business models (Pydantic)
- Pure calculation engines (single source of truth)
- Sensitivity analysis and scenario modeling
- Smart caching and state management
- Reusable UI components
"""

__version__ = "3.0.0"

# New architecture exports
__all__ = [
    "models",
    "engine",
    "engine_pnl",
    "scenario",
    "state",
    "ui_components",
    "dashboard_adapter",
]
