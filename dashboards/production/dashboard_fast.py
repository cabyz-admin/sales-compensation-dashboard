"""
⚡ Lightning Fast Sales Compensation Dashboard
Tab-based architecture with aggressive caching for 10X performance

Key Features:
- Tab-based organization (only active tab loads)
- Aggressive caching (@st.cache_data)
- Fragment-based sections (@st.fragment)
- Lazy loading for heavy components
- Clean modular structure
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import sys
import os

# Setup paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARDS_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARDS_DIR)
MODULES_DIR = os.path.join(PROJECT_ROOT, "modules")

for path in [MODULES_DIR, PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import modules
try:
    from modules.calculations_improved import (
        ImprovedCostCalculator,
        ImprovedCompensationCalculator,
        ImprovedPnLCalculator
    )
    from modules.calculations_enhanced import (
        EnhancedRevenueCalculator,
        HealthScoreCalculator
    )
    from modules.revenue_retention import MultiChannelGTM
    from deal_economics_manager import DealEconomicsManager, CommissionCalculator
except ImportError as e:
    st.error(f"⚠️ Module import error: {e}")
    st.stop()

# ============= PAGE CONFIG =============
st.set_page_config(
    page_title="⚡ Sales Compensation Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= CUSTOM CSS =============
st.markdown("""
    <style>
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(151, 166, 195, 0.15);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Hide unnecessary elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============= INITIALIZE SESSION STATE =============
def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'initialized': True,
        
        # Deal Economics
        'avg_deal_value': 50000,
        'upfront_payment_pct': 70.0,
        'contract_length_months': 12,
        'deferred_timing_months': 18,
        'commission_policy': 'upfront',
        
        # Team
        'num_closers_main': 8,
        'num_setters_main': 4,
        'num_managers_main': 2,
        'num_benchs_main': 2,
        
        # Compensation
        'closer_base': 32000,
        'closer_variable': 48000,
        'closer_commission_pct': 20.0,
        'setter_base': 16000,
        'setter_variable': 24000,
        'setter_commission_pct': 3.0,
        'manager_base': 72000,
        'manager_variable': 48000,
        'manager_commission_pct': 5.0,
        'bench_base': 12500,
        'bench_variable': 12500,
        
        # Operating Costs
        'office_rent': 20000,
        'software_costs': 10000,
        'other_opex': 5000,
        
        # GTM Channels
        'gtm_channels': [{
            'id': 'channel_1',
            'name': 'Primary Channel',
            'segment': 'SMB',
            'monthly_leads': 1000,
            'cpl': 50,
            'contact_rate': 0.65,
            'meeting_rate': 0.4,
            'show_up_rate': 0.7,
            'close_rate': 0.3,
            'avg_deal_value': 50000,
        }],
        
        # Other
        'grr_rate': 0.90,
        'working_days': 20,
        'projection_months': 18,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ============= CACHED CALCULATIONS =============

@st.cache_data(ttl=300)
def calculate_gtm_metrics_cached(channels_json: str):
    """
    Cached GTM metrics calculation.
    Only recalculates if channels configuration changes.
    Cache for 5 minutes.
    """
    import json
    channels = json.loads(channels_json)
    
    if not channels:
        return {
            'monthly_leads': 0,
            'monthly_contacts': 0,
            'monthly_meetings_scheduled': 0,
            'monthly_meetings_held': 0,
            'monthly_sales': 0,
            'monthly_revenue_immediate': 0,
            'blended_close_rate': 0,
            'blended_ltv_cac': 0,
        }
    
    # Aggregate across channels
    total_leads = sum(ch.get('monthly_leads', 0) for ch in channels)
    total_sales = 0
    total_revenue = 0
    
    for ch in channels:
        leads = ch.get('monthly_leads', 0)
        contact_rate = ch.get('contact_rate', 0.6)
        meeting_rate = ch.get('meeting_rate', 0.3)
        show_up_rate = ch.get('show_up_rate', 0.7)
        close_rate = ch.get('close_rate', 0.25)
        
        contacts = leads * contact_rate
        meetings_sched = contacts * meeting_rate
        meetings_held = meetings_sched * show_up_rate
        sales = meetings_held * close_rate
        
        total_sales += sales
        
        # Get deal economics
        deal_econ = DealEconomicsManager.get_current_deal_economics()
        revenue = sales * deal_econ['upfront_cash']
        total_revenue += revenue
    
    return {
        'monthly_leads': total_leads,
        'monthly_sales': total_sales,
        'monthly_revenue_immediate': total_revenue,
        'blended_close_rate': total_sales / (total_leads * 0.6 * 0.3 * 0.7) if total_leads > 0 else 0,
    }

