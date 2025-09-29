"""
Enhanced Calculations Module - Preserves all original calculations + adds new ones
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class EnhancedRevenueCalculator:
    """Enhanced revenue calculations with proper month 18 timing"""
    
    @staticmethod
    def calculate_monthly_timeline(monthly_sales: float,
                                 avg_premium: float,
                                 num_months: int = 24,
                                 carrier_rate: float = 0.027,
                                 pct_immediate: float = 0.7,
                                 pct_deferred: float = 0.3,
                                 persistency: float = 0.9,
                                 growth_rate: float = 0.0) -> pd.DataFrame:
        """
        Calculate revenue timeline with CORRECT month 18 deferred payments
        """
        # Calculate per-sale amounts
        total_comp_per_sale = avg_premium * 300 * carrier_rate  # 300 months contract
        immediate_per_sale = total_comp_per_sale * pct_immediate
        deferred_per_sale = total_comp_per_sale * pct_deferred
        
        timeline = []
        sales_history = {}  # Track sales for deferred calculation
        
        for month in range(1, num_months + 1):
            # Current month sales (with growth)
            current_sales = monthly_sales * ((1 + growth_rate) ** (month - 1))
            sales_history[month] = current_sales
            
            # Immediate revenue from current month
            immediate_revenue = current_sales * immediate_per_sale
            
            # Deferred revenue from month-18 (if applicable)
            deferred_revenue = 0
            if month > 18 and (month - 18) in sales_history:
                deferred_revenue = sales_history[month - 18] * deferred_per_sale * persistency
            
            # Cash collected this month
            cash_collected_today = immediate_revenue  # 70% from today's sales
            cash_pending_month_18 = current_sales * deferred_per_sale  # Will arrive in month+18
            
            timeline.append({
                'month': month,
                'year': (month - 1) // 12 + 1,
                'quarter': (month - 1) // 3 + 1,
                'sales': current_sales,
                'immediate_revenue': immediate_revenue,
                'deferred_revenue': deferred_revenue,
                'total_revenue': immediate_revenue + deferred_revenue,
                'cash_collected_today': cash_collected_today,
                'cash_pending_month_18': cash_pending_month_18,
                'cumulative_immediate': 0,  # Will calculate after
                'cumulative_total': 0  # Will calculate after
            })
        
        df = pd.DataFrame(timeline)
        df['cumulative_immediate'] = df['immediate_revenue'].cumsum()
        df['cumulative_total'] = df['total_revenue'].cumsum()
        
        # Add date columns for clarity
        today = datetime.now()
        df['date'] = pd.date_range(start=today, periods=len(df), freq='MS')
        df['date_deferred_arrives'] = df['date'] + pd.DateOffset(months=18)
        
        return df
    
    @staticmethod
    def calculate_revenue_breakdown(annual_target: float) -> Dict[str, float]:
        """Break down annual revenue target into periods"""
        return {
            'annual': annual_target,
            'quarterly': annual_target / 4,
            'monthly': annual_target / 12,
            'weekly': annual_target / 52,
            'daily': annual_target / 260  # Business days
        }


class TeamMetricsCalculator:
    """Calculate team-specific metrics and OTE structures"""
    
    @staticmethod
    def calculate_ote_by_role(num_closers: int,
                             num_setters: int,
                             num_managers: int,
                             closer_ote: float = 80000,
                             setter_ote: float = 40000,
                             manager_ote: float = 120000,
                             base_pct: float = 0.4) -> Dict[str, Dict]:
        """Calculate OTE structure by role"""
        roles = {
            'closer': {
                'count': num_closers,
                'ote': closer_ote,
                'base': closer_ote * base_pct,
                'variable': closer_ote * (1 - base_pct),
                'total_cost': num_closers * closer_ote
            },
            'setter': {
                'count': num_setters,
                'ote': setter_ote,
                'base': setter_ote * base_pct,
                'variable': setter_ote * (1 - base_pct),
                'total_cost': num_setters * setter_ote
            },
            'manager': {
                'count': num_managers,
                'ote': manager_ote,
                'base': manager_ote * 0.6,  # Managers typically higher base
                'variable': manager_ote * 0.4,
                'total_cost': num_managers * manager_ote
            }
        }
        
        # Calculate averages
        total_headcount = num_closers + num_setters + num_managers
        if total_headcount > 0:
            avg_ote = sum(r['total_cost'] for r in roles.values()) / total_headcount
            avg_base = sum(r['base'] * r['count'] for r in roles.values()) / total_headcount
            avg_variable = sum(r['variable'] * r['count'] for r in roles.values()) / total_headcount
        else:
            avg_ote = avg_base = avg_variable = 0
        
        roles['team_average'] = {
            'count': total_headcount,
            'ote': avg_ote,
            'base': avg_base,
            'variable': avg_variable,
            'total_cost': sum(r['total_cost'] for r in roles.values())
        }
        
        return roles
    
    @staticmethod
    def calculate_ramp_impact(new_hires: int,
                             ramp_months: int = 3,
                             productivity_curve: Optional[List[float]] = None) -> pd.DataFrame:
        """Calculate productivity ramp with financial impact"""
        if productivity_curve is None:
            # Default S-curve: 30%, 60%, 85%, 100%
            productivity_curve = [0.3, 0.6, 0.85, 1.0]
        
        ramp_data = []
        for month in range(1, ramp_months + 2):  # Include fully ramped month
            if month <= len(productivity_curve):
                productivity = productivity_curve[month - 1]
            else:
                productivity = 1.0
            
            effective_capacity = new_hires * productivity
            cost_efficiency = productivity  # They cost 100% but produce X%
            
            ramp_data.append({
                'month': month,
                'new_hires': new_hires,
                'productivity': productivity,
                'effective_capacity': effective_capacity,
                'cost_efficiency': cost_efficiency,
                'status': 'Ramping' if productivity < 1.0 else 'Fully Productive'
            })
        
        return pd.DataFrame(ramp_data)


class BottleneckAnalyzer:
    """Analyze bottlenecks and sensitivity"""
    
    @staticmethod
    def analyze_sensitivity(base_metrics: Dict[str, float],
                          variable_changes: Dict[str, List[float]]) -> pd.DataFrame:
        """
        Analyze what changes when you move X
        Returns impact on key KPIs
        """
        sensitivity_results = []
        
        for variable, changes in variable_changes.items():
            for change_pct in changes:
                # Calculate new value
                new_value = base_metrics.get(variable, 1) * (1 + change_pct)
                
                # Calculate impacts (simplified - you'd implement full recalc)
                impacts = {
                    'variable': variable,
                    'change_pct': change_pct,
                    'new_value': new_value
                }
                
                # Estimate impacts on KPIs based on variable
                if variable == 'close_rate':
                    impacts['sales_impact'] = change_pct
                    impacts['revenue_impact'] = change_pct
                    impacts['ebitda_impact'] = change_pct * 0.8  # Less than proportional
                    impacts['team_needed_impact'] = -change_pct * 0.5  # Need fewer people
                elif variable == 'sales_cycle':
                    impacts['sales_impact'] = -change_pct * 0.3  # Longer cycle = fewer sales
                    impacts['revenue_impact'] = -change_pct * 0.3
                    impacts['pipeline_coverage_impact'] = change_pct * 0.5  # Need more coverage
                    impacts['cash_flow_impact'] = -change_pct  # Delayed cash
                elif variable == 'avg_deal_size':
                    impacts['revenue_impact'] = change_pct
                    impacts['ebitda_impact'] = change_pct * 0.9
                    impacts['ltv_impact'] = change_pct
                elif variable == 'cost_per_lead':
                    impacts['cac_impact'] = change_pct
                    impacts['ebitda_impact'] = -change_pct * 0.2
                    impacts['ltv_cac_impact'] = -change_pct * 0.8
                
                sensitivity_results.append(impacts)
        
        return pd.DataFrame(sensitivity_results)
    
    @staticmethod
    def find_bottlenecks(funnel_metrics: Dict[str, float],
                        team_capacity: Dict[str, float],
                        financial_metrics: Dict[str, float]) -> List[Dict]:
        """Identify bottlenecks in the system"""
        bottlenecks = []
        
        # Funnel bottlenecks
        if 'contact_rate' in funnel_metrics and funnel_metrics['contact_rate'] < 0.5:
            bottlenecks.append({
                'type': 'Funnel',
                'issue': 'Low Contact Rate',
                'current': funnel_metrics['contact_rate'],
                'target': 0.6,
                'impact': 'Reducing lead efficiency',
                'action': 'Improve lead quality or contact strategy'
            })
        
        if 'close_rate' in funnel_metrics and funnel_metrics['close_rate'] < 0.2:
            bottlenecks.append({
                'type': 'Funnel',
                'issue': 'Low Close Rate',
                'current': funnel_metrics['close_rate'],
                'target': 0.25,
                'impact': 'Need more meetings for same revenue',
                'action': 'Sales training or lead qualification'
            })
        
        # Capacity bottlenecks
        if 'closer_utilization' in team_capacity and team_capacity['closer_utilization'] > 0.9:
            bottlenecks.append({
                'type': 'Capacity',
                'issue': 'Closers Overloaded',
                'current': team_capacity['closer_utilization'],
                'target': 0.75,
                'impact': 'Quality degradation, burnout risk',
                'action': 'Hire more closers or improve efficiency'
            })
        
        # Financial bottlenecks
        if 'ltv_cac_ratio' in financial_metrics and financial_metrics['ltv_cac_ratio'] < 3:
            bottlenecks.append({
                'type': 'Financial',
                'issue': 'Low LTV:CAC Ratio',
                'current': financial_metrics['ltv_cac_ratio'],
                'target': 3.0,
                'impact': 'Unsustainable unit economics',
                'action': 'Reduce CAC or increase LTV'
            })
        
        if 'ebitda_margin' in financial_metrics and financial_metrics['ebitda_margin'] < 0.2:
            bottlenecks.append({
                'type': 'Financial',
                'issue': 'Low EBITDA Margin',
                'current': financial_metrics['ebitda_margin'],
                'target': 0.25,
                'impact': 'Limited reinvestment capacity',
                'action': 'Optimize costs or increase prices'
            })
        
        return bottlenecks


class HealthScoreCalculator:
    """Calculate comprehensive health scores"""
    
    @staticmethod
    def calculate_health_metrics(funnel_metrics: Dict,
                                team_metrics: Dict,
                                financial_metrics: Dict) -> Dict[str, any]:
        """Calculate health score across dimensions"""
        scores = {}
        
        # Funnel Health (0-100)
        contact_score = min(100, (funnel_metrics.get('contact_rate', 0) / 0.6) * 100)
        meeting_score = min(100, (funnel_metrics.get('meeting_rate', 0) / 0.35) * 100)
        close_score = min(100, (funnel_metrics.get('close_rate', 0) / 0.25) * 100)
        scores['funnel_health'] = (contact_score + meeting_score + close_score) / 3
        
        # Team Health (0-100)
        utilization = team_metrics.get('utilization', 0.75)
        util_score = 100 - abs(utilization - 0.75) * 200  # Optimal at 75%
        ramp_score = team_metrics.get('ramp_efficiency', 0.7) * 100
        retention_score = (1 - team_metrics.get('attrition_rate', 0.15)) * 100
        scores['team_health'] = (util_score + ramp_score + retention_score) / 3
        
        # Financial Health (0-100)
        ltv_cac = financial_metrics.get('ltv_cac_ratio', 0)
        ltv_score = min(100, (ltv_cac / 5) * 100)  # 5:1 is excellent
        margin_score = min(100, (financial_metrics.get('ebitda_margin', 0) / 0.3) * 100)
        growth_score = min(100, (financial_metrics.get('growth_rate', 0) / 0.2) * 100)
        scores['financial_health'] = (ltv_score + margin_score + growth_score) / 3
        
        # Overall Health
        scores['overall_health'] = (
            scores['funnel_health'] * 0.3 +
            scores['team_health'] * 0.3 +
            scores['financial_health'] * 0.4
        )
        
        # Status determination
        overall = scores['overall_health']
        if overall >= 80:
            scores['status'] = '🟢 Excellent'
            scores['color'] = 'green'
        elif overall >= 60:
            scores['status'] = '🟡 Good'
            scores['color'] = 'yellow'
        elif overall >= 40:
            scores['status'] = '🟠 Needs Attention'
            scores['color'] = 'orange'
        else:
            scores['status'] = '🔴 Critical'
            scores['color'] = 'red'
        
        return scores
