"""
Streamlit Cloud Optimized Version - Lighter dashboard for deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Simplified imports - inline classes instead of module imports
class MultiChannelGTM:
    @staticmethod
    def define_channel(name, lead_source, segment, monthly_leads, contact_rate, 
                      meeting_rate, show_up_rate, close_rate, avg_deal_value, cpl, sales_cycle_days):
        """Define a channel with its funnel metrics"""
        contacts = monthly_leads * contact_rate
        meetings_scheduled = contacts * meeting_rate
        meetings_held = meetings_scheduled * show_up_rate
        sales = meetings_held * close_rate
        revenue = sales * avg_deal_value
        cac = (monthly_leads * cpl) / sales if sales > 0 else 0
        
        return {
            'name': name,
            'lead_source': lead_source,
            'segment': segment,
            'monthly_leads': monthly_leads,
            'contact_rate': contact_rate,
            'meeting_rate': meeting_rate,
            'show_up_rate': show_up_rate,
            'close_rate': close_rate,
            'contacts': contacts,
            'meetings_scheduled': meetings_scheduled,
            'meetings_held': meetings_held,
            'sales': sales,
            'revenue': revenue,
            'avg_deal_value': avg_deal_value,
            'cpl': cpl,
            'cac': cac,
            'sales_cycle_days': sales_cycle_days
        }
    
    @staticmethod
    def aggregate_channels(channels):
        """Aggregate metrics across all channels"""
        return {
            'total_leads': sum(ch['monthly_leads'] for ch in channels),
            'total_contacts': sum(ch['contacts'] for ch in channels),
            'total_meetings_scheduled': sum(ch['meetings_scheduled'] for ch in channels),
            'total_meetings_held': sum(ch['meetings_held'] for ch in channels),
            'total_sales': sum(ch['sales'] for ch in channels),
            'total_revenue': sum(ch['revenue'] for ch in channels),
            'avg_cpl': np.mean([ch['cpl'] for ch in channels]),
            'avg_cac': np.mean([ch['cac'] for ch in channels]) if channels else 0,
            'channels': channels
        }

# ============= CONFIGURATION =============
st.set_page_config(
    page_title="🎯 Sales Compensation Dashboard",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🎯 Sales Compensation Dashboard - Cloud Version")
st.info("Optimized for Streamlit Cloud deployment")

# ============= SIDEBAR INPUTS =============
st.sidebar.header("📊 Configuration")

# Revenue Targets
st.sidebar.subheader("🎯 Revenue Targets")
monthly_revenue_target = st.sidebar.number_input(
    "Monthly Revenue Target ($)",
    value=4166667,
    step=100000
)

# Deal Economics - Insurance Model
st.sidebar.subheader("💰 Deal Economics")
avg_pm = st.sidebar.number_input(
    "Monthly Premium (MXN)",
    min_value=1000, max_value=10000, value=3000, step=100
)
contract_years = st.sidebar.number_input(
    "Contract Years",
    min_value=1, max_value=30, value=25, step=1
)
carrier_rate = st.sidebar.slider(
    "Carrier Compensation Rate (%)",
    min_value=1.0, max_value=5.0, value=2.7, step=0.1
) / 100

# Calculate deal economics
contract_months = contract_years * 12
total_contract_value = avg_pm * contract_months
total_comp = total_contract_value * carrier_rate
comp_immediate = total_comp * 0.7
comp_deferred = total_comp * 0.3

st.sidebar.info(f"""
**Deal Summary:**
• Contract: ${total_contract_value:,.0f} MXN
• Total Comp: ${total_comp:,.0f}
• Upfront (70%): ${comp_immediate:,.0f}
• Month 18 (30%): ${comp_deferred:,.0f}
""")

# Team Structure
st.sidebar.subheader("👥 Team Structure")
num_closers = st.sidebar.number_input("Closers", value=8, min_value=1)
num_setters = st.sidebar.number_input("Setters", value=3, min_value=0)

# Operating Costs
st.sidebar.subheader("💸 Operating Costs")
office_rent = st.sidebar.number_input("Office Rent ($)", value=10000, step=1000)
software_costs = st.sidebar.number_input("Software ($)", value=5000, step=500)
other_opex = st.sidebar.number_input("Other OpEx ($)", value=15000, step=1000)
monthly_opex = office_rent + software_costs + other_opex

# ============= MAIN AREA =============
# Multi-Channel GTM Configuration
st.header("🚀 Multi-Channel GTM Configuration")

# Initialize session state
if 'channels' not in st.session_state:
    st.session_state.channels = []

# Channel management
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("➕ Add Channel", use_container_width=True):
        st.session_state.channels.append({
            'id': f"channel_{len(st.session_state.channels) + 1}",
            'name': f"Channel {len(st.session_state.channels) + 1}"
        })
    if st.button("🗑️ Remove Last", use_container_width=True):
        if st.session_state.channels:
            st.session_state.channels.pop()

with col2:
    st.info(f"Managing {len(st.session_state.channels)} channel(s)")

# Configure channels
channels = []
for idx, channel_config in enumerate(st.session_state.channels):
    with st.expander(f"**{channel_config.get('name', f'Channel {idx+1}')}**", expanded=(idx == 0)):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            channel_name = st.text_input("Name", value=channel_config['name'], key=f"name_{idx}")
            segment = st.selectbox("Segment", ['SMB', 'MID', 'ENT'], key=f"segment_{idx}")
            cost_point = st.selectbox(
                "Cost Input",
                ["Cost per Lead", "Cost per Meeting", "Cost per Sale"],
                key=f"cost_{idx}"
            )
            
            if cost_point == "Cost per Lead":
                cpl = st.number_input("CPL ($)", value=50, step=10, key=f"cpl_{idx}")
                leads = st.number_input("Monthly Leads", value=1000, step=100, key=f"leads_{idx}")
            elif cost_point == "Cost per Meeting":
                cost_per_meeting = st.number_input("Cost/Meeting ($)", value=200, step=25, key=f"cpm_{idx}")
                meetings_target = st.number_input("Meetings Target", value=20, step=5, key=f"meetings_{idx}")
                leads = meetings_target * 5  # Rough estimate
                cpl = cost_per_meeting / 5
            else:  # Cost per Sale
                cost_per_sale = st.number_input("Cost/Sale ($)", value=500, step=50, key=f"cps_{idx}")
                sales_target = st.number_input("Sales Target", value=5, step=1, key=f"sales_{idx}")
                leads = sales_target * 20
                cpl = cost_per_sale / 20
        
        with col2:
            contact_rt = st.slider("Contact %", 0, 100, 65, 5, key=f"contact_{idx}") / 100
            meeting_rt = st.slider("Meeting %", 0, 100, 40, 5, key=f"meeting_{idx}") / 100
            showup_rt = st.slider("Show-up %", 0, 100, 70, 5, key=f"showup_{idx}") / 100
            close_rt = st.slider("Close %", 0, 100, 25, 5, key=f"close_{idx}") / 100
            
            # Recalculate based on cost input
            if cost_point == "Cost per Meeting":
                conversion_to_meeting = contact_rt * meeting_rt * showup_rt
                leads = meetings_target / conversion_to_meeting if conversion_to_meeting > 0 else meetings_target * 5
                cpl = cost_per_meeting / conversion_to_meeting if conversion_to_meeting > 0 else cost_per_meeting
                st.info(f"📊 Need {leads:.0f} leads for {meetings_target} meetings")
            elif cost_point == "Cost per Sale":
                full_conversion = contact_rt * meeting_rt * showup_rt * close_rt
                leads = sales_target / full_conversion if full_conversion > 0 else sales_target * 20
                cpl = cost_per_sale / full_conversion if full_conversion > 0 else cost_per_sale
                st.info(f"📊 Need {leads:.0f} leads for {sales_target} sales")
        
        with col3:
            st.markdown("**Deal Value**")
            st.info(f"💰 ${total_comp:,.0f}")
            st.caption(f"Contract: ${total_contract_value:,.0f}")
            st.caption(f"Upfront: ${comp_immediate:,.0f}")
            cycle_days = st.slider("Sales Cycle", 7, 180, 30, 7, key=f"cycle_{idx}")
            source = st.selectbox("Source", ['Inbound', 'Outbound'], key=f"source_{idx}")
        
        # Calculate channel metrics
        channel = MultiChannelGTM.define_channel(
            name=channel_name,
            lead_source=source,
            segment=segment,
            monthly_leads=leads,
            contact_rate=contact_rt,
            meeting_rate=meeting_rt,
            show_up_rate=showup_rt,
            close_rate=close_rt,
            avg_deal_value=total_comp,
            cpl=cpl,
            sales_cycle_days=cycle_days
        )
        channels.append(channel)
        
        # Show channel metrics
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

# Aggregate metrics if channels exist
if channels:
    st.header("📊 Business Performance Dashboard")
    
    aggregated = MultiChannelGTM.aggregate_channels(channels)
    monthly_sales = aggregated['total_sales']
    monthly_revenue_total = aggregated['total_revenue']
    monthly_meetings = aggregated['total_meetings_held']
    
    # Calculate financial metrics
    monthly_revenue_immediate = monthly_sales * comp_immediate
    monthly_revenue_deferred = monthly_sales * comp_deferred
    total_marketing_costs = sum(ch['monthly_leads'] * ch['cpl'] for ch in channels)
    cac = total_marketing_costs / monthly_sales if monthly_sales > 0 else 0
    ltv = total_comp
    ltv_cac_ratio = ltv / cac if cac > 0 else 0
    
    # Display metrics
    primary_cols = st.columns(6)
    with primary_cols[0]:
        st.metric("💵 Monthly Revenue", f"${monthly_revenue_total:,.0f}", 
                  f"{(monthly_revenue_total/monthly_revenue_target - 1)*100:.1f}% vs target")
    with primary_cols[1]:
        st.metric("📈 Monthly Sales", f"{monthly_sales:.0f}")
    with primary_cols[2]:
        st.metric("🎯 LTV:CAC", f"{ltv_cac_ratio:.1f}:1")
    with primary_cols[3]:
        st.metric("💰 CAC", f"${cac:,.0f}")
    with primary_cols[4]:
        st.metric("🤝 Meetings", f"{monthly_meetings:.0f}/mo")
    with primary_cols[5]:
        capacity_util = monthly_meetings / (num_closers * 60) if num_closers > 0 else 0
        st.metric("📅 Capacity", f"{capacity_util:.0%}")
    
    # Channel comparison
    st.subheader("📊 Channel Performance")
    channel_df = pd.DataFrame(channels)
    channel_df = channel_df[['name', 'monthly_leads', 'sales', 'revenue', 'cac']]
    channel_df.columns = ['Channel', 'Leads', 'Sales', 'Revenue', 'CAC']
    st.dataframe(channel_df, use_container_width=True)
    
    # Funnel visualization
    st.subheader("🔧 Conversion Funnel")
    funnel_data = {
        'Stage': ['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
        'Count': [
            aggregated['total_leads'],
            aggregated['total_contacts'],
            aggregated['total_meetings_scheduled'],
            aggregated['total_meetings_held'],
            aggregated['total_sales']
        ]
    }
    
    fig = go.Figure(data=[go.Funnel(
        y=funnel_data['Stage'],
        x=funnel_data['Count'],
        textposition="inside",
        textinfo="value+percent initial"
    )])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("👆 Add channels to see metrics")

# Footer
st.markdown("---")
st.caption("Sales Compensation Dashboard - Cloud Optimized Version")
