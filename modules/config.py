"""
Configuration module - Centralizes all default values and constants
"""
from dataclasses import dataclass
from typing import Dict, Any

class ModelConfig:
    """Core model configuration with defaults"""
    
    # Compensation model defaults
    CARRIER_RATE: float = 0.027  # 2.7% carrier rate
    CONTRACT_MONTHS: int = 300    # 25 years
    PCT_IMMEDIATE: float = 0.7    # 70% paid immediately
    PCT_DEFERRED: float = 0.3     # 30% paid at month 18
    DEFERRED_MONTH: int = 18      # When deferred payment arrives
    DEFAULT_PERSISTENCY: float = 0.9  # 90% persistency rate
    
    # Team structure defaults
    DEFAULT_CLOSER_BASE: int = 5000
    DEFAULT_SETTER_BASE: int = 3000
    DEFAULT_BENCH_BASE: int = 3000
    DEFAULT_MANAGER_BASE: int = 15000
    
    # Performance defaults
    DEFAULT_MEETINGS_PER_CLOSER: int = 15  # Monthly
    DEFAULT_CONTACTS_PER_SETTER: int = 30  # Daily
    DEFAULT_RAMP_TIME_MONTHS: int = 3      # Time to full productivity
    
    # Commission structure
    DEFAULT_CLOSER_COMM_PCT: float = 0.20  # 20% to closers pool
    DEFAULT_SETTER_OF_CLOSER: float = 0.15  # 15% of closer commission
    DEFAULT_SPEED_BONUS: float = 0.10      # 10% for speed
    DEFAULT_FOLLOWUP_BONUS: float = 0.05   # 5% for followup
    
    # Funnel benchmarks
    CONTACT_RATE_MIN: float = 0.40
    CONTACT_RATE_MAX: float = 0.80
    MEETING_RATE_MIN: float = 0.20
    MEETING_RATE_MAX: float = 0.50
    CLOSE_RATE_MIN: float = 0.15
    CLOSE_RATE_MAX: float = 0.35
    
    # Financial health metrics
    MIN_LTV_CAC_RATIO: float = 3.0
    TARGET_LTV_CAC_RATIO: float = 5.0
    MIN_GROSS_MARGIN: float = 0.70
    TARGET_EBITDA_MARGIN: float = 0.25
    
    # Pipeline coverage ratios
    CONSERVATIVE_PIPELINE_COVERAGE: float = 3.0
    STANDARD_PIPELINE_COVERAGE: float = 4.0
    AGGRESSIVE_PIPELINE_COVERAGE: float = 5.0
    
    def __init__(self):
        # Attainment tiers
        self.ATTAINMENT_TIERS = {
            'tier_1': {'min': 0.0, 'max': 0.40, 'multiplier': 0.6, 'name': 'Below Threshold'},
            'tier_2': {'min': 0.40, 'max': 0.70, 'multiplier': 0.8, 'name': 'Developing'},
            'tier_3': {'min': 0.70, 'max': 1.00, 'multiplier': 1.0, 'name': 'At Target'},
            'tier_4': {'min': 1.00, 'max': 1.50, 'multiplier': 1.2, 'name': 'Exceeding'},
            'tier_5': {'min': 1.50, 'max': 10.0, 'multiplier': 1.6, 'name': 'Overachieving'}
        }
        
        # Sales cycle stages (in days)
        self.SALES_CYCLE_STAGES = {
            'discovery': 2,
            'qualification': 3,
            'evaluation': 7,
            'negotiation': 5,
            'closing': 3
        }
    
    @property
    def default_sales_cycle_days(self) -> int:
        """Total default sales cycle in days"""
        return sum(self.SALES_CYCLE_STAGES.values())
    
    def get_attainment_multiplier(self, attainment_pct: float) -> float:
        """Get multiplier based on attainment percentage"""
        for tier in self.ATTAINMENT_TIERS.values():
            if tier['min'] <= attainment_pct < tier['max']:
                return tier['multiplier']
        return 1.0
    
    def get_ote_health(self, base: float, variable: float) -> Dict[str, Any]:
        """Calculate OTE health metrics"""
        total_ote = base + variable
        base_pct = base / total_ote if total_ote > 0 else 0
        variable_pct = variable / total_ote if total_ote > 0 else 0
        
        # Health assessment
        is_healthy = 0.3 <= base_pct <= 0.5  # 30-50% base is healthy
        health_score = 'Healthy' if is_healthy else 'Review Needed'
        
        return {
            'total_ote': total_ote,
            'base': base,
            'variable': variable,
            'base_pct': base_pct,
            'variable_pct': variable_pct,
            'health_score': health_score,
            'is_healthy': is_healthy
        }

# Singleton instance
config = ModelConfig()
