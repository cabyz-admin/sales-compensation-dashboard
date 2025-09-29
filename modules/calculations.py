"""
Calculations module - Core business logic and calculations
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from .config import config

class RevenueCalculator:
    """Handles all revenue calculations"""
    
    @staticmethod
    def calculate_compensation(premium_monthly: float, 
                              carrier_rate: float = config.CARRIER_RATE,
                              contract_months: int = config.CONTRACT_MONTHS) -> Dict[str, float]:
        """Calculate total compensation structure"""
        total_premium = premium_monthly * contract_months
        total_compensation = total_premium * carrier_rate
        immediate_payment = total_compensation * config.PCT_IMMEDIATE
        deferred_payment = total_compensation * config.PCT_DEFERRED
        
        return {
            'total_premium': total_premium,
            'total_compensation': total_compensation,
            'immediate_payment': immediate_payment,
            'deferred_payment': deferred_payment,
            'immediate_per_sale': immediate_payment,
            'deferred_per_sale': deferred_payment,
            'expected_total': immediate_payment + (deferred_payment * config.DEFAULT_PERSISTENCY)
        }
    
    @staticmethod
    def calculate_monthly_revenue(sales: float, 
                                 avg_premium: float,
                                 month_number: int = 1) -> Dict[str, float]:
        """Calculate revenue for a specific month including deferred payments"""
        comp = RevenueCalculator.calculate_compensation(avg_premium)
        
        # Current month sales
        immediate_revenue = sales * comp['immediate_per_sale']
        
        # Deferred revenue from 18 months ago (if applicable)
        deferred_revenue = 0
        if month_number > config.DEFERRED_MONTH:
            # Assuming same sales 18 months ago for now
            deferred_revenue = sales * comp['deferred_per_sale'] * config.DEFAULT_PERSISTENCY
        
        return {
            'immediate': immediate_revenue,
            'deferred': deferred_revenue,
            'total': immediate_revenue + deferred_revenue,
            'month': month_number
        }
    
    @staticmethod
    def project_revenue_timeline(monthly_sales: float,
                                avg_premium: float,
                                num_months: int,
                                growth_rate: float = 0.0) -> pd.DataFrame:
        """Project revenue over multiple months with growth"""
        timeline = []
        
        for month in range(1, num_months + 1):
            # Apply growth rate
            sales = monthly_sales * ((1 + growth_rate) ** (month - 1))
            
            revenue = RevenueCalculator.calculate_monthly_revenue(sales, avg_premium, month)
            
            timeline.append({
                'month': month,
                'sales': sales,
                'immediate_revenue': revenue['immediate'],
                'deferred_revenue': revenue['deferred'],
                'total_revenue': revenue['total'],
                'cumulative_revenue': 0  # Will calculate after
            })
        
        df = pd.DataFrame(timeline)
        df['cumulative_revenue'] = df['total_revenue'].cumsum()
        
        # Add quarter and year columns
        df['quarter'] = ((df['month'] - 1) // 3) + 1
        df['year'] = ((df['month'] - 1) // 12) + 1
        
        return df


class FunnelCalculator:
    """Handles funnel and conversion calculations"""
    
    @staticmethod
    def calculate_funnel_metrics(leads: float,
                                contact_rate: float,
                                meeting_rate: float,
                                close_rate: float,
                                onboard_rate: float = 0.95) -> Dict[str, float]:
        """Calculate full funnel metrics"""
        contacts = leads * contact_rate
        meetings = contacts * meeting_rate
        sales = meetings * close_rate
        onboarded = sales * onboard_rate
        
        return {
            'leads': leads,
            'contacts': contacts,
            'meetings': meetings,
            'sales': sales,
            'onboarded': onboarded,
            'lead_to_sale': sales / leads if leads > 0 else 0,
            'contact_to_sale': sales / contacts if contacts > 0 else 0,
            'meeting_to_sale': close_rate
        }
    
    @staticmethod
    def reverse_engineer_pipeline(revenue_target: float,
                                 avg_deal_size: float,
                                 close_rate: float,
                                 meeting_rate: float,
                                 contact_rate: float,
                                 pipeline_coverage: float = config.STANDARD_PIPELINE_COVERAGE) -> Dict[str, float]:
        """Reverse engineer required pipeline from revenue target"""
        # Required closed deals
        deals_needed = revenue_target / avg_deal_size
        
        # Pipeline needed (with coverage ratio)
        pipeline_needed = deals_needed * pipeline_coverage
        
        # Work backwards through funnel
        meetings_needed = pipeline_needed / close_rate
        contacts_needed = meetings_needed / meeting_rate
        leads_needed = contacts_needed / contact_rate
        
        return {
            'revenue_target': revenue_target,
            'deals_needed': deals_needed,
            'pipeline_value_needed': pipeline_needed * avg_deal_size,
            'pipeline_deals_needed': pipeline_needed,
            'meetings_needed': meetings_needed,
            'contacts_needed': contacts_needed,
            'leads_needed': leads_needed,
            'pipeline_coverage': pipeline_coverage
        }


class TeamCalculator:
    """Handles team capacity and headcount calculations"""
    
    @staticmethod
    def calculate_team_capacity(num_closers: int,
                              num_setters: int,
                              meetings_per_closer: int = config.DEFAULT_MEETINGS_PER_CLOSER,
                              contacts_per_setter: int = config.DEFAULT_CONTACTS_PER_SETTER) -> Dict[str, float]:
        """Calculate team capacity"""
        # Monthly capacity
        closer_capacity_meetings = num_closers * meetings_per_closer * 4  # 4 weeks
        setter_capacity_contacts = num_setters * contacts_per_setter * 20  # 20 working days
        
        return {
            'closer_capacity_meetings': closer_capacity_meetings,
            'setter_capacity_contacts': setter_capacity_contacts,
            'closers': num_closers,
            'setters': num_setters,
            'meetings_per_closer': meetings_per_closer,
            'contacts_per_setter': contacts_per_setter
        }
    
    @staticmethod
    def calculate_ramp_schedule(new_hires: int,
                               ramp_months: int = config.DEFAULT_RAMP_TIME_MONTHS,
                               productivity_curve: Optional[List[float]] = None) -> pd.DataFrame:
        """Calculate ramping schedule for new hires"""
        if productivity_curve is None:
            # Default S-curve ramp: 30%, 60%, 90%, 100%
            productivity_curve = [0.3, 0.6, 0.9, 1.0]
        
        ramp_data = []
        for month in range(1, ramp_months + 1):
            if month <= len(productivity_curve):
                productivity = productivity_curve[month - 1]
            else:
                productivity = 1.0
            
            ramp_data.append({
                'month': month,
                'new_hires': new_hires,
                'productivity': productivity,
                'effective_capacity': new_hires * productivity
            })
        
        return pd.DataFrame(ramp_data)
    
    @staticmethod
    def calculate_hiring_plan(revenue_targets: List[float],
                            avg_quota_per_rep: float,
                            ramp_months: int = config.DEFAULT_RAMP_TIME_MONTHS,
                            attrition_rate: float = 0.1) -> pd.DataFrame:
        """Create hiring plan based on revenue targets"""
        hiring_plan = []
        current_headcount = 0
        
        for month, target in enumerate(revenue_targets, 1):
            # Calculate required productive reps
            productive_reps_needed = target / avg_quota_per_rep
            
            # Account for attrition
            attrition = current_headcount * (attrition_rate / 12)  # Monthly attrition
            
            # Calculate new hires needed (accounting for ramp)
            new_hires_needed = max(0, productive_reps_needed - current_headcount + attrition)
            
            # When to hire (lead time for ramping)
            hire_by_month = max(1, month - ramp_months)
            
            current_headcount = current_headcount - attrition + new_hires_needed
            
            hiring_plan.append({
                'month': month,
                'revenue_target': target,
                'productive_reps_needed': productive_reps_needed,
                'current_headcount': current_headcount,
                'attrition': attrition,
                'new_hires_needed': new_hires_needed,
                'hire_by_month': hire_by_month
            })
        
        return pd.DataFrame(hiring_plan)


class CommissionCalculator:
    """Handles commission and compensation calculations"""
    
    @staticmethod
    def calculate_attainment_payout(quota: float,
                                   actual: float,
                                   base_commission_rate: float) -> Dict[str, float]:
        """Calculate commission based on attainment tiers"""
        attainment_pct = actual / quota if quota > 0 else 0
        
        # Get multiplier from config
        multiplier = config.get_attainment_multiplier(attainment_pct)
        
        # Calculate payout
        base_payout = actual * base_commission_rate
        adjusted_payout = base_payout * multiplier
        
        # Find tier name
        tier_name = 'Unknown'
        for tier in config.ATTAINMENT_TIERS.values():
            if tier['min'] <= attainment_pct < tier['max']:
                tier_name = tier['name']
                break
        
        return {
            'quota': quota,
            'actual': actual,
            'attainment_pct': attainment_pct,
            'tier': tier_name,
            'multiplier': multiplier,
            'base_payout': base_payout,
            'adjusted_payout': adjusted_payout,
            'effective_rate': adjusted_payout / actual if actual > 0 else 0
        }
    
    @staticmethod
    def calculate_ote_structure(revenue_per_rep: float,
                              target_earnings: float,
                              base_salary_pct: float = 0.4) -> Dict[str, float]:
        """Calculate OTE structure and commission rates"""
        base_salary = target_earnings * base_salary_pct
        variable_comp = target_earnings * (1 - base_salary_pct)
        
        # Commission rate needed
        commission_rate = variable_comp / revenue_per_rep if revenue_per_rep > 0 else 0
        
        # Health check
        health = config.get_ote_health(base_salary, variable_comp)
        
        return {
            'total_ote': target_earnings,
            'base_salary': base_salary,
            'variable_comp': variable_comp,
            'commission_rate': commission_rate,
            'base_salary_pct': base_salary_pct,
            'variable_comp_pct': 1 - base_salary_pct,
            'health_status': health['health_score'],
            'is_healthy': health['is_healthy']
        }


class UnitEconomicsCalculator:
    """Handles unit economics and margin calculations"""
    
    @staticmethod
    def calculate_unit_economics(revenue: float,
                                cogs: float,
                                sales_costs: float,
                                marketing_costs: float,
                                overhead: float,
                                gov_fee_pct: float = 0.1) -> Dict[str, float]:
        """Calculate complete unit economics"""
        # Gross calculations
        gross_profit = revenue - cogs
        gross_margin = gross_profit / revenue if revenue > 0 else 0
        
        # Government fees
        gov_fees = revenue * gov_fee_pct
        
        # Operating profit
        total_opex = sales_costs + marketing_costs + overhead + gov_fees
        operating_profit = gross_profit - total_opex
        operating_margin = operating_profit / revenue if revenue > 0 else 0
        
        # EBITDA (simplified - assuming no D&A)
        ebitda = operating_profit
        ebitda_margin = ebitda / revenue if revenue > 0 else 0
        
        # Cost of sales percentage
        cos_percentage = sales_costs / revenue if revenue > 0 else 0
        
        return {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'gross_margin': gross_margin,
            'sales_costs': sales_costs,
            'marketing_costs': marketing_costs,
            'overhead': overhead,
            'gov_fees': gov_fees,
            'total_opex': total_opex,
            'operating_profit': operating_profit,
            'operating_margin': operating_margin,
            'ebitda': ebitda,
            'ebitda_margin': ebitda_margin,
            'cos_percentage': cos_percentage,
            'is_healthy': ebitda_margin >= config.TARGET_EBITDA_MARGIN
        }
    
    @staticmethod
    def calculate_ltv_cac(avg_deal_value: float,
                         gross_margin: float,
                         retention_months: float,
                         sales_marketing_costs: float,
                         new_customers: float) -> Dict[str, float]:
        """Calculate LTV:CAC ratio"""
        # LTV calculation
        ltv = avg_deal_value * gross_margin * (retention_months / 12)
        
        # CAC calculation
        cac = sales_marketing_costs / new_customers if new_customers > 0 else 0
        
        # Ratio
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        
        # Payback period in months
        payback_months = cac / (avg_deal_value * gross_margin / 12) if gross_margin > 0 else 0
        
        return {
            'ltv': ltv,
            'cac': cac,
            'ltv_cac_ratio': ltv_cac_ratio,
            'payback_months': payback_months,
            'is_healthy': ltv_cac_ratio >= config.MIN_LTV_CAC_RATIO,
            'health_status': 'Healthy' if ltv_cac_ratio >= config.TARGET_LTV_CAC_RATIO else 
                           'Acceptable' if ltv_cac_ratio >= config.MIN_LTV_CAC_RATIO else 
                           'Needs Improvement'
        }
