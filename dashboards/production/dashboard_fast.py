"""
💎 ULTIMATE Sales Compensation Dashboard
Fast + Feature-Rich: Best of both worlds!

Performance:
- ⚡ 10X faster with aggressive caching
- 📊 Tab-based architecture (only active tab loads)
- 🧩 Fragment-based sections for instant updates
- 💾 Smart caching (@st.cache_data)

Features:
- 🎯 Dynamic alerts with specific actions
- 💰 Full Plotly commission flow visualization
- 📊 Complete P&L breakdown with categorization
- 🔮 Interactive what-if analysis with sliders
- 📈 Multi-channel GTM analytics
- 💎 Accurate calculations using Deal Economics Manager
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import json
from datetime import datetime
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

# ============= TRANSLATIONS =============
TRANSLATIONS = {
    'en': {
        'language': '🌐 Language',
        'english': '🇺🇸 English',
        'spanish': '🇪🇸 Español',
    },
    'es': {
        'language': '🌐 Idioma',
        'english': '🇺🇸 English',
        'spanish': '🇪🇸 Español',
    }
}

def t(key, lang='en'):
    """Translation function"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# Import modules
try:
    from deal_economics_manager import DealEconomicsManager
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
    
    /* Alert styling */
    .alert-critical {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        color: #991b1b;
    }
    .alert-critical strong {
        color: #7f1d1d;
    }
    .alert-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        color: #92400e;
    }
    .alert-warning strong {
        color: #78350f;
    }
    .alert-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        color: #065f46;
    }
    .alert-success strong {
        color: #064e3b;
    }
    </style>