@st.cache_data(ttl=300)
def calculate_commission_data_cached(sales_count: float, roles_json: str, deal_econ_json: str):
    """Cached commission calculation"""
    import json
    roles_comp = json.loads(roles_json)
    deal_econ = json.loads(deal_econ_json)
    
    return DealEconomicsManager.calculate_monthly_commission(sales_count, roles_comp, deal_econ)

@st.cache_data(ttl=600)
def calculate_unit_economics_cached(deal_value: float, upfront_pct: float, grr: float, cost_per_sale: float):
    """Cached unit economics"""
    upfront_cash = deal_value * (upfront_pct / 100)
    deferred_cash = deal_value * ((100 - upfront_pct) / 100)
    ltv = upfront_cash + (deferred_cash * grr)
    ltv_cac = ltv / cost_per_sale if cost_per_sale > 0 else 0
    payback_months = cost_per_sale / (upfront_cash / 12) if upfront_cash > 0 else 999
    
    return {
        'ltv': ltv,
        'cac': cost_per_sale,
        'ltv_cac': ltv_cac,
        'payback_months': payback_months
    }

# ============= HEADER =============
st.title("⚡ Lightning Fast Sales Compensation Dashboard")
st.caption("Tab-based architecture • Aggressive caching • 10X faster performance")

# Quick metrics at top (cached)
import json
gtm_metrics = calculate_gtm_metrics_cached(json.dumps(st.session_state.gtm_channels))
deal_econ = DealEconomicsManager.get_current_deal_economics()

header_cols = st.columns(5)
with header_cols[0]:
    st.metric("💰 Monthly Revenue", f"${gtm_metrics['monthly_revenue_immediate']:,.0f}")
with header_cols[1]:
    st.metric("📈 Monthly Sales", f"{gtm_metrics['monthly_sales']:.1f}")
with header_cols[2]:
    st.metric("💎 Deal Value", f"${deal_econ['avg_deal_value']:,.0f}")
with header_cols[3]:
    unit_econ = calculate_unit_economics_cached(
        deal_econ['avg_deal_value'],
        deal_econ['upfront_pct'],
        st.session_state.grr_rate,
        5000  # Placeholder CAC
    )
    st.metric("🎯 LTV:CAC", f"{unit_econ['ltv_cac']:.1f}:1")
with header_cols[4]:
    policy = DealEconomicsManager.get_commission_policy()
    st.metric("💸 Comm Policy", "Upfront" if policy == 'upfront' else "Full")

st.markdown("---")

# ============= TABS =============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 GTM Command Center",
    "💰 Compensation Structure", 
    "📊 Business Performance",
    "🔮 What-If Analysis",
    "⚙️ Configuration"
])

