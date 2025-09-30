# Archived Dashboard Code

This file contains old code that has been replaced or integrated elsewhere. Kept for reference only.

## Old Multi-Channel GTM Tab

**Status**: Integrated into main GTM Command Center tab  
**Date Archived**: 2025-09-30  
**Reason**: Code has been refactored and integrated into the main dashboard. Keeping here for reference in case we need to restore or reference the old implementation.

### Original Implementation

The old tab code below has been integrated into the main GTM Command Center.
Keeping it commented for reference only.

```python
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
gtm_channels = st.session_state.get('gtm_channels', [])
if not gtm_channels:
    gtm_channels = st.session_state['gtm_channels'] = [
        {
            'id': 'channel_1',
            'name': 'Primary Channel',
            'segment': 'SMB',
            'lead_source': 'Inbound Marketing',
            'icon': '🏢'
        }
    ]

if gtm_channels:
    st.markdown("### 📊 Channel Configuration")
    
    # Create expandable sections for each channel
    for idx, channel_config in enumerate(gtm_channels):
        icon_display = channel_config.get('icon', '📊')
        display_name = channel_config.get('name', f"Channel {idx+1}")
        with st.expander(f"{icon_display} **{display_name}**", expanded=(idx == 0)):
            # Channel settings in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic settings
                channel_name = st.text_input(
                    "Channel Name",
                    value=channel_config.get('name', display_name),
                    key=f"{channel_config['id']}_name"
                )
                
                segment = st.selectbox(
                    "Segment",
                    options=['SMB', 'MID', 'ENT', 'Custom'],
                    index=['SMB', 'MID', 'ENT', 'Custom'].index(channel_config.get('segment', 'SMB')),
                    key=f"{channel_config['id']}_segment"
                )
                
                lead_source = st.selectbox(
                    "Lead Source",
                    options=['Inbound Marketing', 'Outbound SDR', 'Account-Based Marketing', 'Partner Channel', 'Events', 'Content Marketing'],
                    index=['Inbound Marketing', 'Outbound SDR', 'Account-Based Marketing', 'Partner Channel', 'Events', 'Content Marketing'].index(channel_config.get('lead_source', 'Inbound Marketing')),
                    key=f"{channel_config['id']}_source"
                )
                
                # Volume and cost
                monthly_leads = st.number_input(
                    "Monthly Leads",
                    value=channel_config.get('monthly_leads', 1000 if segment == 'SMB' else 300 if segment == 'MID' else 50),
                    step=50,
                    key=f"{channel_config['id']}_leads"
                )
                
                cpl = st.number_input(
                    "Cost Per Lead ($)",
                    value=channel_config.get('cpl', 50 if segment == 'SMB' else 200 if segment == 'MID' else 1000),
                    step=10,
                    key=f"{channel_config['id']}_cpl"
                )
            
            with col2:
                # Funnel metrics
                contact_rate = st.slider(
                    "Contact Rate %",
                    0, 100, 
                    int(channel_config.get('contact_rate', 0.65 if segment == 'SMB' else 0.55 if segment == 'MID' else 0.45) * 100),
                    5,
                    key=f"{channel_config['id']}_contact"
                ) / 100.0
                
                meeting_rate = st.slider(
                    "Meeting Rate %",
                    0, 100,
                    int(channel_config.get('meeting_rate', 0.40 if segment == 'SMB' else 0.35 if segment == 'MID' else 0.30) * 100),
                    5,
                    key=f"{channel_config['id']}_meeting"
                ) / 100.0
                
                show_up_rate = st.slider(
                    "Show-up Rate %",
                    0, 100,
                    int(channel_config.get('show_up_rate', 0.70 if segment == 'SMB' else 0.75 if segment == 'MID' else 0.85) * 100),
                    5,
                    key=f"{channel_config['id']}_showup"
                ) / 100.0
                
                close_rate = st.slider(
                    "Close Rate %",
                    0, 100,
                    int(channel_config.get('close_rate', 0.30 if segment == 'SMB' else 0.25 if segment == 'MID' else 0.20) * 100),
                    5,
                    key=f"{channel_config['id']}_close"
                ) / 100.0
                
                avg_deal_value = st.number_input(
                    "Avg Deal Value ($)",
                    value=channel_config.get('avg_deal_value', 15000 if segment == 'SMB' else 50000 if segment == 'MID' else 250000),
                    step=1000,
                    key=f"{channel_config['id']}_deal"
                )
            
            # Sales cycle
            sales_cycle = st.slider(
                "Sales Cycle (days)",
                7, 180,
                channel_config.get('sales_cycle_days', 21 if segment == 'SMB' else 45 if segment == 'MID' else 90),
                7,
                key=f"{channel_config['id']}_cycle"
            )
            
            # Persist updates back to session state
            channel_config.update({
                'name': channel_name,
                'segment': segment,
                'lead_source': lead_source,
                'monthly_leads': monthly_leads,
                'cpl': cpl,
                'contact_rate': contact_rate,
                'meeting_rate': meeting_rate,
                'show_up_rate': show_up_rate,
                'close_rate': close_rate,
                'avg_deal_value': avg_deal_value,
                'sales_cycle_days': sales_cycle,
                'icon': {
                    'SMB': '🏢',
                    'MID': '🏛️',
                    'ENT': '🏰',
                    'Custom': '🎯'
                }.get(segment, '🎯')
            })

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
        total_cost = ch.get('total_marketing_cost', 0)
        daily_cost = total_cost / 30 if total_cost else 0
        weekly_cost = total_cost / 4 if total_cost else 0
        annual_cost = total_cost * 12
        channel_data.append({
            'Channel': ch['name'],
            'Segment': ch['segment'],
            'Leads': ch['monthly_leads'],
            'Meetings Held': f"{ch['meetings_held']:.0f}",
            'Sales': f"{ch['sales']:.0f}",
            'Revenue': f"${ch['revenue']:,.0f}",
            'CAC': f"${ch['cac']:,.0f}",
            'Spend/Day': f"${daily_cost:,.0f}",
            'Spend/Week': f"${weekly_cost:,.0f}",
            'Spend/Month': f"${total_cost:,.0f}",
            'Spend/Year': f"${annual_cost:,.0f}",
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
            "LTV:CAC": st.column_config.TextColumn("LTV:CAC", width="small"),
            "Spend/Day": st.column_config.TextColumn("Spend/Day", width="small"),
            "Spend/Week": st.column_config.TextColumn("Spend/Week", width="small"),
            "Spend/Month": st.column_config.TextColumn("Spend/Month", width="small"),
            "Spend/Year": st.column_config.TextColumn("Spend/Year", width="small")
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
```

---

## Notes

- This code was part of a separate Multi-Channel GTM tab
- Functionality has been integrated and improved in the main GTM Command Center
- Kept for reference in case rollback or feature comparison is needed
- All calculations and logic remain valid, just location changed
