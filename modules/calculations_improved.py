"""
Improved Calculations Module - Fixed math and better integration
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import streamlit as st

class ImprovedCostCalculator:
    """Improved cost calculations with flexibility"""
    
    @staticmethod
    @st.cache_data(ttl=300)
    def calculate_acquisition_costs(input_type: str,
                                  input_value: float,
                                  volume: Dict[str, float]) -> Dict[str, float]:
        """
        Mathematically accurate cost calculation based on input type
        Properly accounts for show-up rate and funnel math
        """
        costs = {}
        
        # Extract rates with proper defaults
        contact_rate = volume.get('contact_rate', 0.6)
        meeting_rate = volume.get('meeting_rate', 0.35)
        show_up_rate = volume.get('show_up_rate', 0.75)
        close_rate = volume.get('close_rate', 0.25)
        leads = volume.get('leads', 0)
        
        if input_type == "CPL":
            # Start from CPL and work down the funnel
            costs['cost_per_lead'] = input_value
            costs['cost_per_contact'] = input_value / contact_rate if contact_rate > 0 else 0
            costs['cost_per_meeting_scheduled'] = costs['cost_per_contact'] / meeting_rate if meeting_rate > 0 else 0
            costs['cost_per_meeting_held'] = costs['cost_per_meeting_scheduled'] / show_up_rate if show_up_rate > 0 else 0
            costs['cost_per_sale'] = costs['cost_per_meeting_held'] / close_rate if close_rate > 0 else 0
            
        elif input_type == "CPA":  # Cost per Appointment (scheduled meeting)
            # Start from CPA and work backwards/forwards
            costs['cost_per_meeting_scheduled'] = input_value
            costs['cost_per_meeting_held'] = input_value / show_up_rate if show_up_rate > 0 else 0
            costs['cost_per_sale'] = costs['cost_per_meeting_held'] / close_rate if close_rate > 0 else 0
            
            # Work backwards to leads
            costs['cost_per_contact'] = input_value * meeting_rate
            costs['cost_per_lead'] = costs['cost_per_contact'] * contact_rate
            
        elif input_type == "Total Budget":
            # Distribute budget across expected leads
            if leads > 0:
                costs['cost_per_lead'] = input_value / leads
                costs['cost_per_contact'] = costs['cost_per_lead'] / contact_rate if contact_rate > 0 else 0
                costs['cost_per_meeting_scheduled'] = costs['cost_per_contact'] / meeting_rate if meeting_rate > 0 else 0
                costs['cost_per_meeting_held'] = costs['cost_per_meeting_scheduled'] / show_up_rate if show_up_rate > 0 else 0
                costs['cost_per_sale'] = costs['cost_per_meeting_held'] / close_rate if close_rate > 0 else 0
            else:
                # Default to zero if no leads
                for key in ['cost_per_lead', 'cost_per_contact', 'cost_per_meeting_scheduled', 'cost_per_meeting_held', 'cost_per_sale']:
                    costs[key] = 0
        
        # Calculate derived metrics
        costs['marketing_cac'] = costs.get('cost_per_sale', 0)
        costs['total_marketing_spend'] = costs.get('cost_per_lead', 0) * leads
        costs['cost_per_meeting'] = costs.get('cost_per_meeting_held', 0)  # For backward compatibility
        
        # Calculate efficiency metrics
        if leads > 0 and costs.get('cost_per_lead', 0) > 0:
            expected_contacts = leads * contact_rate
            expected_meetings_scheduled = expected_contacts * meeting_rate
            expected_meetings_held = expected_meetings_scheduled * show_up_rate
            expected_sales = expected_meetings_held * close_rate
            
            costs['expected_contacts'] = expected_contacts
            costs['expected_meetings_scheduled'] = expected_meetings_scheduled
            costs['expected_meetings_held'] = expected_meetings_held
            costs['expected_sales'] = expected_sales
            costs['total_expected_revenue'] = expected_sales * volume.get('avg_deal_value', 20000)
            
            # No-show cost (wasted meetings)
            no_shows = expected_meetings_scheduled * (1 - show_up_rate)
            costs['no_show_cost'] = no_shows * costs.get('cost_per_meeting_scheduled', 0)
            costs['no_show_rate'] = 1 - show_up_rate
        
        return costs


class ImprovedCompensationCalculator:
    """Modular compensation with custom inputs per role"""
    
    @staticmethod
    def calculate_custom_compensation(roles: Dict[str, Dict]) -> Dict[str, any]:
        """
        Calculate compensation with custom base/variable per role
        
        roles = {
            'closer': {'count': 8, 'base': 30000, 'variable': 50000, 'ote': 80000},
            'setter': {'count': 4, 'base': 15000, 'variable': 25000, 'ote': 40000},
            ...
        }
        """
        total_compensation = {
            'monthly_base': 0,
            'monthly_variable_target': 0,
            'monthly_total_target': 0,
            'annual_base': 0,
            'annual_variable_target': 0,
            'annual_total': 0,
            'by_role': {}
        }
        
        for role, data in roles.items():
            count = data.get('count', 0)
            base = data.get('base', 0)
            variable = data.get('variable', 0)
            ote = data.get('ote', base + variable)
            
            # Validate OTE consistency
            if abs(ote - (base + variable)) > 100:
                # OTE doesn't match base + variable
                variable = ote - base
            
            role_comp = {
                'count': count,
                'base_per_person': base,
                'variable_per_person': variable,
                'ote_per_person': ote,
                'base_pct': base / ote if ote > 0 else 0,
                'variable_pct': variable / ote if ote > 0 else 0,
                'total_base': base * count,
                'total_variable': variable * count,
                'total_ote': ote * count,
                'monthly_base': (base * count) / 12,
                'monthly_variable_target': (variable * count) / 12,
                'monthly_total': (ote * count) / 12
            }
            
            total_compensation['by_role'][role] = role_comp
            total_compensation['monthly_base'] += role_comp['monthly_base']
            total_compensation['monthly_variable_target'] += role_comp['monthly_variable_target']
            total_compensation['monthly_total_target'] += role_comp['monthly_total']
        
        total_compensation['annual_base'] = total_compensation['monthly_base'] * 12
        total_compensation['annual_variable_target'] = total_compensation['monthly_variable_target'] * 12
        total_compensation['annual_total'] = total_compensation['monthly_total_target'] * 12
        
        # Calculate weighted average base %
        total_ote = sum(r['total_ote'] for r in total_compensation['by_role'].values())
        if total_ote > 0:
            weighted_base = sum(r['total_base'] for r in total_compensation['by_role'].values())
            total_compensation['avg_base_pct'] = weighted_base / total_ote
            total_compensation['avg_variable_pct'] = 1 - total_compensation['avg_base_pct']
        else:
            total_compensation['avg_base_pct'] = 0.4
            total_compensation['avg_variable_pct'] = 0.6
        
        return total_compensation


class ImprovedPnLCalculator:
    """Deep P&L analysis with proper categorization"""
    
    @staticmethod
    @st.cache_data(ttl=300)
    def calculate_detailed_pnl(revenue: Dict[str, float],
                              costs: Dict[str, float],
                              projection_months: int = 18) -> pd.DataFrame:
        """
        Create detailed P&L with proper categorization and projections
        """
        # Revenue section
        pnl_items = []
        
        # Revenue breakdown
        pnl_items.append({
            'category': 'REVENUE',
            'subcategory': 'Sales',
            'line_item': 'New Sales (Units)',
            'month_1': revenue.get('monthly_sales', 0),
            'month_18': revenue.get('monthly_sales', 0),
            'total_projection': revenue.get('monthly_sales', 0) * projection_months,
            'pct_of_revenue': None,
            'format': 'units'
        })
        
        pnl_items.append({
            'category': 'REVENUE',
            'subcategory': 'Immediate Revenue',
            'line_item': 'Immediate Collections (70%)',
            'month_1': revenue.get('immediate_revenue', 0),
            'month_18': revenue.get('immediate_revenue', 0),
            'total_projection': revenue.get('immediate_revenue', 0) * projection_months,
            'pct_of_revenue': 0.7,
            'format': 'currency'
        })
        
        pnl_items.append({
            'category': 'REVENUE',
            'subcategory': 'Deferred Revenue',
            'line_item': 'Deferred Collections (30%)',
            'month_1': 0,  # Nothing in month 1
            'month_18': revenue.get('deferred_revenue', 0),  # Starts month 18
            'total_projection': revenue.get('deferred_revenue', 0) * max(0, projection_months - 17),
            'pct_of_revenue': 0.3,
            'format': 'currency'
        })
        
        total_revenue_m1 = revenue.get('immediate_revenue', 0)
        total_revenue_m18 = revenue.get('immediate_revenue', 0) + revenue.get('deferred_revenue', 0)
        
        pnl_items.append({
            'category': 'REVENUE',
            'subcategory': 'Total',
            'line_item': 'GROSS REVENUE',
            'month_1': total_revenue_m1,
            'month_18': total_revenue_m18,
            'total_projection': revenue.get('total_projected', 0),
            'pct_of_revenue': 1.0,
            'format': 'currency_bold'
        })
        
        # COGS (if applicable)
        cogs = costs.get('cogs', 0)
        if cogs > 0:
            pnl_items.append({
                'category': 'COGS',
                'subcategory': 'Direct Costs',
                'line_item': 'Cost of Goods Sold',
                'month_1': -cogs,
                'month_18': -cogs,
                'total_projection': -cogs * projection_months,
                'pct_of_revenue': -cogs / total_revenue_m1 if total_revenue_m1 > 0 else 0,
                'format': 'currency'
            })
        
        # Gross Profit
        gross_profit_m1 = total_revenue_m1 - cogs
        gross_profit_m18 = total_revenue_m18 - cogs
        
        pnl_items.append({
            'category': 'GROSS PROFIT',
            'subcategory': '',
            'line_item': 'GROSS PROFIT',
            'month_1': gross_profit_m1,
            'month_18': gross_profit_m18,
            'total_projection': (gross_profit_m1 * 17 + gross_profit_m18 * max(0, projection_months - 17)),
            'pct_of_revenue': gross_profit_m1 / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency_bold'
        })
        
        # Operating Expenses
        # Sales & Marketing
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'Sales & Marketing',
            'line_item': 'Lead Generation',
            'month_1': -costs.get('marketing_costs', 0),
            'month_18': -costs.get('marketing_costs', 0),
            'total_projection': -costs.get('marketing_costs', 0) * projection_months,
            'pct_of_revenue': -costs.get('marketing_costs', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'Sales & Marketing',
            'line_item': 'Sales Commissions',
            'month_1': -costs.get('commissions', 0),
            'month_18': -costs.get('commissions', 0),
            'total_projection': -costs.get('commissions', 0) * projection_months,
            'pct_of_revenue': -costs.get('commissions', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'Sales & Marketing',
            'line_item': 'Base Salaries - Sales',
            'month_1': -costs.get('sales_base_salaries', 0),
            'month_18': -costs.get('sales_base_salaries', 0),
            'total_projection': -costs.get('sales_base_salaries', 0) * projection_months,
            'pct_of_revenue': -costs.get('sales_base_salaries', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        # G&A
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'G&A',
            'line_item': 'Office Rent',
            'month_1': -costs.get('office_rent', 0),
            'month_18': -costs.get('office_rent', 0),
            'total_projection': -costs.get('office_rent', 0) * projection_months,
            'pct_of_revenue': -costs.get('office_rent', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'G&A',
            'line_item': 'Software & Tools',
            'month_1': -costs.get('software', 0),
            'month_18': -costs.get('software', 0),
            'total_projection': -costs.get('software', 0) * projection_months,
            'pct_of_revenue': -costs.get('software', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'G&A',
            'line_item': 'Other OpEx',
            'month_1': -costs.get('other_opex', 0),
            'month_18': -costs.get('other_opex', 0),
            'total_projection': -costs.get('other_opex', 0) * projection_months,
            'pct_of_revenue': -costs.get('other_opex', 0) / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency'
        })
        
        # Total OpEx
        total_opex = sum([
            costs.get('marketing_costs', 0),
            costs.get('commissions', 0),
            costs.get('sales_base_salaries', 0),
            costs.get('office_rent', 0),
            costs.get('software', 0),
            costs.get('other_opex', 0)
        ])
        
        pnl_items.append({
            'category': 'OPEX',
            'subcategory': 'Total',
            'line_item': 'TOTAL OPERATING EXPENSES',
            'month_1': -total_opex,
            'month_18': -total_opex,
            'total_projection': -total_opex * projection_months,
            'pct_of_revenue': -total_opex / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency_bold'
        })
        
        # EBITDA before fees
        ebitda_before_fees_m1 = gross_profit_m1 - total_opex
        ebitda_before_fees_m18 = gross_profit_m18 - total_opex
        
        pnl_items.append({
            'category': 'EBITDA',
            'subcategory': '',
            'line_item': 'EBITDA (before fees)',
            'month_1': ebitda_before_fees_m1,
            'month_18': ebitda_before_fees_m18,
            'total_projection': ebitda_before_fees_m1 * 17 + ebitda_before_fees_m18 * max(0, projection_months - 17),
            'pct_of_revenue': ebitda_before_fees_m1 / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency_bold'
        })
        
        # Government Fees
        gov_fees_m1 = total_revenue_m1 * costs.get('gov_fee_pct', 0.1)
        gov_fees_m18 = total_revenue_m18 * costs.get('gov_fee_pct', 0.1)
        
        pnl_items.append({
            'category': 'FEES',
            'subcategory': 'Government',
            'line_item': f"Gov Fees ({costs.get('gov_fee_pct', 0.1)*100:.0f}%)",
            'month_1': -gov_fees_m1,
            'month_18': -gov_fees_m18,
            'total_projection': -(gov_fees_m1 * 17 + gov_fees_m18 * max(0, projection_months - 17)),
            'pct_of_revenue': -costs.get('gov_fee_pct', 0.1),
            'format': 'currency'
        })
        
        # Net EBITDA
        net_ebitda_m1 = ebitda_before_fees_m1 - gov_fees_m1
        net_ebitda_m18 = ebitda_before_fees_m18 - gov_fees_m18
        
        pnl_items.append({
            'category': 'NET INCOME',
            'subcategory': '',
            'line_item': 'NET EBITDA',
            'month_1': net_ebitda_m1,
            'month_18': net_ebitda_m18,
            'total_projection': net_ebitda_m1 * 17 + net_ebitda_m18 * max(0, projection_months - 17),
            'pct_of_revenue': net_ebitda_m1 / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'currency_bold'
        })
        
        # Margin %
        pnl_items.append({
            'category': 'MARGINS',
            'subcategory': '',
            'line_item': 'EBITDA Margin %',
            'month_1': net_ebitda_m1 / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'month_18': net_ebitda_m18 / total_revenue_m18 if total_revenue_m18 > 0 else 0,
            'total_projection': None,
            'pct_of_revenue': net_ebitda_m1 / total_revenue_m1 if total_revenue_m1 > 0 else 0,
            'format': 'percentage'
        })
        
        return pd.DataFrame(pnl_items)


class ImprovedReverseEngineering:
    """Integrated reverse engineering - single source of truth"""
    
    @staticmethod
    def calculate_from_target(target_type: str,
                            target_value: float,
                            current_metrics: Dict,
                            constraints: Dict = None) -> Dict[str, any]:
        """
        Reverse engineer requirements from any target
        Uses current dashboard state as baseline
        """
        results = {
            'target_type': target_type,
            'target_value': target_value,
            'current_state': current_metrics.copy(),
            'required_changes': {},
            'feasibility': 'feasible',
            'warnings': [],
            'actions': []
        }
        
        if target_type == "revenue":
            # Work backwards from revenue target
            current_revenue = current_metrics.get('monthly_revenue', 0)
            revenue_gap = target_value - current_revenue
            
            if revenue_gap > 0:
                # Need more revenue
                avg_deal = current_metrics.get('avg_deal_value', 20000)
                additional_sales = revenue_gap / avg_deal
                
                # Calculate funnel requirements
                close_rate = current_metrics.get('close_rate', 0.25)
                meeting_rate = current_metrics.get('meeting_rate', 0.35)
                contact_rate = current_metrics.get('contact_rate', 0.6)
                
                additional_meetings = additional_sales / close_rate
                additional_contacts = additional_meetings / meeting_rate
                additional_leads = additional_contacts / contact_rate
                
                results['required_changes'] = {
                    'additional_sales': additional_sales,
                    'additional_meetings': additional_meetings,
                    'additional_leads': additional_leads,
                    'total_sales_needed': current_metrics.get('monthly_sales', 0) + additional_sales,
                    'total_meetings_needed': current_metrics.get('monthly_meetings', 0) + additional_meetings,
                    'total_leads_needed': current_metrics.get('monthly_leads', 0) + additional_leads
                }
                
                # Check team capacity
                meetings_per_closer = 60  # Monthly capacity
                current_closers = current_metrics.get('num_closers', 8)
                capacity = current_closers * meetings_per_closer
                
                if results['required_changes']['total_meetings_needed'] > capacity:
                    additional_closers = np.ceil((results['required_changes']['total_meetings_needed'] - capacity) / meetings_per_closer)
                    results['required_changes']['additional_closers'] = additional_closers
                    results['warnings'].append(f"Need {additional_closers:.0f} more closers")
                
                # Calculate cost impact
                cpl = current_metrics.get('cost_per_lead', 150)
                additional_marketing = additional_leads * cpl
                results['required_changes']['additional_marketing_spend'] = additional_marketing
                
                # Actions
                results['actions'] = [
                    f"Increase leads to {results['required_changes']['total_leads_needed']:.0f}/month",
                    f"Ensure {results['required_changes']['total_meetings_needed']:.0f} meetings/month",
                    f"Target {results['required_changes']['total_sales_needed']:.0f} sales/month"
                ]
                
        elif target_type == "ebitda":
            # Work from EBITDA target
            current_ebitda = current_metrics.get('monthly_ebitda', 0)
            ebitda_gap = target_value - current_ebitda
            
            if ebitda_gap > 0:
                # Need to improve EBITDA
                # Option 1: Increase revenue
                current_margin = current_metrics.get('ebitda_margin', 0.25)
                revenue_needed = target_value / current_margin if current_margin > 0 else target_value * 4
                
                # Option 2: Reduce costs
                current_costs = current_metrics.get('total_costs', 0)
                cost_reduction_needed = -ebitda_gap
                
                results['required_changes'] = {
                    'option_1_revenue': revenue_needed,
                    'option_1_revenue_increase': revenue_needed - current_metrics.get('monthly_revenue', 0),
                    'option_2_cost_reduction': cost_reduction_needed,
                    'option_2_cost_target': current_costs + cost_reduction_needed
                }
                
                results['actions'] = [
                    f"Option 1: Increase revenue to ${revenue_needed:,.0f}/month",
                    f"Option 2: Reduce costs by ${abs(cost_reduction_needed):,.0f}/month",
                    f"Option 3: Combination of both"
                ]
                
        elif target_type == "ltv_cac":
            # Work from LTV:CAC target
            target_ratio = target_value
            current_ltv = current_metrics.get('ltv', 20000)
            current_cac = current_metrics.get('cac', 5000)
            
            # Option 1: Reduce CAC
            target_cac = current_ltv / target_ratio
            cac_reduction = current_cac - target_cac
            
            # Option 2: Increase LTV
            target_ltv = current_cac * target_ratio
            ltv_increase = target_ltv - current_ltv
            
            results['required_changes'] = {
                'option_1_cac': target_cac,
                'option_1_reduction': cac_reduction,
                'option_2_ltv': target_ltv,
                'option_2_increase': ltv_increase
            }
            
            results['actions'] = [
                f"Option 1: Reduce CAC to ${target_cac:,.0f} (-{(cac_reduction/current_cac)*100:.0f}%)",
                f"Option 2: Increase LTV to ${target_ltv:,.0f} (+{(ltv_increase/current_ltv)*100:.0f}%)"
            ]
        
        return results
