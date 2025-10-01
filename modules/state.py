"""
State management and cache key generation
"""

import json
import hashlib
from typing import Any, List, Dict


def hash_key(*objects: Any) -> str:
    """
    Generate a stable hash key from multiple objects.
    Used for cache invalidation - key changes when inputs change.
    
    Args:
        *objects: Any JSON-serializable objects
    
    Returns:
        MD5 hash string (32 chars)
    """
    try:
        serialized = json.dumps(objects, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode()).hexdigest()
    except (TypeError, ValueError) as e:
        # Fallback to string representation
        return hashlib.md5(str(objects).encode()).hexdigest()


def version_token(prefix: str, *dependencies: Any) -> str:
    """
    Create a version token for cache invalidation.
    
    Args:
        prefix: Human-readable prefix (e.g., 'gtm_v1')
        *dependencies: Values that affect this cache
    
    Returns:
        Version string like 'gtm_v1_abc123def'
    """
    hash_suffix = hash_key(*dependencies)[:8]  # Short hash
    return f"{prefix}_{hash_suffix}"


def extract_gtm_state(session_state) -> Dict:
    """
    Extract GTM-related state for cache keying.
    
    Returns dict with only the fields that affect GTM calculations.
    """
    return {
        'channels': session_state.get('gtm_channels', []),
        'avg_deal_value': session_state.get('avg_deal_value'),
        'upfront_pct': session_state.get('upfront_payment_pct'),
        'grr': session_state.get('grr_rate')
    }


def extract_pnl_state(session_state) -> Dict:
    """
    Extract P&L-related state for cache keying.
    """
    return {
        'team_base': {
            'closers': session_state.get('num_closers_main', 0) * session_state.get('closer_base', 0),
            'setters': session_state.get('num_setters_main', 0) * session_state.get('setter_base', 0),
            'managers': session_state.get('num_managers_main', 0) * session_state.get('manager_base', 0),
            'bench': session_state.get('num_benchs_main', 0) * session_state.get('bench_base', 0)
        },
        'commissions': {
            'closer_pct': session_state.get('closer_commission_pct'),
            'setter_pct': session_state.get('setter_commission_pct'),
            'manager_pct': session_state.get('manager_commission_pct')
        },
        'opex': {
            'office': session_state.get('office_rent'),
            'software': session_state.get('software_costs'),
            'other': session_state.get('other_opex')
        },
        'gov_pct': session_state.get('government_cost_pct')
    }


def extract_compensation_state(session_state) -> Dict:
    """
    Extract compensation-related state for cache keying.
    """
    return {
        'closer': {
            'base': session_state.get('closer_base'),
            'variable': session_state.get('closer_variable'),
            'commission_pct': session_state.get('closer_commission_pct')
        },
        'setter': {
            'base': session_state.get('setter_base'),
            'variable': session_state.get('setter_variable'),
            'commission_pct': session_state.get('setter_commission_pct')
        },
        'manager': {
            'base': session_state.get('manager_base'),
            'variable': session_state.get('manager_variable'),
            'commission_pct': session_state.get('manager_commission_pct')
        }
    }


class StateSnapshot:
    """
    Immutable snapshot of relevant state for calculations.
    Prevents accidental mutation and makes cache keys deterministic.
    """
    
    def __init__(self, **kwargs):
        self._data = dict(kwargs)
        self._hash = hash_key(self._data)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def to_dict(self) -> Dict:
        return self._data.copy()
    
    def cache_key(self) -> str:
        return self._hash
    
    def __hash__(self):
        return hash(self._hash)
    
    def __eq__(self, other):
        if not isinstance(other, StateSnapshot):
            return False
        return self._hash == other._hash


def create_business_snapshot(session_state) -> StateSnapshot:
    """
    Create a complete business state snapshot for caching.
    """
    return StateSnapshot(
        gtm=extract_gtm_state(session_state),
        pnl=extract_pnl_state(session_state),
        comp=extract_compensation_state(session_state),
        timestamp=session_state.get('last_update_timestamp', 0)
    )


def has_state_changed(
    session_state,
    last_snapshot: StateSnapshot,
    scope: str = 'all'
) -> bool:
    """
    Check if relevant state has changed since last snapshot.
    
    Args:
        session_state: Current Streamlit session state
        last_snapshot: Previous snapshot
        scope: Which scope to check ('gtm', 'pnl', 'comp', 'all')
    
    Returns:
        True if state has changed
    """
    if scope == 'gtm':
        current = extract_gtm_state(session_state)
        return hash_key(current) != hash_key(last_snapshot.get('gtm'))
    
    elif scope == 'pnl':
        current = extract_pnl_state(session_state)
        return hash_key(current) != hash_key(last_snapshot.get('pnl'))
    
    elif scope == 'comp':
        current = extract_compensation_state(session_state)
        return hash_key(current) != hash_key(last_snapshot.get('comp'))
    
    else:  # 'all'
        current_snapshot = create_business_snapshot(session_state)
        return current_snapshot.cache_key() != last_snapshot.cache_key()
