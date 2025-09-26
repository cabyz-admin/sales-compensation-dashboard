import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Sales Compensation & Monte Carlo Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("🎯 Advanced Sales Compensation Structure & Monte Carlo Simulation")
st.markdown("**First-Principles Behavioral Psychology-Based Commission Model with Transparent Math**")

# Sidebar for inputs
st.sidebar.header("📋 Model Parameters")

# Team Structure Parameters
st.sidebar.subheader("Team Structure")
total_team_size = st.sidebar.slider("Total Team Size", 5, 50, 20)
bench_percentage = st.sidebar.slider("Bench Percentage (%)", 10, 40, 20)
setter_percentage = st.sidebar.slider("Appointment Setter Percentage (%)", 30, 60, 40)
closer_percentage = 100 - bench_percentage - setter_percentage

# Lead Generation Parameters
st.sidebar.subheader("Lead Generation")
daily_leads = st.sidebar.slider("Daily Leads", 50, 500, 200)
lead_cost = st.sidebar.slider("Cost per Lead ($)", 10, 100, 25)

# Conversion Rates
st.sidebar.subheader("Conversion Rates")
contact_rate = st.sidebar.slider("Contact Rate (%)", 40, 90, 70) / 100
meeting_rate = st.sidebar.slider("Meeting Booking Rate (%)", 20, 60, 35) / 100
close_rate = st.sidebar.slider("Close Rate (%)", 15, 45, 25) / 100

# Financial Parameters
st.sidebar.subheader("Financial Parameters")
avg_acv = st.sidebar.slider("Average Contract Value ($)", 5000, 50000, 15000)
commission_rate = st.sidebar.slider("Base Commission Rate (%)", 1.0, 5.0, 2.7) / 100

# Behavioral Incentives
st.sidebar.subheader("Behavioral Incentives")
quick_response_bonus = st.sidebar.slider("Quick Response Bonus (%)", 5, 15, 10) / 100
follow_up_bonus = st.sidebar.slider("Follow-up Completion Bonus (%)", 2, 8, 5) / 100

# Target Parameters
st.sidebar.subheader("Business Targets")
daily_ebitda_target = st.sidebar.slider("Daily EBITDA Target ($)", 5000, 20000, 10000)

# Calculate team composition
bench_count = int(total_team_size * bench_percentage / 100)
setter_count = int(total_team_size * setter_percentage / 100)
closer_count = total_team_size - bench_count - setter_count

# Main dashboard layout
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Bench Team", f"{bench_count} people", f"{bench_percentage}%")
with col2:
    st.metric("Appointment Setters", f"{setter_count} people", f"{setter_percentage}%")
with col3:
    st.metric("Closers", f"{closer_count} people", f"{closer_percentage}%")

# Compensation Structure Section
st.header("💰 Compensation Structure Design")

# Bench System
st.subheader("🏃‍♂️ Bench System (Performance Recovery)")
st.markdown("""
**Bench Criteria:** Underperforming team members who haven't met KPIs
- **Task:** Call old leads and secure 5 meetings to return to active duty
- **Compensation:** Base salary only ($3,000/month) + $100 per meeting booked
- **Behavioral Psychology:** Creates urgency and clear path back to earning potential
""")

