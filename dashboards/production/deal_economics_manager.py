"""
Deal Economics Manager - Single Source of Truth
Centralized management of deal economics and revenue calculations
"""

import streamlit as st


class DealEconomicsManager:
    """
    Centralized manager for all deal economics calculations.
    This is the SINGLE SOURCE OF TRUTH for deal values, payment terms, and revenue splits.
    """
    
    @staticmethod
    def get_current_deal_economics():
        """
        Get current deal economics from session state.
        Returns a dictionary with all deal-related values.
        
        SINGLE SOURCE: All calculators now write directly to avg_deal_value and contract_length_months.
        """
        # All calculators (Insurance, Subscription, Commission, Direct) now write to the same keys
        avg_deal_value = st.session_state.get('avg_deal_value', 50000)
        contract_length_months = st.session_state.get('contract_length_months', 12)
        
        upfront_pct = st.session_state.get('upfront_payment_pct', 70.0)
        deferred_pct = 100.0 - upfront_pct
        deferred_timing_months = st.session_state.get('deferred_timing_months', 18)
        
        return {
            'avg_deal_value': avg_deal_value,
            'upfront_pct': upfront_pct,
            'deferred_pct': deferred_pct,
            'upfront_pct_decimal': upfront_pct / 100,
            'deferred_pct_decimal': deferred_pct / 100,
            'contract_length_months': contract_length_months,
            'deferred_timing_months': deferred_timing_months,
            'upfront_cash': avg_deal_value * (upfront_pct / 100),
            'deferred_cash': avg_deal_value * (deferred_pct / 100),
        }
    
    @staticmethod
    def get_commission_policy():
        """
        Get commission payment policy.
        Returns 'upfront' or 'full' based on user selection.
        """
        return st.session_state.get('commission_policy', 'upfront')
    
    @staticmethod
    def calculate_commission_base(sales_count, deal_economics=None):
        """
        Calculate the base amount for commission calculations.
        
        Args:
            sales_count: Number of sales/deals closed
            deal_economics: Deal economics dict (if None, fetches current)
        
        Returns:
            dict with commission_base, upfront_revenue, full_revenue
        """
        if deal_economics is None:
            deal_economics = DealEconomicsManager.get_current_deal_economics()
        
        policy = DealEconomicsManager.get_commission_policy()
        
        # Calculate revenue streams
        upfront_revenue = sales_count * deal_economics['upfront_cash']
        full_revenue = sales_count * deal_economics['avg_deal_value']
        deferred_revenue = sales_count * deal_economics['deferred_cash']
        
        # Determine commission base based on policy
        if policy == 'upfront':
            commission_base = upfront_revenue
        else:  # 'full'
            commission_base = full_revenue
        
        return {
            'commission_base': commission_base,
            'upfront_revenue': upfront_revenue,
            'full_revenue': full_revenue,
            'deferred_revenue': deferred_revenue,
            'policy': policy
        }
    
    @staticmethod
    def calculate_per_deal_commission(roles_comp, deal_economics=None):
        """
        Calculate per-deal commission pools for each role.
        
        Args:
            roles_comp: Role compensation configuration
            deal_economics: Deal economics dict (if None, fetches current)
        
        Returns:
            dict with commission pools per role
        """
        if deal_economics is None:
            deal_economics = DealEconomicsManager.get_current_deal_economics()
        
        # Calculate commission base for 1 deal
        comm_calc = DealEconomicsManager.calculate_commission_base(1, deal_economics)
        commission_base = comm_calc['commission_base']
        
        # Calculate pools per role
        closer_comm_pct = roles_comp.get('closer', {}).get('commission_pct', 20.0) / 100
        setter_comm_pct = roles_comp.get('setter', {}).get('commission_pct', 3.0) / 100
        manager_comm_pct = roles_comp.get('manager', {}).get('commission_pct', 5.0) / 100
        
        return {
            'commission_base': commission_base,
            'closer_pool': commission_base * closer_comm_pct,
            'setter_pool': commission_base * setter_comm_pct,
            'manager_pool': commission_base * manager_comm_pct,
            'total_commission': commission_base * (closer_comm_pct + setter_comm_pct + manager_comm_pct),
            'commission_rate': (closer_comm_pct + setter_comm_pct + manager_comm_pct) * 100,
            'policy': comm_calc['policy'],
            'deal_economics': deal_economics
        }
    
    @staticmethod
    def calculate_monthly_commission(sales_count, roles_comp, deal_economics=None):
        """
        Calculate monthly commission pools for each role.
        
        Args:
            sales_count: Number of sales in the month
            roles_comp: Role compensation configuration
            deal_economics: Deal economics dict (if None, fetches current)
        
        Returns:
            dict with monthly commission pools per role
        """
        per_deal = DealEconomicsManager.calculate_per_deal_commission(roles_comp, deal_economics)
        
        return {
            'commission_base': per_deal['commission_base'] * sales_count,
            'closer_pool': per_deal['closer_pool'] * sales_count,
            'setter_pool': per_deal['setter_pool'] * sales_count,
            'manager_pool': per_deal['manager_pool'] * sales_count,
            'total_commission': per_deal['total_commission'] * sales_count,
            'commission_rate': per_deal['commission_rate'],
            'per_deal': per_deal,
            'sales_count': sales_count
        }
    
    @staticmethod
    def calculate_monthly_revenue(sales_count, deal_economics=None, include_deferred=False, month_number=1):
        """
        Calculate monthly revenue based on sales and deal economics.
        
        Args:
            sales_count: Number of sales in the month
            deal_economics: Deal economics dict (if None, fetches current)
            include_deferred: Whether to include deferred revenue from past months
            month_number: Current month number (for deferred calculations)
        
        Returns:
            dict with revenue breakdown
        """
        if deal_economics is None:
            deal_economics = DealEconomicsManager.get_current_deal_economics()
        
        # Current month upfront revenue
        upfront_revenue = sales_count * deal_economics['upfront_cash']
        
        # Deferred revenue (if applicable)
        deferred_revenue = 0
        if include_deferred and month_number >= deal_economics['deferred_timing_months']:
            # Calculate deferred from sales X months ago
            # This would need historical sales data - simplified for now
            # Assuming same sales count for deferred timing
            deferred_revenue = sales_count * deal_economics['deferred_cash']
        
        return {
            'upfront_revenue': upfront_revenue,
            'deferred_revenue': deferred_revenue,
            'total_revenue': upfront_revenue + deferred_revenue,
            'sales_count': sales_count,
            'deal_economics': deal_economics
        }
    
    @staticmethod
    def get_summary_display(deal_economics=None):
        """
        Get formatted summary for display in UI.
        
        Args:
            deal_economics: Deal economics dict (if None, fetches current)
        
        Returns:
            dict with formatted display values
        """
        if deal_economics is None:
            deal_economics = DealEconomicsManager.get_current_deal_economics()
        
        policy = DealEconomicsManager.get_commission_policy()
        policy_display = "Upfront Cash Only" if policy == 'upfront' else "Full Deal Value"
        
        return {
            'deal_value': f"${deal_economics['avg_deal_value']:,.0f}",
            'upfront_cash': f"${deal_economics['upfront_cash']:,.0f}",
            'upfront_pct': f"{deal_economics['upfront_pct']:.0f}%",
            'deferred_cash': f"${deal_economics['deferred_cash']:,.0f}",
            'deferred_pct': f"{deal_economics['deferred_pct']:.0f}%",
            'deferred_timing': f"{deal_economics['deferred_timing_months']} months",
            'commission_policy': policy_display,
            'commission_base_display': f"${deal_economics['upfront_cash']:,.0f}" if policy == 'upfront' else f"${deal_economics['avg_deal_value']:,.0f}"
        }


