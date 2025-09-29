"""
Dynamic Benchmarks System - Industry standards that adapt to context
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional

class DynamicBenchmarks:
    """Dynamic benchmarking system that adapts to industry, company size, and market conditions"""
    
    @staticmethod
    def get_funnel_benchmarks(industry: str = "insurance", 
                            company_size: str = "medium",
                            market_maturity: str = "established") -> Dict[str, Dict]:
        """
        Get dynamic funnel benchmarks based on context
        """
        base_benchmarks = {
            'contact_rate': {'min': 0.45, 'good': 0.60, 'excellent': 0.75},
            'meeting_rate': {'min': 0.25, 'good': 0.35, 'excellent': 0.50},
            'show_up_rate': {'min': 0.65, 'good': 0.75, 'excellent': 0.85},
            'close_rate': {'min': 0.15, 'good': 0.25, 'excellent': 0.35},
            'onboard_rate': {'min': 0.85, 'good': 0.95, 'excellent': 0.98}
        }
        
        # Industry adjustments
        industry_multipliers = {
            'insurance': {'contact_rate': 0.9, 'meeting_rate': 0.8, 'close_rate': 1.2},
            'saas': {'contact_rate': 1.1, 'meeting_rate': 1.2, 'close_rate': 0.8},
            'financial_services': {'contact_rate': 0.8, 'meeting_rate': 0.9, 'close_rate': 1.1},
            'real_estate': {'contact_rate': 1.2, 'meeting_rate': 1.1, 'close_rate': 0.9}
        }
        
        # Company size adjustments
        size_multipliers = {
            'startup': {'contact_rate': 1.1, 'meeting_rate': 1.1, 'close_rate': 0.9},
            'small': {'contact_rate': 1.05, 'meeting_rate': 1.05, 'close_rate': 0.95},
            'medium': {'contact_rate': 1.0, 'meeting_rate': 1.0, 'close_rate': 1.0},
            'large': {'contact_rate': 0.95, 'meeting_rate': 0.95, 'close_rate': 1.05}
        }
        
        # Market maturity adjustments
        maturity_multipliers = {
            'new_market': {'contact_rate': 0.8, 'meeting_rate': 0.9, 'close_rate': 0.7},
            'growing': {'contact_rate': 0.9, 'meeting_rate': 0.95, 'close_rate': 0.85},
            'established': {'contact_rate': 1.0, 'meeting_rate': 1.0, 'close_rate': 1.0},
            'saturated': {'contact_rate': 1.1, 'meeting_rate': 1.05, 'close_rate': 1.2}
        }
        
        # Apply adjustments
        adjusted_benchmarks = {}
        for metric, values in base_benchmarks.items():
            industry_mult = industry_multipliers.get(industry, {}).get(metric, 1.0)
            size_mult = size_multipliers.get(company_size, {}).get(metric, 1.0)
            maturity_mult = maturity_multipliers.get(market_maturity, {}).get(metric, 1.0)
            
            total_mult = industry_mult * size_mult * maturity_mult
            
            adjusted_benchmarks[metric] = {
                'min': min(values['min'] * total_mult, 0.95),
                'good': min(values['good'] * total_mult, 0.98),
                'excellent': min(values['excellent'] * total_mult, 0.99),
                'context': f"{industry.title()} | {company_size.title()} | {market_maturity.title()}"
            }
        
        return adjusted_benchmarks
    
    @staticmethod
    def get_cost_benchmarks(industry: str = "insurance",
                          lead_source: str = "digital",
                          geography: str = "mexico") -> Dict[str, Dict]:
        """
        Get dynamic cost benchmarks
        """
        base_costs = {
            'cpl': {'min': 50, 'good': 150, 'max': 300},
            'cpc': {'min': 100, 'good': 250, 'max': 500},
            'cpm': {'min': 300, 'good': 600, 'max': 1200},
            'cac': {'min': 1000, 'good': 3000, 'max': 6000}
        }
        
        # Industry cost adjustments (Mexico market)
        industry_multipliers = {
            'insurance': {'cpl': 1.2, 'cac': 1.5},  # Higher regulation, longer cycles
            'saas': {'cpl': 0.8, 'cac': 0.7},       # Digital-first, shorter cycles
            'financial_services': {'cpl': 1.4, 'cac': 1.8},  # High regulation
            'real_estate': {'cpl': 1.0, 'cac': 1.2}
        }
        
        # Lead source adjustments
        source_multipliers = {
            'digital': {'cpl': 1.0, 'cac': 1.0},
            'referral': {'cpl': 0.3, 'cac': 0.5},   # Much cheaper
            'cold_outbound': {'cpl': 1.5, 'cac': 1.8},  # More expensive
            'events': {'cpl': 2.0, 'cac': 1.2}      # High CPL, better conversion
        }
        
        # Geography adjustments (relative to Mexico City)
        geo_multipliers = {
            'mexico': 1.0,
            'usa': 3.5,
            'colombia': 0.7,
            'argentina': 0.8
        }
        
        # Apply adjustments
        adjusted_costs = {}
        for metric, values in base_costs.items():
            industry_mult = industry_multipliers.get(industry, {}).get(metric, 1.0)
            source_mult = source_multipliers.get(lead_source, {}).get(metric, 1.0)
            geo_mult = geo_multipliers.get(geography, 1.0)
            
            total_mult = industry_mult * source_mult * geo_mult
            
            adjusted_costs[metric] = {
                'min': values['min'] * total_mult,
                'good': values['good'] * total_mult,
                'max': values['max'] * total_mult,
                'context': f"{industry.title()} | {lead_source.title()} | {geography.title()}"
            }
        
        return adjusted_costs
    
    @staticmethod
    def get_financial_benchmarks(industry: str = "insurance",
                               business_model: str = "recurring") -> Dict[str, Dict]:
        """
        Get dynamic financial benchmarks
        """
        base_metrics = {
            'ltv_cac_ratio': {'min': 3.0, 'good': 5.0, 'excellent': 8.0},
            'ebitda_margin': {'min': 0.15, 'good': 0.25, 'excellent': 0.40},
            'gross_margin': {'min': 0.60, 'good': 0.75, 'excellent': 0.85},
            'payback_months': {'min': 18, 'good': 12, 'excellent': 6}
        }
        
        # Industry adjustments
        industry_adjustments = {
            'insurance': {
                'ltv_cac_ratio': 1.2,  # Higher LTV due to long contracts
                'ebitda_margin': 0.9,  # Lower due to regulation
                'payback_months': 1.5  # Longer due to deferred payments
            },
            'saas': {
                'ltv_cac_ratio': 1.0,
                'ebitda_margin': 1.1,
                'payback_months': 0.8
            }
        }
        
        # Business model adjustments
        model_adjustments = {
            'recurring': {
                'ltv_cac_ratio': 1.3,  # Higher LTV
                'payback_months': 1.2  # Longer payback acceptable
            },
            'transactional': {
                'ltv_cac_ratio': 0.7,
                'payback_months': 0.6
            }
        }
        
        # Apply adjustments
        adjusted_metrics = {}
        for metric, values in base_metrics.items():
            industry_mult = industry_adjustments.get(industry, {}).get(metric, 1.0)
            model_mult = model_adjustments.get(business_model, {}).get(metric, 1.0)
            
            if metric == 'payback_months':
                # For payback, higher multiplier means longer acceptable time
                adjusted_metrics[metric] = {
                    'excellent': values['excellent'] * industry_mult * model_mult,
                    'good': values['good'] * industry_mult * model_mult,
                    'min': values['min'] * industry_mult * model_mult,
                    'context': f"{industry.title()} | {business_model.title()}"
                }
            else:
                # For ratios and margins, apply normally
                adjusted_metrics[metric] = {
                    'min': values['min'] * industry_mult * model_mult,
                    'good': values['good'] * industry_mult * model_mult,
                    'excellent': values['excellent'] * industry_mult * model_mult,
                    'context': f"{industry.title()} | {business_model.title()}"
                }
        
        return adjusted_metrics
    
    @staticmethod
    def get_performance_status(actual_value: float, 
                             benchmark: Dict[str, float]) -> Tuple[str, str, str]:
        """
        Get performance status, color, and emoji based on benchmarks
        """
        # Handle both cost benchmarks (lower is better) and ratio benchmarks (higher is better)
        if 'excellent' in benchmark:
            # For financial benchmarks (higher is better)
            if actual_value >= benchmark['excellent']:
                return "Excellent", "#4CAF50", "🟢"
            elif actual_value >= benchmark['good']:
                return "Good", "#8BC34A", "🟡"
            elif actual_value >= benchmark['min']:
                return "Acceptable", "#FF9800", "🟠"
            else:
                return "Below Standard", "#F44336", "🔴"
        else:
            # For cost benchmarks (lower is better)
            if actual_value <= benchmark['min']:
                return "Excellent", "#4CAF50", "🟢"
            elif actual_value <= benchmark['good']:
                return "Good", "#8BC34A", "🟡"
            elif actual_value <= benchmark.get('max', benchmark['good'] * 2):
                return "Acceptable", "#FF9800", "🟠"
            else:
                return "Below Standard", "#F44336", "🔴"
    
    @staticmethod
    def calculate_benchmark_gaps(current_metrics: Dict[str, float],
                               benchmarks: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Calculate gaps between current performance and benchmarks
        """
        gaps = {}
        
        for metric, current_value in current_metrics.items():
            if metric in benchmarks:
                benchmark = benchmarks[metric]
                
                # Calculate gaps to each benchmark level
                gap_to_min = benchmark['min'] - current_value
                gap_to_good = benchmark['good'] - current_value
                gap_to_excellent = benchmark['excellent'] - current_value
                
                # Determine next target
                if current_value < benchmark['min']:
                    next_target = 'min'
                    gap_to_next = gap_to_min
                elif current_value < benchmark['good']:
                    next_target = 'good'
                    gap_to_next = gap_to_good
                else:
                    next_target = 'excellent'
                    gap_to_next = gap_to_excellent
                
                status, color, emoji = DynamicBenchmarks.get_performance_status(
                    current_value, benchmark
                )
                
                gaps[metric] = {
                    'current': current_value,
                    'status': status,
                    'color': color,
                    'emoji': emoji,
                    'next_target': next_target,
                    'gap_to_next': gap_to_next,
                    'gap_to_min': gap_to_min,
                    'gap_to_good': gap_to_good,
                    'gap_to_excellent': gap_to_excellent,
                    'benchmark': benchmark
                }
        
        return gaps
