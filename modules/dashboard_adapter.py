"""
Adapter to integrate new engine with existing dashboard_fast.py
Provides backward compatibility while using the new architecture
"""

import streamlit as st
from typing import Dict, List, Tuple
from modules.models import (
    Channel, DealEconomics, TeamStructure, OperatingCosts,
    RoleCompensation, CostMethod, Segment, CommissionPolicy
)
from modules.engine import compute_gtm_aggregate
from modules.engine_pnl import (
    calculate_unit_economics, calculate_commission_pools,
    calculate_pnl, calculate_per_person_earnings
)
from modules.state import hash_key
import json


class DashboardAdapter:
    """
    Adapter that converts between st.session_state format and new models.
    Acts as a bridge during migration.
    """
    
    @staticmethod
    def session_to_deal_economics() -> DealEconomics:
        """Convert session state to DealEconomics model"""
        return DealEconomics(
            avg_deal_value=st.session_state.get('avg_deal_value', 50000),
            upfront_pct=st.session_state.get('upfront_payment_pct', 70.0),
            contract_length_months=st.session_state.get('contract_length_months', 12),
            deferred_timing_months=st.session_state.get('deferred_timing_months', 18),
            commission_policy=CommissionPolicy(st.session_state.get('commission_policy', 'upfront')),
            grr=st.session_state.get('grr_rate', 0.90),
            government_cost_pct=st.session_state.get('government_cost_pct', 10.0)
        )
    
    @staticmethod
    def session_to_channels() -> List[Channel]:
        """Convert session state channels to Channel models"""
        channels = []
        
        for ch_data in st.session_state.get('gtm_channels', []):
            # Map cost method string to enum
            cost_method_str = ch_data.get('cost_method', 'Cost per Lead')
            try:
                cost_method = CostMethod(cost_method_str)
            except ValueError:
                cost_method = CostMethod.CPL
            
            # Map segment
            segment_str = ch_data.get('segment', 'SMB')
            try:
                segment = Segment(segment_str)
            except ValueError:
                segment = Segment.SMB
            
            channel = Channel(
                id=ch_data.get('id', 'channel_1'),
                name=ch_data.get('name', 'Channel'),
                segment=segment,
                enabled=ch_data.get('enabled', True),
                monthly_leads=ch_data.get('monthly_leads', 0),
                contact_rate=ch_data.get('contact_rate', 0.6),
                meeting_rate=ch_data.get('meeting_rate', 0.3),
                show_up_rate=ch_data.get('show_up_rate', 0.7),
                close_rate=ch_data.get('close_rate', 0.25),
                cost_method=cost_method,
                cpl=ch_data.get('cpl'),
                cost_per_contact=ch_data.get('cost_per_contact'),
                cost_per_meeting=ch_data.get('cost_per_meeting'),
                cost_per_sale=ch_data.get('cost_per_sale'),
                monthly_budget=ch_data.get('monthly_budget')
            )
            
            channels.append(channel)
        
        return channels
    
    @staticmethod
    def session_to_team_structure() -> TeamStructure:
        """Convert session state to TeamStructure model"""
        return TeamStructure(
            num_closers=st.session_state.get('num_closers_main', 8),
            num_setters=st.session_state.get('num_setters_main', 4),
            num_managers=st.session_state.get('num_managers_main', 2),
            num_bench=st.session_state.get('num_benchs_main', 2),
            closer=RoleCompensation(
                base=st.session_state.get('closer_base', 32000),
                variable=st.session_state.get('closer_variable', 48000),
                commission_pct=st.session_state.get('closer_commission_pct', 20.0)
            ),
            setter=RoleCompensation(
                base=st.session_state.get('setter_base', 16000),
                variable=st.session_state.get('setter_variable', 24000),
                commission_pct=st.session_state.get('setter_commission_pct', 3.0)
            ),
            manager=RoleCompensation(
                base=st.session_state.get('manager_base', 72000),
                variable=st.session_state.get('manager_variable', 48000),
                commission_pct=st.session_state.get('manager_commission_pct', 5.0)
            ),
            bench=RoleCompensation(
                base=st.session_state.get('bench_base', 12500),
                variable=st.session_state.get('bench_variable', 12500),
                commission_pct=0
            )
        )
    
    @staticmethod
    def session_to_operating_costs() -> OperatingCosts:
        """Convert session state to OperatingCosts model"""
        return OperatingCosts(
            office_rent=st.session_state.get('office_rent', 20000),
            software_costs=st.session_state.get('software_costs', 10000),
            other_opex=st.session_state.get('other_opex', 5000)
        )
    
    @staticmethod
    @st.cache_data(ttl=300, show_spinner=False)
    def compute_business_metrics(_cache_key: str) -> Dict:
        """
        Compute all business metrics using the new engine.
        Cached based on business state hash.
        
        Returns dict with all calculated metrics for backward compatibility.
        """
        # Convert session state to models
        deal = DashboardAdapter.session_to_deal_economics()
        channels = DashboardAdapter.session_to_channels()
        team = DashboardAdapter.session_to_team_structure()
        opex = DashboardAdapter.session_to_operating_costs()
        
        # Compute GTM metrics
        per_channel, gtm_total = compute_gtm_aggregate(channels, deal)
        
        # Compute unit economics
        unit_econ = calculate_unit_economics(deal, gtm_total.cost_per_sale)
        
        # Compute commissions
        commissions = calculate_commission_pools(
            gtm_total.sales,
            team.closer,
            team.setter,
            team.manager,
            deal
        )
        
        # Compute P&L
        pnl = calculate_pnl(
            gross_revenue=gtm_total.revenue_upfront,
            team_base_annual=team.total_base,
            commissions=commissions.total_commission,
            marketing_spend=gtm_total.spend,
            operating_costs=opex,
            gov_cost_pct=deal.government_cost_pct
        )
        
        # Compute per-person earnings
        per_person = calculate_per_person_earnings(
            commissions,
            team,
            st.session_state.get('working_days', 20)
        )
        
        # Build channels breakdown
        channels_breakdown = []
        for i, m in enumerate(per_channel):
            channels_breakdown.append({
                'name': channels[i].name,
                'segment': channels[i].segment.value,
                'leads': m.leads,
                'sales': m.sales,
                'revenue': m.revenue_upfront,
                'spend': m.spend,
                'cpa': m.cost_per_sale,
                'roas': m.roas,
                'close_rate': channels[i].close_rate
            })
        
        # Return backward-compatible dict
        return {
            # GTM metrics (flattened for compatibility)
            'monthly_leads': gtm_total.leads,
            'monthly_contacts': gtm_total.contacts,
            'monthly_meetings_scheduled': gtm_total.meetings_scheduled,
            'monthly_meetings_held': gtm_total.meetings_held,
            'monthly_sales': gtm_total.sales,
            'monthly_revenue_immediate': gtm_total.revenue_upfront,
            'total_marketing_spend': gtm_total.spend,
            'cost_per_sale': gtm_total.cost_per_sale,
            'blended_close_rate': gtm_total.blended_close_rate,
            
            # Per-channel breakdown
            'channels_breakdown': channels_breakdown,
            
            # Unit economics
            'unit_economics': {
                'ltv': unit_econ.ltv,
                'cac': unit_econ.cac,
                'ltv_cac': unit_econ.ltv_cac_ratio,
                'payback_months': unit_econ.payback_months,
                'upfront_cash': unit_econ.upfront_cash,
                'deferred_cash': unit_econ.deferred_cash
            },
            
            # Commissions
            'commissions': {
                'closer_pool': commissions.closer_pool,
                'setter_pool': commissions.setter_pool,
                'manager_pool': commissions.manager_pool,
                'total_commission': commissions.total_commission,
                'commission_base': commissions.commission_base
            },
            
            # P&L
            'pnl': {
                'gross_revenue': pnl.gross_revenue,
                'gov_fees': pnl.gov_fees,
                'net_revenue': pnl.net_revenue,
                'team_base': pnl.team_base,
                'commissions': pnl.commissions,
                'cogs': pnl.cogs,
                'gross_profit': pnl.gross_profit,
                'gross_margin': pnl.gross_margin,
                'marketing': pnl.marketing,
                'opex': pnl.opex,
                'total_opex': pnl.total_opex,
                'ebitda': pnl.ebitda,
                'ebitda_margin': pnl.ebitda_margin
            },
            
            # Per-person earnings
            'per_person': per_person,
            
            # Original models (for advanced usage)
            '_models': {
                'deal': deal,
                'channels': channels,
                'team': team,
                'opex': opex,
                'gtm_total': gtm_total,
                'per_channel': per_channel
            }
        }
    
    @staticmethod
    def get_cache_key() -> str:
        """
        Generate cache key from current session state.
        Key changes when any relevant input changes, invalidating cache.
        """
        # For channels, extract only the fields that affect calculations
        # This ensures changes are properly detected
        channels_for_hash = []
        for ch in st.session_state.get('gtm_channels', []):
            channels_for_hash.append({
                'id': ch.get('id'),
                'enabled': ch.get('enabled', True),
                'monthly_leads': ch.get('monthly_leads'),
                'cpl': ch.get('cpl'),
                'cost_per_contact': ch.get('cost_per_contact'),
                'cost_per_meeting': ch.get('cost_per_meeting'),
                'cost_per_sale': ch.get('cost_per_sale'),
                'monthly_budget': ch.get('monthly_budget'),
                'cost_method': ch.get('cost_method'),
                'contact_rate': ch.get('contact_rate'),
                'meeting_rate': ch.get('meeting_rate'),
                'show_up_rate': ch.get('show_up_rate'),
                'close_rate': ch.get('close_rate'),
            })
        
        relevant_state = {
            'deal': {
                'avg_deal_value': st.session_state.get('avg_deal_value'),
                'upfront_pct': st.session_state.get('upfront_payment_pct'),
                'grr': st.session_state.get('grr_rate'),
                'gov_pct': st.session_state.get('government_cost_pct'),
                'policy': st.session_state.get('commission_policy')
            },
            'channels': channels_for_hash,  # Use extracted fields
            'team': {
                'counts': [
                    st.session_state.get('num_closers_main'),
                    st.session_state.get('num_setters_main'),
                    st.session_state.get('num_managers_main'),
                    st.session_state.get('num_benchs_main')
                ],
                'comp': [
                    st.session_state.get('closer_base'),
                    st.session_state.get('closer_commission_pct'),
                    st.session_state.get('setter_base'),
                    st.session_state.get('setter_commission_pct'),
                    st.session_state.get('manager_base'),
                    st.session_state.get('manager_commission_pct')
                ]
            },
            'opex': [
                st.session_state.get('office_rent'),
                st.session_state.get('software_costs'),
                st.session_state.get('other_opex')
            ]
        }
        
        return hash_key(relevant_state)
    
    @staticmethod
    def get_metrics() -> Dict:
        """
        Main entry point: Get all business metrics with caching.
        
        Usage in dashboard:
            metrics = DashboardAdapter.get_metrics()
            revenue = metrics['monthly_revenue_immediate']
            ltv_cac = metrics['unit_economics']['ltv_cac']
        """
        cache_key = DashboardAdapter.get_cache_key()
        return DashboardAdapter.compute_business_metrics(cache_key)


# Convenience functions for common operations

def get_gtm_metrics() -> Dict:
    """Get GTM metrics only"""
    metrics = DashboardAdapter.get_metrics()
    return {
        'monthly_leads': metrics['monthly_leads'],
        'monthly_contacts': metrics['monthly_contacts'],
        'monthly_meetings_scheduled': metrics['monthly_meetings_scheduled'],
        'monthly_meetings_held': metrics['monthly_meetings_held'],
        'monthly_sales': metrics['monthly_sales'],
        'monthly_revenue_immediate': metrics['monthly_revenue_immediate'],
        'total_marketing_spend': metrics['total_marketing_spend'],
        'cost_per_sale': metrics['cost_per_sale'],
        'blended_close_rate': metrics['blended_close_rate'],
        'channels_breakdown': metrics['channels_breakdown']
    }


def get_unit_economics() -> Dict:
    """Get unit economics only"""
    metrics = DashboardAdapter.get_metrics()
    return metrics['unit_economics']


def get_pnl() -> Dict:
    """Get P&L only"""
    metrics = DashboardAdapter.get_metrics()
    return metrics['pnl']


def get_commissions() -> Dict:
    """Get commissions only"""
    metrics = DashboardAdapter.get_metrics()
    return metrics['commissions']