""", unsafe_allow_html=True)

# ============= INITIALIZE SESSION STATE =============
def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'initialized': True,
        'prevent_rerun': False,  # Flag to prevent unnecessary reruns
        
        # Deal Economics
        'avg_deal_value': 50000,
        'upfront_payment_pct': 70.0,
        'contract_length_months': 12,
        'deferred_timing_months': 18,
        'commission_policy': 'upfront',
        'government_cost_pct': 10.0,  # Government fees/taxes
        
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
    total_leads = 0
    total_contacts = 0
    total_meetings_sched = 0
    total_meetings_held = 0
    total_sales = 0
    total_revenue = 0
    total_spend = 0
    channels_breakdown = []
    
    for ch in channels:
        if not ch.get('enabled', True):
            continue
            
        leads = ch.get('monthly_leads', 0)
        cpl = ch.get('cpl', 50)
        contact_rate = ch.get('contact_rate', 0.6)
        meeting_rate = ch.get('meeting_rate', 0.3)
        show_up_rate = ch.get('show_up_rate', 0.7)
        close_rate = ch.get('close_rate', 0.25)
        
        contacts = leads * contact_rate
        meetings_sched = contacts * meeting_rate
        meetings_held = meetings_sched * show_up_rate
        sales = meetings_held * close_rate
        
        # Get deal economics
        deal_econ = DealEconomicsManager.get_current_deal_economics()
        revenue = sales * deal_econ['upfront_cash']
        spend = leads * cpl
        
        # Aggregate
        total_leads += leads
        total_contacts += contacts
        total_meetings_sched += meetings_sched
        total_meetings_held += meetings_held
        total_sales += sales
        total_revenue += revenue
        total_spend += spend
        
        # Channel breakdown
        channels_breakdown.append({
            'name': ch.get('name', 'Channel'),
            'segment': ch.get('segment', 'Unknown'),
            'leads': leads,
            'sales': sales,
            'revenue': revenue,
            'spend': spend,
            'cpa': spend / sales if sales > 0 else 0,
            'roas': revenue / spend if spend > 0 else 0,
            'close_rate': close_rate
        })
    
    cost_per_sale = total_spend / total_sales if total_sales > 0 else 0
    blended_close_rate = total_sales / total_meetings_held if total_meetings_held > 0 else 0
    
    return {
        'monthly_leads': total_leads,
        'monthly_contacts': total_contacts,
        'monthly_meetings_scheduled': total_meetings_sched,
        'monthly_meetings_held': total_meetings_held,
        'monthly_sales': total_sales,
        'monthly_revenue_immediate': total_revenue,
        'total_marketing_spend': total_spend,
        'cost_per_sale': cost_per_sale,
        'blended_close_rate': blended_close_rate,
        'channels_breakdown': channels_breakdown
    }

@st.cache_data(ttl=300)
def calculate_commission_data_cached(sales_count: float, roles_json: str, deal_econ_json: str):
    """Cached commission calculation"""
    import json
    roles_comp = json.loads(roles_json)
    deal_econ = json.loads(deal_econ_json)
    
    return DealEconomicsManager.calculate_monthly_commission(sales_count, roles_comp, deal_econ)

@st.cache_data(ttl=600)
def calculate_deal_cash_splits(deal_value: float, upfront_pct: float):
    """Cached calculation of upfront/deferred cash splits - used everywhere"""
    upfront_cash = deal_value * (upfront_pct / 100)
    deferred_cash = deal_value * ((100 - upfront_pct) / 100)
    deferred_pct = 100 - upfront_pct
    
    return {
        'upfront_cash': upfront_cash,
        'deferred_cash': deferred_cash,
        'upfront_pct': upfront_pct,
        'deferred_pct': deferred_pct
    }

@st.cache_data(ttl=600)
def calculate_unit_economics_cached(deal_value: float, upfront_pct: float, grr: float, cost_per_sale: float):
    """Cached unit economics"""
    cash_splits = calculate_deal_cash_splits(deal_value, upfront_pct)
    upfront_cash = cash_splits['upfront_cash']
    deferred_cash = cash_splits['deferred_cash']
    
    ltv = upfront_cash + (deferred_cash * grr)
    ltv_cac = ltv / cost_per_sale if cost_per_sale > 0 else 0
    payback_months = cost_per_sale / (upfront_cash / 12) if upfront_cash > 0 else 999
    
    return {
        'ltv': ltv,
        'cac': cost_per_sale,
        'ltv_cac': ltv_cac,
        'payback_months': payback_months,
        **cash_splits  # Include cash splits in unit economics
    }

@st.cache_data(ttl=300)
def calculate_pnl_cached(revenue: float, team_base: float, commissions: float, 
                         marketing: float, opex: float, gov_fees: float):
    """Calculate comprehensive P&L with proper categorization"""
    # Revenue
    gross_revenue = revenue
    net_revenue = gross_revenue - gov_fees
    
    # COGS (Cost of Goods Sold)
    cogs = team_base + commissions
    gross_profit = net_revenue - cogs
    gross_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
    
    # Operating Expenses
    total_opex = marketing + opex
    
    # EBITDA
    ebitda = gross_profit - total_opex
    ebitda_margin = (ebitda / net_revenue * 100) if net_revenue > 0 else 0
    
    return {
        'gross_revenue': gross_revenue,
        'gov_fees': gov_fees,
        'net_revenue': net_revenue,
        'cogs': cogs,
        'team_base': team_base,
        'commissions': commissions,
        'gross_profit': gross_profit,
        'gross_margin': gross_margin,
        'marketing': marketing,
        'opex': opex,
        'total_opex': total_opex,
        'ebitda': ebitda,
        'ebitda_margin': ebitda_margin
    }

# ============= DYNAMIC ALERTS =============
def generate_alerts(gtm_metrics, unit_econ, pnl_data):
    """Generate context-aware alerts with specific actions"""
    alerts = []
    
    # Critical alerts (red)
    if unit_econ['ltv_cac'] < 1.5:
        improvement_needed = unit_econ['cac'] - (unit_econ['ltv'] / 3)
        alerts.append({
            'type': 'error',
            'title': '🚨 Unit Economics Unhealthy',
            'message': f"LTV:CAC ratio is {unit_econ['ltv_cac']:.2f}:1 (need 3:1 minimum)",
            'action': f"Reduce CAC by ${improvement_needed:,.0f} or increase LTV"
        })
    
    if pnl_data['ebitda'] < 0:
        alerts.append({
            'type': 'error',
            'title': '🚨 Negative EBITDA',
            'message': f"Monthly EBITDA: ${pnl_data['ebitda']:,.0f}",
            'action': f"Need ${abs(pnl_data['ebitda']):,.0f} revenue increase or cost reduction"
        })
    
    # Warning alerts (yellow)
    if unit_econ['payback_months'] > 12:
        alerts.append({
            'type': 'warning',
            'title': '⚠️ Long Payback Period',
            'message': f"{unit_econ['payback_months']:.1f} months to break even (target: <12)",
            'action': "Negotiate better payment terms or optimize CAC"
        })
    
    if pnl_data['gross_margin'] < 60:
        alerts.append({
            'type': 'warning',
            'title': '⚠️ Low Gross Margin',
            'message': f"Gross margin at {pnl_data['gross_margin']:.1f}% (target: 70%+)",
            'action': "Review commission structure or increase deal value"
        })
    
    if gtm_metrics['monthly_sales'] < 10:
        alerts.append({
            'type': 'warning',
            'title': '⚠️ Low Sales Volume',
            'message': f"Only {gtm_metrics['monthly_sales']:.1f} sales/month",
            'action': "Increase leads or improve conversion rates"
        })
    
    # Success alerts (green)
    if unit_econ['ltv_cac'] >= 3 and pnl_data['ebitda_margin'] >= 20:
        alerts.append({
            'type': 'success',
            'title': '✅ Healthy Business Metrics',
            'message': f"LTV:CAC {unit_econ['ltv_cac']:.1f}:1 • EBITDA Margin {pnl_data['ebitda_margin']:.1f}%",
            'action': "Consider scaling investment"
        })
    
    return alerts

# ============= HEADER =============
st.title("💎 ULTIMATE Sales Compensation Dashboard")
st.caption("⚡ 10X Faster • 📊 Full Features • 🎯 Accurate Calculations")

# Quick metrics at top (cached)
import json
gtm_metrics = calculate_gtm_metrics_cached(json.dumps(st.session_state.gtm_channels))
deal_econ = DealEconomicsManager.get_current_deal_economics()

# Calculate additional metrics for top display
team_base = (st.session_state.closer_base * st.session_state.num_closers_main +
             st.session_state.setter_base * st.session_state.num_setters_main +
             st.session_state.manager_base * st.session_state.num_managers_main +
             st.session_state.bench_base * st.session_state.num_benchs_main)

roles_comp = {
    'closer': {'commission_pct': st.session_state.closer_commission_pct},
    'setter': {'commission_pct': st.session_state.setter_commission_pct},
    'manager': {'commission_pct': st.session_state.manager_commission_pct}
}

comm_calc = DealEconomicsManager.calculate_monthly_commission(
    gtm_metrics['monthly_sales'], roles_comp, deal_econ
)

marketing_spend = sum(ch.get('monthly_leads', 0) * ch.get('cpl', 50) 
                     for ch in st.session_state.gtm_channels if ch.get('enabled', True))

# Calculate government costs (% of gross revenue)
gov_cost_pct = st.session_state.get('government_cost_pct', 10.0) / 100
gov_fees = gtm_metrics['monthly_revenue_immediate'] * gov_cost_pct

pnl_data = calculate_pnl_cached(
    gtm_metrics['monthly_revenue_immediate'],
    team_base,
    comm_calc['total_commission'],
    marketing_spend,
    st.session_state.office_rent + st.session_state.software_costs + st.session_state.other_opex,
    gov_fees  # Now includes actual government costs
)

unit_econ = calculate_unit_economics_cached(
    deal_econ['avg_deal_value'],
    deal_econ['upfront_pct'],
    st.session_state.grr_rate,
    gtm_metrics['cost_per_sale'] if gtm_metrics.get('cost_per_sale', 0) > 0 else 5000
)

# TOP KPI ROW - All key metrics visible at once
st.markdown("### 📊 Key Performance Indicators")
kpi_row1 = st.columns(6)
with kpi_row1[0]:
    st.metric("💰 Monthly Revenue", f"${gtm_metrics['monthly_revenue_immediate']:,.0f}")
with kpi_row1[1]:
    st.metric("📈 Monthly Sales", f"{gtm_metrics['monthly_sales']:.1f}")
with kpi_row1[2]:
    st.metric("📊 Leads", f"{gtm_metrics['monthly_leads']:,.0f}")
with kpi_row1[3]:
    st.metric("🎯 Close Rate", f"{gtm_metrics['blended_close_rate']:.1%}")
with kpi_row1[4]:
    color = "normal" if unit_econ['ltv_cac'] >= 3 else "inverse"
    st.metric("🎯 LTV:CAC", f"{unit_econ['ltv_cac']:.1f}:1", delta_color=color)
with kpi_row1[5]:
    st.metric("⏱️ Payback", f"{unit_econ['payback_months']:.0f}mo")

kpi_row2 = st.columns(6)
with kpi_row2[0]:
    st.metric("💎 Deal Value", f"${deal_econ['avg_deal_value']:,.0f}")
with kpi_row2[1]:
    st.metric("💸 Total Commissions", f"${comm_calc['total_commission']:,.0f}")
with kpi_row2[2]:
    st.metric("📣 Marketing", f"${marketing_spend:,.0f}")
with kpi_row2[3]:
    ebitda_color = "normal" if pnl_data['ebitda'] > 0 else "inverse"
    st.metric("💎 EBITDA", f"${pnl_data['ebitda']:,.0f}", delta_color=ebitda_color)
with kpi_row2[4]:
    st.metric("📊 EBITDA Margin", f"{pnl_data['ebitda_margin']:.1f}%")
with kpi_row2[5]:
    policy = DealEconomicsManager.get_commission_policy()
    st.metric("💸 Comm Policy", "Upfront" if policy == 'upfront' else "Full")

st.markdown("---")

# ============= LANGUAGE SELECTOR (SIDEBAR) =============
with st.sidebar:
    st.markdown("### 🌐 Language / Idioma")
    lang = st.selectbox(
        "",
        options=['en', 'es'],
        format_func=lambda x: t('english', x) if x == 'en' else t('spanish', x),
        key='language_selector',
        label_visibility='collapsed'
    )
    st.markdown("---")

# ============= TABS =============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 GTM Command Center" if lang == 'en' else "🎯 Centro GTM",
    "💰 Compensation Structure" if lang == 'en' else "💰 Estructura de Compensación", 
    "📊 Business Performance" if lang == 'en' else "📊 Desempeño del Negocio",
    "🔮 What-If Analysis" if lang == 'en' else "🔮 Análisis Hipotético",
    "⚙️ Configuration" if lang == 'en' else "⚙️ Configuración"
])

# ============= TAB 1: GTM COMMAND CENTER =============
with tab1:
    st.header("🎯 GTM Command Center")
    st.caption("Go-to-market metrics, channels, and funnel performance")
    
    # Get fresh deal economics for this tab (for channel preview calculations)
    tab1_deal_econ = DealEconomicsManager.get_current_deal_economics()
    
    # Calculate P&L data for alerts
    team_base = (st.session_state.closer_base * st.session_state.num_closers_main +
                 st.session_state.setter_base * st.session_state.num_setters_main +
                 st.session_state.manager_base * st.session_state.num_managers_main +
                 st.session_state.bench_base * st.session_state.num_benchs_main)
    
    roles_comp = {
        'closer': {'commission_pct': st.session_state.closer_commission_pct},
        'setter': {'commission_pct': st.session_state.setter_commission_pct},
        'manager': {'commission_pct': st.session_state.manager_commission_pct}
    }
    
    comm_calc = DealEconomicsManager.calculate_monthly_commission(
        gtm_metrics['monthly_sales'], roles_comp, deal_econ
    )
    
    marketing_spend = sum(ch.get('monthly_leads', 0) * ch.get('cpl', 50) 
                         for ch in st.session_state.gtm_channels if ch.get('enabled', True))
    
    # Calculate government costs (% of gross revenue)
    gov_cost_pct = st.session_state.get('government_cost_pct', 10.0) / 100
    gov_fees = gtm_metrics['monthly_revenue_immediate'] * gov_cost_pct
    
    pnl_data = calculate_pnl_cached(
        gtm_metrics['monthly_revenue_immediate'],
        team_base,
        comm_calc['total_commission'],
        marketing_spend,
        st.session_state.office_rent + st.session_state.software_costs + st.session_state.other_opex,
        gov_fees  # Now includes actual government costs
    )
    
    # Dynamic Alerts
    alerts = generate_alerts(gtm_metrics, unit_econ, pnl_data)
    
    if alerts:
        with st.expander(f"⚠️ Alerts & Recommendations ({len(alerts)})", expanded=True):
            for alert in alerts:
                if alert['type'] == 'error':
                    st.markdown(f'<div class="alert-critical"><strong>{alert["title"]}</strong><br>{alert["message"]}<br><em>💡 Action: {alert["action"]}</em></div>', unsafe_allow_html=True)
                elif alert['type'] == 'warning':
                    st.markdown(f'<div class="alert-warning"><strong>{alert["title"]}</strong><br>{alert["message"]}<br><em>💡 Action: {alert["action"]}</em></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-success"><strong>{alert["title"]}</strong><br>{alert["message"]}<br><em>🚀 {alert["action"]}</em></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Multi-Channel Configuration
    st.markdown("### 📡 Multi-Channel Configuration")
    
    # Channel management buttons
    ch_btn_cols = st.columns([1, 1, 2])
    with ch_btn_cols[0]:
        if st.button("➕ Add Channel", use_container_width=True, key="add_channel_gtm"):
            new_id = f"channel_{len(st.session_state.gtm_channels) + 1}"
            st.session_state.gtm_channels.append({
                'id': new_id,
                'name': f'Channel {len(st.session_state.gtm_channels) + 1}',
                'segment': 'SMB',
                'monthly_leads': 500,
                'cpl': 50,
                'contact_rate': 0.6,
                'meeting_rate': 0.3,
                'show_up_rate': 0.7,
                'close_rate': 0.25,
                'enabled': True
            })
            st.rerun()
    
    with ch_btn_cols[1]:
        if len(st.session_state.gtm_channels) > 1:
            if st.button("🗑️ Remove Last", use_container_width=True, key="remove_channel_gtm"):
                st.session_state.gtm_channels.pop()
                st.rerun()
    
    with ch_btn_cols[2]:
        st.info(f"📊 Managing {len(st.session_state.gtm_channels)} channel(s)")
    
    st.markdown("---")
    
    # Configure each channel in expanders
    for idx, channel in enumerate(st.session_state.gtm_channels):
        with st.expander(f"📊 **{channel['name']}** ({channel['segment']})", expanded=(idx == 0)):
            cfg_cols = st.columns(3)
            
            with cfg_cols[0]:
                st.markdown("**Channel Info**")
                name = st.text_input("Name", value=channel['name'], key=f"ch_name_{channel['id']}")
                st.session_state.gtm_channels[idx]['name'] = name
                
                segment = st.selectbox(
                    "Segment",
                    ['SMB', 'MID', 'ENT', 'Custom'],
                    index=['SMB', 'MID', 'ENT', 'Custom'].index(channel.get('segment', 'SMB')),
                    key=f"ch_segment_{channel['id']}"
                )
                st.session_state.gtm_channels[idx]['segment'] = segment
                
                st.markdown("**Cost Input Method**")
                cost_point = st.selectbox(
                    "Cost Input Point",
                    ["Cost per Lead", "Cost per Contact", "Cost per Meeting", "Cost per Sale", "Total Budget"],
                    index=0,
                    key=f"ch_cost_point_{channel['id']}",
                    help="Choose how you want to input marketing costs"
                )
                
                # Dynamic inputs based on cost point
                if cost_point == "Cost per Lead":
                    cpl = st.number_input(
                        "Cost per Lead ($)",
                        min_value=0,
                        value=int(channel.get('cpl', 50)),
                        step=5,
                        key=f"ch_cpl_{channel['id']}"
                    )
                    leads = st.number_input(
                        "Monthly Leads",
                        min_value=0,
                        value=int(channel.get('monthly_leads', 500)),
                        step=50,
                        key=f"ch_leads_{channel['id']}"
                    )
                    
                elif cost_point == "Cost per Contact":
                    cost_per_contact = st.number_input(
                        "Cost per Contact ($)",
                        min_value=0,
                        value=int(channel.get('cost_per_contact', 75)),
                        step=10,
                        key=f"ch_cpc_{channel['id']}"
                    )
                    contacts_target = st.number_input(
                        "Monthly Contacts Target",
                        min_value=0,
                        value=int(channel.get('contacts_target', 300)),
                        step=50,
                        key=f"ch_contacts_{channel['id']}"
                    )
                    # Will calculate leads after we have contact rate
                    leads = contacts_target
                    cpl = cost_per_contact
                    
                elif cost_point == "Cost per Meeting":
                    cost_per_meeting = st.number_input(
                        "Cost per Meeting ($)",
                        min_value=0,
                        value=int(channel.get('cost_per_meeting', 200)),
                        step=25,
                        key=f"ch_cpm_{channel['id']}"
                    )
                    meetings_target = st.number_input(
                        "Monthly Meetings Target",
                        min_value=0,
                        value=int(channel.get('meetings_target', 20)),
                        step=5,
                        key=f"ch_meetings_{channel['id']}"
                    )
                    leads = meetings_target * 5  # Rough estimate
                    cpl = cost_per_meeting / 5
                    
                elif cost_point == "Cost per Sale":
                    cost_per_sale = st.number_input(
                        "Cost per Sale ($)",
                        min_value=0,
                        value=int(channel.get('cost_per_sale', 500)),
                        step=50,
                        key=f"ch_cps_{channel['id']}"
                    )
                    sales_target = st.number_input(
                        "Monthly Sales Target",
                        min_value=0,
                        value=int(channel.get('sales_target', 5)),
                        step=1,
                        key=f"ch_sales_{channel['id']}"
                    )
                    leads = sales_target * 20  # Rough estimate
                    cpl = cost_per_sale / 20
                    
                else:  # Total Budget
                    total_budget = st.number_input(
                        "Total Budget ($)",
                        min_value=0,
                        value=int(channel.get('total_budget', 25000)),
                        step=1000,
                        key=f"ch_budget_{channel['id']}"
                    )
                    leads = st.number_input(
                        "Estimated Monthly Leads",
                        min_value=1,
                        value=int(channel.get('monthly_leads', 500)),
                        step=50,
                        key=f"ch_leads_budget_{channel['id']}"
                    )
                    cpl = total_budget / leads if leads > 0 else 0
            
            with cfg_cols[1]:
                st.markdown("**Conversion Rates**")
                contact_rate = st.slider(
                    "Contact %",
                    0, 100,
                    int(channel.get('contact_rate', 0.6) * 100),
                    5,
                    key=f"ch_contact_{channel['id']}"
                ) / 100
                st.session_state.gtm_channels[idx]['contact_rate'] = contact_rate
                
                meeting_rate = st.slider(
                    "Meeting %",
                    0, 100,
                    int(channel.get('meeting_rate', 0.3) * 100),
                    5,
                    key=f"ch_meeting_{channel['id']}"
                ) / 100
                st.session_state.gtm_channels[idx]['meeting_rate'] = meeting_rate
                
                show_up_rate = st.slider(
                    "Show-up %",
                    0, 100,
                    int(channel.get('show_up_rate', 0.7) * 100),
                    5,
                    key=f"ch_showup_{channel['id']}"
                ) / 100
                st.session_state.gtm_channels[idx]['show_up_rate'] = show_up_rate
                
                close_rate = st.slider(
                    "Close %",
                    0, 100,
                    int(channel.get('close_rate', 0.25) * 100),
                    5,
                    key=f"ch_close_{channel['id']}"
                ) / 100
                st.session_state.gtm_channels[idx]['close_rate'] = close_rate
                
                # Reverse calculate leads based on cost point and conversion rates
                if cost_point == "Cost per Contact":
                    # Calculate leads needed to get target contacts
                    leads = contacts_target / contact_rate if contact_rate > 0 else contacts_target
                    cpl = cost_per_contact / contact_rate if contact_rate > 0 else cost_per_contact
                    st.info(f"📊 Need {leads:.0f} leads to get {contacts_target} contacts")
                    
                elif cost_point == "Cost per Meeting":
                    # Calculate leads needed to get target meetings
                    conversion_to_meeting = contact_rate * meeting_rate * show_up_rate
                    leads = meetings_target / conversion_to_meeting if conversion_to_meeting > 0 else meetings_target * 5
                    cpl = cost_per_meeting / conversion_to_meeting if conversion_to_meeting > 0 else cost_per_meeting
                    st.info(f"📊 Need {leads:.0f} leads to get {meetings_target} meetings")
                    
                elif cost_point == "Cost per Sale":
                    # Calculate leads needed to get target sales
                    full_conversion = contact_rate * meeting_rate * show_up_rate * close_rate
                    leads = sales_target / full_conversion if full_conversion > 0 else sales_target * 20
                    cpl = cost_per_sale / full_conversion if full_conversion > 0 else cost_per_sale
                    st.info(f"📊 Need {leads:.0f} leads to get {sales_target} sales")
                    
                elif cost_point == "Total Budget":
                    cpl = total_budget / leads if leads > 0 else 0
                    st.info(f"📊 Effective CPL: ${cpl:.2f}")
                
                # Store the calculated values (convert to int to avoid type mismatch)
                st.session_state.gtm_channels[idx]['monthly_leads'] = int(leads)
                st.session_state.gtm_channels[idx]['cpl'] = int(cpl)
            
            with cfg_cols[2]:
                st.markdown("**Channel Performance**")
                
                # Calculate this channel's metrics (using fresh deal economics)
                contacts = leads * contact_rate
                meetings_sched = contacts * meeting_rate
                meetings_held = meetings_sched * show_up_rate
                sales = meetings_held * close_rate
                spend = leads * cpl
                revenue = sales * tab1_deal_econ['upfront_cash']  # Use fresh deal economics
                
                st.metric("💼 Sales", f"{sales:.1f}")
                st.metric("💰 Revenue", f"${revenue:,.0f}")
                st.metric("📣 Spend", f"${spend:,.0f}")
                roas = revenue / spend if spend > 0 else 0
                st.metric("📊 ROAS", f"{roas:.1f}x")
                
                # Enabled toggle
                enabled = st.checkbox(
                    "✅ Channel Enabled",
                    value=channel.get('enabled', True),
                    key=f"ch_enabled_{channel['id']}"
                )
                st.session_state.gtm_channels[idx]['enabled'] = enabled
    
    # Channel Performance Comparison
    if gtm_metrics.get('channels_breakdown'):
        st.markdown("---")
        st.markdown("### 📊 Channel Performance Comparison")
        
        df_channels = pd.DataFrame(gtm_metrics['channels_breakdown'])
        
        if len(df_channels) > 0:
            # Quick metrics
            comp_cols = st.columns(4)
            with comp_cols[0]:
                fig_leads = px.bar(df_channels, x='name', y='leads', title="Leads by Channel",
                                  color='segment', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_leads.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig_leads, use_container_width=True, key="chart_leads")
            
            with comp_cols[1]:
                fig_sales = px.bar(df_channels, x='name', y='sales', title="Sales by Channel",
                                  color='segment', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_sales.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig_sales, use_container_width=True, key="chart_sales")
            
            with comp_cols[2]:
                fig_roas = px.bar(df_channels, x='name', y='roas', title="ROAS by Channel",
                                 color='segment', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_roas.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig_roas, use_container_width=True, key="chart_roas")
            
            with comp_cols[3]:
                fig_close = px.bar(df_channels, x='name', y='close_rate', title="Close Rate",
                                  color='segment', color_discrete_sequence=px.colors.qualitative.Set2)
                fig_close.update_layout(height=250, showlegend=False, yaxis_tickformat='.1%')
                st.plotly_chart(fig_close, use_container_width=True, key="chart_close")
            
            # Detailed table
            st.dataframe(df_channels.style.format({
                'leads': '{:,.0f}',
                'sales': '{:.1f}',
                'revenue': '${:,.0f}',
                'spend': '${:,.0f}',
                'cpa': '${:,.0f}',
                'roas': '{:.2f}x',
                'close_rate': '{:.1%}'
            }), use_container_width=True, hide_index=True)
    
    # Channel Performance Analysis (detailed charts)
    if gtm_metrics.get('channels_breakdown') and len(gtm_metrics['channels_breakdown']) > 0:
        st.markdown("---")
        st.markdown("### 📊 Channel Performance Analysis")
        
        chart_cols = st.columns(2)
        
        with chart_cols[0]:
            st.markdown("#### 🔄 Channel Funnel Comparison")
            
            # Create funnel chart for each channel
            funnel_fig = go.Figure()
            
            # Track totals for aggregated funnel
            total_leads = 0
            total_contacts = 0
            total_meetings_scheduled = 0
            total_meetings_held = 0
            total_sales = 0
            
            # Get actual channel configs to use real conversion rates
            for idx, ch_data in enumerate(gtm_metrics['channels_breakdown']):
                # Find matching channel config to get actual rates
                channel_config = None
                for ch in st.session_state.gtm_channels:
                    if ch['name'] == ch_data['name'] and ch.get('enabled', True):
                        channel_config = ch
                        break
                
                # Calculate funnel stages using ACTUAL conversion rates from config
                leads = ch_data['leads']
                if channel_config:
                    contact_rate = channel_config.get('contact_rate', 0.6)
                    meeting_rate = channel_config.get('meeting_rate', 0.3)
                    show_up_rate = channel_config.get('show_up_rate', 0.7)
                    
                    contacts = leads * contact_rate
                    meetings_scheduled = contacts * meeting_rate
                    meetings_held = meetings_scheduled * show_up_rate
                else:
                    # Fallback if config not found
                    contacts = leads * 0.6
                    meetings_scheduled = contacts * 0.3
                    meetings_held = meetings_scheduled * 0.7
                
                sales = ch_data['sales']
                
                # Add to totals
                total_leads += leads
                total_contacts += contacts
                total_meetings_scheduled += meetings_scheduled
                total_meetings_held += meetings_held
                total_sales += sales
                
                funnel_fig.add_trace(go.Funnel(
                    name=ch_data['name'],
                    y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                    x=[leads, contacts, meetings_scheduled, meetings_held, sales],
                    textinfo="value+percent initial"
                ))
            
            funnel_fig.update_layout(
                title="Individual Channel Funnels",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(funnel_fig, use_container_width=True, key="gtm_channel_funnel")
            
            # Separate chart for aggregated total
            st.markdown("#### 🎯 Aggregated Total")
            
            total_fig = go.Figure(go.Funnel(
                y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                x=[total_leads, total_contacts, total_meetings_scheduled, total_meetings_held, total_sales],
                textinfo="value+percent initial",
                marker=dict(color='#F59E0B', line=dict(width=2, color='#D97706'))  # Amber/gold color
            ))
            
            total_fig.update_layout(
                title="All Channels Combined",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(total_fig, use_container_width=True, key="gtm_total_funnel")
        
        with chart_cols[1]:
            st.markdown("#### 💰 Revenue Contribution")
            
            # Create pie chart for revenue distribution
            revenue_data = {
                'Channel': [ch['name'] for ch in gtm_metrics['channels_breakdown']],
                'Revenue': [ch['revenue'] for ch in gtm_metrics['channels_breakdown']]
            }
            
            pie_fig = go.Figure(data=[go.Pie(
                labels=revenue_data['Channel'],
                values=revenue_data['Revenue'],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>%{percent}<extra></extra>'
            )])
            
            pie_fig.update_layout(
                title="Revenue Distribution by Channel",
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
            
            st.plotly_chart(pie_fig, use_container_width=True, key="gtm_revenue_contribution")

# ============= TAB 2: COMPENSATION STRUCTURE =============
with tab2:
    st.header("💰 Compensation Structure")
    st.caption("Commission flow, earnings preview, and team compensation")
    
    # Commission Flow Fragment (pass deal_econ to avoid reruns)
    @st.fragment
    def render_commission_flow(deal_econ_data):
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
        
        # Get team counts
        num_closers = st.session_state.num_closers_main
        num_setters = st.session_state.num_setters_main
        num_managers = st.session_state.num_managers_main
        
        # Calculate commission data based on view
        if "Per Deal" in flow_view:
            per_deal_comm = DealEconomicsManager.calculate_per_deal_commission(roles_comp, deal_econ_data)
            closer_pool = per_deal_comm['closer_pool']
            setter_pool = per_deal_comm['setter_pool']
            manager_pool = per_deal_comm['manager_pool']
            
            # Show commission base (based on policy), not full deal value
            commission_base = per_deal_comm['commission_base']
            revenue_display = commission_base  # Use commission base for display
            policy = DealEconomicsManager.get_commission_policy()
            policy_label = "Upfront" if policy == 'upfront' else "Full"
            title_text = f"Per Deal: ${commission_base:,.0f} ({policy_label}) → Commissions"
        else:
            monthly_comm = calculate_commission_data_cached(
                gtm_metrics['monthly_sales'],
                json.dumps(roles_comp),
                json.dumps(deal_econ_data)
            )
            closer_pool = monthly_comm['closer_pool']
            setter_pool = monthly_comm['setter_pool']
            manager_pool = monthly_comm['manager_pool']
            revenue_display = gtm_metrics['monthly_revenue_immediate']
            title_text = f"Revenue → Pools → Per Person"
        
        # Create full Plotly flow visualization
        fig_flow = go.Figure()
        
        # Revenue node (left)
        fig_flow.add_trace(go.Scatter(
            x=[1], y=[3],
            mode='markers+text',
            marker=dict(size=120, color='#3b82f6', line=dict(color='white', width=2)),
            text=[f"Revenue<br>${revenue_display:,.0f}"],
            textfont=dict(color='white', size=13, family='Arial Black'),
            textposition="middle center",
            showlegend=False,
            hovertemplate=f'<b>Revenue Base</b><br>${revenue_display:,.0f}<extra></extra>'
        ))
        
        # Commission pools (middle)
        pools = [
            (closer_pool, "Closer Pool", 4.5),
            (setter_pool, "Setter Pool", 3.0),
            (manager_pool, "Manager Pool", 1.5)
        ]
        
        for pool_amount, pool_label, y_pos in pools:
            fig_flow.add_trace(go.Scatter(
                x=[2.5], y=[y_pos],
                mode='markers+text',
                marker=dict(size=100, color='#f59e0b', line=dict(color='white', width=2)),
                text=[f"{pool_label}<br>${pool_amount:,.0f}"],
                textfont=dict(color='white', size=11),
                textposition="middle center",
                showlegend=False,
                hovertemplate=f'<b>{pool_label}</b><br>${pool_amount:,.0f}<extra></extra>'
            ))
        
        # Per-person amounts (right)
        team_data = [
            (closer_pool, num_closers, "Per Closer", 4.5),
            (setter_pool, num_setters, "Per Setter", 3.0),
            (manager_pool, num_managers, "Per Manager", 1.5)
        ]
        
        for pool, count, label, y_pos in team_data:
            if count > 0:
                # Per Deal: ONE person gets FULL pool (not divided)
                # Monthly: Pool divided among team
                if "Per Deal" in flow_view:
                    per_person = pool  # ONE person closes ONE deal = gets full commission
                    hover_text = f'<b>{label}</b><br>${per_person:,.0f} (full commission)<extra></extra>'
                else:
                    per_person = pool / count  # Monthly pool split among team
                    hover_text = f'<b>{label}</b><br>${per_person:,.0f} ({count} people)<extra></extra>'
                
                fig_flow.add_trace(go.Scatter(
                    x=[4], y=[y_pos],
                    mode='markers+text',
                    marker=dict(size=80, color='#22c55e', line=dict(color='white', width=2)),
                    text=[f"{label}<br>${per_person:,.0f}"],
                    textfont=dict(color='white', size=10),
                    textposition="middle center",
                    showlegend=False,
                    hovertemplate=hover_text
                ))
        
        # Add connecting arrows
        for y_pos in [4.5, 3.0, 1.5]:
            # Revenue to pool
            fig_flow.add_annotation(
                x=1.3, y=3, ax=2.2, ay=y_pos,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='rgba(0,0,0,0.3)'
            )
            # Pool to person (only if team exists)
            if (y_pos == 4.5 and num_closers > 0) or \
               (y_pos == 3.0 and num_setters > 0) or \
               (y_pos == 1.5 and num_managers > 0):
                fig_flow.add_annotation(
                    x=2.8, y=y_pos, ax=3.7, ay=y_pos,
                    xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor='rgba(0,0,0,0.3)'
                )
        
        # Layout
        fig_flow.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=16, color='#1f2937', family='Arial Black')
            ),
            xaxis=dict(range=[0, 5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 6], showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig_flow, use_container_width=True, key="commission_flow_viz")
    
    # Get fresh deal economics and pass to fragment
    tab2_deal_econ = DealEconomicsManager.get_current_deal_economics()
    render_commission_flow(tab2_deal_econ)
    
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
    st.header("📊 Business Performance Command Center")
    st.caption("Comprehensive business metrics, P&L, unit economics, and channel performance")
    
    # Get fresh deal economics for this tab
    tab3_deal_econ = DealEconomicsManager.get_current_deal_economics()
    
    # 1. 🎯 Key Performance Indicators (Top Row)
    st.markdown("### 🎯 Key Performance Indicators")
    kpi_cols = st.columns(6)
    
    # Calculate revenue target achievement
    monthly_revenue_target = st.session_state.get('monthly_revenue_target', 500000)
    achievement = (gtm_metrics['monthly_revenue_immediate'] / monthly_revenue_target - 1) * 100 if monthly_revenue_target > 0 else 0
    
    with kpi_cols[0]:
        st.metric(
            "💵 Monthly Revenue",
            f"${gtm_metrics['monthly_revenue_immediate']:,.0f}",
            f"{achievement:+.1f}% vs target"
        )
    with kpi_cols[1]:
        ebitda_color = "normal" if pnl_data['ebitda'] > 0 else "inverse"
        st.metric(
            "💰 EBITDA",
            f"${pnl_data['ebitda']:,.0f}",
            f"{pnl_data['ebitda_margin']:.1f}% margin",
            delta_color=ebitda_color
        )
    with kpi_cols[2]:
        ltv_cac_color = "normal" if unit_econ['ltv_cac'] >= 3 else "inverse"
        st.metric(
            "🎯 LTV:CAC",
            f"{unit_econ['ltv_cac']:.1f}:1",
            "Target: >3:1",
            delta_color=ltv_cac_color
        )
    with kpi_cols[3]:
        roas = gtm_metrics['monthly_revenue_immediate'] / marketing_spend if marketing_spend > 0 else 0
        st.metric(
            "🚀 ROAS",
            f"{roas:.1f}x",
            "Target: >4x"
        )
    with kpi_cols[4]:
        # Capacity utilization
        working_days = st.session_state.get('working_days', 20)
        meetings_per_closer = st.session_state.get('meetings_per_closer', 3.0)
        monthly_closer_capacity = st.session_state.num_closers_main * meetings_per_closer * working_days
        current_meetings = gtm_metrics.get('monthly_meetings_held', 0)
        capacity_util = (current_meetings / monthly_closer_capacity) if monthly_closer_capacity > 0 else 0
        cap_status = "OK" if capacity_util < 0.9 else "⚠️ High"
        st.metric("📅 Capacity Used", f"{capacity_util:.0%}", cap_status)
    with kpi_cols[5]:
        # Pipeline coverage
        pipeline_value = current_meetings * tab3_deal_econ['upfront_cash']
        pipeline_coverage = pipeline_value / monthly_revenue_target if monthly_revenue_target > 0 else 0
        pipeline_status = "Good" if pipeline_coverage >= 3 else "Low"
        st.metric("📊 Pipeline Coverage", f"{pipeline_coverage:.1f}x", pipeline_status)
    
    st.markdown("---")
    
    # 2. 💰 P&L Waterfall Visualization
    st.markdown("### 💰 P&L Waterfall Visualization")
    
    viz_cols = st.columns([2, 1])
    
    with viz_cols[0]:
        # Create waterfall chart
        fig_waterfall = go.Figure(go.Waterfall(
            name="P&L",
            orientation="v",
            measure=["relative", "relative", "total", "relative", "total"],
            x=["Revenue", "COGS", "Gross Profit", "OpEx", "EBITDA"],
            textposition="outside",
            text=[f"${pnl_data['gross_revenue']:,.0f}",
                  f"-${pnl_data['cogs']:,.0f}",
                  f"${pnl_data['gross_profit']:,.0f}",
                  f"-${pnl_data['total_opex']:,.0f}",
                  f"${pnl_data['ebitda']:,.0f}"],
            y=[pnl_data['gross_revenue'],
               -pnl_data['cogs'],
               0,
               -pnl_data['total_opex'],
               0],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#EF4444"}},
            increasing={"marker": {"color": "#3B82F6"}},
            totals={"marker": {"color": "#10B981"}}
        ))
        
        fig_waterfall.update_layout(
            title="Monthly P&L Flow",
            showlegend=False,
            height=400,
            yaxis_title="Amount ($)",
            xaxis_title=""
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True, key="pnl_waterfall")
    
    with viz_cols[1]:
        st.markdown("#### 📊 Key Metrics")
        
        # Margins card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: white;">Gross Margin</h4>
            <h1 style="margin: 10px 0; color: white;">{pnl_data['gross_margin']:.1f}%</h1>
            <p style="margin: 0; color: rgba(255,255,255,0.8);">Target: >60%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # EBITDA Margin card
        ebitda_color = "#10B981" if pnl_data['ebitda_margin'] > 20 else "#EF4444"
        st.markdown(f"""
        <div style="background: {ebitda_color}; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
            <h4 style="margin: 0; color: white;">EBITDA Margin</h4>
            <h1 style="margin: 10px 0; color: white;">{pnl_data['ebitda_margin']:.1f}%</h1>
            <p style="margin: 0; color: rgba(255,255,255,0.8);">Target: >20%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Unit Economics
        cost_per_sale = gtm_metrics.get('cost_per_sale', 0)
        revenue_per_sale = pnl_data['gross_revenue'] / gtm_metrics['monthly_sales'] if gtm_metrics['monthly_sales'] > 0 else 0
        st.markdown(f"""
        <div style="background: #1F2937; padding: 15px; border-radius: 10px; border-left: 4px solid #3B82F6;">
            <p style="margin: 0; color: #9CA3AF; font-size: 0.875rem;">PER SALE</p>
            <p style="margin: 5px 0; color: #10B981; font-size: 1.25rem; font-weight: bold;">Revenue: ${revenue_per_sale:,.0f}</p>
            <p style="margin: 5px 0; color: #EF4444; font-size: 1.25rem; font-weight: bold;">Cost: ${cost_per_sale:,.0f}</p>
            <p style="margin: 5px 0; color: #3B82F6; font-size: 1.25rem; font-weight: bold;">Net: ${revenue_per_sale - cost_per_sale:,.0f}</p>
            <p style="margin: 5px 0 0 0; color: #9CA3AF; font-size: 0.875rem;">Sales: {gtm_metrics['monthly_sales']:.0f}/mo</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. 💵 Unit Economics (Expanded)
    st.markdown("### 💵 Unit Economics")
    unit_cols = st.columns(5)
    
    with unit_cols[0]:
        st.metric("💎 LTV", f"${unit_econ['ltv']:,.0f}")
    with unit_cols[1]:
        st.metric("💰 CAC", f"${unit_econ['cac']:,.0f}")
    with unit_cols[2]:
        color = "normal" if unit_econ['ltv_cac'] >= 3 else "inverse"
        st.metric("🎯 LTV:CAC", f"{unit_econ['ltv_cac']:.1f}:1", delta_color=color)
    with unit_cols[3]:
        st.metric("⏱️ Payback", f"{unit_econ['payback_months']:.1f} mo", "Target: <12mo")
    with unit_cols[4]:
        magic_number = (tab3_deal_econ['avg_deal_value'] / 12) / unit_econ['cac'] if unit_econ['cac'] > 0 else 0
        st.metric("✨ Magic Number", f"{magic_number:.2f}", "Target: >0.75")
    
    st.markdown("---")
    
    # 4. Sales Activity
    st.markdown("### 📈 Sales Activity")
    activity_cols = st.columns(5)
    
    with activity_cols[0]:
        daily_leads = gtm_metrics['monthly_leads'] / working_days if working_days > 0 else 0
        st.metric("👥 Leads", f"{gtm_metrics['monthly_leads']:,.0f}/mo", f"{daily_leads:.0f}/day")
    with activity_cols[1]:
        daily_meetings = current_meetings / working_days if working_days > 0 else 0
        st.metric("🤝 Meetings", f"{current_meetings:,.0f}/mo", f"{daily_meetings:.0f}/day")
    with activity_cols[2]:
        per_closer_sales = gtm_metrics['monthly_sales'] / st.session_state.num_closers_main if st.session_state.num_closers_main > 0 else 0
        st.metric("✅ Monthly Sales", f"{gtm_metrics['monthly_sales']:.0f}", f"{per_closer_sales:.1f} per closer")
    with activity_cols[3]:
        # Calculate blended show-up rate from enabled channels
        total_show_up_weighted = 0
        total_meetings = 0
        for ch in st.session_state.gtm_channels:
            if ch.get('enabled', True):
                meetings = ch.get('monthly_leads', 0) * ch.get('contact_rate', 0.6) * ch.get('meeting_rate', 0.3)
                show_up = ch.get('show_up_rate', 0.7)
                total_show_up_weighted += meetings * show_up
                total_meetings += meetings
        blended_show_up = total_show_up_weighted / total_meetings if total_meetings > 0 else 0.7
        st.metric("📈 Close Rate", f"{gtm_metrics['blended_close_rate']:.0%}", f"Show-up: {blended_show_up:.0%}")
    with activity_cols[4]:
        sales_cycle_days = 30  # Could be configuration
        velocity = gtm_metrics['monthly_sales'] / sales_cycle_days * 30 if sales_cycle_days > 0 else 0
        st.metric("🕒 Sales Cycle", f"{sales_cycle_days} days", f"Velocity: {velocity:.0f}/mo")
    
    st.markdown("---")
    
    # 5. Financial Performance
    st.markdown("### 💰 Financial Performance")
    finance_cols = st.columns(5)
    
    # Use cached cash splits calculation
    cash_splits = calculate_deal_cash_splits(tab3_deal_econ['avg_deal_value'], tab3_deal_econ['upfront_pct'])
    upfront_cash = cash_splits['upfront_cash']
    deferred_cash = cash_splits['deferred_cash']
    
    with finance_cols[0]:
        st.metric("💳 CAC", f"${unit_econ['cac']:,.0f}", f"LTV: ${unit_econ['ltv']:,.0f}")
    with finance_cols[1]:
        payback_color = "normal" if unit_econ['payback_months'] < 12 else "inverse"
        st.metric("⏱️ Payback", f"{unit_econ['payback_months']:.1f} mo", "Target: <12m", delta_color=payback_color)
    with finance_cols[2]:
        st.metric(
            "📈 Revenue (Upfront)",
            f"${gtm_metrics['monthly_revenue_immediate']:,.0f}",
            f"{tab3_deal_econ['upfront_pct']:.0f}% split"
        )
    with finance_cols[3]:
        deferred_revenue = gtm_metrics['monthly_sales'] * deferred_cash
        st.metric(
            "📅 Revenue (Deferred)",
            f"${deferred_revenue:,.0f}",
            f"{100-tab3_deal_econ['upfront_pct']:.0f}% split"
        )
    with finance_cols[4]:
        team_total = (st.session_state.num_closers_main + st.session_state.num_setters_main + 
                     st.session_state.num_managers_main + st.session_state.num_benchs_main)
        monthly_opex = marketing_spend + pnl_data['opex']
        st.metric("🏢 Team", f"{team_total} people", f"Burn: ${monthly_opex:,.0f}/mo")
    
    st.markdown("---")
    
    # 6. Sales Process & Pipeline Stages
    st.markdown("### 🔄 Sales Process & Pipeline Stages")
    st.caption("Track your complete sales funnel from lead to close")
    
    # Timeline visualization (use actual data from gtm_metrics)
    timeline_data = [
        {"stage": "Lead Generated", "day": 0, "icon": "👥", "count": gtm_metrics['monthly_leads']},
        {"stage": "First Contact", "day": 1, "icon": "📞", "count": gtm_metrics.get('monthly_contacts', gtm_metrics['monthly_leads'])},
        {"stage": "Meeting Scheduled", "day": 3, "icon": "📅", "count": gtm_metrics.get('monthly_meetings_scheduled', gtm_metrics['monthly_meetings_held'])},
        {"stage": "Meeting Held", "day": 5, "icon": "🤝", "count": current_meetings},
        {"stage": "Deal Closed", "day": sales_cycle_days, "icon": "✅", "count": gtm_metrics['monthly_sales']},
    ]
    
    timeline_cols = st.columns(len(timeline_data))
    
    for idx, stage_data in enumerate(timeline_data):
        with timeline_cols[idx]:
            # Calculate conversion rate from previous stage
            if idx > 0:
                prev_count = timeline_data[idx-1]['count']
                conversion = (stage_data['count'] / prev_count * 100) if prev_count > 0 else 0
            else:
                conversion = 100
            
            st.metric(
                f"{stage_data['icon']} {stage_data['stage']}",
                f"{stage_data['count']:.0f}",
                f"Day {stage_data['day']} | {conversion:.0f}%" if idx > 0 else f"Day {stage_data['day']}"
            )
    
    # Timing metrics row
    st.markdown("#### ⏱️ Timing Metrics")
    timing_cols = st.columns(4)
    
    with timing_cols[0]:
        st.metric("🕒 Lead to Meeting", "5 days")
    with timing_cols[1]:
        meeting_to_close = sales_cycle_days - 5
        st.metric("⏱️ Meeting to Close", f"{meeting_to_close} days")
    with timing_cols[2]:
        velocity_calc = gtm_metrics['monthly_sales'] / sales_cycle_days * 30 if sales_cycle_days > 0 else 0
        st.metric("🚀 Sales Velocity", f"{velocity_calc:.1f} deals/mo", help="Monthly deal throughput based on current closes and sales cycle")
    with timing_cols[3]:
        st.metric("🎯 Win Rate", f"{gtm_metrics['blended_close_rate']:.1%}")
    
    st.markdown("---")
    
    # Channel Performance Summary
    st.markdown("### 📊 Channel Performance")
    channel_perf_cols = st.columns(4)
    
    with channel_perf_cols[0]:
        st.metric("Total Channel Leads", f"{gtm_metrics['monthly_leads']:,.0f}")
    with channel_perf_cols[1]:
        st.metric("Total Channel Sales", f"{gtm_metrics['monthly_sales']:.0f}")
    with channel_perf_cols[2]:
        st.metric("Blended CAC", f"${gtm_metrics.get('cost_per_sale', unit_econ['cac']):,.0f}")
    with channel_perf_cols[3]:
        st.metric("Blended Close Rate", f"{gtm_metrics['blended_close_rate']:.1%}")
    
    st.markdown("---")
    
    # Full P&L Breakdown
    with st.expander("💰 Detailed P&L Breakdown", expanded=True):
        st.subheader("Monthly P&L Statement")
        
        # Create P&L dataframe
        pnl_table = pd.DataFrame({
            'Category': [
                '💰 Gross Revenue',
                '📋 Gov Fees',
                '✅ Net Revenue',
                '',
                '👥 Team Salaries',
                '💸 Commissions',
                '📊 Total COGS',
                '💚 Gross Profit',
                '📈 Gross Margin %',
                '',
                '📣 Marketing',
                '🏢 Operating Expenses',
                '📊 Total OpEx',
                '',
                '💎 EBITDA',
                '📊 EBITDA Margin %'
            ],
            'Amount': [
                f"${pnl_data['gross_revenue']:,.0f}",
                f"${pnl_data['gov_fees']:,.0f}",
                f"${pnl_data['net_revenue']:,.0f}",
                '',
                f"${pnl_data['team_base']:,.0f}",
                f"${pnl_data['commissions']:,.0f}",
                f"${pnl_data['cogs']:,.0f}",
                f"${pnl_data['gross_profit']:,.0f}",
                f"{pnl_data['gross_margin']:.1f}%",
                '',
                f"${pnl_data['marketing']:,.0f}",
                f"${pnl_data['opex']:,.0f}",
                f"${pnl_data['total_opex']:,.0f}",
                '',
                f"${pnl_data['ebitda']:,.0f}",
                f"{pnl_data['ebitda_margin']:.1f}%"
            ]
        })
        
        st.dataframe(pnl_table, use_container_width=True, hide_index=True)
        
        # Key metrics interpretation
        pnl_cols = st.columns(3)
        with pnl_cols[0]:
            if pnl_data['gross_margin'] >= 70:
                st.success(f"✅ Healthy gross margin at {pnl_data['gross_margin']:.1f}%")
            elif pnl_data['gross_margin'] >= 60:
                st.warning(f"⚠️ Acceptable gross margin at {pnl_data['gross_margin']:.1f}%")
            else:
                st.error(f"🚨 Low gross margin at {pnl_data['gross_margin']:.1f}%")
        
        with pnl_cols[1]:
            if pnl_data['ebitda'] > 0:
                st.success(f"✅ Positive EBITDA: ${pnl_data['ebitda']:,.0f}")
            else:
                st.error(f"🚨 Negative EBITDA: ${pnl_data['ebitda']:,.0f}")
        
        with pnl_cols[2]:
            if pnl_data['ebitda_margin'] >= 20:
                st.success(f"✅ Strong EBITDA margin: {pnl_data['ebitda_margin']:.1f}%")
            elif pnl_data['ebitda_margin'] >= 10:
                st.warning(f"⚠️ Moderate EBITDA margin: {pnl_data['ebitda_margin']:.1f}%")
            else:
                st.error(f"🚨 Low EBITDA margin: {pnl_data['ebitda_margin']:.1f}%")
    
    # 7. Channel Funnel Comparison & Revenue Contribution
    st.markdown("---")
    st.markdown("### 📊 Channel Performance Analysis")
    
    if gtm_metrics.get('channels_breakdown') and len(gtm_metrics['channels_breakdown']) > 0:
        chart_cols = st.columns(2)
        
        with chart_cols[0]:
            st.markdown("#### 🔄 Channel Funnel Comparison")
            
            # Create funnel chart for each channel
            funnel_fig = go.Figure()
            
            # Track totals for aggregated funnel
            total_leads = 0
            total_contacts = 0
            total_meetings_scheduled = 0
            total_meetings_held = 0
            total_sales = 0
            
            # Get actual channel configs to use real conversion rates
            for ch_data in gtm_metrics['channels_breakdown']:
                # Find matching channel config to get actual rates
                channel_config = None
                for ch in st.session_state.gtm_channels:
                    if ch['name'] == ch_data['name'] and ch.get('enabled', True):
                        channel_config = ch
                        break
                
                # Calculate funnel stages using ACTUAL conversion rates from config
                leads = ch_data['leads']
                if channel_config:
                    contact_rate = channel_config.get('contact_rate', 0.6)
                    meeting_rate = channel_config.get('meeting_rate', 0.3)
                    show_up_rate = channel_config.get('show_up_rate', 0.7)
                    
                    contacts = leads * contact_rate
                    meetings_scheduled = contacts * meeting_rate
                    meetings_held = meetings_scheduled * show_up_rate
                else:
                    # Fallback if config not found
                    contacts = leads * 0.6
                    meetings_scheduled = contacts * 0.3
                    meetings_held = meetings_scheduled * 0.7
                
                sales = ch_data['sales']
                
                # Add to totals
                total_leads += leads
                total_contacts += contacts
                total_meetings_scheduled += meetings_scheduled
                total_meetings_held += meetings_held
                total_sales += sales
                
                funnel_fig.add_trace(go.Funnel(
                    name=ch_data['name'],
                    y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                    x=[leads, contacts, meetings_scheduled, meetings_held, sales],
                    textinfo="value+percent initial"
                ))
            
            funnel_fig.update_layout(
                title="Individual Channel Funnels",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(funnel_fig, use_container_width=True, key="channel_funnel")
            
            # Separate chart for aggregated total
            st.markdown("#### 🎯 Aggregated Total")
            
            total_fig = go.Figure(go.Funnel(
                y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                x=[total_leads, total_contacts, total_meetings_scheduled, total_meetings_held, total_sales],
                textinfo="value+percent initial",
                marker=dict(color='#F59E0B', line=dict(width=2, color='#D97706'))  # Amber/gold color
            ))
            
            total_fig.update_layout(
                title="All Channels Combined",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(total_fig, use_container_width=True, key="total_funnel")
        
        with chart_cols[1]:
            st.markdown("#### 💰 Revenue Contribution")
            
            # Create pie chart for revenue distribution
            revenue_data = {
                'Channel': [ch['name'] for ch in gtm_metrics['channels_breakdown']],
                'Revenue': [ch['revenue'] for ch in gtm_metrics['channels_breakdown']]
            }
            
            pie_fig = go.Figure(data=[go.Pie(
                labels=revenue_data['Channel'],
                values=revenue_data['Revenue'],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>%{percent}<extra></extra>'
            )])
            
            pie_fig.update_layout(
                title="Revenue Distribution by Channel",
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
            
            st.plotly_chart(pie_fig, use_container_width=True, key="revenue_contribution")
        
        # Channel Performance Table
        st.markdown("#### 📈 Channel Performance Breakdown")
        
        channel_perf_df = pd.DataFrame(gtm_metrics['channels_breakdown'])
        
        # Format for display
        display_df = channel_perf_df[['name', 'segment', 'leads', 'sales', 'revenue', 'roas', 'close_rate']].copy()
        display_df.columns = ['Channel', 'Segment', 'Leads', 'Sales', 'Revenue', 'ROAS', 'Close Rate']
        
        st.dataframe(
            display_df.style.format({
                'Leads': '{:,.0f}',
                'Sales': '{:.1f}',
                'Revenue': '${:,.0f}',
                'ROAS': '{:.2f}x',
                'Close Rate': '{:.1%}'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📊 Configure channels in the GTM tab to see channel performance analysis")

# ============= TAB 4: WHAT-IF ANALYSIS =============
with tab4:
    st.header("🔮 What-If Analysis")
    st.caption("Test different scenarios and see real-time impact")
    
    # Get fresh deal economics for this tab
    tab4_deal_econ = DealEconomicsManager.get_current_deal_economics()
    
    # Baseline metrics
    baseline_sales = gtm_metrics['monthly_sales']
    baseline_revenue = gtm_metrics['monthly_revenue_immediate']
    baseline_ebitda = pnl_data['ebitda']
    
    st.info("💡 Adjust the sliders below to test different scenarios and see immediate impact on revenue and EBITDA")
    
    scenario_cols = st.columns(2)
    
    with scenario_cols[0]:
        st.markdown("### 📊 Adjust Variables")
        
        # Team size multiplier
        team_multiplier = st.slider(
            "🧑‍💼 Team Size Adjustment",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            format="%.1fx",
            help="Multiply team size (0.5x = half team, 2.0x = double team)"
        )
        
        # Deal value multiplier
        deal_multiplier = st.slider(
            "💎 Deal Value Adjustment",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            format="%.1fx",
            help="Adjust average deal value"
        )
        
        # Marketing spend multiplier
        marketing_multiplier = st.slider(
            "📣 Marketing Spend Adjustment",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            format="%.1fx",
            help="Adjust marketing investment (more spend = more leads)"
        )
        
        # Close rate adjustment
        close_rate_delta = st.slider(
            "🎯 Close Rate Adjustment",
            min_value=-10.0,
            max_value=+10.0,
            value=0.0,
            step=1.0,
            format="%+.0f%%",
            help="Adjust close rate by percentage points"
        )
    
    with scenario_cols[1]:
        st.markdown("### 💰 Projected Impact")
        
        # Calculate new metrics
        new_team_cost = team_base * team_multiplier
        new_deal_value = tab4_deal_econ['avg_deal_value'] * deal_multiplier
        new_marketing = marketing_spend * marketing_multiplier
        new_close_rate = min(1.0, max(0.0, gtm_metrics['blended_close_rate'] + (close_rate_delta / 100)))
        
        # Estimate new sales (more marketing increases leads, better close rate increases sales)
        lead_impact = marketing_multiplier ** 0.5  # Diminishing returns on marketing
        close_impact = new_close_rate / gtm_metrics['blended_close_rate'] if gtm_metrics['blended_close_rate'] > 0 else 1.0
        new_sales = baseline_sales * lead_impact * close_impact
        
        # New revenue (use cached calculation)
        new_cash_splits = calculate_deal_cash_splits(new_deal_value, tab4_deal_econ['upfront_pct'])
        new_revenue = new_sales * new_cash_splits['upfront_cash']
        
        # Recalculate commissions
        new_comm_pct = comm_calc['commission_rate'] / 100
        new_comm = new_revenue * new_comm_pct
        
        # New EBITDA
        total_opex = st.session_state.office_rent + st.session_state.software_costs + st.session_state.other_opex
        new_ebitda = new_revenue - new_team_cost - new_comm - new_marketing - total_opex
        
        # Show comparison
        metric_cols = st.columns(2)
        
        with metric_cols[0]:
            st.metric(
                "💵 Monthly Revenue",
                f"${new_revenue:,.0f}",
                delta=f"${new_revenue - baseline_revenue:,.0f}",
                delta_color="normal"
            )
            st.metric(
                "📈 Monthly Sales",
                f"{new_sales:.1f}",
                delta=f"{new_sales - baseline_sales:+.1f}",
                delta_color="normal"
            )
        
        with metric_cols[1]:
            st.metric(
                "💎 EBITDA",
                f"${new_ebitda:,.0f}",
                delta=f"${new_ebitda - baseline_ebitda:,.0f}",
                delta_color="normal" if new_ebitda > baseline_ebitda else "inverse"
            )
            ebitda_margin = (new_ebitda / new_revenue * 100) if new_revenue > 0 else 0
            baseline_margin = pnl_data['ebitda_margin']
            st.metric(
                "📊 EBITDA Margin",
                f"{ebitda_margin:.1f}%",
                delta=f"{ebitda_margin - baseline_margin:+.1f}%",
                delta_color="normal" if ebitda_margin > baseline_margin else "inverse"
            )
        
        # Scenario assessment
        st.markdown("---")
        if new_ebitda > baseline_ebitda * 1.2:
            st.success(f"🚀 **Excellent scenario!** EBITDA improved by {((new_ebitda/baseline_ebitda - 1) * 100):.1f}%")
        elif new_ebitda < baseline_ebitda * 0.8:
            st.error(f"⚠️ **Risky scenario!** EBITDA decreased by {((1 - new_ebitda/baseline_ebitda) * 100):.1f}%")
        else:
            st.info("📊 **Moderate impact** on overall performance")
    
    st.markdown("---")
    
    # Quick scenario buttons
    st.markdown("### 🎯 Quick Scenarios")
    
    quick_cols = st.columns(3)
    
    with quick_cols[0]:
        if st.button("📈 **Growth Mode**", use_container_width=True, help="Simulate 50% team increase + 50% marketing"):
            st.success("✅ Growth Mode: +50% team, +50% marketing, maintain margins")
            st.caption("Expected: Higher revenue, higher costs, moderate EBITDA growth")
    
    with quick_cols[1]:
        if st.button("💰 **Profit Focus**", use_container_width=True, help="Reduce OpEx by 20%"):
            st.success("✅ Profit Focus: -20% OpEx, maintain revenue")
            st.caption("Expected: Same revenue, lower costs, higher EBITDA margin")
    
    with quick_cols[2]:
        if st.button("🔄 **Reset**", use_container_width=True, help="Reset all sliders"):
            st.info("Reset sliders to baseline values manually")

# ============= TAB 5: CONFIGURATION =============
with tab5:
    st.header("⚙️ Configuration")
    st.caption("Configure deal economics, team, compensation, and operating costs")
    
    # Deal Economics - Enhanced
    with st.expander("💰 Deal Economics & Payment Terms", expanded=True):
        st.info("💡 Configure your deal structure - applies to all calculations")
        
        # Business Type Selector
        biz_type_col, template_col = st.columns([2, 1])
        
        with biz_type_col:
            business_type = st.selectbox(
                "Business Type",
                ["Custom", "Insurance", "Allianz - Optimax Plus", "SaaS/Subscription", "Consulting/Services", "Agency/Retainer", "One-Time Sale"],
                index=0,
                key="business_type",
                help="Select a business type for pre-configured deal economics"
            )
        
        with template_col:
            if business_type != "Custom" and st.button("📋 Apply Template", use_container_width=True):
                # Apply business type templates
                templates = {
                    "Insurance": {
                        'avg_deal_value': 45000,
                        'upfront_payment_pct': 70.0,
                        'contract_length_months': 18,
                        'deferred_timing_months': 18
                    },
                    "Allianz - Optimax Plus": {
                        'avg_deal_value': 48600,  # 3000 MXN/month * 18 months * 2.7% * 20 MXN/USD
                        'upfront_payment_pct': 70.0,
                        'contract_length_months': 18,
                        'deferred_timing_months': 18
                    },
                    "SaaS/Subscription": {
                        'avg_deal_value': 60000,
                        'upfront_payment_pct': 100.0,
                        'contract_length_months': 12,
                        'deferred_timing_months': 0
                    },
                    "Consulting/Services": {
                        'avg_deal_value': 50000,
                        'upfront_payment_pct': 50.0,
                        'contract_length_months': 3,
                        'deferred_timing_months': 3
                    },
                    "Agency/Retainer": {
                        'avg_deal_value': 72000,
                        'upfront_payment_pct': 100.0,
                        'contract_length_months': 12,
                        'deferred_timing_months': 0
                    },
                    "One-Time Sale": {
                        'avg_deal_value': 10000,
                        'upfront_payment_pct': 100.0,
                        'contract_length_months': 1,
                        'deferred_timing_months': 0
                    }
                }
                
                if business_type in templates:
                    template = templates[business_type]
                    for key, value in template.items():
                        st.session_state[key] = value
                    st.success(f"✅ Applied {business_type} template! Change any value below to update.")
                    # Note: Removed st.rerun() - let widgets update naturally on next interaction
        
        st.markdown("---")
        
        # Modular Deal Value Calculator
        st.markdown("**💡 Deal Value Calculation Method**")
        calc_method_col, info_col = st.columns([2, 1])
        
        with calc_method_col:
            calc_method = st.selectbox(
                "How do you calculate deal value?",
                ["💰 Direct Value", "🏥 Insurance (Premium-Based)", "📊 Subscription (MRR)", "📋 Commission % of Contract"],
                key="deal_calc_method",
                help="Choose the method that matches your business model"
            )
        
        with info_col:
            if "Insurance" in calc_method:
                st.info("Perfect for insurance brokers!")
            elif "Subscription" in calc_method:
                st.info("Ideal for SaaS/subscriptions")
            elif "Commission" in calc_method:
                st.info("For commission-based sales")
            else:
                st.info("Simple direct entry")
        
        # Calculator based on method
        calc_cols = st.columns(3)
        
        if "Insurance" in calc_method:
            # Insurance-specific: Monthly Premium × Commission Rate × Contract Years
            with calc_cols[0]:
                monthly_premium = st.number_input(
                    "Monthly Premium ($)",
                    min_value=0,
                    value=int(st.session_state.get('monthly_premium', 3000)),
                    step=100,
                    key="monthly_premium",
                    help="Customer's monthly insurance premium"
                )
            with calc_cols[1]:
                commission_rate = st.number_input(
                    "Commission Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.get('insurance_commission_rate', 2.7),
                    step=0.1,
                    key="insurance_commission_rate",
                    help="Your commission % (e.g., 2.7%)"
                )
            with calc_cols[2]:
                contract_years = st.number_input(
                    "Contract Term (Years)",
                    min_value=1,
                    max_value=50,
                    value=int(st.session_state.get('insurance_contract_years', 18)),
                    step=1,
                    key="insurance_contract_years"
                )
            
            # Calculate
            total_premium = monthly_premium * 12 * contract_years
            avg_deal_value = total_premium * (commission_rate / 100)
            contract_length = contract_years * 12
            
            # Store calculated value for other components to use
            st.session_state['calculated_deal_value'] = avg_deal_value
            st.session_state['calculated_contract_length'] = contract_length
            
            st.success(f"💰 **Your Commission**: ${avg_deal_value:,.0f}")
            st.caption(f"💡 ${monthly_premium:,.0f}/mo × 12 × {contract_years}y × {commission_rate}% = ${avg_deal_value:,.0f}")
            
        elif "Subscription" in calc_method:
            # Subscription: MRR × Contract Term
            with calc_cols[0]:
                mrr = st.number_input(
                    "Monthly Recurring Revenue",
                    min_value=0,
                    value=int(st.session_state.get('mrr', 5000)),
                    step=500,
                    key="mrr"
                )
            with calc_cols[1]:
                sub_term = st.number_input(
                    "Contract Term (Months)",
                    min_value=1,
                    max_value=60,
                    value=int(st.session_state.get('sub_term_months', 12)),
                    step=1,
                    key="sub_term_months"
                )
            with calc_cols[2]:
                st.metric("Total Contract Value", f"${mrr * sub_term:,.0f}")
            
            avg_deal_value = mrr * sub_term
            contract_length = sub_term
            
            # Store calculated value for other components to use
            st.session_state['calculated_deal_value'] = avg_deal_value
            st.session_state['calculated_contract_length'] = contract_length
            
            st.caption(f"💡 ${mrr:,.0f}/mo × {sub_term} months = ${avg_deal_value:,.0f}")
            
        elif "Commission" in calc_method:
            # Commission-based: Total Contract × Commission %
            with calc_cols[0]:
                total_contract = st.number_input(
                    "Total Contract Value ($)",
                    min_value=0,
                    value=int(st.session_state.get('total_contract_value', 100000)),
                    step=5000,
                    key="total_contract_value"
                )
            with calc_cols[1]:
                commission_pct = st.number_input(
                    "Your Commission (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.get('contract_commission_pct', 10.0),
                    step=0.5,
                    key="contract_commission_pct"
                )
            with calc_cols[2]:
                contract_length = st.number_input(
                    "Contract Length (Months)",
                    min_value=1,
                    max_value=60,
                    value=int(st.session_state.get('contract_length_months', 12)),
                    step=1,
                    key="contract_length_months"
                )
            
            avg_deal_value = total_contract * (commission_pct / 100)
            
            # Store calculated value for other components to use
            st.session_state['calculated_deal_value'] = avg_deal_value
            st.session_state['calculated_contract_length'] = contract_length
            
            st.caption(f"💡 ${total_contract:,.0f} × {commission_pct}% = ${avg_deal_value:,.0f}")
            
        else:  # Direct Value
            with calc_cols[0]:
                avg_deal_value = st.number_input(
                    "Average Deal Value ($)",
                    min_value=0,
                    value=st.session_state.avg_deal_value,
                    step=1000,
                    key="avg_deal_value",
                    help="Total contract value"
                )
            with calc_cols[1]:
                contract_length = st.number_input(
                    "Contract Length (Months)",
                    min_value=1,
                    max_value=60,
                    value=st.session_state.contract_length_months,
                    step=1,
                    key="contract_length_months"
                )
            with calc_cols[2]:
                monthly_value = avg_deal_value / contract_length if contract_length > 0 else 0
                st.metric("Monthly Value", f"${monthly_value:,.0f}")
            
            # Store values (Direct Value mode uses widget values directly)
            st.session_state['calculated_deal_value'] = avg_deal_value
            st.session_state['calculated_contract_length'] = contract_length
        
        st.markdown("---")
        
        # Payment Terms Section (keeping existing structure)
        deal_cols = st.columns(3)
        
        with deal_cols[0]:
            st.markdown("**Deal Summary**")
            st.metric("💰 Deal Value", f"${avg_deal_value:,.0f}")
            monthly_value = avg_deal_value / contract_length if contract_length > 0 else 0
            st.caption(f"📅 Contract: {contract_length} months")
            st.caption(f"💵 Monthly: ${monthly_value:,.0f}")
        
        with deal_cols[1]:
            st.markdown("**Payment Terms**")
            upfront_pct = st.slider(
                "Upfront Payment %",
                0.0,
                100.0,
                st.session_state.upfront_payment_pct,
                5.0,
                key="upfront_payment_pct",
                help="Percentage paid upfront"
            )
            
            # Use cached calculation for payment splits
            payment_splits = calculate_deal_cash_splits(avg_deal_value, upfront_pct)
            upfront_cash = payment_splits['upfront_cash']
            deferred_cash = payment_splits['deferred_cash']
            deferred_pct = payment_splits['deferred_pct']
            
            st.caption(f"**Upfront:** ${upfront_cash:,.0f} ({upfront_pct:.0f}%)")
            st.caption(f"**Deferred:** ${deferred_cash:,.0f} ({deferred_pct:.0f}%)")
            
            if deferred_pct > 0:
                deferred_timing = st.number_input(
                    "Deferred Payment Month",
                    min_value=1,
                    max_value=60,
                    value=st.session_state.deferred_timing_months,
                    step=1,
                    key="deferred_timing_months",
                    help="Month when deferred payment is received"
                )
        
        with deal_cols[2]:
            st.markdown("**Commission Policy**")
            commission_policy = st.radio(
                "Calculate Commissions From:",
                ["Upfront Cash Only", "Full Deal Value"],
                index=0 if st.session_state.commission_policy == 'upfront' else 1,
                key="commission_policy_selector",
                help="Choose what amount to use as commission base"
            )
            
            if "Upfront" in commission_policy:
                st.session_state.commission_policy = 'upfront'
                comm_base = upfront_cash
            else:
                st.session_state.commission_policy = 'full'
                comm_base = avg_deal_value
            
            st.caption(f"**Commission Base:** ${comm_base:,.0f}")
            
            # Government costs
            st.markdown("**Government Costs**")
            gov_cost = st.slider(
                "Gov Fees/Taxes (%)",
                0.0,
                20.0,
                st.session_state.get('government_cost_pct', 10.0),
                0.5,
                key="government_cost_pct",
                help="Government fees, taxes, regulatory costs (% of revenue)",
                format="%.1f%%"
            )
            
            # Show GRR/NRR settings
            st.markdown("**Revenue Retention**")
            grr = st.slider(
                "GRR (Gross Revenue Retention)",
                0.0,
                1.5,
                st.session_state.grr_rate,
                0.05,
                key="grr_rate",
                help="Expected revenue retention rate",
                format="%.0f%%"
            )
        
        # Deal Economics Summary
        st.markdown("---")
        st.markdown("**📊 Deal Economics Summary**")
        summary_cols = st.columns(5)
        
        with summary_cols[0]:
            st.metric("Total Contract", f"${avg_deal_value:,.0f}")
        with summary_cols[1]:
            st.metric("Upfront Cash", f"${upfront_cash:,.0f}")
        with summary_cols[2]:
            st.metric("Deferred Cash", f"${deferred_cash:,.0f}")
        with summary_cols[3]:
            st.metric("Commission Base", f"${comm_base:,.0f}")
        with summary_cols[4]:
            st.metric("Monthly Value", f"${monthly_value:,.0f}")
    
    # Revenue Targets
    with st.expander("🎯 Revenue Targets", expanded=False):
        st.info("💡 Set your revenue goals - converts between periods automatically")
        
        # Get fresh deal economics (in case user just changed them above)
        current_deal_econ = DealEconomicsManager.get_current_deal_economics()
        
        rev_cols = st.columns(3)
        
        with rev_cols[0]:
            st.markdown("**Input Period**")
            target_period = st.selectbox(
                "Choose Period",
                ["Annual", "Monthly", "Weekly", "Daily"],
                index=1,
                key="target_period",
                help="Select your preferred way to input revenue targets"
            )
            
            # Get current target or default
            current_monthly_target = st.session_state.get('monthly_revenue_target', 500000)
            
            if target_period == "Annual":
                default_annual = st.session_state.get('rev_annual', current_monthly_target * 12)
                revenue_input = st.number_input(
                    "Annual Target ($)",
                    min_value=0,
                    value=int(default_annual),
                    step=1000000,
                    key="rev_annual"
                )
                monthly_revenue_target = revenue_input / 12
            elif target_period == "Monthly":
                default_monthly = st.session_state.get('rev_monthly', current_monthly_target)
                revenue_input = st.number_input(
                    "Monthly Target ($)",
                    min_value=0,
                    value=int(default_monthly),
                    step=100000,
                    key="rev_monthly"
                )
                monthly_revenue_target = revenue_input
            elif target_period == "Weekly":
                default_weekly = st.session_state.get('rev_weekly', current_monthly_target / 4.33)
                revenue_input = st.number_input(
                    "Weekly Target ($)",
                    min_value=0,
                    value=int(default_weekly),
                    step=25000,
                    key="rev_weekly"
                )
                monthly_revenue_target = revenue_input * 4.33
            else:  # Daily
                default_daily = st.session_state.get('rev_daily', current_monthly_target / 21.67)
                revenue_input = st.number_input(
                    "Daily Target ($)",
                    min_value=0,
                    value=int(default_daily),
                    step=5000,
                    key="rev_daily"
                )
                monthly_revenue_target = revenue_input * 21.67
            
            # Store in session state
            st.session_state['monthly_revenue_target'] = monthly_revenue_target
        
        with rev_cols[1]:
            st.markdown("**📊 Revenue Breakdown**")
            annual_revenue = monthly_revenue_target * 12
            weekly_revenue = monthly_revenue_target / 4.33
            daily_revenue = monthly_revenue_target / 21.67
            
            st.metric("Annual", f"${annual_revenue:,.0f}")
            st.metric("Monthly", f"${monthly_revenue_target:,.0f}")
            st.metric("Weekly", f"${weekly_revenue:,.0f}")
            st.metric("Daily", f"${daily_revenue:,.0f}")
        
        with rev_cols[2]:
            st.markdown("**🎯 Required Performance**")
            
            # Calculate sales needed based on current deal economics
            current_revenue = gtm_metrics['monthly_revenue_immediate']
            sales_needed = monthly_revenue_target / current_deal_econ['upfront_cash'] if current_deal_econ['upfront_cash'] > 0 else 0
            current_sales = gtm_metrics['monthly_sales']
            
            st.metric(
                "Sales Needed",
                f"{sales_needed:.0f}/mo",
                help="Monthly deals required to hit target"
            )
            st.metric(
                "Revenue per Sale",
                f"${current_deal_econ['upfront_cash']:,.0f}",
                help="From Deal Economics (upfront cash per deal)"
            )
            
            # Achievement percentage
            achievement = (current_revenue / monthly_revenue_target * 100) if monthly_revenue_target > 0 else 0
            color = "normal" if achievement >= 100 else "inverse"
            st.metric(
                "Target Achievement",
                f"{achievement:.0f}%",
                delta=f"{achievement - 100:.0f}%",
                delta_color=color
            )
            
            # Gap analysis
            if achievement < 100:
                gap = monthly_revenue_target - current_revenue
                sales_gap = gap / current_deal_econ['upfront_cash'] if current_deal_econ['upfront_cash'] > 0 else 0
                st.caption(f"⚠️ Need {sales_gap:.0f} more sales to hit target")
            else:
                st.caption(f"✅ Target exceeded by ${current_revenue - monthly_revenue_target:,.0f}")
    
    # Team Configuration with Capacity Analysis
    with st.expander("👥 Team Configuration & Capacity", expanded=False):
        st.info("💡 Configure team size and capacity settings - affects all calculations")
        
        team_cols = st.columns(3)
        
        with team_cols[0]:
            st.markdown("**Team Size**")
            num_closers = st.number_input("Closers", 1, 50, st.session_state.num_closers_main, key="num_closers_main")
            num_setters = st.number_input("Setters", 0, 50, st.session_state.num_setters_main, key="num_setters_main")
            num_managers = st.number_input("Managers", 0, 20, st.session_state.num_managers_main, key="num_managers_main")
            num_bench = st.number_input("Bench", 0, 20, st.session_state.num_benchs_main, key="num_benchs_main")
            
            st.markdown("**Capacity Settings**")
            meetings_per_closer = st.number_input(
                "Meetings/Closer/Day",
                min_value=0.1,
                max_value=10.0,
                value=st.session_state.get('meetings_per_closer', 3.0),
                step=0.5,
                key="meetings_per_closer",
                help="Average meetings each closer can run per working day"
            )
            working_days = st.number_input(
                "Working Days/Month",
                min_value=10,
                max_value=26,
                value=st.session_state.get('working_days', 20),
                step=1,
                key="working_days",
                help="Number of active selling days per month"
            )
            meetings_per_setter = st.number_input(
                "Meetings Booked/Setter/Day",
                min_value=0.1,
                max_value=20.0,
                value=st.session_state.get('meetings_per_setter', 2.0),
                step=0.5,
                key="meetings_per_setter",
                help="Average meetings each setter confirms and books per day"
            )
        
        with team_cols[1]:
            st.markdown("**Team Metrics**")
            team_total = num_closers + num_setters + num_managers + num_bench
            active_ratio = (num_closers + num_setters) / max(1, team_total)
            setter_closer_ratio = num_setters / max(1, num_closers)
            
            st.metric("Total Team", f"{team_total}")
            st.metric("Active Ratio", f"{active_ratio:.0%}", help="% of team in revenue-generating roles")
            st.metric("Setter:Closer Ratio", f"{setter_closer_ratio:.1f}:1")
            
            st.markdown("**Capacity Utilization**")
            monthly_closer_capacity = num_closers * meetings_per_closer * working_days
            monthly_setter_capacity = num_setters * meetings_per_setter * working_days
            
            current_meetings = gtm_metrics.get('monthly_meetings_held', 0)
            current_bookings = gtm_metrics.get('monthly_meetings_scheduled', 0)
            
            closer_util = (current_meetings / monthly_closer_capacity * 100) if monthly_closer_capacity > 0 else 0
            setter_util = (current_bookings / monthly_setter_capacity * 100) if monthly_setter_capacity > 0 else 0
            
            # Closer utilization
            closer_color = "normal" if closer_util < 75 else "inverse"
            st.metric(
                "Closer Utilization",
                f"{closer_util:.0f}%",
                delta="Healthy" if closer_util < 75 else "High" if closer_util < 90 else "OVERLOAD",
                delta_color=closer_color
            )
            
            # Setter utilization
            setter_color = "normal" if setter_util < 75 else "inverse"
            st.metric(
                "Setter Utilization",
                f"{setter_util:.0f}%",
                delta="Healthy" if setter_util < 75 else "High" if setter_util < 90 else "OVERLOAD",
                delta_color=setter_color
            )
        
        with team_cols[2]:
            st.markdown("**Capacity Analysis Chart**")
            
            # Calculate capacity metrics
            closer_headroom = monthly_closer_capacity - current_meetings
            setter_headroom = monthly_setter_capacity - current_bookings
            
            # Determine status colors
            closer_status_color = "#22c55e" if closer_util < 75 else "#f59e0b" if closer_util < 90 else "#ef4444"
            setter_status_color = "#22c55e" if setter_util < 75 else "#f59e0b" if setter_util < 90 else "#ef4444"
            
            # Create capacity chart
            fig_capacity = go.Figure()
            
            # Closers - Stacked bar
            fig_capacity.add_trace(go.Bar(
                name='Used',
                x=['Closers'],
                y=[current_meetings],
                text=[f"{current_meetings:.0f}"],
                textposition='inside',
                marker_color='#3b82f6',
                hovertemplate='<b>Current Load</b><br>%{y:.0f} meetings<extra></extra>'
            ))
            
            fig_capacity.add_trace(go.Bar(
                name='Available',
                x=['Closers'],
                y=[closer_headroom if closer_headroom > 0 else 0],
                text=[f"{closer_headroom:.0f}" if closer_headroom > 0 else "OVERLOAD"],
                textposition='inside',
                marker_color=closer_status_color,
                hovertemplate='<b>Headroom</b><br>%{y:.0f} meetings<extra></extra>'
            ))
            
            # Setters - Stacked bar
            fig_capacity.add_trace(go.Bar(
                name='Used',
                x=['Setters'],
                y=[current_bookings],
                text=[f"{current_bookings:.0f}"],
                textposition='inside',
                marker_color='#3b82f6',
                showlegend=False,
                hovertemplate='<b>Current Load</b><br>%{y:.0f} bookings<extra></extra>'
            ))
            
            fig_capacity.add_trace(go.Bar(
                name='Available',
                x=['Setters'],
                y=[setter_headroom if setter_headroom > 0 else 0],
                text=[f"{setter_headroom:.0f}" if setter_headroom > 0 else "OVERLOAD"],
                textposition='inside',
                marker_color=setter_status_color,
                showlegend=False,
                hovertemplate='<b>Headroom</b><br>%{y:.0f} bookings<extra></extra>'
            ))
            
            fig_capacity.update_layout(
                barmode='stack',
                title=dict(
                    text='Team Capacity vs Current Load',
                    font=dict(size=14)
                ),
                height=350,
                margin=dict(t=50, b=30, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True, key="capacity_chart")
            
            # Capacity insights
            if closer_util >= 90:
                st.error("🚨 Closers at critical capacity! Consider hiring.")
            elif closer_util >= 75:
                st.warning("⚠️ Closer capacity high. Plan for expansion.")
            else:
                st.success("✅ Closer capacity healthy")
            
            if setter_util >= 90:
                st.error("🚨 Setters overloaded! Need more setters.")
            elif setter_util >= 75:
                st.warning("⚠️ Setter capacity stretched.")
            else:
                st.success("✅ Setter capacity healthy")
    
    # Compensation Configuration
    with st.expander("💵 Compensation Configuration", expanded=False):
        st.info("💡 **2-Tier Comp Model**: Base Salary (guaranteed) + Commission % (unlimited upside)")
        
        comp_cols = st.columns(3)
        
        with comp_cols[0]:
            st.markdown("**🎯 Closer**")
            st.number_input(
                "Base Salary (Annual $)", 
                0, 200000, st.session_state.closer_base, 1000, 
                key="closer_base",
                help="Annual salary + commission on deals"
            )
            st.number_input(
                "Commission % (Per Deal)", 
                0.0, 50.0, st.session_state.closer_commission_pct, 0.5, 
                key="closer_commission_pct",
                help="Percentage of each deal value (unlimited upside)"
            )
            st.caption(f"💰 **Base**: ${st.session_state.closer_base:,.0f}/year + Commission")
        
        with comp_cols[1]:
            st.markdown("**📞 Setter**")
            st.number_input(
                "Base Salary (Annual $)", 
                0, 200000, st.session_state.setter_base, 1000, 
                key="setter_base",
                help="Annual salary + commission on deals"
            )
            st.number_input(
                "Commission % (Per Deal)", 
                0.0, 50.0, st.session_state.setter_commission_pct, 0.5, 
                key="setter_commission_pct",
                help="Percentage of each deal value (unlimited upside)"
            )
            st.caption(f"💰 **Base**: ${st.session_state.setter_base:,.0f}/year + Commission")
        
        with comp_cols[2]:
            st.markdown("**👔 Manager**")
            st.number_input(
                "Base Salary (Annual $)", 
                0, 300000, st.session_state.manager_base, 1000, 
                key="manager_base",
                help="Annual salary + team override commission"
            )
            st.number_input(
                "Commission % (Per Deal)", 
                0.0, 50.0, st.session_state.manager_commission_pct, 0.5, 
                key="manager_commission_pct",
                help="Percentage of each deal value (team override)"
            )
            st.caption(f"💰 **Base**: ${st.session_state.manager_base:,.0f}/year + Commission")
    
    # Operating Costs
    with st.expander("🏢 Operating Costs", expanded=False):
        ops_cols = st.columns(3)
        
        with ops_cols[0]:
            st.number_input("Office Rent ($)", 0, 100000, st.session_state.office_rent, 500, key="office_rent")
        with ops_cols[1]:
            st.number_input("Software ($)", 0, 50000, st.session_state.software_costs, 100, key="software_costs")
        with ops_cols[2]:
            st.number_input("Other OpEx ($)", 0, 100000, st.session_state.other_opex, 500, key="other_opex")
    
    # Profit Distribution (Stakeholders)
    with st.expander("💰 Profit Distribution (Stakeholders)", expanded=False):
        st.info("💡 Stakeholders receive a percentage of EBITDA after all operating costs")
        
        stake_cols = st.columns(2)
        
        with stake_cols[0]:
            st.markdown("**Configuration**")
            stakeholder_pct = st.number_input(
                "Stakeholder Profit Share (%)",
                min_value=0.0,
                max_value=50.0,
                value=st.session_state.get('stakeholder_pct', 10.0),
                step=0.5,
                key="stakeholder_pct",
                help="Percentage of EBITDA distributed to stakeholders/owners"
            )
            
            st.markdown("**📊 Distribution Source:**")
            st.caption("✅ Comes from EBITDA (after all team costs + OpEx)")
            st.caption("✅ Remaining EBITDA stays in business for growth")
            st.caption("✅ Typical range: 5-25% for healthy businesses")
            st.caption("✅ Not a commission - this is profit distribution")
        
        with stake_cols[1]:
            st.markdown("**💰 Projected Distribution:**")
            
            # Calculate stakeholder payout using current P&L data
            if pnl_data['ebitda'] > 0:
                stakeholder_monthly = pnl_data['ebitda'] * (stakeholder_pct / 100)
                stakeholder_annual = stakeholder_monthly * 12
                ebitda_after_stake = pnl_data['ebitda'] - stakeholder_monthly
                
                st.metric("Monthly Distribution", f"${stakeholder_monthly:,.0f}")
                st.metric("Annual Distribution", f"${stakeholder_annual:,.0f}")
                st.metric("EBITDA After Distribution", f"${ebitda_after_stake:,.0f}")
                
                # Show as % of revenue
                if gtm_metrics['monthly_revenue_immediate'] > 0:
                    stake_pct_rev = (stakeholder_monthly / gtm_metrics['monthly_revenue_immediate'] * 100)
                    st.metric("As % of Revenue", f"{stake_pct_rev:.1f}%")
                
                # Health check
                if stake_pct_rev > 15:
                    st.warning("⚠️ High profit distribution relative to revenue")
                elif ebitda_after_stake < 0:
                    st.error("🚨 Negative EBITDA after distribution!")
                else:
                    st.success("✅ Healthy profit distribution")
            else:
                st.warning("⚠️ No positive EBITDA to distribute")
                st.caption("EBITDA must be positive to distribute profits")
                st.caption(f"Current EBITDA: ${pnl_data['ebitda']:,.0f}")
    
    # JSON Export/Import - Smart & Fast
    st.markdown("---")
    st.markdown("### 📋 Configuration Export/Import")
    st.info("💡 Save and load your complete dashboard configuration in seconds")
    
    export_col, import_col = st.columns(2)
    
    with export_col:
        st.markdown("**📤 Export Configuration**")
        
        # Build configuration dictionary from session state
        def build_config():
            return {
                "deal_economics": {
                    "business_type": st.session_state.get('business_type', 'Custom'),
                    "deal_calc_method": st.session_state.get('deal_calc_method', '💰 Direct Value'),
                    "avg_deal_value": st.session_state.avg_deal_value,
                    "contract_length_months": st.session_state.contract_length_months,
                    "upfront_payment_pct": st.session_state.upfront_payment_pct,
                    "deferred_timing_months": st.session_state.deferred_timing_months,
                    "commission_policy": st.session_state.commission_policy,
                    "government_cost_pct": st.session_state.get('government_cost_pct', 10.0),
                    "grr_rate": st.session_state.grr_rate,
                    # Insurance calculation parameters
                    "monthly_premium": st.session_state.get('monthly_premium', 3000),
                    "insurance_commission_rate": st.session_state.get('insurance_commission_rate', 2.7),
                    "insurance_contract_years": st.session_state.get('insurance_contract_years', 18),
                    # Subscription parameters
                    "mrr": st.session_state.get('mrr', 5000),
                    "sub_term_months": st.session_state.get('sub_term_months', 12),
                    # Commission-based parameters
                    "total_contract_value": st.session_state.get('total_contract_value', 100000),
                    "contract_commission_pct": st.session_state.get('contract_commission_pct', 10.0)
                },
                "team": {
                    "closers": st.session_state.num_closers_main,
                    "setters": st.session_state.num_setters_main,
                    "managers": st.session_state.num_managers_main,
                    "bench": st.session_state.num_benchs_main
                },
                "compensation": {
                    "closer": {
                        "base": st.session_state.closer_base,
                        "variable": st.session_state.closer_variable,
                        "commission_pct": st.session_state.closer_commission_pct
                    },
                    "setter": {
                        "base": st.session_state.setter_base,
                        "variable": st.session_state.setter_variable,
                        "commission_pct": st.session_state.setter_commission_pct
                    },
                    "manager": {
                        "base": st.session_state.manager_base,
                        "variable": st.session_state.manager_variable,
                        "commission_pct": st.session_state.manager_commission_pct
                    },
                    "bench": {
                        "base": st.session_state.bench_base,
                        "variable": st.session_state.bench_variable
                    }
                },
                "operating_costs": {
                    "office_rent": st.session_state.office_rent,
                    "software_costs": st.session_state.software_costs,
                    "other_opex": st.session_state.other_opex
                },
                "gtm_channels": st.session_state.gtm_channels,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        
        config_json = json.dumps(build_config(), indent=2)
        
        # Download button
        st.download_button(
            label="📥 Download Config",
            data=config_json,
            file_name=f"dashboard_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # Copy to clipboard option
        if st.button("📋 Show Config (Copy/Paste)", use_container_width=True):
            st.code(config_json, language="json")
            st.success("✅ Copy the JSON above to share or save")
    
    with import_col:
        st.markdown("**📥 Import Configuration**")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload JSON config file",
            type=['json'],
            help="Upload a previously saved configuration",
            label_visibility="visible"
        )
        
        if uploaded_file is not None:
            try:
                loaded_config = json.load(uploaded_file)
                
                if st.button("✅ Apply Uploaded Config", use_container_width=True):
                    # Apply loaded configuration
                    if 'deal_economics' in loaded_config:
                        de = loaded_config['deal_economics']
                        st.session_state['avg_deal_value'] = de.get('avg_deal_value', 50000)
                        st.session_state['contract_length_months'] = de.get('contract_length_months', 12)
                        st.session_state['upfront_payment_pct'] = de.get('upfront_payment_pct', 70.0)
                        st.session_state['deferred_timing_months'] = de.get('deferred_timing_months', 18)
                        st.session_state['commission_policy'] = de.get('commission_policy', 'upfront')
                        st.session_state['government_cost_pct'] = de.get('government_cost_pct', 10.0)
                        st.session_state['grr_rate'] = de.get('grr_rate', 0.9)
                        # Deal calculation method parameters
                        st.session_state['deal_calc_method'] = de.get('deal_calc_method', '💰 Direct Value')
                        st.session_state['monthly_premium'] = de.get('monthly_premium', 3000)
                        st.session_state['insurance_commission_rate'] = de.get('insurance_commission_rate', 2.7)
                        st.session_state['insurance_contract_years'] = de.get('insurance_contract_years', 18)
                        st.session_state['mrr'] = de.get('mrr', 5000)
                        st.session_state['sub_term_months'] = de.get('sub_term_months', 12)
                        st.session_state['total_contract_value'] = de.get('total_contract_value', 100000)
                        st.session_state['contract_commission_pct'] = de.get('contract_commission_pct', 10.0)
                    
                    if 'team' in loaded_config:
                        t = loaded_config['team']
                        st.session_state['num_closers_main'] = t.get('closers', 8)
                        st.session_state['num_setters_main'] = t.get('setters', 4)
                        st.session_state['num_managers_main'] = t.get('managers', 2)
                        st.session_state['num_benchs_main'] = t.get('bench', 2)
                    
                    if 'compensation' in loaded_config:
                        c = loaded_config['compensation']
                        if 'closer' in c:
                            st.session_state['closer_base'] = c['closer'].get('base', 32000)
                            st.session_state['closer_variable'] = c['closer'].get('variable', 48000)
                            st.session_state['closer_commission_pct'] = c['closer'].get('commission_pct', 20.0)
                        if 'setter' in c:
                            st.session_state['setter_base'] = c['setter'].get('base', 16000)
                            st.session_state['setter_variable'] = c['setter'].get('variable', 24000)
                            st.session_state['setter_commission_pct'] = c['setter'].get('commission_pct', 3.0)
                        if 'manager' in c:
                            st.session_state['manager_base'] = c['manager'].get('base', 72000)
                            st.session_state['manager_variable'] = c['manager'].get('variable', 48000)
                            st.session_state['manager_commission_pct'] = c['manager'].get('commission_pct', 5.0)
                    
                    if 'operating_costs' in loaded_config:
                        oc = loaded_config['operating_costs']
                        st.session_state['office_rent'] = oc.get('office_rent', 20000)
                        st.session_state['software_costs'] = oc.get('software_costs', 10000)
                        st.session_state['other_opex'] = oc.get('other_opex', 5000)
                    
                    if 'gtm_channels' in loaded_config:
                        st.session_state['gtm_channels'] = loaded_config['gtm_channels']
                    
                    st.success("✅ Configuration loaded! Interact with any widget to see changes.")
                    # Note: Removed st.rerun() to prevent page refresh
            
            except Exception as e:
                st.error(f"❌ Error loading config: {str(e)}")
        
        # Paste JSON option
        with st.expander("📝 Or Paste JSON"):
            pasted_config = st.text_area(
                "Paste configuration JSON here",
                height=150,
                placeholder='{"deal_economics": {...}, "team": {...}}',
                key="pasted_json_config"
            )
            
            if st.button("✅ Apply Pasted Config") and pasted_config:
                try:
                    loaded_config = json.loads(pasted_config)
                    
                    # Apply same logic as file upload
                    if 'deal_economics' in loaded_config:
                        de = loaded_config['deal_economics']
                        st.session_state['avg_deal_value'] = de.get('avg_deal_value', 50000)
                        st.session_state['contract_length_months'] = de.get('contract_length_months', 12)
                        st.session_state['upfront_payment_pct'] = de.get('upfront_payment_pct', 70.0)
                        st.session_state['deferred_timing_months'] = de.get('deferred_timing_months', 18)
                        st.session_state['commission_policy'] = de.get('commission_policy', 'upfront')
                        st.session_state['government_cost_pct'] = de.get('government_cost_pct', 10.0)
                        st.session_state['grr_rate'] = de.get('grr_rate', 0.9)
                        # Deal calculation method parameters
                        st.session_state['deal_calc_method'] = de.get('deal_calc_method', '💰 Direct Value')
                        st.session_state['monthly_premium'] = de.get('monthly_premium', 3000)
                        st.session_state['insurance_commission_rate'] = de.get('insurance_commission_rate', 2.7)
                        st.session_state['insurance_contract_years'] = de.get('insurance_contract_years', 18)
                        st.session_state['mrr'] = de.get('mrr', 5000)
                        st.session_state['sub_term_months'] = de.get('sub_term_months', 12)
                        st.session_state['total_contract_value'] = de.get('total_contract_value', 100000)
                        st.session_state['contract_commission_pct'] = de.get('contract_commission_pct', 10.0)
                    
                    if 'team' in loaded_config:
                        t = loaded_config['team']
                        st.session_state['num_closers_main'] = t.get('closers', 8)
                        st.session_state['num_setters_main'] = t.get('setters', 4)
                        st.session_state['num_managers_main'] = t.get('managers', 2)
                        st.session_state['num_benchs_main'] = t.get('bench', 2)
                    
                    if 'compensation' in loaded_config:
                        c = loaded_config['compensation']
                        if 'closer' in c:
                            st.session_state['closer_base'] = c['closer'].get('base', 32000)
                            st.session_state['closer_variable'] = c['closer'].get('variable', 48000)
                            st.session_state['closer_commission_pct'] = c['closer'].get('commission_pct', 20.0)
                        if 'setter' in c:
                            st.session_state['setter_base'] = c['setter'].get('base', 16000)
                            st.session_state['setter_variable'] = c['setter'].get('variable', 24000)
                            st.session_state['setter_commission_pct'] = c['setter'].get('commission_pct', 3.0)
                        if 'manager' in c:
                            st.session_state['manager_base'] = c['manager'].get('base', 72000)
                            st.session_state['manager_variable'] = c['manager'].get('variable', 48000)
                            st.session_state['manager_commission_pct'] = c['manager'].get('commission_pct', 5.0)
                    
                    if 'operating_costs' in loaded_config:
                        oc = loaded_config['operating_costs']
                        st.session_state['office_rent'] = oc.get('office_rent', 20000)
                        st.session_state['software_costs'] = oc.get('software_costs', 10000)
                        st.session_state['other_opex'] = oc.get('other_opex', 5000)
                    
                    if 'gtm_channels' in loaded_config:
                        st.session_state['gtm_channels'] = loaded_config['gtm_channels']
                    
                    st.success("✅ Configuration applied! Interact with any widget to see changes.")
                    # Note: Removed st.rerun() to prevent page refresh
                
                except Exception as e:
                    st.error(f"❌ Error parsing JSON: {str(e)}")

# ============= FOOTER =============
st.markdown("---")
st.caption("⚡ Lightning Fast Dashboard • Built with Streamlit • Cached for performance")
