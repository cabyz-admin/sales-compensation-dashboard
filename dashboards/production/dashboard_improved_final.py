"""
Improved Final Dashboard - All issues fixed
Deep integration, better inputs, proper math
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Ensure project root and modules directory are on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARDS_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARDS_DIR)
MODULES_DIR = os.path.join(PROJECT_ROOT, "modules")

for path in [MODULES_DIR, PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import improved modules
try:
    from modules.calculations_improved import (
        ImprovedCostCalculator,
        ImprovedCompensationCalculator,
        ImprovedPnLCalculator,
        ImprovedReverseEngineering
    )
    from modules.calculations_enhanced import (
        EnhancedRevenueCalculator,
        BottleneckAnalyzer,
        HealthScoreCalculator
    )
    from modules.revenue_retention import (
        RevenueRetentionCalculator,
        MultiChannelGTM
    )
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.stop()

# ============= CONFIGURACIÓN =============
st.set_page_config(
    page_title="🎯 Sales Compensation Model - Final Version",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stNumberInput > div > div > input {
        background-color: #f0f2f6;
    }
    .compensation-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 10px;
        background: #f0f2f6;
        border-radius: 10px;
    }
    .alert-box {
        padding: 25px 30px;
        border-radius: 15px;
        margin: 20px 0;
        border: 3px solid;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        font-size: 16px;
        font-weight: 600;
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff5252 0%, #f44336 100%);
        border-color: #d32f2f;
        color: white;
        animation: pulse-critical 2s infinite;
    }
    .alert-warning {
        background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%);
        border-color: #f57c00;
        color: white;
        animation: pulse-warning 3s infinite;
    }
    .alert-success {
        background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        border-color: #388e3c;
        color: white;
    }
    .alert-critical::before {
        content: '🚨';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
        animation: bounce 1s infinite;
    }
    .alert-warning::before {
        content: '⚠️';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
        animation: shake 2s infinite;
    }
    .alert-success::before {
        content: '✅';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
    }
    @keyframes pulse-critical {
        0% { box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(244, 67, 54, 0.6); }
        100% { box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3); }
    }
    @keyframes pulse-warning {
        0% { box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(255, 152, 0, 0.5); }
        100% { box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3); }
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    .alert-title {
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .alert-message {
        font-size: 16px;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .alert-action {
        background: rgba(255,255,255,0.2);
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 4px solid rgba(255,255,255,0.5);
        font-size: 15px;
        font-weight: 700;
        margin-top: 15px;
    }
    .sensitivity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for dynamic values
if 'cost_input_type' not in st.session_state:
    st.session_state.cost_input_type = 'CPL'
if 'compensation_mode' not in st.session_state:
    st.session_state.compensation_mode = 'simple'
if 'reverse_target' not in st.session_state:
    st.session_state.reverse_target = None

# ============= HEADER =============
st.title("💎 Sales Compensation Model - Improved Final Version")
st.markdown("**Complete integration with proper calculations and flexible inputs**")

# Hide the sidebar since everything is now in the main view
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ============= SIDEBAR - IMPROVED INPUTS (KEPT FOR BACKWARDS COMPATIBILITY) =============
st.sidebar.title("⚙️ Model Configuration")

# SECTION 1: REVENUE TARGETS (Flexible)
st.sidebar.header("🎯 1. Revenue Targets")

col1, col2 = st.sidebar.columns(2)
with col1:
    target_period = st.sidebar.selectbox(
        "Input Period",
        ["Annual", "Monthly", "Weekly", "Daily"],
        index=1
    )
with col2:
    if target_period == "Annual":
        revenue_input = st.sidebar.number_input("Annual Target ($)", value=50000000, step=1000000)
        monthly_revenue_target = revenue_input / 12
    elif target_period == "Monthly":
        revenue_input = st.sidebar.number_input("Monthly Target ($)", value=4166667, step=100000)
        monthly_revenue_target = revenue_input
    elif target_period == "Weekly":
        revenue_input = st.sidebar.number_input("Weekly Target ($)", value=961538, step=25000)
        monthly_revenue_target = revenue_input * 4.33
    else:  # Daily
        revenue_input = st.sidebar.number_input("Daily Target ($)", value=192308, step=5000)
        monthly_revenue_target = revenue_input * 21.67

# Show all breakdowns
annual_revenue = monthly_revenue_target * 12
# Fixed spacing in revenue breakdown with black background
st.sidebar.markdown(f"""
<div style="background: #121212; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3; color: white;">
    <h4 style="margin: 0; color: #64B5F6;">📊 Revenue Breakdown</h4>
    <div style="margin-top: 10px; line-height: 1.8; color: white;">
        • <b>Annual:</b> ${annual_revenue:,.0f}<br>
        • <b>Monthly:</b> ${monthly_revenue_target:,.0f}<br>
        • <b>Weekly:</b> ${monthly_revenue_target/4.33:,.0f}<br>
        • <b>Daily:</b> ${monthly_revenue_target/21.67:,.0f}
    </div>
</div>
""", unsafe_allow_html=True)

# SECTION 2: TEAM CONTROL (Improved from fixed)
st.sidebar.header("👥 2. Team Structure")

# Better layout with clear categories
st.sidebar.markdown("""<div style="background: #121212; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><h5 style="margin: 0; color: #81C784;">🏢 Sales Team</h5></div>""", unsafe_allow_html=True)
col1, col2 = st.sidebar.columns(2)
with col1:
    num_closers = st.sidebar.number_input(
        "💼 Closers", min_value=0, max_value=50, value=8, step=1,
        help="Active closers handling meetings"
    )
    num_setters = st.sidebar.number_input(
        "📞 Setters", min_value=0, max_value=50, value=4, step=1,
        help="SDRs setting appointments"
    )
with col2:
    num_bench = st.sidebar.number_input(
        "🏈 Bench", min_value=0, max_value=20, value=2, step=1,
        help="In recovery/training"
    )
    num_managers = st.sidebar.number_input(
        "👔 Managers", min_value=0, max_value=10, value=2, step=1,
        help="Team leads & supervisors"
    )

# Team metrics
team_total = num_closers + num_setters + num_bench + num_managers
active_ratio = (num_closers + num_setters) / max(1, team_total)
setter_closer_ratio = num_setters / max(1, num_closers)

# Alerts for team structure
team_alerts = []
if num_bench / max(1, team_total) > 0.25:
    team_alerts.append("⚠️ >25% on bench indicates training issues")
if setter_closer_ratio < 0.5:
    team_alerts.append("⚠️ Low setter:closer ratio may limit lead coverage")
if setter_closer_ratio > 2:
    team_alerts.append("⚠️ High setter:closer ratio may create bottlenecks")

# Fixed spacing in team metrics with black background
st.sidebar.markdown(f"""
<div style="background: #121212; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; color: white;">
    <h4 style="margin: 0; color: #81C784;">👥 Team Metrics</h4>
    <div style="margin-top: 10px; line-height: 1.8; color: white;">
        • <b>Total:</b> {team_total} people<br>
        • <b>Active:</b> {active_ratio:.0%}<br>
        • <b>S:C Ratio:</b> {setter_closer_ratio:.1f}:1
    </div>
</div>
""", unsafe_allow_html=True)

if team_alerts:
    for alert in team_alerts:
        st.sidebar.warning(alert)

# SECTION 3: LEAD GENERATION (Flexible input)
st.sidebar.header("📈 3. Lead Generation")

# Choose input method
cost_input_type = st.sidebar.radio(
    "Cost Input Method",
    ["CPL (Cost per Lead)", "CPA (Cost per Appointment)", "Total Budget"],
    index=0
)

if cost_input_type == "CPL (Cost per Lead)":
    cost_value = st.sidebar.number_input(
        "Cost per Lead ($)", min_value=0, max_value=1000, value=150, step=10
    )
    cost_type = "CPL"
elif cost_input_type == "CPA (Cost per Appointment)":
    cost_value = st.sidebar.number_input(
        "Cost per Appointment ($)", min_value=0, max_value=5000, value=500, step=50
    )
    cost_type = "CPA"
else:
    cost_value = st.sidebar.number_input(
        "Monthly Marketing Budget ($)", min_value=0, max_value=1000000, value=100000, step=5000
    )
    cost_type = "Total Budget"

# Lead volume (can be input or calculated)
if cost_type != "Total Budget":
    daily_leads = st.sidebar.number_input(
        "Daily Lead Volume", min_value=0, max_value=2000, value=155, step=5
    )
else:
    # Calculate leads from budget
    estimated_cpl = 150  # Default assumption
    daily_leads = (cost_value / estimated_cpl) / 30

monthly_leads = daily_leads * 30

# SECTION 4: DEFAULT RATES (Used only if no channels configured)
st.sidebar.header("📊 4. Channel Configuration")
st.sidebar.info("🚀 Configure channels in the main view for granular control")
st.sidebar.markdown("**Default rates (fallback):**")

# Default conversion rates (used only when no channels are configured)
contact_rate = 0.60  # Default 60%
meeting_rate = 0.35  # Default 35%
show_up_rate = 0.75  # Default 75%
close_rate = 0.25    # Default 25%
onboard_rate = 0.95  # Default 95%

# Display defaults for reference
st.sidebar.text(f"• Contact: {contact_rate*100:.0f}%")
st.sidebar.text(f"• Meeting: {meeting_rate*100:.0f}%")
st.sidebar.text(f"• Show-up: {show_up_rate*100:.0f}%")
st.sidebar.text(f"• Close: {close_rate*100:.0f}%")

# Post-sale metrics (still needed for all channels)
st.sidebar.markdown("""<div style="background: #121212; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><h5 style="margin: 0; color: #64B5F6;">🔄 Retention Metrics</h5></div>""", unsafe_allow_html=True)
grr_rate = st.sidebar.number_input(
    "GRR @ 18m (%)", min_value=0, max_value=100, value=90, step=5
) / 100

# SECTION 5: DEAL ECONOMICS - Insurance Model (Allianz)
st.sidebar.header("💰 5. Deal Economics")

st.sidebar.markdown("**Insurance Contract Model**")
avg_pm = st.sidebar.number_input(
    "Monthly Premium (MXN)",
    min_value=1000, max_value=10000, value=3000, step=100,
    help="Monthly premium paid by client (e.g., $3,000 MXN)"
)

contract_years = st.sidebar.number_input(
    "Contract Length (years)",
    min_value=1, max_value=30, value=25, step=1,
    help="Insurance contract duration (e.g., 25 years)"
)

# Allianz/Insurance carrier compensation model
carrier_rate = st.sidebar.slider(
    "Carrier Compensation Rate (%)",
    min_value=1.0, max_value=5.0, value=2.7, step=0.1,
    help="% of total premium that carrier pays as compensation"
) / 100

# Calculate total compensation based on insurance model
contract_months = contract_years * 12
total_contract_value = avg_pm * contract_months
total_comp = total_contract_value * carrier_rate  # What corporation receives

# Payment split (70/30 structure)
immediate_pct = st.sidebar.slider(
    "Upfront Payment (%)",
    min_value=50, max_value=100, value=70, step=5,
    help="% paid immediately upon closing"
) / 100
deferred_pct = 1 - immediate_pct

comp_immediate = total_comp * immediate_pct  # Paid upfront
comp_deferred = total_comp * deferred_pct    # Paid at month 18

# Display deal economics summary
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Deal Summary**")
st.sidebar.info(f"""
• Contract Value: ${total_contract_value:,.0f} MXN
• Total Comp (2.7%): ${total_comp:,.0f} MXN
• Upfront (70%): ${comp_immediate:,.0f} MXN
• Month 18 (30%): ${comp_deferred:,.0f} MXN
""")

st.sidebar.success(f"""
**Per Sale Value:**
• Total: ${total_comp:,.0f}
• Immediate (70%): ${comp_immediate:,.0f}
• Deferred (30%): ${comp_deferred:,.0f}
""")

# SECTION 6: COMPENSATION (Improved modular)
st.sidebar.header("💸 6. Compensation Structure")

comp_mode = st.sidebar.radio(
    "Configuration Mode",
    ["Simple (% split)", "Custom per Role"],
    index=0
)

if comp_mode == "Simple (% split)":
    # Simple mode with single base %
    base_pct = st.sidebar.slider(
        "Base Salary %", min_value=20, max_value=60, value=40, step=5
    ) / 100
    
    # OTE inputs
    closer_ote = st.sidebar.number_input("Closer OTE ($)", value=80000, step=5000)
    setter_ote = st.sidebar.number_input("Setter OTE ($)", value=40000, step=2500)
    manager_ote = st.sidebar.number_input("Manager OTE ($)", value=120000, step=10000)
    
    # Calculate compensation
    roles_comp = {
        'closer': {
            'count': num_closers,
            'base': closer_ote * base_pct,
            'variable': closer_ote * (1 - base_pct),
            'ote': closer_ote
        },
        'setter': {
            'count': num_setters,
            'base': setter_ote * base_pct,
            'variable': setter_ote * (1 - base_pct),
            'ote': setter_ote
        },
        'manager': {
            'count': num_managers,
            'base': manager_ote * 0.6,  # Managers typically 60% base
            'variable': manager_ote * 0.4,
            'ote': manager_ote
        },
        'bench': {
            'count': num_bench,
            'base': 25000 * 0.5,  # Bench at 50% of reduced OTE
            'variable': 25000 * 0.5,
            'ote': 25000
        }
    }
    