# Appointment Setter Incentives
st.subheader("📞 Appointment Setter Incentives")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **Base Commission:** 15% of closer's commission when lead closes
    
    **Speed Incentives:**
    - +10% bonus for contacting lead within 15 minutes
    - Research shows 5-minute response = 21x higher conversion
    
    **Quality Incentives:**
    - +5% bonus for completing 2+ follow-ups per lead
    - Minimum 2 follow-up calls required for commission eligibility
    """)

with col2:
    # Calculate setter economics
    monthly_leads = daily_leads * 30
    monthly_contacts = monthly_leads * contact_rate
    monthly_meetings = monthly_contacts * meeting_rate
    monthly_closes = monthly_meetings * close_rate
    
    base_setter_commission = (monthly_closes * avg_acv * commission_rate * 0.15) / setter_count
    speed_bonus = base_setter_commission * quick_response_bonus
    quality_bonus = base_setter_commission * follow_up_bonus
    total_setter_commission = base_setter_commission + speed_bonus + quality_bonus
    
    st.metric("Base Monthly Commission", f"${base_setter_commission:,.0f}")
    st.metric("With Speed Bonus", f"${base_setter_commission + speed_bonus:,.0f}")
    st.metric("Total with All Bonuses", f"${total_setter_commission:,.0f}")

# Closer Compensation
st.subheader("🎯 Closer Compensation Structure")

# Tiered commission structure based on your CSV data
tiers = [
    {"attainment": "0-40%", "multiplier": 0.6, "description": "Recovery Mode"},
    {"attainment": "40-70%", "multiplier": 0.8, "description": "Building Momentum"},
    {"attainment": "70-100%", "multiplier": 1.0, "description": "Target Performance"},
    {"attainment": "100-150%", "multiplier": 1.2, "description": "Exceeding Expectations"},
    {"attainment": "150%+", "multiplier": 1.6, "description": "Elite Performance"}
]

tier_df = pd.DataFrame(tiers)
st.table(tier_df)

# Monte Carlo Simulation Section
st.header("🎲 Monte Carlo Simulation (1000+ Trials)")

if st.button("Run Monte Carlo Simulation", type="primary"):
    with st.spinner("Running 5000 Monte Carlo simulations..."):
        
        # Monte Carlo parameters
        n_simulations = 5000
        results = []
        
        for i in range(n_simulations):
            # Add variability to key parameters
            sim_daily_leads = np.random.normal(daily_leads, daily_leads * 0.1)
            sim_contact_rate = np.random.beta(7, 3) * 0.9  # Beta distribution for rates
            sim_meeting_rate = np.random.beta(4, 6) * 0.6
            sim_close_rate = np.random.beta(3, 9) * 0.4
            sim_acv = np.random.lognormal(np.log(avg_acv), 0.2)
            
            # Calculate monthly metrics
            monthly_leads = sim_daily_leads * 30
            monthly_contacts = monthly_leads * sim_contact_rate
            monthly_meetings = monthly_contacts * sim_meeting_rate
            monthly_sales = monthly_meetings * sim_close_rate
            
            # Revenue calculations
            monthly_revenue = monthly_sales * sim_acv
            
            # Cost calculations
            lead_costs = monthly_leads * lead_cost
            base_salaries = total_team_size * 4000  # Average base salary
            
            # Commission calculations
            total_commission = monthly_revenue * commission_rate
            
            # EBITDA calculation
            monthly_ebitda = monthly_revenue - lead_costs - base_salaries - total_commission
            daily_ebitda = monthly_ebitda / 30
            
            # CAC and LTV
            cac = (lead_costs + base_salaries * 0.3) / monthly_sales if monthly_sales > 0 else 0
            ltv = sim_acv * 2.5  # Assuming 2.5x multiple for LTV
            ltv_cac_ratio = ltv / cac if cac > 0 else 0
            
            results.append({
                'monthly_leads': monthly_leads,
                'monthly_contacts': monthly_contacts,
                'monthly_meetings': monthly_meetings,
                'monthly_sales': monthly_sales,
                'monthly_revenue': monthly_revenue,
                'monthly_commission': total_commission,
                'monthly_ebitda': monthly_ebitda,
                'daily_ebitda': daily_ebitda,
                'cac': cac,
                'ltv': ltv,
                'ltv_cac_ratio': ltv_cac_ratio
            })
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)
        
        # Display results
        st.subheader("📊 Monte Carlo Results Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg Monthly Revenue", 
                f"${results_df['monthly_revenue'].mean():,.0f}",
                f"±${results_df['monthly_revenue'].std():,.0f}"
            )
        
        with col2:
            st.metric(
                "Avg Daily EBITDA", 
                f"${results_df['daily_ebitda'].mean():,.0f}",
                f"Target: ${daily_ebitda_target:,.0f}"
            )
        
        with col3:
            st.metric(
                "Avg LTV:CAC Ratio", 
                f"{results_df['ltv_cac_ratio'].mean():.1f}:1",
                "Target: 3:1"
            )
        
        with col4:
            success_rate = (results_df['daily_ebitda'] >= daily_ebitda_target).mean() * 100
            st.metric(
                "Target Achievement", 
                f"{success_rate:.1f}%",
                "Days hitting target"
            )
        
        # Visualizations
        st.subheader("📈 Distribution Analysis")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily EBITDA Distribution', 'Monthly Revenue Distribution', 
                          'LTV:CAC Ratio Distribution', 'Monthly Sales Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Daily EBITDA histogram
        fig.add_trace(
            go.Histogram(x=results_df['daily_ebitda'], name="Daily EBITDA", nbinsx=50),
            row=1, col=1
        )
        
        # Monthly Revenue histogram
        fig.add_trace(
            go.Histogram(x=results_df['monthly_revenue'], name="Monthly Revenue", nbinsx=50),
            row=1, col=2
        )
        
        # LTV:CAC Ratio histogram
        fig.add_trace(
            go.Histogram(x=results_df['ltv_cac_ratio'], name="LTV:CAC Ratio", nbinsx=50),
            row=2, col=1
        )
        
        # Monthly Sales histogram
        fig.add_trace(
            go.Histogram(x=results_df['monthly_sales'], name="Monthly Sales", nbinsx=50),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Percentile Analysis
        st.subheader("📊 Percentile Analysis")
        
        percentiles = [10, 25, 50, 75, 90]
        percentile_data = []
        
        for p in percentiles:
            percentile_data.append({
                'Percentile': f"{p}th",
                'Daily EBITDA': f"${np.percentile(results_df['daily_ebitda'], p):,.0f}",
                'Monthly Revenue': f"${np.percentile(results_df['monthly_revenue'], p):,.0f}",
                'Monthly Sales': f"{np.percentile(results_df['monthly_sales'], p):.0f}",
                'LTV:CAC Ratio': f"{np.percentile(results_df['ltv_cac_ratio'], p):.1f}:1"
            })
        
        percentile_df = pd.DataFrame(percentile_data)
        st.table(percentile_df)

# Transparent Math Section
st.header("🔢 Transparent Mathematical Formulas")

st.subheader("Sales Funnel Mathematics")
st.code(f"""
# Daily Lead Processing
Daily Leads = {daily_leads}
Contact Rate = {contact_rate:.1%}
Meeting Rate = {meeting_rate:.1%} 
Close Rate = {close_rate:.1%}

