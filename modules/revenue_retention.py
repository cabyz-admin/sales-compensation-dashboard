"""
Revenue Retention Metrics Module
Calculates GRR (Gross Revenue Retention) and NRR (Net Revenue Retention)
Supports multi-channel GTM motions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class RevenueRetentionCalculator:
    """Calculate GRR, NRR, and expansion metrics"""
    
    @staticmethod
    def calculate_grr_nrr(
        starting_mrr: float,
        ending_mrr: float,
        churned_mrr: float,
        downgrade_mrr: float,
        expansion_mrr: float,
        new_mrr: float
    ) -> Dict[str, float]:
        """
        Calculate Gross and Net Revenue Retention
        
        GRR = (Starting MRR - Churned MRR - Downgrade MRR) / Starting MRR
        NRR = (Starting MRR - Churned MRR - Downgrade MRR + Expansion MRR) / Starting MRR
        """
        if starting_mrr == 0:
            return {
                'grr': 0,
                'nrr': 0,
                'grr_percentage': 0,
                'nrr_percentage': 0,
                'expansion_rate': 0,
                'churn_rate': 0,
                'net_growth_rate': 0
            }
        
        # Calculate retention metrics
        grr = (starting_mrr - churned_mrr - downgrade_mrr) / starting_mrr
        nrr = (starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr) / starting_mrr
        
        # Calculate rates
        churn_rate = churned_mrr / starting_mrr
        expansion_rate = expansion_mrr / starting_mrr
        net_growth_rate = (ending_mrr - starting_mrr) / starting_mrr
        
        return {
            'grr': grr,
            'nrr': nrr,
            'grr_percentage': grr * 100,
            'nrr_percentage': nrr * 100,
            'expansion_rate': expansion_rate * 100,
            'churn_rate': churn_rate * 100,
            'net_growth_rate': net_growth_rate * 100,
            'retained_revenue': starting_mrr - churned_mrr - downgrade_mrr,
            'expanded_revenue': expansion_mrr,
            'total_retention_revenue': starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr
        }
    
    @staticmethod
    def calculate_cohort_retention(
        cohorts: Dict[str, Dict[str, float]],
        current_month: int
    ) -> pd.DataFrame:
        """
        Calculate retention by cohort over time
        """
        retention_data = []
        
        for cohort_month, cohort_data in cohorts.items():
            initial_customers = cohort_data.get('initial_customers', 0)
            initial_mrr = cohort_data.get('initial_mrr', 0)
            
            for month in range(current_month + 1):
                retained_customers = cohort_data.get(f'month_{month}_customers', initial_customers)
                retained_mrr = cohort_data.get(f'month_{month}_mrr', initial_mrr)
                
                retention_rate = (retained_customers / initial_customers * 100) if initial_customers > 0 else 0
                revenue_retention = (retained_mrr / initial_mrr * 100) if initial_mrr > 0 else 0
                
                retention_data.append({
                    'Cohort': cohort_month,
                    'Month': month,
                    'Customer_Retention': retention_rate,
                    'Revenue_Retention': revenue_retention,
                    'Retained_Customers': retained_customers,
                    'Retained_MRR': retained_mrr
                })
        
        return pd.DataFrame(retention_data)
    
    @staticmethod
    def project_retention_impact(
        current_mrr: float,
        monthly_churn_rate: float,
        monthly_expansion_rate: float,
        months_forward: int = 12
    ) -> Dict[str, List]:
        """
        Project future MRR based on retention metrics
        """
        projections = {
            'month': list(range(months_forward + 1)),
            'mrr': [current_mrr],
            'grr_mrr': [current_mrr],
            'nrr_mrr': [current_mrr],
            'churned_cumulative': [0],
            'expanded_cumulative': [0]
        }
        
        for month in range(1, months_forward + 1):
            # GRR projection (only churn)
            grr_mrr = projections['grr_mrr'][-1] * (1 - monthly_churn_rate)
            projections['grr_mrr'].append(grr_mrr)
            
            # NRR projection (churn + expansion)
            nrr_mrr = projections['nrr_mrr'][-1] * (1 - monthly_churn_rate + monthly_expansion_rate)
            projections['nrr_mrr'].append(nrr_mrr)
            
            # Track cumulative impact
            churned = projections['nrr_mrr'][-2] * monthly_churn_rate
            expanded = projections['nrr_mrr'][-2] * monthly_expansion_rate
            
            projections['churned_cumulative'].append(
                projections['churned_cumulative'][-1] + churned
            )
            projections['expanded_cumulative'].append(
                projections['expanded_cumulative'][-1] + expanded
            )
        
        return projections


class MultiChannelGTM:
    """
    Multi-channel Go-To-Market model
    Supports different segments (SMB, MID, ENT) with different conversion rates
    """
    
    @staticmethod
    def define_channel(
        name: str,
        lead_source: str,
        segment: str,
        monthly_leads: int,
        contact_rate: float,
        meeting_rate: float,
        show_up_rate: float,
        close_rate: float,
        avg_deal_value: float,
        cpl: float,
        sales_cycle_days: int = 30
    ) -> Dict:
        """
        Define a GTM channel with its own funnel metrics
        """
        return {
            'name': name,
            'lead_source': lead_source,
            'segment': segment,
            'monthly_leads': monthly_leads,
            'contact_rate': contact_rate,
            'meeting_rate': meeting_rate,
            'show_up_rate': show_up_rate,
            'close_rate': close_rate,
            'avg_deal_value': avg_deal_value,
            'cpl': cpl,
            'sales_cycle_days': sales_cycle_days,
            
            # Calculated metrics
            'contacts': monthly_leads * contact_rate,
            'meetings_scheduled': monthly_leads * contact_rate * meeting_rate,
            'meetings_held': monthly_leads * contact_rate * meeting_rate * show_up_rate,
            'sales': monthly_leads * contact_rate * meeting_rate * show_up_rate * close_rate,
            'revenue': monthly_leads * contact_rate * meeting_rate * show_up_rate * close_rate * avg_deal_value,
            'cac': cpl / (contact_rate * meeting_rate * show_up_rate * close_rate) if close_rate > 0 else 0
        }
    
    @staticmethod
    def aggregate_channels(channels: List[Dict]) -> Dict:
        """
        Aggregate multiple GTM channels into overall metrics
        """
        if not channels:
            return {}
        
        total_leads = sum(ch['monthly_leads'] for ch in channels)
        total_contacts = sum(ch['contacts'] for ch in channels)
        total_meetings_scheduled = sum(ch['meetings_scheduled'] for ch in channels)
        total_meetings_held = sum(ch['meetings_held'] for ch in channels)
        total_sales = sum(ch['sales'] for ch in channels)
        total_revenue = sum(ch['revenue'] for ch in channels)
        total_cost = sum(ch['monthly_leads'] * ch['cpl'] for ch in channels)
        
        # Calculate blended rates
        blended_contact_rate = total_contacts / total_leads if total_leads > 0 else 0
        blended_meeting_rate = total_meetings_scheduled / total_contacts if total_contacts > 0 else 0
        blended_show_up_rate = total_meetings_held / total_meetings_scheduled if total_meetings_scheduled > 0 else 0
        blended_close_rate = total_sales / total_meetings_held if total_meetings_held > 0 else 0
        blended_cac = total_cost / total_sales if total_sales > 0 else 0
        avg_deal_value = total_revenue / total_sales if total_sales > 0 else 0
        
        return {
            'total_leads': total_leads,
            'total_contacts': total_contacts,
            'total_meetings_scheduled': total_meetings_scheduled,
            'total_meetings_held': total_meetings_held,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'blended_contact_rate': blended_contact_rate,
            'blended_meeting_rate': blended_meeting_rate,
            'blended_show_up_rate': blended_show_up_rate,
            'blended_close_rate': blended_close_rate,
            'blended_cac': blended_cac,
            'avg_deal_value': avg_deal_value,
            'roas': total_revenue / total_cost if total_cost > 0 else 0,
            'channels': channels
        }
    
    @staticmethod
    def get_default_channels() -> List[Dict]:
        """
        Get default channel configurations for SMB, MID, ENT
        """
        smb_channel = MultiChannelGTM.define_channel(
            name="SMB Channel",
            lead_source="Inbound Marketing",
            segment="SMB",
            monthly_leads=1000,
            contact_rate=0.65,
            meeting_rate=0.40,
            show_up_rate=0.70,
            close_rate=0.30,
            avg_deal_value=15000,
            cpl=50,
            sales_cycle_days=21
        )
        
        mid_channel = MultiChannelGTM.define_channel(
            name="MID Channel",
            lead_source="Outbound SDR",
            segment="MID",
            monthly_leads=300,
            contact_rate=0.55,
            meeting_rate=0.35,
            show_up_rate=0.75,
            close_rate=0.25,
            avg_deal_value=50000,
            cpl=200,
            sales_cycle_days=45
        )
        
        ent_channel = MultiChannelGTM.define_channel(
            name="ENT Channel",
            lead_source="Account-Based Marketing",
            segment="ENT",
            monthly_leads=50,
            contact_rate=0.45,
            meeting_rate=0.30,
            show_up_rate=0.85,
            close_rate=0.20,
            avg_deal_value=250000,
            cpl=1000,
            sales_cycle_days=90
        )
        
        return [smb_channel, mid_channel, ent_channel]
    
    @staticmethod
    def calculate_channel_efficiency(channel: Dict) -> Dict[str, float]:
        """
        Calculate efficiency metrics for a channel
        """
        return {
            'lead_to_sale': channel['sales'] / channel['monthly_leads'] if channel['monthly_leads'] > 0 else 0,
            'cost_per_meeting': channel['cpl'] / (channel['contact_rate'] * channel['meeting_rate'] * channel['show_up_rate']) if channel['show_up_rate'] > 0 else 0,
            'meeting_to_sale': channel['close_rate'],
            'revenue_per_lead': channel['revenue'] / channel['monthly_leads'] if channel['monthly_leads'] > 0 else 0,
            'ltv_cac_ratio': (channel['avg_deal_value'] * 0.8) / channel['cac'] if channel['cac'] > 0 else 0,  # Assuming 80% gross margin
            'payback_months': channel['cac'] / (channel['avg_deal_value'] * 0.08) if channel['avg_deal_value'] > 0 else 0  # Assuming 8% monthly retention
        }