class CommissionCalculator:
    """Helper class for commission calculations using Deal Economics Manager"""
    
    @staticmethod
    def calculate_period_earnings(roles_comp, monthly_sales, team_counts, working_days=20):
        """
        Calculate period-based earnings (daily, weekly, monthly, annual) per role.
        
        Args:
            roles_comp: Role compensation configuration
            monthly_sales: Number of sales per month
            team_counts: Dict with count per role (e.g., {'closer': 8, 'setter': 4})
            working_days: Working days per month
        
        Returns:
            List of dicts with earnings breakdown per role
        """
        # Get monthly commission pools
        monthly_comm = DealEconomicsManager.calculate_monthly_commission(monthly_sales, roles_comp)
        
        period_data = []
        
        for role_key in ['closer', 'setter', 'manager', 'bench']:
            role_count = team_counts.get(role_key, 0)
            if role_count == 0:
                continue
            
            role_config = roles_comp.get(role_key, {})
            
            # Base salary
            base_monthly = role_config.get('base', 0)
            base_daily = base_monthly / 30
            base_weekly = base_monthly / 4.33
            base_annual = base_monthly * 12
            
            # Commission (if applicable)
            if role_key == 'closer':
                comm_pool = monthly_comm['closer_pool']
            elif role_key == 'setter':
                comm_pool = monthly_comm['setter_pool']
            elif role_key == 'manager':
                comm_pool = monthly_comm['manager_pool']
            else:
                comm_pool = 0
            
            comm_per_person = comm_pool / role_count if role_count > 0 else 0
            comm_daily = comm_per_person / working_days
            comm_weekly = comm_per_person / 4.33
            comm_annual = comm_per_person * 12
            
            # Total earnings
            period_data.append({
                'Role': role_key.capitalize(),
                'Count': role_count,
                'Daily': f"${base_daily + comm_daily:,.0f}",
                'Weekly': f"${base_weekly + comm_weekly:,.0f}",
                'Monthly': f"${base_monthly + comm_per_person:,.0f}",
                'Annual': f"${base_annual + comm_annual:,.0f}",
                'vs OTE': f"{((base_monthly + comm_per_person)/role_config.get('ote', 1)*100):.0f}%" if role_config.get('ote', 0) > 0 else "N/A"
            })
        
        return period_data
    
    @staticmethod
    def get_commission_summary(monthly_sales, roles_comp):
        """
        Get commission summary for display.
        
        Args:
            monthly_sales: Number of sales per month
            roles_comp: Role compensation configuration
        
        Returns:
            dict with commission summary
        """
        monthly_comm = DealEconomicsManager.calculate_monthly_commission(monthly_sales, roles_comp)
        per_deal = monthly_comm['per_deal']
        
        return {
            'monthly_total': monthly_comm['total_commission'],
            'monthly_closer': monthly_comm['closer_pool'],
            'monthly_setter': monthly_comm['setter_pool'],
            'monthly_manager': monthly_comm['manager_pool'],
            'per_deal_total': per_deal['total_commission'],
            'per_deal_closer': per_deal['closer_pool'],
            'per_deal_setter': per_deal['setter_pool'],
            'per_deal_manager': per_deal['manager_pool'],
            'commission_rate': monthly_comm['commission_rate'],
            'commission_base': monthly_comm['commission_base'],
            'policy': monthly_comm['per_deal']['policy']
        }