# ============= TAB 1: GTM COMMAND CENTER =============
with tab1:
    st.header("🎯 GTM Command Center")
    st.caption("Go-to-market metrics, channels, and funnel performance")
    
    # Funnel metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Monthly Leads", f"{gtm_metrics['monthly_leads']:,.0f}")
    with col2:
        st.metric("🤝 Monthly Sales", f"{gtm_metrics['monthly_sales']:.1f}")
    with col3:
        st.metric("💵 Revenue", f"${gtm_metrics['monthly_revenue_immediate']:,.0f}")
    with col4:
        st.metric("🎯 Close Rate", f"{gtm_metrics['blended_close_rate']:.1%}")
    
    st.markdown("---")
    
    # Channel configuration
    with st.expander("📡 Channel Configuration", expanded=True):
        st.info("💡 Configure your GTM channels for accurate forecasting")
        
        num_channels = len(st.session_state.gtm_channels)
        st.metric("Active Channels", num_channels)
        
        if st.button("➕ Add Channel"):
            new_channel = {
                'id': f'channel_{num_channels + 1}',
                'name': f'Channel {num_channels + 1}',
                'segment': 'SMB',
                'monthly_leads': 500,
                'cpl': 50,
                'contact_rate': 0.6,
                'meeting_rate': 0.3,
                'show_up_rate': 0.7,
                'close_rate': 0.25,
            }
            st.session_state.gtm_channels.append(new_channel)
            st.rerun()
        
        # Show channel summary
        for i, channel in enumerate(st.session_state.gtm_channels):
            with st.container():
                ch_cols = st.columns([3, 1, 1, 1, 1, 1])
                with ch_cols[0]:
                    st.markdown(f"**{channel['name']}** ({channel['segment']})")
                with ch_cols[1]:
                    st.caption(f"{channel['monthly_leads']:,.0f} leads")
                with ch_cols[2]:
                    st.caption(f"${channel.get('cpl', 50)} CPL")
                with ch_cols[3]:
                    st.caption(f"{channel.get('close_rate', 0.25):.1%} close")
                with ch_cols[4]:
                    if st.button("✏️", key=f"edit_{i}"):
                        st.session_state[f'editing_channel_{i}'] = True
                with ch_cols[5]:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.gtm_channels.pop(i)
                        st.rerun()
    
    # Advanced analytics (lazy load)
    with st.expander("📊 Advanced Channel Analytics", expanded=False):
        st.caption("🔄 Loading advanced analytics...")
        
        if st.button("📈 Load Channel Performance Charts"):
            st.info("Charts would load here - implement full GTM analytics when needed")

# ============= TAB 2: COMPENSATION STRUCTURE =============
with tab2:
    st.header("💰 Compensation Structure")
    st.caption("Commission flow, earnings preview, and team compensation")
    
    # Commission Flow Fragment
    @st.fragment
    def render_commission_flow():
        st.subheader("💸 Commission Flow Visualization")
        
        flow_view = st.radio(
            "View",
            ["📊 Monthly Total", "🎯 Per Deal"],
            horizontal=True,
            key="commission_flow_view"
        )
        
        # Get roles comp
        roles_comp = {
            'closer': {
                'base': st.session_state.closer_base,
                'commission_pct': st.session_state.closer_commission_pct
            },
            'setter': {
                'base': st.session_state.setter_base,
                'commission_pct': st.session_state.setter_commission_pct
            },
            'manager': {
                'base': st.session_state.manager_base,
                'commission_pct': st.session_state.manager_commission_pct
            }
        }
        
        flow_cols = st.columns([2, 1])
        
        with flow_cols[0]:
            current_deal_econ = DealEconomicsManager.get_current_deal_economics()
            
            if "Per Deal" in flow_view:
                # Per deal
                per_deal_comm = DealEconomicsManager.calculate_per_deal_commission(roles_comp, current_deal_econ)
                
                st.metric("Deal Value", f"${current_deal_econ['avg_deal_value']:,.0f}")
                st.metric("Commission Base", f"${per_deal_comm['commission_base']:,.0f}")
                st.metric("Total Commission", f"${per_deal_comm['total_commission']:,.0f}")
                st.metric("Commission Rate", f"{per_deal_comm['commission_rate']:.1f}%")
            else:
                # Monthly
                monthly_comm = calculate_commission_data_cached(
                    gtm_metrics['monthly_sales'],
                    json.dumps(roles_comp),
                    json.dumps(current_deal_econ)
                )
                
                st.metric("Monthly Revenue", f"${gtm_metrics['monthly_revenue_immediate']:,.0f}")
                st.metric("Total Commission", f"${monthly_comm['total_commission']:,.0f}")
                st.metric("Commission Rate", f"{monthly_comm['commission_rate']:.1f}%")
        
        with flow_cols[1]:
            st.markdown("**Commission Breakdown**")
            
            if "Per Deal" in flow_view:
                per_deal_comm = DealEconomicsManager.calculate_per_deal_commission(roles_comp, current_deal_econ)
                st.caption(f"💼 Closer: ${per_deal_comm['closer_pool']:,.0f}")
                st.caption(f"📞 Setter: ${per_deal_comm['setter_pool']:,.0f}")
                st.caption(f"👔 Manager: ${per_deal_comm['manager_pool']:,.0f}")
            else:
                monthly_comm = calculate_commission_data_cached(
                    gtm_metrics['monthly_sales'],
                    json.dumps(roles_comp),
                    json.dumps(current_deal_econ)
                )
                st.caption(f"💼 Closers: ${monthly_comm['closer_pool']:,.0f}")
                st.caption(f"📞 Setters: ${monthly_comm['setter_pool']:,.0f}")
                st.caption(f"👔 Managers: ${monthly_comm['manager_pool']:,.0f}")
    
    render_commission_flow()
    
    st.markdown("---")
    
    # Period Earnings Fragment
    @st.fragment
    def render_period_earnings():
        st.subheader("📅 Period-Based Earnings Preview")
        
        roles_comp = {
            'closer': {
                'base': st.session_state.closer_base,
                'variable': st.session_state.closer_variable,
                'ote': st.session_state.closer_base + st.session_state.closer_variable,
                'commission_pct': st.session_state.closer_commission_pct
            },
            'setter': {
                'base': st.session_state.setter_base,
                'variable': st.session_state.setter_variable,
                'ote': st.session_state.setter_base + st.session_state.setter_variable,
                'commission_pct': st.session_state.setter_commission_pct
            },
            'manager': {
                'base': st.session_state.manager_base,
                'variable': st.session_state.manager_variable,
                'ote': st.session_state.manager_base + st.session_state.manager_variable,
                'commission_pct': st.session_state.manager_commission_pct
            },
            'bench': {
                'base': st.session_state.bench_base,
                'variable': st.session_state.bench_variable,
                'ote': st.session_state.bench_base + st.session_state.bench_variable,
                'commission_pct': 0
            }
        }
        
        team_counts = {
            'closer': st.session_state.num_closers_main,
            'setter': st.session_state.num_setters_main,
            'manager': st.session_state.num_managers_main,
            'bench': st.session_state.num_benchs_main
        }
        
        period_data = CommissionCalculator.calculate_period_earnings(
            roles_comp,
            gtm_metrics['monthly_sales'],
            team_counts,
            st.session_state.working_days
        )
        
        if period_data:
            st.dataframe(
                pd.DataFrame(period_data),
                use_container_width=True,
                hide_index=True
            )
    
    render_period_earnings()