# Monthly Calculations
Monthly Leads = {daily_leads} × 30 = {daily_leads * 30:,.0f}
Monthly Contacts = {daily_leads * 30:,.0f} × {contact_rate:.1%} = {daily_leads * 30 * contact_rate:,.0f}
Monthly Meetings = {daily_leads * 30 * contact_rate:,.0f} × {meeting_rate:.1%} = {daily_leads * 30 * contact_rate * meeting_rate:,.0f}
Monthly Sales = {daily_leads * 30 * contact_rate * meeting_rate:,.0f} × {close_rate:.1%} = {daily_leads * 30 * contact_rate * meeting_rate * close_rate:,.0f}
""")

st.subheader("Revenue & Commission Calculations")
monthly_sales_calc = daily_leads * 30 * contact_rate * meeting_rate * close_rate
monthly_revenue_calc = monthly_sales_calc * avg_acv
total_commission_calc = monthly_revenue_calc * commission_rate

st.code(f"""
# Revenue Calculation
Monthly Revenue = {monthly_sales_calc:.0f} sales × ${avg_acv:,} ACV = ${monthly_revenue_calc:,.0f}

# Commission Calculation
Total Commission = ${monthly_revenue_calc:,.0f} × {commission_rate:.1%} = ${total_commission_calc:,.0f}

# Commission Split (70% immediate, 30% after 13 months)
Immediate Commission = ${total_commission_calc:,.0f} × 70% = ${total_commission_calc * 0.7:,.0f}
Deferred Commission = ${total_commission_calc:,.0f} × 30% = ${total_commission_calc * 0.3:,.0f}
""")

st.subheader("CAC & LTV Analysis")
total_costs = (daily_leads * 30 * lead_cost) + (total_team_size * 4000)
cac_calc = total_costs / monthly_sales_calc if monthly_sales_calc > 0 else 0
ltv_calc = avg_acv * 2.5

st.code(f"""
# Customer Acquisition Cost (CAC)
Total Monthly Costs = (Lead Costs + Salaries + Marketing)
Total Monthly Costs = ${daily_leads * 30 * lead_cost:,.0f} + ${total_team_size * 4000:,.0f} = ${total_costs:,.0f}
CAC = ${total_costs:,.0f} ÷ {monthly_sales_calc:.0f} sales = ${cac_calc:,.0f}