else:
    # Custom mode - individual inputs
    st.sidebar.markdown("""<div style="background: #121212; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><h5 style="margin: 0; color: #BA68C8;">💰 Custom Base/Variable per Role</h5></div>""", unsafe_allow_html=True)
    
    roles_comp = {}
    
    # Closer compensation
    st.sidebar.markdown("""<div style="background: #1E1E1E; color: white; padding: 8px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #FFA726;"><b>💼 Closers</b></div>""", unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        closer_base = st.sidebar.number_input("Base ($)", value=32000, step=2500, key="c_base")
    with col2:
        closer_var = st.sidebar.number_input("Variable ($)", value=48000, step=2500, key="c_var")
    roles_comp['closer'] = {
        'count': num_closers, 'base': closer_base, 
        'variable': closer_var, 'ote': closer_base + closer_var
    }
    
    # Setter compensation
    st.sidebar.markdown("""<div style="background: #1E1E1E; color: white; padding: 8px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #42A5F5;"><b>📞 Setters</b></div>""", unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        setter_base = st.sidebar.number_input("Base ($)", value=16000, step=1000, key="s_base")
    with col2:
        setter_var = st.sidebar.number_input("Variable ($)", value=24000, step=1000, key="s_var")
    roles_comp['setter'] = {
        'count': num_setters, 'base': setter_base,
        'variable': setter_var, 'ote': setter_base + setter_var
    }
    
    # Manager compensation
    st.sidebar.markdown("""<div style="background: #1E1E1E; color: white; padding: 8px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #EC407A;"><b>👔 Managers</b></div>""", unsafe_allow_html=True)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        manager_base = st.sidebar.number_input("Base ($)", value=72000, step=5000, key="m_base")
    with col2:
        manager_var = st.sidebar.number_input("Variable ($)", value=48000, step=5000, key="m_var")
    roles_comp['manager'] = {
        'count': num_managers, 'base': manager_base,
        'variable': manager_var, 'ote': manager_base + manager_var
    }
    
    # Bench
    roles_comp['bench'] = {
        'count': num_bench, 'base': 12500, 'variable': 12500, 'ote': 25000
    }

# Calculate total compensation
comp_structure = ImprovedCompensationCalculator.calculate_custom_compensation(roles_comp)

# Commission structure
st.sidebar.markdown("""<div style="background: #121212; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px;"><h5 style="margin: 0; color: #FFD54F;">💵 Commission Splits</h5></div>""", unsafe_allow_html=True)
closer_comm_pct = st.sidebar.number_input(
    "Closer Pool %", min_value=10, max_value=30, value=20, step=1
) / 100
setter_comm_pct = st.sidebar.number_input(
    "Setter Pool %", min_value=0, max_value=10, value=3, step=1
) / 100

# SECTION 7: OPERATING COSTS
st.sidebar.header("💵 7. Operating Costs")

office_rent = st.sidebar.number_input("Office Rent", value=20000, step=5000)
software_costs = st.sidebar.number_input("Software/Tools", value=10000, step=1000)
other_opex = st.sidebar.number_input("Other OpEx", value=5000, step=1000)

# Government fees
gov_fee_pct = st.sidebar.number_input(
    "Gov Fees %", min_value=0, max_value=30, value=10, step=1
) / 100

# SECTION 8: PROJECTION
st.sidebar.header("📅 8. Projection Settings")

projection_months = st.sidebar.selectbox(
    "Projection Horizon",
    [6, 12, 18, 24, 36],
    index=2
)

sales_cycle_days = st.sidebar.number_input(
    "Sales Cycle (days)", min_value=7, max_value=180, value=20, step=1
)

# ============= CALCULATIONS =============

# Initialize with zeros - will be calculated from channels
monthly_contacts = 0
monthly_meetings_scheduled = 0
monthly_meetings_held = 0
monthly_sales = 0
monthly_onboarded = 0
monthly_meetings = 0

# These will be overridden by channel calculations
# Only use legacy calculations if no channels are defined
if 'gtm_channels' not in st.session_state or len(st.session_state.gtm_channels) == 0:
    # Fallback to simple calculations for initial state
    monthly_contacts = monthly_leads * contact_rate
    monthly_meetings_scheduled = monthly_contacts * meeting_rate
    monthly_meetings_held = monthly_meetings_scheduled * show_up_rate
    monthly_sales = monthly_meetings_held * close_rate
    monthly_onboarded = monthly_sales * onboard_rate
    monthly_meetings = monthly_meetings_held

# Cost calculations
volume_metrics = {
    'leads': monthly_leads,
    'contact_rate': contact_rate,
    'meeting_rate': meeting_rate,
    'show_up_rate': show_up_rate,
    'close_rate': close_rate,
    'avg_deal_value': comp_immediate
}

cost_breakdown = ImprovedCostCalculator.calculate_acquisition_costs(
    cost_type, cost_value, volume_metrics
)

# Revenue calculations - safe calculation even during configuration
try:
    revenue_timeline = EnhancedRevenueCalculator.calculate_monthly_timeline(
        max(monthly_sales, 0), avg_pm, projection_months,
        carrier_rate, 0.7, 0.3, grr_rate, 0.0
    )
except:
    revenue_timeline = []

# Current month values - safe calculations
monthly_revenue_immediate = max(monthly_sales, 0) * comp_immediate
monthly_revenue_deferred = 0  # Month 1 has no deferred
monthly_revenue_total = monthly_revenue_immediate

# Month 18 values (if applicable)
if projection_months >= 18:
    month_18_revenue_immediate = monthly_sales * comp_immediate
    month_18_revenue_deferred = monthly_sales * comp_deferred * grr_rate
    month_18_revenue_total = month_18_revenue_immediate + month_18_revenue_deferred
else:
    month_18_revenue_immediate = monthly_revenue_immediate
    month_18_revenue_deferred = 0
    month_18_revenue_total = monthly_revenue_total

# Cost structure for P&L
monthly_marketing = cost_breakdown.get('total_marketing_spend', cost_breakdown.get('cost_per_lead', 0) * monthly_leads)
monthly_commissions = monthly_revenue_immediate * (closer_comm_pct + setter_comm_pct)
monthly_base_salaries = comp_structure['monthly_base']
monthly_opex = office_rent + software_costs + other_opex
monthly_costs_before_fees = monthly_marketing + monthly_commissions + monthly_base_salaries + monthly_opex
monthly_gov_fees = monthly_revenue_total * gov_fee_pct
monthly_total_costs = monthly_costs_before_fees + monthly_gov_fees

# EBITDA
monthly_ebitda = monthly_revenue_total - monthly_total_costs
ebitda_margin = monthly_ebitda / monthly_revenue_total if monthly_revenue_total > 0 else 0

# Unit Economics
ltv = comp_immediate + (comp_deferred * grr_rate)
cac = cost_breakdown['cost_per_sale'] + (monthly_commissions / monthly_sales if monthly_sales > 0 else 0)
ltv_cac_ratio = ltv / cac if cac > 0 else 0
payback_months = cac / (comp_immediate / 12) if comp_immediate > 0 else 999  # Months to recover CAC
roas = monthly_revenue_target / monthly_marketing if monthly_marketing > 0 else 0  # Return on Ad Spend

# Current state for reverse engineering
current_state = {
    'monthly_revenue': monthly_revenue_total,
    'monthly_sales': monthly_sales,
    'monthly_meetings': monthly_meetings,
    'monthly_leads': monthly_leads,
    'monthly_ebitda': monthly_ebitda,
    'ebitda_margin': ebitda_margin,
    'num_closers': num_closers,
    'num_setters': num_setters,
    'close_rate': close_rate,
    'meeting_rate': meeting_rate,
    'contact_rate': contact_rate,
    'avg_deal_value': comp_immediate,
    'cost_per_lead': cost_breakdown['cost_per_lead'],
    'ltv': ltv,
    'cac': cac,
    'total_costs': monthly_total_costs
}

# ============= MAIN DASHBOARD =============

# Top metrics moved to consolidated Business Performance Dashboard section
# All metrics are now displayed in the aggregated section below


def get_capacity_metrics(default_closers, default_setters, fallback_working_days=20, fallback_closer_meetings=3.0, fallback_setter_meetings=2.0):
    """Return capacity configuration and derived totals based on stored settings."""
    settings = st.session_state.get('team_capacity_settings', {})
    working_days = settings.get('working_days', fallback_working_days)
    meetings_per_closer = settings.get('meetings_per_closer', fallback_closer_meetings)
    meetings_per_setter = settings.get('meetings_per_setter', fallback_setter_meetings)
    per_closer_monthly_capacity = meetings_per_closer * working_days
    per_setter_monthly_capacity = meetings_per_setter * working_days
    monthly_closer_capacity = settings.get('monthly_closer_capacity', default_closers * per_closer_monthly_capacity)
    monthly_setter_capacity = settings.get('monthly_setter_capacity', default_setters * per_setter_monthly_capacity)
    return {
        'working_days': working_days,
        'meetings_per_closer': meetings_per_closer,
        'meetings_per_setter': meetings_per_setter,
        'per_closer_monthly_capacity': per_closer_monthly_capacity,
        'per_setter_monthly_capacity': per_setter_monthly_capacity,
        'monthly_closer_capacity': monthly_closer_capacity,
        'monthly_setter_capacity': monthly_setter_capacity
    }

# ============= ALERTS AND SUGGESTIONS (Improved) =============

# Dynamic alerts based on current state
alerts = []
suggestions = []

# Check revenue gap with enhanced urgency
revenue_gap = monthly_revenue_target - monthly_revenue_total
if revenue_gap > 0:
    gap_pct = (revenue_gap / monthly_revenue_target) * 100
    if gap_pct > 30:
        alert_type = 'critical'
        urgency = '🔥 CRITICAL SHORTFALL'
    elif gap_pct > 15:
        alert_type = 'critical' 
        urgency = '⚠️ MAJOR GAP'
    else:
        alert_type = 'warning'
        urgency = '📊 BELOW TARGET'
    
    # Calculate required metrics safely
    required_sales = revenue_gap / comp_immediate if comp_immediate > 0 else 0
    required_close_rate = (monthly_sales * monthly_revenue_target / max(monthly_revenue_total, 1)) / max(monthly_meetings, 1)
    
    alerts.append({
        'type': alert_type,
        'message': f'{urgency}: Revenue shortfall of ${revenue_gap:,.0f} ({gap_pct:.1f}% below target) - Missing {required_sales:.0f} sales',
        'action': f'URGENT: Increase sales by {required_sales:.0f} units/month OR improve close rate to {required_close_rate:.1%}'
    })

cap_settings_global = get_capacity_metrics(num_closers, num_setters)
working_days_effective = max(cap_settings_global['working_days'], 1)
monthly_closer_capacity_global = cap_settings_global['monthly_closer_capacity']
monthly_setter_capacity_global = cap_settings_global['monthly_setter_capacity']
per_closer_capacity = max(cap_settings_global['per_closer_monthly_capacity'], 1)
per_setter_capacity = max(cap_settings_global['per_setter_monthly_capacity'], 1)
capacity_util = monthly_meetings / monthly_closer_capacity_global if monthly_closer_capacity_global > 0 else 0
setter_util_global = monthly_meetings_scheduled / monthly_setter_capacity_global if monthly_setter_capacity_global > 0 else 0

# Check team capacity with multiple thresholds
if capacity_util > 0.95:
    high_capacity_target = per_closer_capacity * num_closers * 0.8
    excess_meetings_high = monthly_meetings - high_capacity_target
    additional_closers_high = np.ceil(max(excess_meetings_high, 0) / per_closer_capacity) if per_closer_capacity > 0 else 0
    meeting_reduction_high = (max(excess_meetings_high, 0) / monthly_meetings * 100) if monthly_meetings > 0 else 0
    alerts.append({
        'type': 'critical',
        'message': f'🚨 TEAM OVERLOAD: {capacity_util:.0%} capacity - Quality degradation imminent, burnout risk HIGH',
        'action': f'IMMEDIATE: Hire {additional_closers_high:.0f} closers OR cut meetings by {meeting_reduction_high:.0f}%'
    })
elif capacity_util > 0.85:
    warn_capacity_target = per_closer_capacity * num_closers * 0.75
    excess_meetings_warn = monthly_meetings - warn_capacity_target
    additional_closers_warn = np.ceil(max(excess_meetings_warn, 0) / per_closer_capacity) if per_closer_capacity > 0 else 0
    alerts.append({
        'type': 'warning',
        'message': f'⚠️ HIGH UTILIZATION: {capacity_util:.0%} capacity - Approaching danger zone',
        'action': f'Plan hiring: Need {additional_closers_warn:.0f} closers within 30 days to maintain quality'
    })

# Check LTV:CAC with severity levels
if ltv_cac_ratio < 2:
    alerts.append({
        'type': 'critical',
        'message': f'💀 UNSUSTAINABLE ECONOMICS: LTV:CAC {ltv_cac_ratio:.1f}:1 - Business model failing, immediate action required',
        'action': f'EMERGENCY: Reduce CAC by ${cac - ltv/3:.0f} ({((cac - ltv/3)/cac)*100:.0f}%) OR increase LTV by ${ltv*3/ltv_cac_ratio - ltv:.0f}'
    })
elif ltv_cac_ratio < 3:
    target_cac = ltv / 3
    cac_reduction = cac - target_cac
    alerts.append({
        'type': 'warning',
        'message': f'📉 POOR UNIT ECONOMICS: LTV:CAC {ltv_cac_ratio:.1f}:1 below healthy 3:1 benchmark',
        'action': f'Optimize: Reduce CAC by ${cac_reduction:.0f} through better targeting, conversion, or pricing'
    })

# Check conversion rates with benchmarks
if close_rate < 0.15:
    alerts.append({
        'type': 'critical',
        'message': f'💔 CRITICAL CONVERSION: {close_rate:.1%} close rate - Massive efficiency loss, wasting {(1-close_rate)*100:.0f}% of meetings',
        'action': f'URGENT: Sales training + lead quality audit. Target: 25% close rate (+{(0.25-close_rate)*100:.1f} points)'
    })
elif close_rate < 0.2:
    alerts.append({
        'type': 'warning',
        'message': f'📊 BELOW BENCHMARK: {close_rate:.1%} close rate under industry standard (20-25%)',
        'action': f'Improve sales process: Need +{(0.22-close_rate)*100:.1f} percentage points to reach 22% benchmark'
    })

# Check contact rate
if contact_rate < 0.5:
    wasted_leads = monthly_leads * (1 - contact_rate)
    alerts.append({
        'type': 'warning',
        'message': f'📞 POOR LEAD CONTACT: {contact_rate:.1%} contact rate - Wasting {wasted_leads:.0f} leads/month (${wasted_leads * cost_breakdown["cost_per_lead"]:,.0f})',
        'action': f'Fix lead routing/quality OR increase setter capacity. Target: 60% contact rate'
    })

# Check EBITDA margin
if ebitda_margin < 0:
    alerts.append({
        'type': 'critical',
        'message': f'🔴 LOSING MONEY: {ebitda_margin:.1%} EBITDA margin - Business is unprofitable',
        'action': f'EMERGENCY: Cut costs by ${abs(monthly_ebitda):,.0f}/month OR increase revenue by ${abs(monthly_ebitda)/0.25:,.0f}/month'
    })
elif ebitda_margin < 0.15:
    alerts.append({
        'type': 'warning',
        'message': f'📉 THIN MARGINS: {ebitda_margin:.1%} EBITDA margin below healthy 20-25% range',
        'action': f'Optimize operations: Improve margin by {(0.2 - ebitda_margin)*100:.1f} percentage points'
    })

# Check pipeline coverage
pipeline_coverage = (monthly_meetings * comp_immediate / close_rate) / monthly_revenue_target if monthly_revenue_target > 0 else 0
if pipeline_coverage < 2:
    alerts.append({
        'type': 'critical',
        'message': f'🔍 INSUFFICIENT PIPELINE: {pipeline_coverage:.1f}x coverage - High risk of missing targets',
        'action': f'URGENT: Increase pipeline to {monthly_revenue_target * 3 / comp_immediate:.0f} opportunities (need {(3 - pipeline_coverage) * monthly_revenue_target / comp_immediate:.0f} more)'
    })

# Check show-up rate
if show_up_rate < 0.7:
    no_shows_monthly = monthly_meetings_scheduled * (1 - show_up_rate)
    wasted_cost = no_shows_monthly * cost_breakdown.get('cost_per_meeting_scheduled', 0)
    alerts.append({
        'type': 'warning',
        'message': f'😞 POOR SHOW-UP RATE: {show_up_rate:.1%} attendance - Wasting {no_shows_monthly:.0f} meetings/month',
        'action': f'Implement confirmation system, reschedule policies, or meeting incentives. Potential savings: ${wasted_cost:,.0f}/month'
    })

# Sort alerts by severity (critical first)
alerts.sort(key=lambda x: 0 if x['type'] == 'critical' else 1)

# Display alerts in a dropdown for cleaner UI
if alerts:
    # Count critical vs warning alerts
    critical_count = sum(1 for alert in alerts if alert['type'] == 'critical')
    warning_count = len(alerts) - critical_count
    
    # Create expander with count in title
    alert_title = f"🚨 **Business Alerts & Recommendations** ({critical_count} critical, {warning_count} warnings)"
    with st.expander(alert_title, expanded=False):
        for i, alert in enumerate(alerts):
            alert_class = 'alert-critical' if alert['type'] == 'critical' else 'alert-warning'
            alert_icon = '🔴' if alert['type'] == 'critical' else '⚠️'
            
            # Enhanced alert with dramatic visual impact
            st.markdown(
                f'''
                <div class="alert-box {alert_class}">
                    <div class="alert-title">
                        {alert_icon} Alert #{i+1}: {alert['type'].upper()} Issue Detected
                    </div>
                    <div class="alert-message">
                        {alert["message"]}
                    </div>
                    <div class="alert-action">
                        🎯 RECOMMENDED ACTION: {alert["action"]}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            # Add spacing between alerts
            st.markdown('<div style="margin: 15px 0;"></div>', unsafe_allow_html=True)
else:
    # Show success state when no alerts
    st.markdown(
        f'''
        <div class="alert-box alert-success">
            <div class="alert-title">🎉 ALL SYSTEMS HEALTHY</div>
            <div class="alert-message">
                No critical issues detected. Your sales model is performing within healthy parameters.
            </div>
            <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div style="text-align: center; background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 28px; font-weight: 900;">{monthly_revenue_total / monthly_revenue_target if monthly_revenue_target > 0 else 0:.0%}</div>
                    <div style="font-size: 12px; opacity: 0.9;">TARGET ACHIEVEMENT</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 28px; font-weight: 900;">{ltv_cac_ratio:.1f}:1</div>
                    <div style="font-size: 12px; opacity: 0.9;">LTV:CAC RATIO</div>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.2); padding: 15px; border-radius: 10px;">
                    <div style="font-size: 28px; font-weight: 900;">{capacity_util:.0%}</div>
                    <div style="font-size: 12px; opacity: 0.9;">CAPACITY USED</div>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# ============= HEALTH MONITORING (Moved from Critical Alerts) =============

# This section shows health metrics and recommendations in a calmer way
# Actual critical alerts logic is preserved but displayed differently in the main tab

# ============= MAIN TABS =============

tabs = st.tabs([
    "🎯 GTM Command Center",
    "💰 Costos Unit",
    "💵 Compensación",
    "📊 P&L Detallado",
    "🚀 Simulador",
    "🔄 Ingeniería Inversa"
])

# TAB 1: BOWTIE & MULTI-CHANNEL GTM INTEGRATED
with tabs[0]:
    st.header("🎯 GTM Command Center")
    st.markdown("**Unified view of your Go-to-Market strategy with all KPIs**")
    
    # Configuration Sections - All inputs in main view
    st.markdown("### ⚙️ Configuration Center")
    st.markdown("Configure all parameters directly in the main view with immediate feedback")
    
    # Revenue Targets Configuration
    with st.expander("🎯 **Revenue Targets**", expanded=True):
        rev_col1, rev_col2, rev_col3 = st.columns(3)
        
        with rev_col1:
            target_period_main = st.selectbox(
                "Input Period",
                ["Annual", "Monthly", "Weekly", "Daily"],
                index=1,
                key="target_period_main"
            )
            
            if target_period_main == "Annual":
                revenue_input_main = st.number_input("Annual Target ($)", value=50000000, step=1000000, key="rev_annual_main")
                monthly_revenue_target_main = revenue_input_main / 12
            elif target_period_main == "Monthly":
                revenue_input_main = st.number_input("Monthly Target ($)", value=4166667, step=100000, key="rev_monthly_main")
                monthly_revenue_target_main = revenue_input_main
            elif target_period_main == "Weekly":
                revenue_input_main = st.number_input("Weekly Target ($)", value=961538, step=25000, key="rev_weekly_main")
                monthly_revenue_target_main = revenue_input_main * 4.33
            else:  # Daily
                revenue_input_main = st.number_input("Daily Target ($)", value=192308, step=5000, key="rev_daily_main")
                monthly_revenue_target_main = revenue_input_main * 21.67
        
        with rev_col2:
            st.markdown("**📊 Revenue Breakdown**")
            annual_revenue_main = monthly_revenue_target_main * 12
            st.metric("Annual", f"${annual_revenue_main:,.0f}")
            st.metric("Monthly", f"${monthly_revenue_target_main:,.0f}")
            st.metric("Daily", f"${monthly_revenue_target_main/21.67:,.0f}")
        
        with rev_col3:
            st.markdown("**🎯 Impact Metrics**")
            sales_needed = monthly_revenue_target_main / comp_immediate if comp_immediate > 0 else 0
            st.metric("Sales Needed", f"{sales_needed:.0f}/mo")
            st.metric("Revenue/Sale", f"${comp_immediate:,.0f}")
            st.metric("Target vs Current", f"{(monthly_revenue_total/monthly_revenue_target_main*100):.0f}%")
    
    # Pull latest GTM metrics (updates set after channel aggregation)
    gtm_metrics = st.session_state.get('gtm_metrics', {})
    gtm_monthly_leads = gtm_metrics.get('monthly_leads', monthly_leads)
    gtm_monthly_meetings_scheduled = gtm_metrics.get('monthly_meetings_scheduled', monthly_meetings_scheduled)
    gtm_monthly_meetings = gtm_metrics.get('monthly_meetings', monthly_meetings)
    gtm_monthly_sales = gtm_metrics.get('monthly_sales', monthly_sales)
    gtm_monthly_revenue_immediate = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate)
    gtm_blended_contact_rate = gtm_metrics.get('blended_contact_rate', contact_rate)

    # Team Structure Configuration
    with st.expander("👥 **Team Structure**", expanded=False):
        team_col1, team_col2, team_col3 = st.columns(3)
        
        with team_col1:
            st.markdown("**Sales Team**")
            num_closers_main = st.number_input("💼 Closers", min_value=0, max_value=50, value=num_closers, step=1, key="closers_main")
            num_setters_main = st.number_input("📞 Setters", min_value=0, max_value=50, value=num_setters, step=1, key="setters_main")
            num_bench_main = st.number_input("🏋 Bench", min_value=0, max_value=20, value=num_bench, step=1, key="bench_main")
            num_managers_main = st.number_input("👔 Managers", min_value=0, max_value=10, value=num_managers, step=1, key="managers_main")
            st.markdown("**Capacity Settings**")
            meetings_per_closer = st.number_input(
                "Meetings/Closer/Day",
                min_value=0.0,
                value=3.0,
                step=0.1,
                help="Average meetings each closer can run per working day"
            )
            working_days = st.number_input(
                "Working Days/Month",
                min_value=10,
                max_value=26,
                value=20,
                step=1,
                help="Number of active selling days per month"
            )
            meetings_per_setter = st.number_input(
                "Meetings Booked/Setter/Day",
                min_value=0.0,
                value=2.0,
                step=0.1,
                help="Average meetings each setter confirms and books per day"
            )
        
        with team_col2:
            st.markdown("**Team Metrics**")
            team_total_main = num_closers_main + num_setters_main + num_bench_main + num_managers_main
            active_ratio_main = (num_closers_main + num_setters_main) / max(1, team_total_main)
            setter_closer_ratio_main = num_setters_main / max(1, num_closers_main)
            st.metric("Total Team", f"{team_total_main}")
            st.metric("Active Ratio", f"{active_ratio_main:.0%}")
            st.metric("S:C Ratio", f"{setter_closer_ratio_main:.1f}:1")
        
        with team_col3:
            st.markdown("**Capacity Analysis**")
            monthly_closer_capacity = num_closers_main * meetings_per_closer * working_days
            capacity_util_main = gtm_monthly_meetings / monthly_closer_capacity if monthly_closer_capacity > 0 else 0
            st.metric("Closer Capacity", f"{monthly_closer_capacity:,.0f} meetings/mo")
            monthly_setter_capacity = num_setters_main * meetings_per_setter * working_days
            setter_util = gtm_monthly_meetings_scheduled / monthly_setter_capacity if monthly_setter_capacity > 0 else 0
            st.metric("Setter Booking Capacity", f"{monthly_setter_capacity:,.0f} meetings/mo")
            st.metric("Utilization", f"{capacity_util_main:.0%}")
            st.metric("Setter Utilization", f"{setter_util:.0%}")
            if capacity_util_main > 0.9:
                st.warning("⚠️ Overloaded!")
            elif capacity_util_main > 0.75:
                st.info("🟡 Near capacity")
            else:
                st.success("✅ Healthy capacity")

            st.session_state['team_capacity_settings'] = {
                'meetings_per_closer': meetings_per_closer,
                'meetings_per_setter': meetings_per_setter,
                'working_days': working_days,
                'monthly_closer_capacity': monthly_closer_capacity,
                'monthly_setter_capacity': monthly_setter_capacity
            }
        
        # Daily Activities Section within Team Structure
        st.markdown("**Daily Activity Requirements**")
        daily_col1, daily_col2, daily_col3 = st.columns(3)
        
        daily_leads = gtm_monthly_leads / working_days if working_days > 0 else 0
        daily_contacts = daily_leads * gtm_blended_contact_rate
        daily_meetings_scheduled = gtm_monthly_meetings_scheduled / working_days if working_days > 0 else 0
        daily_meetings = gtm_monthly_meetings / working_days if working_days > 0 else 0
        daily_sales = gtm_monthly_sales / working_days if working_days > 0 else 0
        daily_revenue = gtm_monthly_revenue_immediate / working_days if working_days > 0 else 0
        
        with daily_col1:
            st.markdown("**Per Setter:**")
            if num_setters_main > 0:
                setter_metrics = {
                    "Leads to process": f"{daily_leads/num_setters_main:.1f}",
                    "Contacts to make": f"{daily_contacts/num_setters_main:.1f}",
                    "Meetings to book": f"{daily_meetings_scheduled/num_setters_main:.1f}",
                    "Capacity target": f"{meetings_per_setter:.1f} bookings"
                }
                for metric, value in setter_metrics.items():
                    st.write(f"🔹 {metric}: {value}")
        
        with daily_col2:
            st.markdown("**Per Closer:**")
            if num_closers_main > 0:
                closer_metrics = {
                    "Meetings to run": f"{daily_meetings/num_closers_main:.1f}",
                    "Capacity target": f"{meetings_per_closer:.1f} meetings",
                    "Sales to close": f"{daily_sales/num_closers_main:.2f}",
                    "Revenue to generate": f"${(daily_revenue)/num_closers_main:,.0f}"
                }
                for metric, value in closer_metrics.items():
                    st.write(f"🔹 {metric}: {value}")
        
        with daily_col3:
            st.markdown("**Team Totals:**")
            team_metrics = {
                "Total leads/day": f"{daily_leads:.0f}",
                "Total meetings/day": f"{daily_meetings:.1f}",
                "Total sales/day": f"{daily_sales:.1f}",
                "Revenue/day": f"${daily_revenue:,.0f}"
            }
            for metric, value in team_metrics.items():
                st.write(f"🔹 {metric}: {value}")
    
    # Multi-Channel GTM is now the primary funnel configuration
    # Legacy conversion funnel removed - all configuration happens through channels
    
    # Deal Economics Configuration
    with st.expander("💰 **Deal Economics** (Used by All Channels)", expanded=False):
        st.info("⚠️ These values automatically apply to all channels")
        deal_col1, deal_col2, deal_col3 = st.columns(3)
        
        with deal_col1:
            st.markdown("**Insurance Contract Structure**")
            avg_pm_main = st.number_input("Monthly Premium (MXN)", value=avg_pm, step=100, key="avg_pm_main")
            contract_years_main = st.number_input("Contract Years", value=contract_years, min_value=1, max_value=30, key="contract_years_main")
            carrier_rate_main = st.slider("Carrier Rate %", 1.0, 5.0, carrier_rate*100, 0.1, key="carrier_rate_main") / 100
            
            # Recalculate based on insurance model
            total_contract_main = avg_pm_main * contract_years_main * 12
            total_comp_main = total_contract_main * carrier_rate_main
            comp_immediate_val = total_comp_main * 0.7
            comp_deferred_val = total_comp_main * 0.3
        
        with deal_col2:
            st.markdown("**Compensation Breakdown**")
            st.metric("Contract Value", f"${total_contract_main:,.0f} MXN")
            st.metric("Total Comp (2.7%)", f"${total_comp_main:,.0f}")
            st.metric("Upfront (70%)", f"${comp_immediate_val:,.0f}")
            st.metric("Month 18 (30%)", f"${comp_deferred_val:,.0f}")
        
        with deal_col3:
            st.markdown("**Per Deal Economics**")
            # Convert to USD for display (using 18:1 exchange rate)
            deal_size_usd = total_comp_main / 18
            monthly_value = avg_pm_main / 18
            st.metric("Deal Size (USD)", f"${deal_size_usd:,.0f}")
            st.metric("Monthly Premium (USD)", f"${monthly_value:,.0f}")
            st.metric("Contract Length", f"{contract_years_main} years")
            st.info(f"📊 Effective commission: {carrier_rate_main*100:.1f}% of premium")
    
    # Operating Costs Configuration (Marketing moved to channels)
    with st.expander("🏢 **Operating Costs**", expanded=False):
        ops_col1, ops_col2, ops_col3 = st.columns(3)
        
        with ops_col1:
            st.markdown("**Fixed Costs**")
            office_rent_main = st.number_input("Office Rent ($)", value=office_rent, step=500, key="rent_main")
            software_costs_main = st.number_input("Software ($)", value=software_costs, step=100, key="software_main")
            other_opex_main = st.number_input("Other OpEx ($)", value=other_opex, step=500, key="opex_main")
        
        with ops_col2:
            st.markdown("**Cost Summary**")
            total_opex_main = office_rent_main + software_costs_main + other_opex_main
            st.metric("Total OpEx", f"${total_opex_main:,.0f}/mo")
            st.metric("Annual OpEx", f"${total_opex_main*12:,.0f}")
            st.metric("Per Employee", f"${total_opex_main/max(1,team_total):.0f}")
        
        with ops_col3:
            st.markdown("**Efficiency Metrics**")
            opex_per_sale = total_opex_main / max(1, monthly_sales)
            opex_ratio = total_opex_main / max(1, monthly_revenue_total)
            st.metric("OpEx per Sale", f"${opex_per_sale:.0f}")
            st.metric("OpEx Ratio", f"{opex_ratio*100:.1f}%")
            if opex_ratio > 0.3:
                st.warning("🟡 High OpEx ratio")
            else:
                st.success("✅ Healthy OpEx")
    
    # What-If Analysis Configuration
    with st.expander("🔮 **What-If Scenario Analysis**", expanded=False):
        whatif_col1, whatif_col2 = st.columns(2)
        
        with whatif_col1:
            st.markdown("**Adjust Variables**")
            close_change = st.number_input("Close Rate Change (%)", min_value=-50, max_value=50, value=0, step=5, key="close_change_main")
            deal_change = st.number_input("Deal Size Change (%)", min_value=-50, max_value=50, value=0, step=5, key="deal_change_main")
            cost_change = st.number_input("Cost Reduction (%)", min_value=0, max_value=50, value=0, step=5, key="cost_change_main")
            team_change = st.number_input("Add Closers", min_value=0, max_value=10, value=0, step=1, key="team_change_main")
        
        with whatif_col2:
            st.markdown("**Impact Results**")
            
            # Close rate impact
            if close_change != 0:
                new_close = close_rate * (1 + close_change/100)
                new_sales = monthly_meetings * new_close
                impact_revenue = (new_sales - monthly_sales) * comp_immediate
                st.metric("Revenue from Close Rate", f"${impact_revenue:,.0f}", f"{close_change:+d}%")
            
            # Deal size impact
            if deal_change != 0:
                new_deal = comp_immediate * (1 + deal_change/100)
                impact_revenue = monthly_sales * (new_deal - comp_immediate)
                st.metric("Revenue from Deal Size", f"${impact_revenue:,.0f}", f"{deal_change:+d}%")
            
            # Cost reduction impact
            if cost_change != 0:
                cost_savings = monthly_costs_before_fees * (cost_change/100)
                new_ebitda = monthly_ebitda + cost_savings
                st.metric("EBITDA Improvement", f"${cost_savings:,.0f}", f"{cost_change}% saved")
            
            # Team expansion impact (uses current capacity settings)
            if team_change != 0:
                cap_settings = get_capacity_metrics(num_closers_main if 'num_closers_main' in locals() else num_closers,
                                                   num_setters_main if 'num_setters_main' in locals() else num_setters)
                meetings_per_closer_change = cap_settings['meetings_per_closer']
                working_days_change = cap_settings['working_days']
                capacity_increase = team_change * meetings_per_closer_change * working_days_change
                potential_sales = capacity_increase * close_rate
                potential_revenue = potential_sales * comp_immediate
                st.metric("Sales Potential", f"+{potential_sales:.0f} sales", f"${potential_revenue:,.0f}")
    
    # Use the main page values if they exist, otherwise use sidebar values
    if 'target_period_main' in locals():
        monthly_revenue_target = monthly_revenue_target_main
        annual_revenue = annual_revenue_main
    if 'num_closers_main' in locals():
        num_closers = num_closers_main
        num_setters = num_setters_main
        num_bench = num_bench_main
        num_managers = num_managers_main
        team_total = team_total_main
        active_ratio = active_ratio_main
    if 'contact_rate_main' in locals():
        contact_rate = contact_rate_main
        meeting_rate = meeting_rate_main
        show_up_rate = show_up_rate_main
        close_rate = close_rate_main
    if 'avg_pm_main' in locals():
        avg_pm = avg_pm_main
        if 'total_comp_main' in locals():
            total_comp = total_comp_main
            comp_immediate = comp_immediate_val
            comp_deferred = comp_deferred_val
        else:
            comp_immediate = comp_immediate_val
            comp_deferred = comp_deferred_val
    if 'office_rent_main' in locals():
        office_rent = office_rent_main
        software_costs = software_costs_main
        other_opex = other_opex_main
    
    # MULTI-CHANNEL GTM INTEGRATION
    st.markdown("### 🚀 Multi-Channel GTM Configuration")
    
    # Initialize session state for channels
    if 'gtm_channels' not in st.session_state:
        st.session_state.gtm_channels = [
            {
                'id': 'channel_1',
                'name': 'Primary Channel',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            }
        ]
    
    # Channel management in compact form
    ch_col1, ch_col2, ch_col3, ch_col4 = st.columns([1.5, 1.5, 2, 3])
    with ch_col1:
        if st.button("➕ Add Channel", use_container_width=True, key="add_channel_main"):
            new_id = f"channel_{len(st.session_state.gtm_channels) + 1}"
            st.session_state.gtm_channels.append({
                'id': new_id,
                'name': f'Channel {len(st.session_state.gtm_channels) + 1}',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            })
            st.rerun()
    
    with ch_col2:
        if len(st.session_state.gtm_channels) > 1:
            if st.button("🗑️ Remove Last", use_container_width=True, key="remove_channel_main"):
                st.session_state.gtm_channels.pop()
                st.rerun()
    
    with ch_col3:
        template = st.selectbox(
            "Templates:",
            options=['Custom', 'SMB+MID+ENT', 'Inbound+Outbound'],
            key="gtm_template_main"
        )
    
    with ch_col4:
        st.info(f"Managing {len(st.session_state.gtm_channels)} channel(s)")
    
    # Configure channels in expandable sections
    channels = []
    for idx, channel_config in enumerate(st.session_state.gtm_channels):
        with st.expander(f"{channel_config['icon']} **{channel_config.get('name', f'Channel {idx+1}')}**", expanded=(idx == 0)):
            # Quick configuration in columns
            cfg_col1, cfg_col2, cfg_col3 = st.columns(3)
            
            with cfg_col1:
                channel_name = st.text_input("Name", value=channel_config['name'], key=f"main_{channel_config['id']}_name")
                segment = st.selectbox("Segment", ['SMB', 'MID', 'ENT'], key=f"main_{channel_config['id']}_segment")
                
                # Dynamic cost input method per channel
                cost_point = st.selectbox(
                    "Cost Input Point",
                    ["Cost per Lead", "Cost per Contact", "Cost per Meeting", "Cost per Sale", "Total Budget"],
                    key=f"main_{channel_config['id']}_cost_point"
                )
                
                # Dynamic quantity input based on cost point
                # Input the quantity that matches the cost point
                if cost_point == "Cost per Lead":
                    cpl = st.number_input("Cost per Lead ($)", value=50, step=10, key=f"main_{channel_config['id']}_cpl_direct")
                    leads = st.number_input("Monthly Leads", value=1000, step=100, key=f"main_{channel_config['id']}_leads")
                    
                elif cost_point == "Cost per Contact":
                    cost_per_contact = st.number_input("Cost per Contact ($)", value=75, step=10, key=f"main_{channel_config['id']}_cpc")
                    contacts_target = st.number_input("Monthly Contacts Target", value=650, step=50, key=f"main_{channel_config['id']}_contacts")
                    # Leads will be calculated after we get contact rate
                    leads = contacts_target  # Temporary, will recalculate with actual rate
                    cpl = cost_per_contact  # Temporary
                    
                elif cost_point == "Cost per Meeting":
                    cost_per_meeting = st.number_input("Cost per Meeting ($)", value=200, step=25, key=f"main_{channel_config['id']}_cpm")
                    meetings_target = st.number_input("Monthly Meetings Target", value=20, step=5, key=f"main_{channel_config['id']}_meetings")
                    # Leads will be calculated after we get conversion rates
                    leads = meetings_target * 5  # Rough estimate
                    cpl = cost_per_meeting / 5  # Temporary
                    
                elif cost_point == "Cost per Sale":
                    cost_per_sale = st.number_input("Cost per Sale ($)", value=500, step=50, key=f"main_{channel_config['id']}_cps")
                    sales_target = st.number_input("Monthly Sales Target", value=5, step=1, key=f"main_{channel_config['id']}_sales")
                    # Leads will be calculated after we get conversion rates
                    leads = sales_target * 20  # Rough estimate
                    cpl = cost_per_sale / 20  # Temporary
                    
                else:  # Total Budget
                    total_budget = st.number_input("Total Budget ($)", value=10000, step=1000, key=f"main_{channel_config['id']}_budget")
                    # For budget, still ask for estimated leads
                    leads = st.number_input("Estimated Monthly Leads", value=1000, step=100, key=f"main_{channel_config['id']}_leads_budget")
                    cpl = total_budget / leads if leads > 0 else 0
            
            with cfg_col2:
                contact_rt = st.slider("Contact %", 0, 100, 65, 5, key=f"main_{channel_config['id']}_contact") / 100
                meeting_rt = st.slider("Meeting %", 0, 100, 40, 5, key=f"main_{channel_config['id']}_meeting") / 100
                showup_rt = st.slider("Show-up %", 0, 100, 70, 5, key=f"main_{channel_config['id']}_showup") / 100
                close_rt = st.slider("Close %", 0, 100, 25, 5, key=f"main_{channel_config['id']}_close") / 100
                
                # Now calculate actual leads needed based on target quantities and rates
                if cost_point == "Cost per Contact":
                    # Calculate leads from contact target
                    leads = contacts_target / contact_rt if contact_rt > 0 else contacts_target
                    cpl = cost_per_contact / contact_rt if contact_rt > 0 else cost_per_contact
                    st.info(f"📊 Need {leads:.0f} leads to get {contacts_target} contacts")
                    
                elif cost_point == "Cost per Meeting":
                    # Calculate leads from meeting target
                    conversion_to_meeting = contact_rt * meeting_rt * showup_rt
                    leads = meetings_target / conversion_to_meeting if conversion_to_meeting > 0 else meetings_target * 5
                    cpl = cost_per_meeting / conversion_to_meeting if conversion_to_meeting > 0 else cost_per_meeting
                    st.info(f"📊 Need {leads:.0f} leads to get {meetings_target} meetings")
                    
                elif cost_point == "Cost per Sale":
                    # Calculate leads from sales target
                    full_conversion = contact_rt * meeting_rt * showup_rt * close_rt
                    leads = sales_target / full_conversion if full_conversion > 0 else sales_target * 20
                    cpl = cost_per_sale / full_conversion if full_conversion > 0 else cost_per_sale
                    st.info(f"📊 Need {leads:.0f} leads to get {sales_target} sales")
                    
                elif cost_point == "Total Budget":
                    cpl = total_budget / leads if leads > 0 else 0
                    st.info(f"📊 Effective CPL: ${cpl:.2f}")
            
            with cfg_col3:
                # Use the deal value from insurance model
                st.markdown("**Deal Value (from Insurance Model)**")
                st.info(f"💰 Deal Value: ${total_comp:,.0f}")
                st.caption(f"• Contract: ${total_contract_value:,.0f} MXN")
                st.caption(f"• Commission: {carrier_rate*100:.1f}%")
                st.caption(f"• Upfront: ${comp_immediate:,.0f}")
                st.caption(f"• Month 18: ${comp_deferred:,.0f}")
                
                cycle_days = st.slider("Sales Cycle", 7, 180, 30, 7, key=f"main_{channel_config['id']}_cycle")
                source = st.selectbox("Source", ['Inbound', 'Outbound', 'Partner', 'Events'], key=f"main_{channel_config['id']}_source")
            
            # Calculate channel metrics with proper cost point handling
            # The key is to calculate total marketing cost correctly based on selected method
            if cost_point == "Cost per Lead":
                total_marketing_cost = leads * cpl
            elif cost_point == "Cost per Contact":
                contacts_needed = leads * contact_rt
                total_marketing_cost = contacts_needed * cost_per_contact
            elif cost_point == "Cost per Meeting":
                meetings_from_channel = leads * contact_rt * meeting_rt * showup_rt
                total_marketing_cost = meetings_from_channel * cost_per_meeting
            elif cost_point == "Cost per Sale":
                sales_from_channel = leads * contact_rt * meeting_rt * showup_rt * close_rt
                total_marketing_cost = sales_from_channel * cost_per_sale
            elif cost_point == "Total Budget":
                total_marketing_cost = total_budget
            
            # Now define channel with corrected metrics - using deal value from insurance model
            channel = MultiChannelGTM.define_channel(
                name=channel_name,
                lead_source=source,
                segment=segment,
                monthly_leads=leads,
                contact_rate=contact_rt,
                meeting_rate=meeting_rt,
                show_up_rate=showup_rt,
                close_rate=close_rt,
                avg_deal_value=total_comp,  # Use total compensation from insurance model
                cpl=total_marketing_cost / leads if leads > 0 else 0,  # Effective CPL
                sales_cycle_days=cycle_days
            )
            
            # Add comprehensive cost info to channel
            channel['cost_point'] = cost_point
            channel['total_marketing_cost'] = total_marketing_cost
            channel['effective_cpl'] = total_marketing_cost / leads if leads > 0 else 0
            
            # Recalculate CAC based on actual total cost
            channel['cac'] = total_marketing_cost / channel['sales'] if channel['sales'] > 0 else 0
            
            # Calculate proper LTV and metrics using insurance model
            channel['ltv'] = total_comp  # Use full deal value from insurance model
            channel['ltv_cac'] = channel['ltv'] / channel['cac'] if channel['cac'] > 0 else 0
            channel['roas'] = channel['revenue'] / total_marketing_cost if total_marketing_cost > 0 else 0
            
            channels.append(channel)
            
            # Show channel metrics (without duplicate ROAS)
            m_cols = st.columns(5)
            with m_cols[0]:
                st.metric("Leads", f"{channel['monthly_leads']:,.0f}")
            with m_cols[1]:
                st.metric("Meetings", f"{channel['meetings_held']:,.0f}")
            with m_cols[2]:
                st.metric("Sales", f"{channel['sales']:,.0f}")
            with m_cols[3]:
                st.metric("Revenue", f"${channel['revenue']:,.0f}")
            with m_cols[4]:
                st.metric("CAC", f"${channel['cac']:,.0f}")
    
    # Aggregate all channels and show comprehensive funnel breakdown
    if channels:
        aggregated = MultiChannelGTM.aggregate_channels(channels)

        cap_settings = get_capacity_metrics(num_closers, num_setters)
        working_days_effective = max(cap_settings['working_days'], 1)
        monthly_closer_capacity = cap_settings['monthly_closer_capacity']
        monthly_setter_capacity = cap_settings['monthly_setter_capacity']

        # Update global metrics from channels (use aggregated values)
        monthly_leads = aggregated.get('total_leads', monthly_leads)
        monthly_sales = aggregated.get('total_sales', monthly_sales)
        monthly_revenue_total = aggregated.get('total_revenue', monthly_revenue_total)
        monthly_contacts = aggregated.get('total_contacts', 0)
        monthly_meetings_scheduled = aggregated.get('total_meetings_scheduled', 0)
        monthly_meetings = aggregated.get('total_meetings_held', 0)
        blended_contact_rate = aggregated.get('blended_contact_rate', 0)
        blended_meeting_rate = aggregated.get('blended_meeting_rate', 0)
        blended_showup_rate = aggregated.get('blended_show_up_rate', 0)
        blended_close_rate = aggregated.get('blended_close_rate', 0)
        
        # Recalculate revenue components based on channel sales
        monthly_revenue_immediate = monthly_sales * comp_immediate
        monthly_revenue_deferred = monthly_sales * comp_deferred
        monthly_revenue_total = monthly_revenue_immediate + monthly_revenue_deferred
        
        # Persist GTM metrics for team capacity section
        st.session_state['gtm_metrics'] = {
            'monthly_leads': monthly_leads,
            'monthly_meetings_scheduled': monthly_meetings_scheduled,
            'monthly_meetings': monthly_meetings,
            'monthly_sales': monthly_sales,
            'monthly_revenue_immediate': monthly_revenue_immediate,
            'monthly_revenue_total': monthly_revenue_total,
            'blended_contact_rate': blended_contact_rate
        }

        # Recalculate financial metrics with updated values
        # Total costs (marketing + compensation + opex)
        total_marketing_costs = aggregated.get('total_cost', sum(ch.get('total_marketing_cost', 0) for ch in channels))
        total_sales_comp = monthly_sales * (comp_immediate + comp_deferred) * 0.3  # Assume 30% goes to sales team
        monthly_total_costs = total_marketing_costs + total_sales_comp + monthly_opex
        
        # EBITDA calculation
        monthly_ebitda = monthly_revenue_total - monthly_total_costs
        ebitda_margin = monthly_ebitda / monthly_revenue_total if monthly_revenue_total > 0 else 0
        
        # CAC and other metrics
        cac = total_marketing_costs / monthly_sales if monthly_sales > 0 else 0
        ltv = total_comp  # Use insurance model value
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        roas = monthly_revenue_total / total_marketing_costs if total_marketing_costs > 0 else 0
        # Update global spend & payback with channel-derived values
        monthly_marketing = total_marketing_costs
        payback_months = cac / (comp_immediate / 12) if comp_immediate > 0 else 999
        
        # Consolidated Business Metrics Section - Moved to aggregated area
        st.markdown("### 📊 Business Performance Dashboard")
        
        # Primary KPIs - Most Important (First Row)
        st.markdown("**Primary Business Metrics**")
        primary_cols = st.columns(6)
        
        with primary_cols[0]:
            st.metric("💵 Monthly Revenue", f"${monthly_revenue_total:,.0f}", f"{(monthly_revenue_total/monthly_revenue_target - 1)*100:.1f}% vs target")
        with primary_cols[1]:
            st.metric("💰 EBITDA", f"${monthly_ebitda:,.0f}", f"{ebitda_margin:.1%} margin")
        with primary_cols[2]:
            st.metric("🎯 LTV:CAC", f"{ltv_cac_ratio:.1f}:1", "Target: >3:1")
        with primary_cols[3]:
            st.metric("🚀 ROAS", f"{roas:.1f}x", f"Target: >4x")
        with primary_cols[4]:
            cap_settings = get_capacity_metrics(num_closers, num_setters)
            monthly_closer_capacity = cap_settings['monthly_closer_capacity']
            capacity_util = monthly_meetings / monthly_closer_capacity if monthly_closer_capacity > 0 else 0
            st.metric("📅 Capacity Used", f"{capacity_util:.0%}", "OK" if capacity_util < 0.9 else "Overloaded")
        with primary_cols[5]:
            if monthly_meetings > 0 and blended_close_rate > 0:
                pipeline_value = monthly_meetings * comp_immediate / blended_close_rate
                pipeline_coverage = pipeline_value / monthly_revenue_target if monthly_revenue_target > 0 else 0
            else:
                pipeline_coverage = 0
            st.metric("📊 Pipeline Coverage", f"{pipeline_coverage:.1f}x", "Good" if pipeline_coverage >= 3 else "Low")
        
        # Sales Activity Metrics (Second Row)
        st.markdown("**Sales Activity**")
        activity_cols = st.columns(5)
        
        with activity_cols[0]:
            st.metric("👥 Leads", f"{monthly_leads:,.0f}/mo", f"{daily_leads:.0f}/day")
        with activity_cols[1]:
            st.metric("🤝 Meetings", f"{monthly_meetings:,.0f}/mo", f"{monthly_meetings/working_days_effective:.0f}/day")
        with activity_cols[2]:
            per_closer_daily_capacity = per_closer_capacity / working_days_effective if working_days_effective > 0 else 0
            st.metric("✅ Monthly Sales", f"{monthly_sales:.0f}",
                    f"{monthly_sales/num_closers:.1f} per closer" if num_closers > 0 else "N/A")
        with activity_cols[3]:
            st.metric("📈 Close Rate", f"{blended_close_rate:.0%}", f"Show-up: {blended_showup_rate:.0%}")
        with activity_cols[4]:
            st.metric("🕒 Sales Cycle", f"{sales_cycle_days} days", f"Velocity: {monthly_sales/sales_cycle_days*30:.0f}/mo" if sales_cycle_days > 0 else "-")
        
        # Financial Details (Third Row)
        st.markdown("**Financial Performance**")
        finance_cols = st.columns(5)
        
        with finance_cols[0]:
            st.metric("💳 CAC", f"${cac:,.0f}", f"LTV: ${ltv:,.0f}")
        with finance_cols[1]:
            st.metric("⏱️ Payback", f"{payback_months:.1f} mo", "Target: <18m")
        with finance_cols[2]:
            st.metric("📈 Revenue (Imm)", f"${monthly_revenue_immediate:,.0f}", "70% split")
        with finance_cols[3]:
            st.metric("📅 Revenue (Def)", f"${monthly_revenue_deferred:,.0f}", "30% split")
        with finance_cols[4]:
            st.metric("🏢 Team", f"{team_total} people", f"Burn: ${monthly_opex:,.0f}/mo")
        
        # Sales Process Timeline - Moved from Analytics section
        st.markdown("**Sales Process & Pipeline Stages**")
        
        # Create a visual timeline of the sales process
        timeline_data = [
            {"stage": "Lead Generated", "day": 0, "icon": "👥", "count": monthly_leads},
            {"stage": "First Contact", "day": 1, "icon": "📞", "count": monthly_contacts},
            {"stage": "Meeting Scheduled", "day": 3, "icon": "📅", "count": monthly_meetings_scheduled},
            {"stage": "Meeting Held", "day": 5, "icon": "🤝", "count": monthly_meetings},
            {"stage": "Deal Closed", "day": sales_cycle_days, "icon": "✅", "count": monthly_sales},
        ]
        
        # Create compact timeline visualization
        timeline_cols = st.columns(len(timeline_data))
        
        for idx, stage_data in enumerate(timeline_data):
            with timeline_cols[idx]:
                # Calculate conversion rate from previous stage
                if idx > 0:
                    prev_count = timeline_data[idx-1]['count']
                    conversion = (stage_data['count'] / prev_count * 100) if prev_count > 0 else 0
                    color = "#4CAF50" if conversion >= 70 else "#FF9800" if conversion >= 50 else "#F44336"
                else:
                    conversion = 100
                    color = "#2196F3"
                
                st.metric(
                    stage_data['icon'] + " " + stage_data['stage'],
                    f"{stage_data['count']:.0f}",
                    f"Day {stage_data['day']} | {conversion:.0f}%" if idx > 0 else f"Day {stage_data['day']}"
                )
        
        # Timing metrics row
        timing_metrics = st.columns(4)
        with timing_metrics[0]:
            st.metric("🕒 Lead to Meeting", "5 days")
        with timing_metrics[1]:
            st.metric("⏱️ Meeting to Close", f"{sales_cycle_days - 5} days")
        with timing_metrics[2]:
            velocity = monthly_sales / sales_cycle_days * 30 if sales_cycle_days > 0 else 0
            st.metric("🚀 Sales Velocity", f"{velocity:.1f} deals/mo")
        with timing_metrics[3]:
            st.metric("🎯 Win Rate", f"{blended_close_rate:.1%}")
        
        # Channel-specific metrics
        st.markdown("**Channel Performance**")
        channel_summary = st.columns(4)
        with channel_summary[0]:
            st.metric("Total Channel Leads", f"{monthly_leads:,.0f}")
        with channel_summary[1]:
            st.metric("Total Channel Sales", f"{monthly_sales:,.0f}")
        with channel_summary[2]:
            st.metric("Blended CAC", f"${aggregated.get('blended_cac', cac):,.0f}")
        with channel_summary[3]:
            st.metric("Blended Close Rate", f"{blended_close_rate:.1%}")
        
        # Channel comparison table
        st.markdown("### 📈 Channel Performance Breakdown")
        
        channel_data = []
        for ch in channels:
            efficiency = MultiChannelGTM.calculate_channel_efficiency(ch)
            channel_data.append({
                'Channel': ch['name'],
                'Segment': ch['segment'],
                'Leads': ch['monthly_leads'],
                'Meetings Held': f"{ch['meetings_held']:.0f}",
                'Sales': f"{ch['sales']:.0f}",
                'Revenue': f"${ch['revenue']:,.0f}",
                'CAC': f"${ch['cac']:,.0f}",
                'LTV:CAC': f"{ch['ltv_cac']:.1f}x",
                'Payback': f"{efficiency['payback_months']:.1f} mo"
            })
        
        channel_df = pd.DataFrame(channel_data)
        st.dataframe(
            channel_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Revenue": st.column_config.TextColumn("Revenue", width="medium"),
                "LTV:CAC": st.column_config.TextColumn("LTV:CAC", width="small")
            }
        )
        
        # Funnel visualization by channel
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔄 Channel Funnel Comparison")
            
            funnel_fig = go.Figure()
            
            for ch in channels:
                funnel_fig.add_trace(go.Funnel(
                    name=ch['segment'],
                    y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                    x=[ch['monthly_leads'], ch['contacts'], ch['meetings_scheduled'], 
                       ch['meetings_held'], ch['sales']],
                    textinfo="value+percent initial"
                ))
            
            funnel_fig.update_layout(
                title="Funnel by Channel",
                height=400
            )
            
            st.plotly_chart(funnel_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Revenue Contribution")
            
            revenue_data = {
                'Channel': [ch['segment'] for ch in channels],
                'Revenue': [ch['revenue'] for ch in channels]
            }
            
            pie_fig = go.Figure(data=[go.Pie(
                labels=revenue_data['Channel'],
                values=revenue_data['Revenue'],
                hole=0.3
            )])
            
            pie_fig.update_layout(
                title="Revenue by Channel",
                height=400
            )
            
            st.plotly_chart(pie_fig, use_container_width=True)
        
        # Channel efficiency heatmap
        st.markdown("### 🎯 Channel Efficiency Matrix")
        
        efficiency_data = []
        for ch in channels:
            eff = MultiChannelGTM.calculate_channel_efficiency(ch)
            efficiency_data.append({
                'Channel': ch['segment'],
                'Lead→Sale': eff['lead_to_sale'] * 100,
                'Meeting→Sale': eff['meeting_to_sale'] * 100,
                'Rev/Lead': eff['revenue_per_lead'] / 1000,  # in thousands
                'LTV:CAC': eff['ltv_cac_ratio']
            })
        
        eff_df = pd.DataFrame(efficiency_data)
        eff_df = eff_df.set_index('Channel')
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=eff_df.values,
            x=eff_df.columns,
            y=eff_df.index,
            colorscale='Viridis',
            text=eff_df.values.round(1),
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>"
        ))
        
        fig_heatmap.update_layout(
            title="Channel Efficiency Heatmap",
            height=300
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Health Monitoring Section in Expandable Format
    with st.expander("🌱 **System Health & Recommendations**", expanded=False):
        # Check various health metrics
        health_issues = []
        
        # Check revenue gap
        revenue_gap = monthly_revenue_target - monthly_revenue_total
        if revenue_gap > 0:
            gap_pct = (revenue_gap / monthly_revenue_target) * 100
            if gap_pct > 30:
                health_issues.append({
                'severity': 'high',
                'category': 'Revenue',
                'issue': f'Revenue {gap_pct:.0f}% below target',
                'recommendation': f'Increase sales by {revenue_gap/comp_immediate:.0f} or improve close rate to {(monthly_sales * monthly_revenue_target / monthly_revenue_total) / monthly_meetings:.1%}'
            })
            elif gap_pct > 15:
                health_issues.append({
                'severity': 'medium',
                'category': 'Revenue',
                'issue': f'Revenue gap of ${revenue_gap:,.0f}',
                'recommendation': f'Focus on closing {revenue_gap/comp_immediate:.0f} additional sales'
            })
    
        
        # Check capacity utilization
        health_capacity_settings = get_capacity_metrics(num_closers, num_setters)
        capacity_util = monthly_meetings / health_capacity_settings['monthly_closer_capacity'] if health_capacity_settings['monthly_closer_capacity'] > 0 else 0
        setter_utilization = monthly_meetings_scheduled / health_capacity_settings['monthly_setter_capacity'] if health_capacity_settings['monthly_setter_capacity'] > 0 else 0
        if capacity_util > 0.9:
            health_issues.append({
                'severity': 'high',
                'category': 'Capacity',
                'issue': f'Team at {capacity_util:.0%} capacity',
                'recommendation': f'Hire {np.ceil(max(monthly_meetings - health_capacity_settings["per_closer_monthly_capacity"] * num_closers * 0.8, 0) / health_capacity_settings["per_closer_monthly_capacity"]):.0f} closers to reduce load'
            })
        
        # Check LTV:CAC ratio
        if ltv_cac_ratio < 3:
            health_issues.append({
                'severity': 'medium',
                'category': 'Unit Economics',
                'issue': f'LTV:CAC ratio {ltv_cac_ratio:.1f}:1 below target',
                'recommendation': f'Reduce CAC by ${cac - ltv/3:.0f} or increase LTV'
            })
    
        # Display health issues in a friendly way
        if health_issues:
            health_cols = st.columns(len(health_issues[:3]))  # Show up to 3 issues
            for idx, issue in enumerate(health_issues[:3]):
                with health_cols[idx]:
                    if issue['severity'] == 'high':
                        st.warning(f"""
                        **{issue['category']}**  
                        🟡 {issue['issue']}  
                        💡 {issue['recommendation']}
                        """)
                    else:
                        st.info(f"""
                        **{issue['category']}**  
                        ℹ️ {issue['issue']}  
                        💡 {issue['recommendation']}
                        """)
        else:
            st.success("✅ All systems healthy! No major issues detected.")
    
    # Integrated Health Metrics & Bottleneck Analysis in Expandable Format
    with st.expander("🔍 **Bottleneck Analysis & Health Scores**", expanded=False):
        # Calculate health scores
        funnel_health = HealthScoreCalculator.calculate_health_metrics(
            {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
            {'utilization': capacity_util, 'attrition_rate': 0.15},
            {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin, 'growth_rate': 0.1}
        )
        
        # Display health scores in columns
        health_col1, health_col2, health_col3, health_col4 = st.columns(4)
        
        with health_col1:
            score = funnel_health['overall_health']
            if score >= 80:
                color = "normal"
                emoji = "🚀"
            elif score >= 60:
                color = "normal"
                emoji = "⚠️"
            else:
                color = "inverse"
                emoji = "🔴"
            st.metric(
                "Overall Health",
                f"{score:.0f}/100 {emoji}",
                funnel_health['status'],
                delta_color=color
            )
    
    with health_col2:
        score = funnel_health['funnel_health']
        st.metric(
            "Funnel Health",
            f"{score:.0f}/100",
            "Conversion flow" if score > 70 else "Needs attention"
        )
    
    with health_col3:
        score = funnel_health['team_health']
        st.metric(
            "Team Health",
            f"{score:.0f}/100",
            "Capacity OK" if score > 70 else "Overloaded"
        )
    
    with health_col4:
        score = funnel_health['financial_health']
        st.metric(
            "Financial Health",
            f"{score:.0f}/100",
            "Profitable" if score > 70 else "Review costs"
        )
    
    # Bottleneck identification
    bottlenecks = BottleneckAnalyzer.find_bottlenecks(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {
            'closer_utilization': capacity_util,
            'setter_utilization': setter_util_global
        },
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin}
    )
    
    if bottlenecks:
        st.markdown("**🎯 Identified Bottlenecks:**")
        bottleneck_cols = st.columns(min(len(bottlenecks), 3))
        
        for idx, bottleneck in enumerate(bottlenecks[:3]):
            with bottleneck_cols[idx]:
                # Color code by type
                if bottleneck['type'] == 'Financial':
                    st.error(f"""
                    **{bottleneck['type']}**  
                    🔴 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
                elif bottleneck['type'] == 'Capacity':
                    st.warning(f"""
                    **{bottleneck['type']}**  
                    🟡 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
                else:
                    st.info(f"""
                    **{bottleneck['type']}**  
                    🔵 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
        else:
            st.success("🎆 No bottlenecks detected! System running smoothly.")
    
    # Charts Section - Consolidating visual analytics
    st.markdown("### 📈 Analytics & Charts")
    
    # Revenue Retention Metrics in expandable format
    with st.expander("💹 **Revenue Retention Analysis**", expanded=False):
        retention_col1, retention_col2 = st.columns(2)
    
    with retention_col1:
        # Retention inputs in expandable section
        with st.expander("📊 **Configure Retention Metrics**", expanded=False):
            # Use actual current MRR from business metrics
            starting_mrr = monthly_revenue_total  # Use actual monthly revenue
            st.info(f"💵 Using Current MRR: ${starting_mrr:,.0f}")
            
            # Retention components
            churn_pct = st.slider("Monthly Churn %", 0.0, 20.0, 3.0, 0.5, key="retention_churn") / 100
            downgrade_pct = st.slider("Monthly Downgrade %", 0.0, 10.0, 2.0, 0.5, key="retention_downgrade") / 100
            expansion_pct = st.slider("Monthly Expansion %", 0.0, 20.0, 5.0, 0.5, key="retention_expansion") / 100
            new_customer_pct = st.slider("New Customer Growth %", 0.0, 50.0, 10.0, 1.0, key="retention_new") / 100
    
    # Calculate absolute values
    churned_mrr = starting_mrr * churn_pct
    downgrade_mrr = starting_mrr * downgrade_pct
    expansion_mrr = starting_mrr * expansion_pct
    new_mrr = starting_mrr * new_customer_pct
    ending_mrr = starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr + new_mrr
    
    # Calculate GRR and NRR
    retention_metrics = RevenueRetentionCalculator.calculate_grr_nrr(
        starting_mrr=starting_mrr,
        ending_mrr=ending_mrr,
        churned_mrr=churned_mrr,
        downgrade_mrr=downgrade_mrr,
        expansion_mrr=expansion_mrr,
        new_mrr=new_mrr
    )
    
    # Display retention metrics
    ret_metric_cols = st.columns(4)
    
    with ret_metric_cols[0]:
        grr_status = "Excellent" if retention_metrics['grr_percentage'] >= 95 else "Good" if retention_metrics['grr_percentage'] >= 90 else "Needs Work"
        st.metric(
            "Gross Revenue Retention",
            f"{retention_metrics['grr_percentage']:.1f}%",
            grr_status
        )
    
    with ret_metric_cols[1]:
        nrr_status = "Excellent" if retention_metrics['nrr_percentage'] >= 120 else "Good" if retention_metrics['nrr_percentage'] >= 110 else "Review"
        st.metric(
            "Net Revenue Retention",
            f"{retention_metrics['nrr_percentage']:.1f}%",
            nrr_status
        )
    
    with ret_metric_cols[2]:
        st.metric(
            "Expansion Rate",
            f"{retention_metrics['expansion_rate']:.1f}%",
            f"+${expansion_mrr:,.0f}/mo"
        )
    
    with ret_metric_cols[3]:
        churn_status = "Healthy" if retention_metrics['churn_rate'] <= 3 else "Watch" if retention_metrics['churn_rate'] <= 5 else "High"
        st.metric(
            "Monthly Churn",
            f"{retention_metrics['churn_rate']:.1f}%",
            churn_status
        )
    
    # Revenue Waterfall Chart
    with retention_col2:
        st.markdown("**💧 Revenue Movement Waterfall**")
        
        waterfall_data = {
            'measure': ['absolute', 'relative', 'relative', 'relative', 'relative', 'total'],
            'x': ['Starting MRR', 'Churned', 'Downgrades', 'Expansion', 'New Customers', 'Ending MRR'],
            'y': [starting_mrr, -churned_mrr, -downgrade_mrr, expansion_mrr, new_mrr, ending_mrr]
        }
        
        fig_waterfall = go.Figure(go.Waterfall(
            measure=waterfall_data['measure'],
            x=waterfall_data['x'],
            y=waterfall_data['y'],
            text=[f"${abs(val):,.0f}" for val in waterfall_data['y']],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#4CAF50"}},
            decreasing={"marker": {"color": "#F44336"}},
            totals={"marker": {"color": "#2196F3"}}
        ))
        
        fig_waterfall.update_layout(
            height=350,
            margin=dict(t=20, b=20),
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True, key="retention_waterfall")
    
    # Visual Timeline moved to Charts section
    with st.expander("📖 **Sales Process Timeline**", expanded=True):
        # Create a visual timeline of the sales process
        timeline_data = [
            {"stage": "Lead Generated", "day": 0, "icon": "👥", "count": monthly_leads},
            {"stage": "First Contact", "day": 1, "icon": "📞", "count": monthly_contacts},
            {"stage": "Meeting Scheduled", "day": 3, "icon": "📅", "count": monthly_meetings_scheduled},
            {"stage": "Meeting Held", "day": 5, "icon": "🤝", "count": monthly_meetings},
            {"stage": "Proposal Sent", "day": 7, "icon": "📝", "count": monthly_meetings * 0.8},
            {"stage": "Deal Closed", "day": sales_cycle_days, "icon": "✅", "count": monthly_sales},
            {"stage": "Revenue Received", "day": sales_cycle_days + 30, "icon": "💰", "count": monthly_sales}
        ]
    
    # Create timeline visualization
    timeline_cols = st.columns(len(timeline_data))
    
    for idx, stage_data in enumerate(timeline_data):
        with timeline_cols[idx]:
            # Calculate conversion rate from previous stage
            if idx > 0:
                prev_count = timeline_data[idx-1]['count']
                conversion = (stage_data['count'] / prev_count * 100) if prev_count > 0 else 0
                color = "#4CAF50" if conversion >= 70 else "#FF9800" if conversion >= 50 else "#F44336"
            else:
                conversion = 100
                color = "#2196F3"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: {color}; border-radius: 10px; color: white;">
                <div style="font-size: 28px;">{stage_data['icon']}</div>
                <div style="font-weight: bold; margin-top: 5px;">{stage_data['stage']}</div>
                <div style="font-size: 20px; margin-top: 5px;">{stage_data['count']:.0f}</div>
                <div style="font-size: 12px; margin-top: 5px;">Day {stage_data['day']}</div>
                {f'<div style="font-size: 11px; margin-top: 3px;">{conversion:.1f}% conv</div>' if idx > 0 else ''}
            </div>
            """, unsafe_allow_html=True)
    
    # Timing metrics
    timing_cols = st.columns(4)
    with timing_cols[0]:
        st.metric("Avg Sales Cycle", f"{sales_cycle_days} days")
    with timing_cols[1]:
        st.metric("Lead to Meeting", "5 days")
    with timing_cols[2]:
        st.metric("Meeting to Close", f"{sales_cycle_days - 5} days")
    with timing_cols[3]:
        velocity = monthly_sales / sales_cycle_days * 30 if sales_cycle_days > 0 else 0
        st.metric("Sales Velocity", f"{velocity:.1f} deals/mo")
    
    # Daily Activities integrated into Team Structure expandable section
    # This section is now properly organized within Team Structure configuration

# TAB 2: UNIT COSTS (10x Better One-Pager Design)
with tabs[1]:
    # Import dynamic benchmarks
    from modules.dynamic_benchmarks import DynamicBenchmarks
    
    # Header with dramatic styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 20px; margin-bottom: 30px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 36px; font-weight: 900;">💰 UNIT ECONOMICS COMMAND CENTER</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Complete cost analysis with dynamic benchmarks</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get dynamic benchmarks
    cost_benchmarks = DynamicBenchmarks.get_cost_benchmarks("insurance", "digital", "mexico")
    financial_benchmarks = DynamicBenchmarks.get_financial_benchmarks("insurance", "recurring")
    
    # Key metrics with show-up rate impact
    no_show_cost = cost_breakdown.get('no_show_cost', 0)
    no_show_rate = cost_breakdown.get('no_show_rate', 0)
    
    # TOP METRICS DASHBOARD
    st.markdown("### 🎯 KEY PERFORMANCE INDICATORS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cpl_status, cpl_color, cpl_emoji = DynamicBenchmarks.get_performance_status(
            cost_breakdown['cost_per_lead'], cost_benchmarks['cpl']
        )
        st.markdown(f"""
        <div style="background: {cpl_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{cpl_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">${cost_breakdown['cost_per_lead']:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Cost per Lead</div>
            <div style="font-size: 12px; margin-top: 5px;">{cpl_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cac_status, cac_color, cac_emoji = DynamicBenchmarks.get_performance_status(
            cac, cost_benchmarks['cac']
        )
        st.markdown(f"""
        <div style="background: {cac_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{cac_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">${cac:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Total CAC</div>
            <div style="font-size: 12px; margin-top: 5px;">{cac_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ltv_cac_status, ltv_cac_color, ltv_cac_emoji = DynamicBenchmarks.get_performance_status(
            ltv_cac_ratio, financial_benchmarks['ltv_cac_ratio']
        )
        st.markdown(f"""
        <div style="background: {ltv_cac_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{ltv_cac_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">{ltv_cac_ratio:.1f}:1</div>
            <div style="font-size: 14px; opacity: 0.9;">LTV:CAC Ratio</div>
            <div style="font-size: 12px; margin-top: 5px;">{ltv_cac_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        payback_months = cac / (comp_immediate * ebitda_margin) if (comp_immediate * ebitda_margin) > 0 else 999
        # For payback, we need to invert the logic (lower is better)
        if payback_months <= financial_benchmarks['payback_months']['excellent']:
            payback_status, payback_color, payback_emoji = "Excellent", "#4CAF50", "🟢"
        elif payback_months <= financial_benchmarks['payback_months']['good']:
            payback_status, payback_color, payback_emoji = "Good", "#8BC34A", "🟡"
        elif payback_months <= financial_benchmarks['payback_months']['min']:
            payback_status, payback_color, payback_emoji = "Acceptable", "#FF9800", "🟠"
        else:
            payback_status, payback_color, payback_emoji = "Below Standard", "#F44336", "🔴"
        st.markdown(f"""
        <div style="background: {payback_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{payback_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">{payback_months:.1f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Payback Months</div>
            <div style="font-size: 12px; margin-top: 5px;">{payback_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        revenue_per_lead = monthly_revenue_immediate / monthly_leads if monthly_leads > 0 else 0
        rpl_color = "#4CAF50" if revenue_per_lead > cost_breakdown['cost_per_lead'] * 3 else "#FF9800" if revenue_per_lead > cost_breakdown['cost_per_lead'] else "#F44336"
        st.markdown(f"""
        <div style="background: {rpl_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">💰</div>
            <div style="font-size: 28px; font-weight: 900;">${revenue_per_lead:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Revenue/Lead</div>
            <div style="font-size: 12px; margin-top: 5px;">{"Excellent" if revenue_per_lead > cost_breakdown['cost_per_lead'] * 3 else "Good" if revenue_per_lead > cost_breakdown['cost_per_lead'] else "Poor"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # FUNNEL COST BREAKDOWN
    st.markdown("### 🔄 COMPLETE FUNNEL COST ANALYSIS")
    
    # Create comprehensive funnel visualization
    funnel_data = {
        'Stage': ['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales', 'Onboarded'],
        'Volume': [monthly_leads, monthly_contacts, monthly_meetings_scheduled, monthly_meetings_held, monthly_sales, monthly_onboarded],
        'Cost_Per_Unit': [
            cost_breakdown.get('cost_per_lead', 0),
            cost_breakdown.get('cost_per_contact', 0),
            cost_breakdown.get('cost_per_meeting_scheduled', 0),
            cost_breakdown.get('cost_per_meeting_held', 0),
            cost_breakdown.get('cost_per_sale', 0),
            cost_breakdown.get('cost_per_sale', 0) / onboard_rate if onboard_rate > 0 else 0
        ],
        'Conversion_Rate': [
            1.0,
            contact_rate,
            meeting_rate,
            show_up_rate,
            close_rate,
            onboard_rate
        ],
        'Total_Cost': [
            cost_breakdown.get('cost_per_lead', 0) * monthly_leads,
            cost_breakdown.get('cost_per_contact', 0) * monthly_contacts,
            cost_breakdown.get('cost_per_meeting_scheduled', 0) * monthly_meetings_scheduled,
            cost_breakdown.get('cost_per_meeting_held', 0) * monthly_meetings_held,
            cost_breakdown.get('cost_per_sale', 0) * monthly_sales,
            (cost_breakdown.get('cost_per_sale', 0) / onboard_rate if onboard_rate > 0 else 0) * monthly_onboarded
        ]
    }
    
    funnel_df = pd.DataFrame(funnel_data)
    
    # Display as professional OG table like compensation tables
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center; font-weight: 900;">
            📊 COMPLETE FUNNEL BREAKDOWN
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the professional table
    st.dataframe(
        funnel_df.style.format({
            'Volume': '{:,.0f}',
            'Cost_Per_Unit': '${:,.0f}',
            'Conversion_Rate': '{:.1%}',
            'Total_Cost': '${:,.0f}'
        }).set_properties(**{
            'background-color': '#f8f9fa',
            'color': '#333',
            'border': '1px solid #dee2e6',
            'text-align': 'center',
            'font-weight': '600'
        }).set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', '#495057'),
                    ('color', 'white'),
                    ('font-weight', '900'),
                    ('text-align', 'center'),
                    ('padding', '12px'),
                    ('border', '1px solid #495057')
                ]
            },
            {
                'selector': 'tbody td',
                'props': [
                    ('padding', '10px'),
                    ('border', '1px solid #dee2e6'),
                    ('text-align', 'center')
                ]
            },
            {
                'selector': 'tbody tr:nth-child(even)',
                'props': [
                    ('background-color', '#ffffff')
                ]
            },
            {
                'selector': 'tbody tr:hover',
                'props': [
                    ('background-color', '#e9ecef'),
                    ('cursor', 'pointer')
                ]
            }
        ]),
        use_container_width=True,
        hide_index=True
    )
    
    # NO-SHOW IMPACT ANALYSIS
    if no_show_cost > 0:
        st.markdown("### 🚫 NO-SHOW IMPACT ANALYSIS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">😞</div>
                <div style="font-size: 24px; font-weight: 900;">{no_show_rate:.1%}</div>
                <div style="font-size: 14px; opacity: 0.9;">No-Show Rate</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    {monthly_meetings_scheduled * (1-show_up_rate):.0f} missed meetings/month
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">💸</div>
                <div style="font-size: 24px; font-weight: 900;">${no_show_cost:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">Wasted Cost/Month</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    ${no_show_cost * 12:,.0f} annually
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            potential_sales = monthly_meetings_scheduled * (1-show_up_rate) * close_rate
            potential_revenue = potential_sales * comp_immediate
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ab47bc 0%, #9c27b0 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">📉</div>
                <div style="font-size: 24px; font-weight: 900;">${potential_revenue:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">Lost Revenue/Month</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    {potential_sales:.0f} lost sales
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # OPTIMIZATION RECOMMENDATIONS
    st.markdown("### 🎯 OPTIMIZATION RECOMMENDATIONS")
    
    recommendations = []
    
    # Check each metric against benchmarks
    if cost_breakdown['cost_per_lead'] > cost_benchmarks['cpl']['good']:
        reduction_needed = cost_breakdown['cost_per_lead'] - cost_benchmarks['cpl']['good']
        recommendations.append({
            'priority': 'HIGH',
            'metric': 'Cost per Lead',
            'issue': f"${cost_breakdown['cost_per_lead']:,.0f} is ${reduction_needed:.0f} above benchmark",
            'action': f"Optimize targeting or channels to reduce CPL by {(reduction_needed/cost_breakdown['cost_per_lead'])*100:.0f}%",
            'impact': f"Save ${reduction_needed * monthly_leads:,.0f}/month"
        })
    
    if ltv_cac_ratio < financial_benchmarks['ltv_cac_ratio']['good']:
        recommendations.append({
            'priority': 'CRITICAL',
            'metric': 'LTV:CAC Ratio',
            'issue': f"{ltv_cac_ratio:.1f}:1 below {financial_benchmarks['ltv_cac_ratio']['good']:.1f}:1 benchmark",
            'action': f"Reduce CAC by ${cac - ltv/financial_benchmarks['ltv_cac_ratio']['good']:,.0f} or increase LTV",
            'impact': f"Improve unit economics sustainability"
        })
    
    if no_show_rate > 0.3:
        recommendations.append({
            'priority': 'MEDIUM',
            'metric': 'Show-up Rate',
            'issue': f"{no_show_rate:.1%} no-show rate is high",
            'action': f"Implement confirmation calls, better scheduling, or penalties",
            'impact': f"Recover ${no_show_cost:,.0f}/month in wasted costs"
        })
    
    # Display recommendations
    for i, rec in enumerate(recommendations):
        priority_color = {"CRITICAL": "#f44336", "HIGH": "#ff9800", "MEDIUM": "#2196f3"}[rec['priority']]
        st.markdown(f"""
        <div style="background: {priority_color}; padding: 20px; border-radius: 15px; 
                    margin: 10px 0; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 18px; font-weight: 900;">
                        {rec['priority']} PRIORITY: {rec['metric']}
                    </div>
                    <div style="font-size: 14px; margin: 5px 0; opacity: 0.9;">
                        {rec['issue']}
                    </div>
                    <div style="font-size: 14px; font-weight: 600;">
                        🎯 Action: {rec['action']}
                    </div>
                </div>
                <div style="text-align: right; font-size: 12px; opacity: 0.8;">
                    💰 {rec['impact']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: COMPENSATION (Improved modular)
with tabs[2]:
    st.header("💵 Estructura de Compensación Modular")
    
    # Show current structure
    st.subheader("💼 OTE Structure by Role")
    
    comp_data = []
    for role, data in comp_structure['by_role'].items():
        comp_data.append({
            'Role': role.capitalize(),
            'Count': data['count'],
            'Base/Person': f"${data['base_per_person']:,.0f}",
            'Variable/Person': f"${data['variable_per_person']:,.0f}",
            'OTE/Person': f"${data['ote_per_person']:,.0f}",
            'Base %': f"{data['base_pct']:.0%}",
            'Total Cost': f"${data['total_ote']:,.0f}"
        })
    
    comp_df = pd.DataFrame(comp_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Annual Comp", f"${comp_structure['annual_total']:,.0f}")
    with col2:
        st.metric("Monthly Base", f"${comp_structure['monthly_base']:,.0f}")
    with col3:
        st.metric("Monthly Variable", f"${comp_structure['monthly_variable_target']:,.0f}")
    with col4:
        st.metric("Avg Base %", f"{comp_structure['avg_base_pct']:.0%}")
    
    # Commission waterfall
    st.subheader("💸 Commission Flow")
    
    commission_flow = {
        'Revenue': monthly_revenue_immediate,
        'Closer Pool': monthly_revenue_immediate * closer_comm_pct,
        'Setter Pool': monthly_revenue_immediate * setter_comm_pct,
        'Per Closer': (monthly_revenue_immediate * closer_comm_pct) / num_closers if num_closers > 0 else 0,
        'Per Setter': (monthly_revenue_immediate * setter_comm_pct) / num_setters if num_setters > 0 else 0
    }
    
    flow_df = pd.DataFrame([
        {'Level': k, 'Amount': f"${v:,.0f}", 'Per Sale': f"${v/monthly_sales if monthly_sales > 0 else 0:,.0f}"}
        for k, v in commission_flow.items()
    ])
    
    st.dataframe(flow_df, use_container_width=True, hide_index=True)

# TAB 4: P&L (Deep analysis)
with tabs[3]:
    st.header("📊 P&L Detallado - Análisis Profundo")
    
    # Prepare P&L data
    revenue_dict = {
        'monthly_sales': monthly_sales,
        'immediate_revenue': monthly_revenue_immediate,
        'deferred_revenue': monthly_sales * comp_deferred,
        'total_projected': revenue_timeline['cumulative_total'].iloc[-1] if len(revenue_timeline) > 0 else 0
    }
    
    costs_dict = {
        'cogs': 0,
        'marketing_costs': monthly_marketing,
        'commissions': monthly_commissions,
        'sales_base_salaries': comp_structure['monthly_base'],
        'office_rent': office_rent,
        'software': software_costs,
        'other_opex': other_opex,
        'gov_fee_pct': gov_fee_pct
    }
    
    pnl_df = ImprovedPnLCalculator.calculate_detailed_pnl(
        revenue_dict, costs_dict, projection_months
    )
    
    # Format P&L display - include format column for processing
    display_pnl = pnl_df.copy()
    
    # Format columns
    for col in ['month_1', 'month_18', 'total_projection']:
        display_pnl[col] = display_pnl.apply(
            lambda x: f"${x[col]:,.0f}" if x['format'] in ['currency', 'currency_bold'] 
            else f"{x[col]:.0f}" if x['format'] == 'units'
            else f"{x[col]:.1%}" if x['format'] == 'percentage'
            else x[col],
            axis=1
        )
    
    display_pnl['pct_of_revenue'] = display_pnl['pct_of_revenue'].apply(
        lambda x: f"{x:.1%}" if pd.notna(x) and x != 0 else ""
    )
    
    # Select and display only the key columns
    final_pnl = display_pnl[['line_item', 'month_1', 'month_18', 'total_projection', 'pct_of_revenue']].copy()
    final_pnl.columns = ['Line Item', 'Month 1', 'Month 18', f'{projection_months}M Total', '% of Rev']
    
    st.dataframe(final_pnl, use_container_width=True, height=600, hide_index=True)

# TAB 5: SIMULATOR (was TAB 6)
with tabs[4]:  # Simulator tab
    st.header("📅 Revenue Timeline - Proyección Detallada")
    
    # Key milestone dates
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0; color: #64B5F6;">📆 Key Dates</h4>
            <div style="margin-top: 10px; line-height: 1.8;">
                • <b>Today:</b> {datetime.now().strftime('%B %Y')}<br>
                • <b>Month 18:</b> {(datetime.now() + timedelta(days=540)).strftime('%B %Y')}<br>
                • <b>End:</b> {(datetime.now() + timedelta(days=projection_months*30)).strftime('%B %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if projection_months >= 18:
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h4 style="margin: 0; color: #81C784;">💰 Month 18 Revenue</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Immediate:</b> ${month_18_revenue_immediate:,.0f}<br>
                    • <b>Deferred:</b> ${month_18_revenue_deferred:,.0f}<br>
                    • <b>Total:</b> ${month_18_revenue_total:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        total_projection = revenue_timeline['cumulative_total'].iloc[-1] if len(revenue_timeline) > 0 else 0
        st.markdown(f"""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
            <h4 style="margin: 0; color: #FFB74D;">📊 {projection_months}M Projection</h4>
            <div style="margin-top: 10px; line-height: 1.8;">
                • <b>Total Revenue:</b> ${total_projection:,.0f}<br>
                • <b>Avg Monthly:</b> ${total_projection/projection_months:,.0f}<br>
                • <b>Run Rate:</b> ${(total_projection/projection_months)*12:,.0f}/yr
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Timeline visualization
    fig_timeline = go.Figure()
    
    # Immediate revenue
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['immediate_revenue'],
        name='Immediate (70%)',
        marker_color='#2ecc71'
    ))
    
    # Deferred revenue
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['deferred_revenue'],
        name='Deferred (30%)',
        marker_color='#3498db'
    ))
    
    # Cumulative line
    fig_timeline.add_trace(go.Scatter(
        x=revenue_timeline['month'],
        y=revenue_timeline['cumulative_total'],
        name='Cumulative',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        yaxis='y2'
    ))
    
    # Add month 18 marker
    if projection_months >= 18:
        fig_timeline.add_vline(
            x=18, line_dash="dash", line_color="red",
            annotation_text="Deferred Payments Start"
        )
    
    # Add quarters
    for q in range(1, (projection_months // 3) + 1):
        fig_timeline.add_vline(x=q*3, line_dash="dot", line_color="gray", opacity=0.3)
    
    fig_timeline.update_layout(
        title="Revenue Timeline with 70/30 Split",
        xaxis_title="Month",
        yaxis_title="Monthly Revenue ($)",
        yaxis2=dict(title="Cumulative ($)", overlaying='y', side='right'),
        barmode='stack',
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# TAB 6: REVERSE ENGINEERING (was TAB 7)
with tabs[5]:  # Reverse Engineering tab
    st.header("🚀 Simulador Avanzado")
    
    # Optimization target
    opt_col1, opt_col2 = st.columns([1, 3])
    
    with opt_col1:
        optimize_for = st.radio(
            "Optimize for:",
            ["Revenue", "EBITDA", "LTV:CAC", "Margin %"],
            index=1
        )
    
    with opt_col2:
        if optimize_for == "Revenue":
            target_revenue = st.number_input(
                "Target Monthly Revenue ($)",
                value=int(monthly_revenue_target * 1.5),
                step=100000
            )
            
            # Calculate requirements
            sales_needed = target_revenue / comp_immediate
            meetings_needed = sales_needed / close_rate
            leads_needed = meetings_needed / (contact_rate * meeting_rate)
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h4 style="margin: 0; color: #81C784;">🎯 Requirements for ${target_revenue:,.0f}/month</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>{sales_needed:.0f} sales</b> ({sales_needed - monthly_sales:+.0f})<br>
                    • <b>{meetings_needed:.0f} meetings</b> ({meetings_needed - monthly_meetings:+.0f})<br>
                    • <b>{leads_needed:.0f} leads</b> ({leads_needed - monthly_leads:+.0f})<br>
                    • <b>{np.ceil(meetings_needed/per_closer_capacity):.0f} closers needed</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif optimize_for == "EBITDA":
            target_ebitda = st.number_input(
                "Target Monthly EBITDA ($)",
                value=int(monthly_ebitda * 2),
                step=50000
            )
            
            # Calculate options
            revenue_for_ebitda = (target_ebitda + monthly_costs_before_fees) / (1 - gov_fee_pct)
            cost_reduction = monthly_ebitda - target_ebitda
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
                <h4 style="margin: 0; color: #64B5F6;">🎯 Options for ${target_ebitda:,.0f} EBITDA</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Option 1:</b> Increase revenue to ${revenue_for_ebitda:,.0f}<br>
                    • <b>Option 2:</b> Reduce costs by ${abs(cost_reduction):,.0f}<br>
                    • <b>Option 3:</b> Combination approach
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif optimize_for == "LTV:CAC":
            target_ratio = st.number_input(
                "Target LTV:CAC Ratio",
                value=5.0,
                step=0.5,
                min_value=3.0,
                max_value=10.0
            )
            
            # Calculate requirements
            target_cac = ltv / target_ratio
            cac_reduction = cac - target_cac
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0; color: #FFB74D;">🎯 To achieve {target_ratio:.1f}:1 ratio</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Reduce CAC</b> from ${cac:,.0f} to ${target_cac:,.0f}<br>
                    • <b>Reduction needed:</b> ${cac_reduction:,.0f} (-{(cac_reduction/cac)*100:.0f}%)<br>
                    • <b>Or increase LTV</b> by {((target_ratio * cac) - ltv)/ltv*100:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

# REMOVED - Now only 6 tabs
# Old TAB 7 content removed
if False:  # This code is no longer used
    st.header("🔄 Ingeniería Inversa - Integrada")
    st.markdown("**Single source of truth - uses current dashboard values**")
    
    # Select target
    rev_col1, rev_col2 = st.columns([1, 2])
    
    with rev_col1:
        target_type = st.selectbox(
            "Start from:",
            ["Revenue Target", "EBITDA Target", "LTV:CAC Target", "Sales Target"]
        )
    
    with rev_col2:
        if target_type == "Revenue Target":
            target_value = st.number_input(
                "Monthly Revenue Target ($)",
                value=int(monthly_revenue_target),
                step=100000
            )
            
            # Use integrated reverse engineering
            results = ImprovedReverseEngineering.calculate_from_target(
                'revenue', target_value, current_state
            )
            
        elif target_type == "EBITDA Target":
            target_value = st.number_input(
                "Monthly EBITDA Target ($)",
                value=int(monthly_ebitda * 1.5),
                step=50000
            )
            
            results = ImprovedReverseEngineering.calculate_from_target(
                'ebitda', target_value, current_state
            )
            
        elif target_type == "LTV:CAC Target":
            target_value = st.number_input(
                "Target Ratio",
                value=5.0,
                step=0.5,
                min_value=3.0,
                max_value=10.0
            )
            
            results = ImprovedReverseEngineering.calculate_from_target(
                'ltv_cac', target_value, current_state
            )
        else:
            target_value = st.number_input(
                "Monthly Sales Target",
                value=int(monthly_sales * 1.5),
                step=10
            )
            
            # Convert sales target to revenue and calculate
            revenue_target = target_value * comp_immediate
            results = ImprovedReverseEngineering.calculate_from_target(
                'revenue', revenue_target, current_state
            )
    
    # Display results
    if 'results' in locals():
        st.markdown("### 📊 Results")
        
        # Show required changes
        if results['required_changes']:
            change_col1, change_col2 = st.columns(2)
            
            with change_col1:
                st.markdown("**🔄 Required Changes:**")
                for key, value in results['required_changes'].items():
                    if 'additional' in key or 'total' in key:
                        if isinstance(value, (int, float)):
                            if 'cost' in key or 'spend' in key or 'revenue' in key:
                                st.write(f"• {key.replace('_', ' ').title()}: ${value:,.0f}")
                            else:
                                st.write(f"• {key.replace('_', ' ').title()}: {value:.0f}")
            
            with change_col2:
                st.markdown("**🎯 Action Items:**")
                for action in results['actions']:
                    st.write(f"✅ {action}")
        
        # Show warnings
        if results['warnings']:
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0; color: #FFB74D;">⚠️ Warnings</h4>
            </div>
            """, unsafe_allow_html=True)
            for warning in results['warnings']:
                st.write(f"• {warning}")
        
        # Feasibility indicator
        if results['feasibility'] == 'feasible':
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; display: flex; align-items: center;">
                <div style="font-size: 24px; margin-right: 10px;">✅</div>
                <div style="font-weight: bold;">Target is achievable with current resources</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #F44336; display: flex; align-items: center;">
                <div style="font-size: 24px; margin-right: 10px;">❌</div>
                <div style="font-weight: bold;">Target requires significant changes</div>
            </div>
            """, unsafe_allow_html=True)

# REMOVED - Health metrics integrated into GTM Command Center
if False:  # Old Health Metrics tab
    st.header("📈 Health Metrics Dashboard")
    
    # Calculate health scores
    funnel_health = HealthScoreCalculator.calculate_health_metrics(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {'utilization': capacity_util, 'attrition_rate': 0.15},
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin, 'growth_rate': 0.1}
    )
    
    # Display scores
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    
    with health_col1:
        st.metric(
            "Overall Health",
            f"{funnel_health['overall_health']:.0f}/100",
            funnel_health['status']
        )
    
    with health_col2:
        st.metric(
            "Funnel Health",
            f"{funnel_health['funnel_health']:.0f}/100"
        )
    
    with health_col3:
        st.metric(
            "Team Health",
            f"{funnel_health['team_health']:.0f}/100"
        )
    
    with health_col4:
        st.metric(
            "Financial Health",
            f"{funnel_health['financial_health']:.0f}/100"
        )
    
    # Bottleneck analysis
    st.subheader("🔍 Bottleneck Analysis")
    
    bottlenecks = BottleneckAnalyzer.find_bottlenecks(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {'closer_utilization': capacity_util, 'setter_utilization': monthly_contacts / (num_setters * 600) if num_setters > 0 else 0},
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin}
    )
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            bottleneck_type = 'alert-critical' if bottleneck['type'] == 'Financial' else 'alert-warning'
            st.markdown(
                f'<div class="alert-box {bottleneck_type}">' +
                f'<strong>{bottleneck["type"]} Issue: {bottleneck["issue"]}</strong><br>' +
                f'Current: {bottleneck["current"]:.2f} | Target: {bottleneck["target"]:.2f}<br>' +
                f'Impact: {bottleneck["impact"]}<br>' +
                f'👉 Action: {bottleneck["action"]}' +
                '</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown("""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; display: flex; align-items: center;">
            <div style="font-size: 24px; margin-right: 10px;">✅</div>
            <div style="font-weight: bold;">No major bottlenecks detected!</div>
        </div>
        """, unsafe_allow_html=True)

# REMOVED - Revenue retention integrated into GTM Command Center
if False:  # Old Revenue Retention tab
    st.header("📈 Revenue Retention Metrics (GRR & NRR)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Input Retention Data")
        
        # MRR inputs
        starting_mrr = st.number_input(
            "Starting MRR ($)", 
            value=float(monthly_revenue_total),
            step=10000.0,
            help="Monthly Recurring Revenue at start of period"
        )
        
        # Retention components
        churn_pct = st.slider("Monthly Churn %", 0.0, 20.0, 3.0, 0.5) / 100
        downgrade_pct = st.slider("Monthly Downgrade %", 0.0, 10.0, 2.0, 0.5) / 100
        expansion_pct = st.slider("Monthly Expansion %", 0.0, 20.0, 5.0, 0.5) / 100
        
        # Calculate absolute values
        churned_mrr = starting_mrr * churn_pct
        downgrade_mrr = starting_mrr * downgrade_pct
        expansion_mrr = starting_mrr * expansion_pct
        
        # New customer MRR
        new_customer_pct = st.slider("New Customer Growth %", 0.0, 50.0, 10.0, 1.0) / 100
        new_mrr = starting_mrr * new_customer_pct
        
        # Calculate ending MRR
        ending_mrr = starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr + new_mrr
        
    with col2:
        st.subheader("📈 Retention Analysis")
        
        # Calculate GRR and NRR
        retention_metrics = RevenueRetentionCalculator.calculate_grr_nrr(
            starting_mrr=starting_mrr,
            ending_mrr=ending_mrr,
            churned_mrr=churned_mrr,
            downgrade_mrr=downgrade_mrr,
            expansion_mrr=expansion_mrr,
            new_mrr=new_mrr
        )
        
        # Display key metrics
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            grr_color = "#4CAF50" if retention_metrics['grr_percentage'] >= 90 else "#FF9800" if retention_metrics['grr_percentage'] >= 80 else "#F44336"
            st.markdown(f"""
            <div style="background: {grr_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['grr_percentage']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Gross Revenue Retention</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    Retained: ${retention_metrics['retained_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[1]:
            nrr_color = "#4CAF50" if retention_metrics['nrr_percentage'] >= 110 else "#2196F3" if retention_metrics['nrr_percentage'] >= 100 else "#FF9800"
            st.markdown(f"""
            <div style="background: {nrr_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['nrr_percentage']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Net Revenue Retention</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    Total: ${retention_metrics['total_retention_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[2]:
            st.markdown(f"""
            <div style="background: #9C27B0; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['expansion_rate']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Expansion Rate</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    +${expansion_mrr:,.0f}/mo
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[3]:
            churn_color = "#4CAF50" if retention_metrics['churn_rate'] <= 3 else "#FF9800" if retention_metrics['churn_rate'] <= 5 else "#F44336"
            st.markdown(f"""
            <div style="background: {churn_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['churn_rate']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Monthly Churn</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    -${churned_mrr:,.0f}/mo
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Revenue Waterfall Chart
    st.subheader("💧 Revenue Waterfall")
    
    waterfall_data = {
        'Category': ['Starting MRR', 'Churned', 'Downgraded', 'Expanded', 'New Customers', 'Ending MRR'],
        'Amount': [starting_mrr, -churned_mrr, -downgrade_mrr, expansion_mrr, new_mrr, ending_mrr],
        'Type': ['Start', 'Negative', 'Negative', 'Positive', 'Positive', 'End']
    }
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Revenue Movement",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=waterfall_data['Category'],
        text=[f"${v:,.0f}" for v in waterfall_data['Amount']],
        y=waterfall_data['Amount'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#4CAF50"}},
        decreasing={"marker": {"color": "#F44336"}},
        totals={"marker": {"color": "#2196F3"}}
    ))
    
    fig_waterfall.update_layout(
        title="Monthly Revenue Movement",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Projection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 12-Month Projection")
        projections = RevenueRetentionCalculator.project_retention_impact(
            current_mrr=starting_mrr,
            monthly_churn_rate=churn_pct,
            monthly_expansion_rate=expansion_pct,
            months_forward=12
        )
        
        projection_df = pd.DataFrame({
            'Month': projections['month'],
            'GRR MRR': projections['grr_mrr'],
            'NRR MRR': projections['nrr_mrr']
        })
        
        fig_projection = go.Figure()
        fig_projection.add_trace(go.Scatter(
            x=projection_df['Month'],
            y=projection_df['GRR MRR'],
            name='GRR Projection',
            line=dict(color='#FF9800', width=2)
        ))
        fig_projection.add_trace(go.Scatter(
            x=projection_df['Month'],
            y=projection_df['NRR MRR'],
            name='NRR Projection',
            line=dict(color='#4CAF50', width=2)
        ))
        
        fig_projection.update_layout(
            title="MRR Projection (GRR vs NRR)",
            xaxis_title="Month",
            yaxis_title="MRR ($)",
            height=350
        )
        
        st.plotly_chart(fig_projection, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Retention Benchmarks")
        
        benchmark_data = {
            'Metric': ['GRR', 'NRR', 'Churn Rate', 'Expansion Rate'],
            'Your Value': [
                f"{retention_metrics['grr_percentage']:.1f}%",
                f"{retention_metrics['nrr_percentage']:.1f}%",
                f"{retention_metrics['churn_rate']:.1f}%",
                f"{retention_metrics['expansion_rate']:.1f}%"
            ],
            'Best in Class': ['95%+', '120%+', '<2%', '15%+'],
            'Good': ['90-95%', '105-120%', '2-3%', '10-15%'],
            'Average': ['80-90%', '95-105%', '3-5%', '5-10%'],
            'Status': [
                '🟢' if retention_metrics['grr_percentage'] >= 95 else '🟡' if retention_metrics['grr_percentage'] >= 90 else '🔴',
                '🟢' if retention_metrics['nrr_percentage'] >= 120 else '🟡' if retention_metrics['nrr_percentage'] >= 105 else '🔴',
                '🟢' if retention_metrics['churn_rate'] <= 2 else '🟡' if retention_metrics['churn_rate'] <= 3 else '🔴',
                '🟢' if retention_metrics['expansion_rate'] >= 15 else '🟡' if retention_metrics['expansion_rate'] >= 10 else '🔴'
            ]
        }
        
        benchmark_df = pd.DataFrame(benchmark_data)
        st.dataframe(
            benchmark_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )

# Old Multi-Channel GTM tab removed - now integrated into main GTM Command Center tab

# The following code is the old Multi-Channel GTM tab that has been integrated above
'''
The old tab code below has been integrated into the main GTM Command Center.
Keeping it commented for reference only.
    if 'gtm_channels' not in st.session_state:
        st.session_state.gtm_channels = [
            {
                'id': 'channel_1',
                'name': 'Channel 1',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            }
        ]
    
    # Channel management buttons
    col_add, col_clear, col_template = st.columns([1.5, 1.5, 3])
    with col_add:
        if st.button("➕ Add Channel", use_container_width=True):
            new_id = f"channel_{len(st.session_state.gtm_channels) + 1}"
            st.session_state.gtm_channels.append({
                'id': new_id,
                'name': f'Channel {len(st.session_state.gtm_channels) + 1}',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            })
            st.rerun()
    
    with col_clear:
        if len(st.session_state.gtm_channels) > 1:
            if st.button("🗑️ Remove Last", use_container_width=True):
                st.session_state.gtm_channels.pop()
                st.rerun()
    
    with col_template:
        template = st.selectbox(
            "Quick Templates:",
            options=['Custom', 'SMB + MID + ENT', 'Inbound + Outbound', 'Direct + Partner'],
            key="gtm_template"
        )
        if template == 'SMB + MID + ENT' and st.button("🚀 Apply Template"):
            st.session_state.gtm_channels = [
                {'id': 'channel_1', 'name': 'SMB Channel', 'segment': 'SMB', 'lead_source': 'Inbound Marketing', 'icon': '🏢'},
                {'id': 'channel_2', 'name': 'MID Channel', 'segment': 'MID', 'lead_source': 'Outbound SDR', 'icon': '🏛️'},
                {'id': 'channel_3', 'name': 'ENT Channel', 'segment': 'ENT', 'lead_source': 'Account-Based Marketing', 'icon': '🏰'}
            ]
            st.rerun()
        elif template == 'Inbound + Outbound' and st.button("🚀 Apply Template"):
            st.session_state.gtm_channels = [
                {'id': 'channel_1', 'name': 'Inbound', 'segment': 'SMB', 'lead_source': 'Inbound Marketing', 'icon': '📥'},
                {'id': 'channel_2', 'name': 'Outbound', 'segment': 'MID', 'lead_source': 'Outbound SDR', 'icon': '📤'}
            ]
            st.rerun()
        elif template == 'Direct + Partner' and st.button("🚀 Apply Template"):
            st.session_state.gtm_channels = [
                {'id': 'channel_1', 'name': 'Direct Sales', 'segment': 'MID', 'lead_source': 'Outbound SDR', 'icon': '💨'},
                {'id': 'channel_2', 'name': 'Partner Channel', 'segment': 'SMB', 'lead_source': 'Partner Channel', 'icon': '🤝'}
            ]
            st.rerun()
    
    # Channel configuration
    channels = []
    
    # Display channels dynamically
    if st.session_state.gtm_channels:
        st.markdown("### 📊 Channel Configuration")
        
        # Create expandable sections for each channel
        for idx, channel_config in enumerate(st.session_state.gtm_channels):
            with st.expander(f"{channel_config['icon']} **{channel_config['name']}**", expanded=(idx == 0)):
                # Channel settings in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    # Basic settings
                    channel_name = st.text_input(
                        "Channel Name",
                        value=channel_config['name'],
                        key=f"{channel_config['id']}_name"
                    )
                    
                    segment = st.selectbox(
                        "Segment",
                        options=['SMB', 'MID', 'ENT', 'Custom'],
                        index=['SMB', 'MID', 'ENT', 'Custom'].index(channel_config.get('segment', 'SMB')),
                        key=f"{channel_config['id']}_segment"
                    )
                    
                    # Update icon based on segment
                    icon_map = {
                        'SMB': '🏢',
                        'MID': '🏛️',
                        'ENT': '🏰',
                        'Custom': '🎯'
                    }
                    channel_config['icon'] = icon_map.get(segment, '🎯')
                    
                    lead_source = st.selectbox(
                        "Lead Source",
                        options=['Inbound Marketing', 'Outbound SDR', 'Account-Based Marketing', 'Partner Channel', 'Events', 'Content Marketing'],
                        index=0,
                        key=f"{channel_config['id']}_source"
                    )
                    
                    # Volume and cost
                    monthly_leads = st.number_input(
                        "Monthly Leads",
                        value=1000 if segment == 'SMB' else 300 if segment == 'MID' else 50,
                        step=50,
                        key=f"{channel_config['id']}_leads"
                    )
                    
                    cpl = st.number_input(
                        "Cost Per Lead ($)",
                        value=50 if segment == 'SMB' else 200 if segment == 'MID' else 1000,
                        step=10,
                        key=f"{channel_config['id']}_cpl"
                    )
                
                with col2:
                    # Funnel metrics
                    contact_rate = st.slider(
                        "Contact Rate %",
                        0, 100, 
                        65 if segment == 'SMB' else 55 if segment == 'MID' else 45,
                        5,
                        key=f"{channel_config['id']}_contact"
                    ) / 100
                    
                    meeting_rate = st.slider(
                        "Meeting Rate %",
                        0, 100,
                        40 if segment == 'SMB' else 35 if segment == 'MID' else 30,
                        5,
                        key=f"{channel_config['id']}_meeting"
                    ) / 100
                    
                    show_up_rate = st.slider(
                        "Show-up Rate %",
                        0, 100,
                        70 if segment == 'SMB' else 75 if segment == 'MID' else 85,
                        5,
                        key=f"{channel_config['id']}_showup"
                    ) / 100
                    
                    close_rate = st.slider(
                        "Close Rate %",
                        0, 100,
                        30 if segment == 'SMB' else 25 if segment == 'MID' else 20,
                        5,
                        key=f"{channel_config['id']}_close"
                    ) / 100
                    
                    avg_deal_value = st.number_input(
                        "Avg Deal Value ($)",
                        value=15000 if segment == 'SMB' else 50000 if segment == 'MID' else 250000,
                        step=1000,
                        key=f"{channel_config['id']}_deal"
                    )
                
                # Sales cycle
                sales_cycle = st.slider(
                    "Sales Cycle (days)",
                    7, 180,
                    21 if segment == 'SMB' else 45 if segment == 'MID' else 90,
                    7,
                    key=f"{channel_config['id']}_cycle"
                )
                
                # Create channel object
                channel = MultiChannelGTM.define_channel(
                    name=channel_name,
                    lead_source=lead_source,
                    segment=segment,
                    monthly_leads=monthly_leads,
                    contact_rate=contact_rate,
                    meeting_rate=meeting_rate,
                    show_up_rate=show_up_rate,
                    close_rate=close_rate,
                    avg_deal_value=avg_deal_value,
                    cpl=cpl,
                    sales_cycle_days=sales_cycle
                )
                
                # Display channel metrics
                metric_cols = st.columns(5)
                with metric_cols[0]:
                    st.metric("Leads", f"{channel['monthly_leads']:,.0f}")
                with metric_cols[1]:
                    st.metric("Meetings", f"{channel['meetings_held']:,.0f}")
                with metric_cols[2]:
                    st.metric("Sales", f"{channel['sales']:,.0f}")
                with metric_cols[3]:
                    st.metric("Revenue", f"${channel['revenue']:,.0f}")
                with metric_cols[4]:
                    st.metric("CAC", f"${channel['cac']:,.0f}")
                
                channels.append(channel)
    
    if channels:
        # Aggregate metrics
        aggregated = MultiChannelGTM.aggregate_channels(channels)
        
        # Display aggregated results
        st.markdown("### 📊 Aggregated Performance")
        
        metric_cols = st.columns(6)
        with metric_cols[0]:
            st.metric("Total Leads", f"{aggregated['total_leads']:,.0f}")
        with metric_cols[1]:
            st.metric("Total Sales", f"{aggregated['total_sales']:,.0f}")
        with metric_cols[2]:
            st.metric("Total Revenue", f"${aggregated['total_revenue']:,.0f}")
        with metric_cols[3]:
            st.metric("Blended CAC", f"${aggregated['blended_cac']:,.0f}")
        with metric_cols[4]:
            st.metric("Blended Close Rate", f"{aggregated['blended_close_rate']:.1%}")
        with metric_cols[5]:
            st.metric("ROAS", f"{aggregated['roas']:.2f}x")
        
        # Channel comparison table
        st.markdown("### 📈 Channel Performance Breakdown")
        
        channel_data = []
        for ch in channels:
            efficiency = MultiChannelGTM.calculate_channel_efficiency(ch)
            channel_data.append({
                'Channel': ch['name'],
                'Segment': ch['segment'],
                'Leads': ch['monthly_leads'],
                'Meetings Held': f"{ch['meetings_held']:.0f}",
                'Sales': f"{ch['sales']:.0f}",
                'Revenue': f"${ch['revenue']:,.0f}",
                'CAC': f"${ch['cac']:,.0f}",
                'LTV:CAC': f"{efficiency['ltv_cac_ratio']:.1f}x",
                'Payback': f"{efficiency['payback_months']:.1f} mo"
            })
        
        channel_df = pd.DataFrame(channel_data)
        st.dataframe(
            channel_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Revenue": st.column_config.TextColumn("Revenue", width="medium"),
                "LTV:CAC": st.column_config.TextColumn("LTV:CAC", width="small")
            }
        )
        
        # Funnel visualization by channel
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔄 Channel Funnel Comparison")
            
            funnel_fig = go.Figure()
            
            for ch in channels:
                funnel_fig.add_trace(go.Funnel(
                    name=ch['segment'],
                    y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
                    x=[ch['monthly_leads'], ch['contacts'], ch['meetings_scheduled'], 
                       ch['meetings_held'], ch['sales']],
                    textinfo="value+percent initial"
                ))
            
            funnel_fig.update_layout(
                title="Funnel by Channel",
                height=400
            )
            
            st.plotly_chart(funnel_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 💰 Revenue Contribution")
            
            revenue_data = {
                'Channel': [ch['segment'] for ch in channels],
                'Revenue': [ch['revenue'] for ch in channels]
            }
            
            pie_fig = go.Figure(data=[go.Pie(
                labels=revenue_data['Channel'],
                values=revenue_data['Revenue'],
                hole=0.3
            )])
            
            pie_fig.update_layout(
                title="Revenue by Channel",
                height=400
            )
            
            st.plotly_chart(pie_fig, use_container_width=True)
        
        # Channel efficiency heatmap
        st.markdown("### 🎯 Channel Efficiency Matrix")
        
        efficiency_data = []
        for ch in channels:
            eff = MultiChannelGTM.calculate_channel_efficiency(ch)
            efficiency_data.append({
                'Channel': ch['segment'],
                'Lead→Sale': eff['lead_to_sale'] * 100,
                'Meeting→Sale': eff['meeting_to_sale'] * 100,
                'Rev/Lead': eff['revenue_per_lead'] / 1000,  # in thousands
                'LTV:CAC': eff['ltv_cac_ratio']
            })
        
        eff_df = pd.DataFrame(efficiency_data)
        eff_df = eff_df.set_index('Channel')
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=eff_df.values,
            x=eff_df.columns,
            y=eff_df.index,
            colorscale='Viridis',
            text=eff_df.values.round(1),
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>"
        ))
        
        fig_heatmap.update_layout(
            title="Channel Efficiency Heatmap",
            height=300
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.markdown("""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800; display: flex; align-items: center;">
            <div style="font-size: 24px; margin-right: 10px;">⚠️</div>
            <div style="font-weight: bold;">Please enable at least one channel to see results</div>
        </div>
        """, unsafe_allow_html=True)
'''  # End of commented old Multi-Channel GTM tab code