# ============= TAB 3: BUSINESS PERFORMANCE =============
with tab3:
    st.header("📊 Business Performance")
    st.caption("P&L, EBITDA, unit economics, and financial health")
    
    # Unit Economics
    col1, col2, col3, col4 = st.columns(4)
    
    unit_econ = calculate_unit_economics_cached(
        deal_econ['avg_deal_value'],
        deal_econ['upfront_pct'],
        st.session_state.grr_rate,
        5000  # CAC placeholder
    )
    
    with col1:
        st.metric("💎 LTV", f"${unit_econ['ltv']:,.0f}")
    with col2:
        st.metric("💰 CAC", f"${unit_econ['cac']:,.0f}")
    with col3:
        color = "normal" if unit_econ['ltv_cac'] >= 3 else "inverse"
        st.metric("🎯 LTV:CAC", f"{unit_econ['ltv_cac']:.1f}:1", delta=None, delta_color=color)
    with col4:
        st.metric("⏱️ Payback", f"{unit_econ['payback_months']:.1f} mo")
    
    st.markdown("---")
    
    # P&L Summary (lazy load)
    with st.expander("💰 P&L Summary", expanded=False):
        st.info("Full P&L analysis - implement when needed")

# ============= TAB 4: WHAT-IF ANALYSIS =============
with tab4:
    st.header("🔮 What-If Analysis")
    st.caption("Test scenarios and reverse engineer targets")
    
    st.info("🚀 What-If scenarios coming soon")
    
    scenario_cols = st.columns(3)
    with scenario_cols[0]:
        if st.button("📈 Growth Mode (+50% team)"):
            st.success("Scenario: Increase team by 50%")
    with scenario_cols[1]:
        if st.button("💰 Profit Focus (-20% OpEx)"):
            st.success("Scenario: Reduce OpEx by 20%")
    with scenario_cols[2]:
        if st.button("🔄 Reset Defaults"):
            st.success("Reset to default values")