# Lifetime Value (LTV)
LTV = ${avg_acv:,} × 2.5 (retention multiplier) = ${ltv_calc:,.0f}

# LTV:CAC Ratio
LTV:CAC = ${ltv_calc:,.0f} ÷ ${cac_calc:,.0f} = {ltv_calc/cac_calc if cac_calc > 0 else 0:.1f}:1
Target: 3:1 (Healthy business ratio)
""")

# Reverse Engineering Section
st.header("🔄 Reverse Engineering for $10K Daily EBITDA")

st.subheader("Target Achievement Analysis")
target_monthly_ebitda = daily_ebitda_target * 30
required_revenue = target_monthly_ebitda + total_costs + total_commission_calc
required_sales = required_revenue / avg_acv
required_leads = required_sales / (contact_rate * meeting_rate * close_rate)

st.code(f"""
# Reverse Engineering Calculation
Target Daily EBITDA = ${daily_ebitda_target:,}
Target Monthly EBITDA = ${target_monthly_ebitda:,}

# Required Revenue Calculation
Required Revenue = EBITDA + Costs + Commissions
Required Revenue = ${target_monthly_ebitda:,} + ${total_costs:,} + ${total_commission_calc:,.0f}
Required Revenue = ${required_revenue:,.0f}

# Required Sales & Leads
Required Sales = ${required_revenue:,.0f} ÷ ${avg_acv:,} = {required_sales:.0f} sales/month
Required Leads = {required_sales:.0f} ÷ ({contact_rate:.1%} × {meeting_rate:.1%} × {close_rate:.1%})
Required Leads = {required_leads:.0f} leads/month = {required_leads/30:.0f} leads/day

Current vs Required:
Current Daily Leads: {daily_leads}
Required Daily Leads: {required_leads/30:.0f}
Gap: {(required_leads/30) - daily_leads:+.0f} leads/day
""")

# Behavioral Psychology Insights
st.header("🧠 Behavioral Psychology Implementation")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Speed Response Psychology")
    st.markdown("""
    **Research-Based Incentives:**
    - 5-minute response = 21x higher conversion
    - 15-minute response bonus drives urgency
    - Creates competitive environment among setters
    
    **Implementation:**
    - Real-time lead alerts
    - Leaderboard for response times
    - Immediate bonus visibility
    """)

with col2:
    st.subheader("Follow-up Persistence")
    st.markdown("""
    **Quality Over Quantity:**
    - Minimum 2 follow-ups required
    - Bonus for completion drives thoroughness
    - Prevents "spray and pray" mentality
    
    **Tracking:**
    - CRM integration for follow-up verification
    - Quality scoring system
    - Peer recognition for best practices
    """)

# Footer with key insights
st.header("🎯 Key Performance Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Current Model Performance**
    - Monthly Revenue: ${monthly_revenue_calc:,.0f}
    - Daily EBITDA: ${(monthly_revenue_calc - total_costs - total_commission_calc)/30:,.0f}
    - Team Efficiency: {monthly_sales_calc/total_team_size:.1f} sales/person
    """)

with col2:
    st.warning(f"""
    **Optimization Opportunities**
    - Increase contact rate by 10% → +${monthly_revenue_calc * 0.1:,.0f} revenue
    - Improve close rate by 5% → +${monthly_revenue_calc * 0.2:,.0f} revenue
    - Reduce lead cost by $5 → +${daily_leads * 30 * 5:,.0f} monthly savings
    """)

with col3:
    st.success(f"""
    **Behavioral Impact**
    - Speed bonus potential: +{quick_response_bonus:.0%} commission
    - Quality bonus potential: +{follow_up_bonus:.0%} commission
    - Combined uplift: +{(quick_response_bonus + follow_up_bonus):.0%} total
    """)

st.markdown("---")
st.markdown("**Built with first-principles thinking and behavioral psychology research**")
