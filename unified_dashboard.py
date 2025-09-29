"""
Unified Sales Compensation Dashboard - One-Pager with Full Integration
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional

# Import our modular components
from modules.config import config
from modules.calculations import (
    RevenueCalculator, FunnelCalculator, TeamCalculator, 
    CommissionCalculator, UnitEconomicsCalculator
)
from modules.visualizations import (
    TimelineVisualizer, FunnelVisualizer, TeamVisualizer,
    MetricsVisualizer, ComparisonVisualizer
)
from modules.validation import ModelValidator, DataConsistencyChecker

# Page configuration
st.set_page_config(
    page_title="💎 Sales Compensation Model",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for persistent values
if 'scenario_data' not in st.session_state:
    st.session_state.scenario_data = {}
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = {}

# Custom CSS for better UX
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 2px;}
    .stTabs [data-baseweb="tab"] {padding: 10px 20px;}
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 10px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ================== SIDEBAR CONFIGURATION ==================
st.sidebar.title("⚙️ Configuration Center")
st.sidebar.caption("All inputs in one place - no duplicates")

# Revenue Target (Primary Input)
st.sidebar.header("🎯 1. Revenue Target")
annual_revenue_target = st.sidebar.number_input(
    "Annual Revenue Target ($)",
    min_value=1_000_000,
    max_value=1_000_000_000,
    value=50_000_000,
    step=1_000_000,
    help="This drives all downstream calculations"
)
monthly_revenue_target = annual_revenue_target / 12
quarterly_revenue_target = annual_revenue_target / 4

# Sales Cycle Configuration
st.sidebar.header("⏱️ 2. Sales Cycle")
sales_cycle_days = st.sidebar.slider(
    "Average Sales Cycle (days)",
    min_value=7,
    max_value=180,
    value=config.default_sales_cycle_days,
    help="Affects pipeline coverage and capacity planning"
)

# Deal Economics
st.sidebar.header("💰 3. Deal Economics")
avg_premium_monthly = st.sidebar.number_input(
    "Average Monthly Premium (MXN)",
    min_value=1000,
    max_value=10000,
    value=3000,
    step=100
)

# Calculate compensation automatically
comp_structure = RevenueCalculator.calculate_compensation(avg_premium_monthly)
avg_deal_size = comp_structure['immediate_per_sale']

st.sidebar.info(f"""
**Per Sale Economics:**
- Immediate (70%): ${comp_structure['immediate_per_sale']:,.0f}
- Deferred (30%): ${comp_structure['deferred_per_sale']:,.0f}
- Expected Total: ${comp_structure['expected_total']:,.0f}
""")

# Conversion Rates (Single source of truth)
st.sidebar.header("📊 4. Conversion Rates")
col1, col2 = st.sidebar.columns(2)
with col1:
    contact_rate = st.sidebar.slider("Contact Rate", 0.4, 0.8, 0.6, 0.05)
    meeting_rate = st.sidebar.slider("Meeting Rate", 0.2, 0.5, 0.35, 0.05)
with col2:
    close_rate = st.sidebar.slider("Close Rate", 0.15, 0.35, 0.25, 0.05)
    onboard_rate = st.sidebar.slider("Onboard Rate", 0.9, 1.0, 0.95, 0.01)

# Pipeline Coverage (Based on sales cycle)
suggested_coverage = 3.0 + (sales_cycle_days / 30) * 0.5  # More coverage for longer cycles
pipeline_coverage = st.sidebar.slider(
    "Pipeline Coverage Ratio",
    min_value=2.0,
    max_value=6.0,
    value=min(6.0, suggested_coverage),
    step=0.5,
    help=f"Suggested: {suggested_coverage:.1f}x based on {sales_cycle_days} day cycle"
)

# Team Structure
st.sidebar.header("👥 5. Team Structure")
num_closers = st.sidebar.number_input("Closers", 1, 50, 10)
num_setters = st.sidebar.number_input("Setters", 1, 50, 5)
num_managers = st.sidebar.number_input("Managers", 0, 10, 2)

# Compensation Structure
st.sidebar.header("💸 6. Compensation")
avg_ote_closer = st.sidebar.number_input(
    "Avg OTE Closer ($)",
    min_value=30000,
    max_value=200000,
    value=80000,
    step=5000
)
base_salary_pct = st.sidebar.slider(
    "Base Salary %",
    min_value=0.2,
    max_value=0.6,
    value=0.4,
    step=0.05
)

# Costs
st.sidebar.header("💵 7. Operating Costs")
cost_per_lead = st.sidebar.number_input("Cost per Lead ($)", 50, 500, 150, 10)
gov_fee_pct = st.sidebar.slider("Gov Fees %", 0.0, 0.2, 0.1, 0.01)

# Advanced Settings
with st.sidebar.expander("⚡ Advanced Settings"):
    ramp_months = st.number_input("Ramp Time (months)", 1, 6, 3)
    attrition_rate = st.slider("Annual Attrition %", 0.0, 0.3, 0.15, 0.05)
    projection_months = st.selectbox("Projection Period", [6, 12, 18, 24], index=2)

# ================== MAIN CALCULATIONS ==================

# Calculate required pipeline
pipeline_data = FunnelCalculator.reverse_engineer_pipeline(
    monthly_revenue_target,
    avg_deal_size,
    close_rate,
    meeting_rate,
    contact_rate,
    pipeline_coverage
)

# Calculate funnel metrics
monthly_leads = pipeline_data['leads_needed']
funnel_metrics = FunnelCalculator.calculate_funnel_metrics(
    monthly_leads,
    contact_rate,
    meeting_rate,
    close_rate,
    onboard_rate
)

# Calculate team capacity
team_capacity = TeamCalculator.calculate_team_capacity(
    num_closers,
    num_setters
)

# Check capacity vs demand
capacity_check = DataConsistencyChecker.check_capacity_alignment(
    funnel_metrics['meetings'],
    funnel_metrics['contacts'],
    team_capacity['closer_capacity_meetings'],
    team_capacity['setter_capacity_contacts']
)

# Calculate revenue timeline
revenue_timeline = RevenueCalculator.project_revenue_timeline(
    funnel_metrics['sales'],
    avg_premium_monthly,
    projection_months,
    growth_rate=0.0  # Can be adjusted
)

# Calculate compensation
ote_structure = CommissionCalculator.calculate_ote_structure(
    monthly_revenue_target / num_closers,  # Revenue per rep
    avg_ote_closer,
    base_salary_pct
)

# Calculate unit economics
monthly_costs = {
    'cogs': 0,  # No COGS in insurance model
    'sales_costs': num_closers * avg_ote_closer / 12 + num_setters * (avg_ote_closer * 0.5) / 12,
    'marketing_costs': monthly_leads * cost_per_lead,
    'overhead': num_managers * 100000 / 12 + 35000  # Manager cost + fixed overhead
}

unit_economics = UnitEconomicsCalculator.calculate_unit_economics(
    revenue_timeline.iloc[0]['total_revenue'],  # First month revenue
    monthly_costs['cogs'],
    monthly_costs['sales_costs'],
    monthly_costs['marketing_costs'],
    monthly_costs['overhead'],
    gov_fee_pct
)

# Calculate activities required
daily_activities = {
    'leads_per_day': monthly_leads / 20,
    'contacts_per_day': funnel_metrics['contacts'] / 20,
    'meetings_per_day': funnel_metrics['meetings'] / 20,
    'sales_per_day': funnel_metrics['sales'] / 20
}

weekly_activities = {k: v * 5 for k, v in daily_activities.items()}

# Validate everything
validation_data = {
    'contact_rate': contact_rate,
    'meeting_rate': meeting_rate,
    'close_rate': close_rate,
    'ltv_cac_ratio': unit_economics['ebitda'] * 12 / (monthly_costs['marketing_costs'] + monthly_costs['sales_costs']) if (monthly_costs['marketing_costs'] + monthly_costs['sales_costs']) > 0 else 0,
    'ebitda_margin': unit_economics['ebitda_margin'],
    'gross_margin': unit_economics['gross_margin'],
    'cos_percentage': unit_economics['cos_percentage'],
    'leads': monthly_leads,
    'meetings_needed': funnel_metrics['meetings'],
    'contacts_needed': funnel_metrics['contacts'],
    'num_closers': num_closers,
    'num_setters': num_setters
}

validation_results = ModelValidator.validate_scenario(validation_data)

# ================== MAIN DASHBOARD ==================

# Header with key metrics
st.title("💎 Unified Sales Compensation Model")

# Top-line metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric(
        "Monthly Target",
        f"${monthly_revenue_target:,.0f}",
        f"${monthly_revenue_target - revenue_timeline.iloc[0]['total_revenue']:,.0f}",
        delta_color="inverse"
    )
with col2:
    st.metric(
        "Sales Needed",
        f"{funnel_metrics['sales']:.0f}",
        f"{funnel_metrics['sales'] / num_closers:.1f} per rep"
    )
with col3:
    st.metric(
        "Pipeline Coverage",
        f"{pipeline_coverage:.1f}x",
        f"${pipeline_data['pipeline_value_needed']:,.0f}"
    )
with col4:
    st.metric(
        "EBITDA Margin",
        f"{unit_economics['ebitda_margin']:.1%}",
        "Healthy" if unit_economics['is_healthy'] else "Review",
        delta_color="normal" if unit_economics['is_healthy'] else "inverse"
    )
with col5:
    st.metric(
        "Team Capacity",
        f"{capacity_check['closer_utilization']:.0%}",
        "OK" if capacity_check['is_aligned'] else "Overloaded",
        delta_color="normal" if capacity_check['is_aligned'] else "inverse"
    )
with col6:
    st.metric(
        "Model Health",
        f"{validation_results['health_score']:.0f}/100",
        validation_results['status']
    )

# Show validation alerts
if validation_results['errors']:
    st.error("🚨 **Critical Issues Found:**")
    for error in validation_results['errors']:
        st.write(f"• {error}")

if validation_results['warnings']:
    st.warning("⚠️ **Warnings:**")
    for warning in validation_results['warnings'][:3]:  # Show top 3
        st.write(f"• {warning}")

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Timeline View",
    "🎯 Activity Requirements",
    "💰 Compensation Model",
    "📊 Unit Economics",
    "🔮 Scenarios"
])

with tab1:
    st.header("Revenue Timeline & Projections")
    
    # Show payment structure clarity
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"""
        **🏦 Payment Structure**
        - 70% Immediate: ${comp_structure['immediate_per_sale']:,.0f}
        - 30% Month 18: ${comp_structure['deferred_per_sale']:,.0f}
        - Persistency: {config.DEFAULT_PERSISTENCY:.0%}
        """)
    with col2:
        st.success(f"""
        **📈 Monthly Targets**
        - Sales: {funnel_metrics['sales']:.0f}
        - Revenue: ${monthly_revenue_target:,.0f}
        - EBITDA: ${unit_economics['ebitda']:,.0f}
        """)
    with col3:
        st.warning(f"""
        **📅 Key Dates**
        - First Payment: Today
        - Deferred Start: Month {config.DEFERRED_MONTH}
        - Full Ramp: Month {ramp_months}
        """)
    
    # Revenue timeline chart
    timeline_viz = TimelineVisualizer()
    fig_timeline = timeline_viz.create_revenue_timeline(revenue_timeline)
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Daily/Weekly/Monthly breakdown
    st.subheader("Period Breakdown")
    col1, col2, col3 = st.columns(3)
    targets = timeline_viz.create_daily_weekly_monthly_view(monthly_revenue_target)
    with col1:
        st.plotly_chart(targets['daily'], use_container_width=True)
    with col2:
        st.plotly_chart(targets['weekly'], use_container_width=True)
    with col3:
        st.plotly_chart(targets['monthly'], use_container_width=True)

with tab2:
    st.header("Activity Requirements")
    
    # Activity metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Daily Activities Required")
        daily_df = pd.DataFrame([
            {"Activity": "Leads", "Required": daily_activities['leads_per_day'], "Per Rep": daily_activities['leads_per_day']/(num_setters if num_setters > 0 else 1)},
            {"Activity": "Contacts", "Required": daily_activities['contacts_per_day'], "Per Rep": daily_activities['contacts_per_day']/(num_setters if num_setters > 0 else 1)},
            {"Activity": "Meetings", "Required": daily_activities['meetings_per_day'], "Per Rep": daily_activities['meetings_per_day']/(num_closers if num_closers > 0 else 1)},
            {"Activity": "Sales", "Required": daily_activities['sales_per_day'], "Per Rep": daily_activities['sales_per_day']/(num_closers if num_closers > 0 else 1)}
        ])
        st.dataframe(daily_df.style.format({"Required": "{:.1f}", "Per Rep": "{:.1f}"}), use_container_width=True)
        
        # Funnel visualization
        funnel_viz = FunnelVisualizer()
        fig_funnel = funnel_viz.create_funnel_chart(funnel_metrics)
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        st.subheader("👥 Capacity Analysis")
        
        # Capacity utilization
        team_viz = TeamVisualizer()
        actual_data = {
            'actual_meetings': funnel_metrics['meetings'],
            'actual_contacts': funnel_metrics['contacts']
        }
        fig_capacity = team_viz.create_capacity_utilization(team_capacity, actual_data)
        st.plotly_chart(fig_capacity, use_container_width=True)
        
        # Pipeline coverage
        pipeline_viz = FunnelVisualizer()
        pipeline_data['current_pipeline'] = pipeline_data['pipeline_value_needed'] * 0.85  # Example
        fig_pipeline = pipeline_viz.create_pipeline_coverage_chart(pipeline_data)
        st.plotly_chart(fig_pipeline, use_container_width=True)

with tab3:
    st.header("Compensation Structure")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💼 OTE Structure")
        
        # OTE breakdown
        ote_df = pd.DataFrame({
            'Component': ['Base Salary', 'Variable Comp', 'Total OTE'],
            'Amount': [
                ote_structure['base_salary'],
                ote_structure['variable_comp'],
                ote_structure['total_ote']
            ],
            'Percentage': [
                ote_structure['base_salary_pct'],
                ote_structure['variable_comp_pct'],
                1.0
            ]
        })
        
        st.dataframe(
            ote_df.style.format({"Amount": "${:,.0f}", "Percentage": "{:.0%}"}),
            use_container_width=True
        )
        
        # Health indicator
        if ote_structure['is_healthy']:
            st.success(f"✅ OTE Structure: {ote_structure['health_status']}")
        else:
            st.warning(f"⚠️ OTE Structure: {ote_structure['health_status']}")
        
        st.info(f"""
        **Commission Details:**
        - Effective Rate: {ote_structure['commission_rate']:.2%}
        - Monthly Quota: ${monthly_revenue_target/num_closers:,.0f}
        - Deals per Month: {funnel_metrics['sales']/num_closers:.1f}
        """)
    
    with col2:
        st.subheader("📈 Attainment Tiers")
        
        # Show attainment tiers
        tiers_data = []
        for tier_key, tier in config.ATTAINMENT_TIERS.items():
            sample_quota = monthly_revenue_target / num_closers
            sample_actual = sample_quota * ((tier['min'] + tier['max']) / 2)
            payout = CommissionCalculator.calculate_attainment_payout(
                sample_quota,
                sample_actual,
                ote_structure['commission_rate']
            )
            
            tiers_data.append({
                'Tier': tier['name'],
                'Range': f"{tier['min']:.0%} - {tier['max']:.0%}",
                'Multiplier': f"{tier['multiplier']:.1f}x",
                'Example Payout': f"${payout['adjusted_payout']:,.0f}"
            })
        
        tiers_df = pd.DataFrame(tiers_data)
        st.dataframe(tiers_df, use_container_width=True)
        
        # Attainment distribution (simulated)
        np.random.seed(42)
        attainment_dist = np.random.normal(1.0, 0.3, num_closers) * 100
        attainment_dist = np.clip(attainment_dist, 0, 200)
        
        metrics_viz = MetricsVisualizer()
        fig_dist = metrics_viz.create_attainment_distribution(attainment_dist.tolist())
        st.plotly_chart(fig_dist, use_container_width=True)

with tab4:
    st.header("Unit Economics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 P&L Breakdown")
        
        pl_data = pd.DataFrame({
            'Line Item': [
                'Revenue',
                '- COGS',
                '= Gross Profit',
                '- Sales Costs',
                '- Marketing',
                '- Overhead',
                '- Gov Fees',
                '= EBITDA'
            ],
            'Amount': [
                unit_economics['revenue'],
                -unit_economics['cogs'],
                unit_economics['gross_profit'],
                -unit_economics['sales_costs'],
                -unit_economics['marketing_costs'],
                -unit_economics['overhead'],
                -unit_economics['gov_fees'],
                unit_economics['ebitda']
            ],
            'Margin %': [
                1.0,
                0,
                unit_economics['gross_margin'],
                -unit_economics['sales_costs']/unit_economics['revenue'] if unit_economics['revenue'] > 0 else 0,
                -unit_economics['marketing_costs']/unit_economics['revenue'] if unit_economics['revenue'] > 0 else 0,
                -unit_economics['overhead']/unit_economics['revenue'] if unit_economics['revenue'] > 0 else 0,
                -gov_fee_pct,
                unit_economics['ebitda_margin']
            ]
        })
        
        # Style the dataframe
        def style_pl(val):
            if isinstance(val, str):
                return ''
            return 'color: red' if val < 0 else 'color: green' if val > 0 else ''
        
        st.dataframe(
            pl_data.style.format({"Amount": "${:,.0f}", "Margin %": "{:.1%}"})
                        .applymap(style_pl, subset=['Amount', 'Margin %']),
            use_container_width=True
        )
    
    with col2:
        st.subheader("📊 Health Metrics")
        
        # Calculate LTV:CAC
        cac = (monthly_costs['marketing_costs'] + monthly_costs['sales_costs']) / funnel_metrics['sales'] if funnel_metrics['sales'] > 0 else 0
        ltv = comp_structure['expected_total'] * 0.7  # Assuming 70% gross margin
        ltv_cac = ltv / cac if cac > 0 else 0
        
        # Health scorecard
        health_metrics = {
            'ltv_cac_ratio': ltv_cac,
            'ebitda_margin': unit_economics['ebitda_margin'],
            'pipeline_coverage': pipeline_coverage,
            'team_utilization': capacity_check['closer_utilization'] * 100,
            'ote_health_score': 90 if ote_structure['is_healthy'] else 60
        }
        
        metrics_viz = MetricsVisualizer()
        fig_health = metrics_viz.create_health_scorecard(health_metrics)
        st.plotly_chart(fig_health, use_container_width=True)
        
        # Key metrics summary
        st.info(f"""
        **Key Metrics:**
        - LTV: ${ltv:,.0f}
        - CAC: ${cac:,.0f}
        - LTV:CAC: {ltv_cac:.1f}:1
        - Payback: {cac/(comp_structure['immediate_per_sale']*unit_economics['gross_margin']) if unit_economics['gross_margin'] > 0 else 0:.1f} months
        - Cost of Sales: {unit_economics['cos_percentage']:.1%}
        """)

with tab5:
    st.header("Scenario Analysis")
    
    # Scenario inputs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Conservative")
        cons_close_rate = close_rate * 0.8
        cons_sales = funnel_metrics['meetings'] * cons_close_rate
        cons_revenue = cons_sales * avg_deal_size
        
        st.metric("Close Rate", f"{cons_close_rate:.1%}", f"{(cons_close_rate/close_rate-1):.0%}")
        st.metric("Monthly Sales", f"{cons_sales:.0f}", f"{cons_sales-funnel_metrics['sales']:.0f}")
        st.metric("Revenue", f"${cons_revenue:,.0f}", f"${cons_revenue-monthly_revenue_target:,.0f}")
    
    with col2:
        st.subheader("🎯 Base Case")
        st.metric("Close Rate", f"{close_rate:.1%}", "Current")
        st.metric("Monthly Sales", f"{funnel_metrics['sales']:.0f}", "Target")
        st.metric("Revenue", f"${monthly_revenue_target:,.0f}", "Target")
    
    with col3:
        st.subheader("🚀 Optimistic")
        opt_close_rate = close_rate * 1.2
        opt_sales = funnel_metrics['meetings'] * opt_close_rate
        opt_revenue = opt_sales * avg_deal_size
        
        st.metric("Close Rate", f"{opt_close_rate:.1%}", f"{(opt_close_rate/close_rate-1):.0%}")
        st.metric("Monthly Sales", f"{opt_sales:.0f}", f"{opt_sales-funnel_metrics['sales']:.0f}")
        st.metric("Revenue", f"${opt_revenue:,.0f}", f"${opt_revenue-monthly_revenue_target:,.0f}")
    
    # Sensitivity analysis
    st.subheader("Sensitivity Analysis")
    
    sensitivity_var = st.selectbox(
        "Variable to Test",
        ["Close Rate", "Average Deal Size", "Lead Volume", "Cost per Lead"]
    )
    
    # Calculate sensitivity
    base_ebitda = unit_economics['ebitda']
    changes = [-0.2, -0.1, 0, 0.1, 0.2]
    impacts = {}
    
    for change in changes:
        if sensitivity_var == "Close Rate":
            new_sales = funnel_metrics['meetings'] * close_rate * (1 + change)
            new_revenue = new_sales * avg_deal_size
            impacts[change] = new_revenue - unit_economics['total_opex']
        elif sensitivity_var == "Average Deal Size":
            new_revenue = funnel_metrics['sales'] * avg_deal_size * (1 + change)
            impacts[change] = new_revenue - unit_economics['total_opex']
        # Add more sensitivity calculations
    
    comparison_viz = ComparisonVisualizer()
    fig_sensitivity = comparison_viz.create_sensitivity_analysis(base_ebitda, sensitivity_var, impacts)
    st.plotly_chart(fig_sensitivity, use_container_width=True)

# Footer with export options
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📊 Export to Excel"):
        st.info("Excel export would be implemented here")
with col2:
    if st.button("📄 Generate PDF Report"):
        st.info("PDF generation would be implemented here")
with col3:
    if st.button("💾 Save Scenario"):
        st.session_state.scenario_data = validation_data
        st.success("Scenario saved!")