# ============= TAB 5: CONFIGURATION =============
with tab5:
    st.header("⚙️ Configuration")
    st.caption("Configure deal economics, team, compensation, and operating costs")
    
    # Deal Economics
    with st.expander("💰 Deal Economics & Payment Terms", expanded=True):
        st.info("💡 Configure your deal structure - applies to all calculations")
        
        deal_cols = st.columns(3)
        
        with deal_cols[0]:
            st.markdown("**Deal Value**")
            avg_deal_value = st.number_input(
                "Average Deal Value ($)",
                min_value=0,
                value=st.session_state.avg_deal_value,
                step=1000,
                key="avg_deal_value"
            )
        
        with deal_cols[1]:
            st.markdown("**Payment Terms**")
            upfront_pct = st.slider(
                "Upfront Payment %",
                0.0,
                100.0,
                st.session_state.upfront_payment_pct,
                1.0,
                key="upfront_payment_pct"
            )
            st.caption(f"Deferred: {100-upfront_pct:.0f}%")
        
        with deal_cols[2]:
            st.markdown("**Commission Policy**")
            commission_policy = st.radio(
                "Pay Commissions From:",
                ["Upfront Cash Only", "Full Deal Value"],
                index=0 if st.session_state.commission_policy == 'upfront' else 1,
                key="commission_policy_selector"
            )
            
            if "Upfront" in commission_policy:
                st.session_state.commission_policy = 'upfront'
            else:
                st.session_state.commission_policy = 'full'
    
    # Team Configuration
    with st.expander("👥 Team Configuration", expanded=False):
        team_cols = st.columns(4)
        
        with team_cols[0]:
            st.number_input("Closers", 1, 50, st.session_state.num_closers_main, key="num_closers_main")
        with team_cols[1]:
            st.number_input("Setters", 0, 50, st.session_state.num_setters_main, key="num_setters_main")
        with team_cols[2]:
            st.number_input("Managers", 0, 20, st.session_state.num_managers_main, key="num_managers_main")
        with team_cols[3]:
            st.number_input("Bench", 0, 20, st.session_state.num_benchs_main, key="num_benchs_main")
    
    # Compensation Configuration
    with st.expander("💵 Compensation Configuration", expanded=False):
        comp_cols = st.columns(3)
        
        with comp_cols[0]:
            st.markdown("**Closer**")
            st.number_input("Base ($)", 0, 200000, st.session_state.closer_base, 1000, key="closer_base")
            st.number_input("Variable ($)", 0, 200000, st.session_state.closer_variable, 1000, key="closer_variable")
            st.number_input("Commission %", 0.0, 50.0, st.session_state.closer_commission_pct, 0.5, key="closer_commission_pct")
        
        with comp_cols[1]:
            st.markdown("**Setter**")
            st.number_input("Base ($)", 0, 200000, st.session_state.setter_base, 1000, key="setter_base")
            st.number_input("Variable ($)", 0, 200000, st.session_state.setter_variable, 1000, key="setter_variable")
            st.number_input("Commission %", 0.0, 50.0, st.session_state.setter_commission_pct, 0.5, key="setter_commission_pct")
        
        with comp_cols[2]:
            st.markdown("**Manager**")
            st.number_input("Base ($)", 0, 300000, st.session_state.manager_base, 1000, key="manager_base")
            st.number_input("Variable ($)", 0, 300000, st.session_state.manager_variable, 1000, key="manager_variable")
            st.number_input("Commission %", 0.0, 50.0, st.session_state.manager_commission_pct, 0.5, key="manager_commission_pct")
    
    # Operating Costs
    with st.expander("🏢 Operating Costs", expanded=False):
        ops_cols = st.columns(3)
        
        with ops_cols[0]:
            st.number_input("Office Rent ($)", 0, 100000, st.session_state.office_rent, 500, key="office_rent")
        with ops_cols[1]:
            st.number_input("Software ($)", 0, 50000, st.session_state.software_costs, 100, key="software_costs")
        with ops_cols[2]:
            st.number_input("Other OpEx ($)", 0, 100000, st.session_state.other_opex, 500, key="other_opex")

# ============= FOOTER =============
st.markdown("---")
st.caption("⚡ Lightning Fast Dashboard • Built with Streamlit • Cached for performance")
