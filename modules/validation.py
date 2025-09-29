"""
Validation module - QA checks and error detection
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from .config import config

class ModelValidator:
    """Validates model inputs and outputs for errors"""
    
    @staticmethod
    def validate_funnel_metrics(contact_rate: float, 
                               meeting_rate: float, 
                               close_rate: float) -> Tuple[List[str], List[str]]:
        """Validate funnel conversion rates"""
        errors = []
        warnings = []
        
        # Check ranges
        if not 0 <= contact_rate <= 1:
            errors.append(f"Contact rate {contact_rate:.1%} is outside valid range [0-100%]")
        elif contact_rate < config.CONTACT_RATE_MIN:
            warnings.append(f"Contact rate {contact_rate:.1%} is below benchmark {config.CONTACT_RATE_MIN:.1%}")
        elif contact_rate > config.CONTACT_RATE_MAX:
            warnings.append(f"Contact rate {contact_rate:.1%} is above benchmark {config.CONTACT_RATE_MAX:.1%}")
        
        if not 0 <= meeting_rate <= 1:
            errors.append(f"Meeting rate {meeting_rate:.1%} is outside valid range [0-100%]")
        elif meeting_rate < config.MEETING_RATE_MIN:
            warnings.append(f"Meeting rate {meeting_rate:.1%} is below benchmark {config.MEETING_RATE_MIN:.1%}")
        elif meeting_rate > config.MEETING_RATE_MAX:
            warnings.append(f"Meeting rate {meeting_rate:.1%} is above benchmark {config.MEETING_RATE_MAX:.1%}")
        
        if not 0 <= close_rate <= 1:
            errors.append(f"Close rate {close_rate:.1%} is outside valid range [0-100%]")
        elif close_rate < config.CLOSE_RATE_MIN:
            warnings.append(f"Close rate {close_rate:.1%} is below benchmark {config.CLOSE_RATE_MIN:.1%}")
        elif close_rate > config.CLOSE_RATE_MAX:
            warnings.append(f"Close rate {close_rate:.1%} is above benchmark {config.CLOSE_RATE_MAX:.1%}")
        
        # Check logical consistency
        lead_to_sale = contact_rate * meeting_rate * close_rate
        if lead_to_sale < 0.001:  # Less than 0.1%
            errors.append(f"Lead to sale conversion {lead_to_sale:.2%} is unrealistically low")
        elif lead_to_sale > 0.20:  # More than 20%
            warnings.append(f"Lead to sale conversion {lead_to_sale:.1%} seems very high")
        
        return errors, warnings
    
    @staticmethod
    def validate_team_capacity(leads: float,
                              meetings_needed: float,
                              contacts_needed: float,
                              num_closers: int,
                              num_setters: int) -> Tuple[List[str], List[str]]:
        """Validate team has capacity for volume"""
        errors = []
        warnings = []
        
        # Calculate capacity
        closer_capacity = num_closers * config.DEFAULT_MEETINGS_PER_CLOSER * 4
        setter_capacity = num_setters * config.DEFAULT_CONTACTS_PER_SETTER * 20
        
        # Check closer capacity
        if meetings_needed > closer_capacity:
            shortage = meetings_needed - closer_capacity
            additional_closers = int(np.ceil(shortage / (config.DEFAULT_MEETINGS_PER_CLOSER * 4)))
            errors.append(f"Need {additional_closers} more closers. Current capacity: {closer_capacity:.0f}, Need: {meetings_needed:.0f}")
        elif meetings_needed < closer_capacity * 0.5:
            warnings.append(f"Closers at {(meetings_needed/closer_capacity)*100:.0f}% capacity. Consider reducing headcount")
        
        # Check setter capacity  
        if contacts_needed > setter_capacity:
            shortage = contacts_needed - setter_capacity
            additional_setters = int(np.ceil(shortage / (config.DEFAULT_CONTACTS_PER_SETTER * 20)))
            errors.append(f"Need {additional_setters} more setters. Current capacity: {setter_capacity:.0f}, Need: {contacts_needed:.0f}")
        elif contacts_needed < setter_capacity * 0.5:
            warnings.append(f"Setters at {(contacts_needed/setter_capacity)*100:.0f}% capacity. Consider reducing headcount")
        
        return errors, warnings
    
    @staticmethod
    def validate_financial_health(ltv_cac_ratio: float,
                                 ebitda_margin: float,
                                 gross_margin: float,
                                 cos_percentage: float) -> Tuple[List[str], List[str]]:
        """Validate financial health metrics"""
        errors = []
        warnings = []
        
        # LTV:CAC validation
        if ltv_cac_ratio < 1:
            errors.append(f"LTV:CAC ratio {ltv_cac_ratio:.1f} is below 1. Losing money on every customer!")
        elif ltv_cac_ratio < config.MIN_LTV_CAC_RATIO:
            warnings.append(f"LTV:CAC ratio {ltv_cac_ratio:.1f} is below healthy minimum of {config.MIN_LTV_CAC_RATIO}:1")
        elif ltv_cac_ratio > 10:
            warnings.append(f"LTV:CAC ratio {ltv_cac_ratio:.1f} might be too good to be true. Verify calculations")
        
        # EBITDA margin validation
        if ebitda_margin < 0:
            errors.append(f"EBITDA margin is negative ({ebitda_margin:.1%}). Business is unprofitable")
        elif ebitda_margin < 0.10:
            warnings.append(f"EBITDA margin {ebitda_margin:.1%} is below 10%. Consider cost optimization")
        elif ebitda_margin > 0.50:
            warnings.append(f"EBITDA margin {ebitda_margin:.1%} seems very high. Verify calculations")
        
        # Gross margin validation
        if gross_margin < config.MIN_GROSS_MARGIN:
            warnings.append(f"Gross margin {gross_margin:.1%} is below target {config.MIN_GROSS_MARGIN:.1%}")
        
        # Cost of sales validation
        if cos_percentage > 0.30:
            warnings.append(f"Cost of sales {cos_percentage:.1%} is above 30%. Consider commission structure")
        elif cos_percentage < 0.05:
            warnings.append(f"Cost of sales {cos_percentage:.1%} seems very low. Might impact talent retention")
        
        return errors, warnings
    
    @staticmethod
    def validate_compensation_structure(base_pct: float,
                                       commission_rate: float,
                                       ote: float,
                                       market_ote: float) -> Tuple[List[str], List[str]]:
        """Validate compensation structure"""
        errors = []
        warnings = []
        
        # Base/variable split
        if base_pct < 0.20:
            warnings.append(f"Base salary {base_pct:.0%} is very low. May cause retention issues")
        elif base_pct > 0.60:
            warnings.append(f"Base salary {base_pct:.0%} is high. May reduce motivation")
        
        # Commission rate
        if commission_rate > 0.30:
            warnings.append(f"Commission rate {commission_rate:.1%} is very high")
        elif commission_rate < 0.05:
            warnings.append(f"Commission rate {commission_rate:.1%} may not be motivating")
        
        # OTE comparison
        ote_variance = (ote - market_ote) / market_ote if market_ote > 0 else 0
        if ote_variance < -0.20:
            errors.append(f"OTE ${ote:,.0f} is {abs(ote_variance):.0%} below market ${market_ote:,.0f}")
        elif ote_variance > 0.30:
            warnings.append(f"OTE ${ote:,.0f} is {ote_variance:.0%} above market. Check budget")
        
        return errors, warnings
    
    @staticmethod
    def validate_sales_cycle(cycle_days: int,
                           deal_velocity: float,
                           pipeline_coverage: float) -> Tuple[List[str], List[str]]:
        """Validate sales cycle metrics"""
        errors = []
        warnings = []
        
        # Sales cycle length
        if cycle_days < 7:
            warnings.append(f"Sales cycle {cycle_days} days seems very short for B2B")
        elif cycle_days > 180:
            warnings.append(f"Sales cycle {cycle_days} days is very long. Consider pipeline coverage")
        
        # Deal velocity (deals per rep per month)
        if deal_velocity < 1:
            warnings.append(f"Deal velocity {deal_velocity:.1f} deals/rep/month is very low")
        elif deal_velocity > 10:
            warnings.append(f"Deal velocity {deal_velocity:.1f} deals/rep/month seems high for quality")
        
        # Pipeline coverage vs sales cycle
        if cycle_days > 60 and pipeline_coverage < 4:
            warnings.append(f"Long sales cycle ({cycle_days} days) needs higher pipeline coverage (currently {pipeline_coverage:.1f}x)")
        
        return errors, warnings
    
    @staticmethod
    def validate_scenario(scenario_data: Dict) -> Dict[str, any]:
        """Complete scenario validation"""
        all_errors = []
        all_warnings = []
        
        # Validate funnel
        if all(k in scenario_data for k in ['contact_rate', 'meeting_rate', 'close_rate']):
            errors, warnings = ModelValidator.validate_funnel_metrics(
                scenario_data['contact_rate'],
                scenario_data['meeting_rate'],
                scenario_data['close_rate']
            )
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        # Validate financials
        if all(k in scenario_data for k in ['ltv_cac_ratio', 'ebitda_margin', 'gross_margin', 'cos_percentage']):
            errors, warnings = ModelValidator.validate_financial_health(
                scenario_data['ltv_cac_ratio'],
                scenario_data['ebitda_margin'],
                scenario_data['gross_margin'],
                scenario_data['cos_percentage']
            )
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        # Validate team capacity
        if all(k in scenario_data for k in ['leads', 'meetings_needed', 'contacts_needed', 'num_closers', 'num_setters']):
            errors, warnings = ModelValidator.validate_team_capacity(
                scenario_data['leads'],
                scenario_data['meetings_needed'],
                scenario_data['contacts_needed'],
                scenario_data['num_closers'],
                scenario_data['num_setters']
            )
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        # Calculate health score
        health_score = 100
        health_score -= len(all_errors) * 20  # Each error reduces score by 20
        health_score -= len(all_warnings) * 5  # Each warning reduces score by 5
        health_score = max(0, health_score)
        
        return {
            'errors': all_errors,
            'warnings': all_warnings,
            'health_score': health_score,
            'status': 'Critical' if all_errors else 'Warning' if all_warnings else 'Healthy',
            'is_valid': len(all_errors) == 0
        }


class DataConsistencyChecker:
    """Checks for data consistency and relationships"""
    
    @staticmethod
    def check_pipeline_math(revenue_target: float,
                          avg_deal_size: float,
                          close_rate: float,
                          pipeline_value: float,
                          pipeline_coverage: float) -> Dict[str, any]:
        """Verify pipeline math is consistent"""
        # Calculate expected values
        deals_needed = revenue_target / avg_deal_size
        pipeline_needed = deals_needed / close_rate * pipeline_coverage
        
        # Check consistency
        pipeline_gap = pipeline_needed - pipeline_value
        gap_percentage = pipeline_gap / pipeline_needed if pipeline_needed > 0 else 0
        
        issues = []
        if abs(gap_percentage) > 0.10:  # More than 10% off
            issues.append(f"Pipeline math inconsistent: Need ${pipeline_needed:,.0f}, Have ${pipeline_value:,.0f} ({gap_percentage:.1%} gap)")
        
        return {
            'is_consistent': len(issues) == 0,
            'pipeline_needed': pipeline_needed,
            'pipeline_actual': pipeline_value,
            'gap': pipeline_gap,
            'gap_percentage': gap_percentage,
            'issues': issues
        }
    
    @staticmethod
    def check_capacity_alignment(meetings_scheduled: float,
                                contacts_made: float,
                                closer_capacity: float,
                                setter_capacity: float) -> Dict[str, any]:
        """Check if capacity aligns with activity"""
        closer_utilization = meetings_scheduled / closer_capacity if closer_capacity > 0 else 0
        setter_utilization = contacts_made / setter_capacity if setter_capacity > 0 else 0
        
        issues = []
        if closer_utilization > 1.2:
            issues.append(f"Closers overloaded at {closer_utilization:.0%} capacity")
        if setter_utilization > 1.2:
            issues.append(f"Setters overloaded at {setter_utilization:.0%} capacity")
        
        return {
            'is_aligned': len(issues) == 0,
            'closer_utilization': closer_utilization,
            'setter_utilization': setter_utilization,
            'issues': issues
        }
    
    @staticmethod
    def check_revenue_consistency(monthly_revenue: float,
                                 sales: float,
                                 avg_deal_size: float,
                                 immediate_pct: float = 0.7) -> Dict[str, any]:
        """Check revenue calculations consistency"""
        expected_revenue = sales * avg_deal_size * immediate_pct
        revenue_variance = abs(monthly_revenue - expected_revenue) / expected_revenue if expected_revenue > 0 else 0
        
        issues = []
        if revenue_variance > 0.05:  # More than 5% variance
            issues.append(f"Revenue inconsistent: Reported ${monthly_revenue:,.0f} vs Expected ${expected_revenue:,.0f}")
        
        return {
            'is_consistent': len(issues) == 0,
            'reported_revenue': monthly_revenue,
            'expected_revenue': expected_revenue,
            'variance': revenue_variance,
            'issues': issues
        }
