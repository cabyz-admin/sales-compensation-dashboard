"""
Enhanced Compensation Structure Module
Real-time compensation modeling and decision tool
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Tuple

def create_compensation_structure(
    team_metrics: Dict,
    gtm_metrics: Dict,
    deal_economics: Dict,
    actual_monthly_revenue: float,
    actual_monthly_sales: float
) -> None:
    """
    Create enhanced compensation structure with real-time data integration
    """
    
    st.markdown("### 💰 **Compensation Structure & Decision Tool**")
    st.info("📊 Real-time compensation modeling based on actual GTM performance")
    
    # Extract team counts
    num_closers = team_metrics.get('num_closers', 8)
    num_setters = team_metrics.get('num_setters', 4)
    num_managers = team_metrics.get('num_managers', 2)
    num_bench = team_metrics.get('num_bench', 2)
    
    # Create tabs for different views
    comp_tabs = st.tabs(["⚙️ Configuration", "📊 Analysis", "💵 Earnings Preview", "🎯 Decision Matrix", "📈 Impact Analysis"])
    
    with comp_tabs[0]:  # Configuration Tab
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            st.markdown("#### **Compensation Model**")
            comp_mode = st.radio(
                "Select structure",
                ["🎯 Performance-Based (30/70)", "⚖️ Balanced (40/60)", "🛡️ Stability-First (60/40)", "🔧 Custom"],
                index=1,
                key="comp_model_selection",
                help="Choose compensation philosophy based on your team culture"
            )
            
            # Smart defaults based on mode
            if comp_mode == "🎯 Performance-Based (30/70)":
                base_pct = 0.30
                closer_ote = 90000
                setter_ote = 45000
                closer_comm = 0.25
                setter_comm = 0.04
            elif comp_mode == "⚖️ Balanced (40/60)":
                base_pct = 0.40
                closer_ote = 80000
                setter_ote = 40000
                closer_comm = 0.20
                setter_comm = 0.03
            elif comp_mode == "🛡️ Stability-First (60/40)":
                base_pct = 0.60
                closer_ote = 75000
                setter_ote = 35000
                closer_comm = 0.15
                setter_comm = 0.02
            else:  # Custom
                base_pct = st.slider("Base/Variable Split", 20, 80, 40, 5, key="custom_base_split") / 100
                closer_ote = st.number_input("Closer OTE ($)", 50000, 150000, 80000, 5000, key="custom_closer_ote")
                setter_ote = st.number_input("Setter OTE ($)", 30000, 70000, 40000, 2500, key="custom_setter_ote")
                closer_comm = st.slider("Closer Commission Pool %", 10, 35, 20, 1, key="custom_closer_pool") / 100
                setter_comm = st.slider("Setter Commission Pool %", 0, 10, 3, 1, key="custom_setter_pool") / 100
            
            manager_ote = st.number_input("Manager OTE ($)", 80000, 200000, 120000, 10000, key="manager_ote_config")
            
            # Show base/variable breakdown
            st.markdown("##### **Structure Breakdown**")
            breakdown_cols = st.columns(2)
            with breakdown_cols[0]:
                st.metric("Base %", f"{base_pct:.0%}")
            with breakdown_cols[1]:
                st.metric("Variable %", f"{1-base_pct:.0%}")
        
        with config_col2:
            st.markdown("#### **Commission Flow Visualization**")
            
            # Calculate actual commissions
            closer_pool = actual_monthly_revenue * closer_comm
            setter_pool = actual_monthly_revenue * setter_comm
            total_commission = closer_pool + setter_pool
            
            # Visual flow diagram
            fig = go.Figure()
            
            # Add revenue box
            fig.add_trace(go.Scatter(
                x=[1], y=[3],
                mode='markers+text',
                marker=dict(size=80, color='#3b82f6'),
                text=[f"Revenue<br>${actual_monthly_revenue:,.0f}"],
                textposition="middle center",
                showlegend=False
            ))
            
            # Add commission pools
            fig.add_trace(go.Scatter(
                x=[2, 2], y=[3.5, 2.5],
                mode='markers+text',
                marker=dict(size=60, color='#f59e0b'),
                text=[f"Closer Pool<br>${closer_pool:,.0f}", f"Setter Pool<br>${setter_pool:,.0f}"],
                textposition="middle right",
                showlegend=False
            ))
            
            # Add per-person amounts
            if num_closers > 0:
                fig.add_trace(go.Scatter(
                    x=[3], y=[3.5],
                    mode='markers+text',
                    marker=dict(size=50, color='#22c55e'),
                    text=[f"Per Closer<br>${closer_pool/num_closers:,.0f}"],
                    textposition="middle right",
                    showlegend=False
                ))
            
            if num_setters > 0:
                fig.add_trace(go.Scatter(
                    x=[3], y=[2.5],
                    mode='markers+text',
                    marker=dict(size=50, color='#22c55e'),
                    text=[f"Per Setter<br>${setter_pool/num_setters:,.0f}"],
                    textposition="middle right",
                    showlegend=False
                ))
            
            # Add arrows
            fig.add_annotation(x=1.5, y=3.25, ax=1, ay=3, xref="x", yref="y", axref="x", ayref="y",
                             arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#94a3b8")
            fig.add_annotation(x=1.5, y=2.75, ax=1, ay=3, xref="x", yref="y", axref="x", ayref="y",
                             arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#94a3b8")
            
            fig.update_layout(
                height=300,
                showlegend=False,
                xaxis=dict(visible=False, range=[0, 4]),
                yaxis=dict(visible=False, range=[2, 4]),
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Commission metrics
            st.markdown("##### **Monthly Commission Metrics**")
            comm_cols = st.columns(2)
            with comm_cols[0]:
                st.metric("Total Commission", f"${total_commission:,.0f}")
                st.metric("Commission Rate", f"{(total_commission/actual_monthly_revenue)*100:.1f}%")
            with comm_cols[1]:
                st.metric("Per Sale Commission", f"${total_commission/max(actual_monthly_sales, 1):,.0f}")
                st.metric("Commission/Employee", f"${total_commission/(num_closers+num_setters):,.0f}" if (num_closers+num_setters) > 0 else "$0")
    
    with comp_tabs[1]:  # Analysis Tab
        st.markdown("#### **Compensation Analytics Dashboard**")
        
        # Build compensation structure
        comp_structure = {
            'closer': {
                'count': num_closers,
                'base': closer_ote * base_pct,
                'variable': closer_ote * (1 - base_pct),
                'ote': closer_ote,
                'actual_commission': closer_pool / num_closers if num_closers > 0 else 0
            },
            'setter': {
                'count': num_setters,
                'base': setter_ote * base_pct,
                'variable': setter_ote * (1 - base_pct),
                'ote': setter_ote,
                'actual_commission': setter_pool / num_setters if num_setters > 0 else 0
            },
            'manager': {
                'count': num_managers,
                'base': manager_ote * 0.6,
                'variable': manager_ote * 0.4,
                'ote': manager_ote,
                'actual_commission': 0  # Managers typically don't get direct commission
            },
            'bench': {
                'count': num_bench,
                'base': 25000 * 0.5,
                'variable': 25000 * 0.5,
                'ote': 25000,
                'actual_commission': 0
            }
        }
        
        # Calculate totals
        total_base = sum(role['base'] * role['count'] for role in comp_structure.values())
        total_ote = sum(role['ote'] * role['count'] for role in comp_structure.values())
        total_actual = total_base + total_commission * 12  # Annualized
        
        # Top metrics
        metric_cols = st.columns(5)
        metric_cols[0].metric("Total OTE", f"${total_ote:,.0f}")
        metric_cols[1].metric("Total Base", f"${total_base:,.0f}")
        metric_cols[2].metric("Actual Total (Projected)", f"${total_actual:,.0f}")
        metric_cols[3].metric("vs OTE", f"{(total_actual/total_ote-1)*100:+.0f}%" if total_ote > 0 else "0%")
        metric_cols[4].metric("Comp/Revenue", f"{(total_actual/(actual_monthly_revenue*12))*100:.1f}%" if actual_monthly_revenue > 0 else "0%")
        
        # Detailed breakdown table
        st.markdown("##### **Compensation Breakdown by Role**")
        
        comp_data = []
        for role_name, role_data in comp_structure.items():
            if role_data['count'] > 0:
                monthly_base = role_data['base'] / 12
                monthly_commission = role_data['actual_commission']
                monthly_total = monthly_base + monthly_commission
                annual_projection = monthly_total * 12
                
                comp_data.append({
                    'Role': role_name.capitalize(),
                    'Count': role_data['count'],
                    'OTE': f"${role_data['ote']:,.0f}",
                    'Base/Mo': f"${monthly_base:,.0f}",
                    'Commission/Mo': f"${monthly_commission:,.0f}",
                    'Total/Mo': f"${monthly_total:,.0f}",
                    'Annual Projection': f"${annual_projection:,.0f}",
                    'vs OTE': f"{(annual_projection/role_data['ote']-1)*100:+.0f}%" if role_data['ote'] > 0 else "N/A",
                    'Performance': "🟢" if annual_projection >= role_data['ote'] else "🟡" if annual_projection >= role_data['ote']*0.8 else "🔴"
                })
        
        df_comp = pd.DataFrame(comp_data)
        if not df_comp.empty:
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        # Visualizations
        viz_cols = st.columns(2)
        
        with viz_cols[0]:
            # Pie chart of compensation distribution
            roles = [r for r, d in comp_structure.items() if d['count'] > 0]
            values = [d['count'] * d['ote'] for r, d in comp_structure.items() if d['count'] > 0]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=roles,
                values=values,
                hole=0.3,
                marker_colors=['#3b82f6', '#f59e0b', '#22c55e', '#ef4444']
            )])
            fig_pie.update_layout(
                title="OTE Distribution by Role",
                height=350
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with viz_cols[1]:
            # Bar chart of base vs variable
            fig_bar = go.Figure()
            
            for role_name, role_data in comp_structure.items():
                if role_data['count'] > 0:
                    fig_bar.add_trace(go.Bar(
                        name=role_name.capitalize(),
                        x=['Base', 'Variable', 'Actual Commission'],
                        y=[
                            role_data['base'],
                            role_data['variable'],
                            role_data['actual_commission'] * 12
                        ]
                    ))
            
            fig_bar.update_layout(
                title="Base vs Variable vs Actual by Role (Annual)",
                height=350,
                barmode='group',
                yaxis_title="Amount ($)"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    return comp_structure, closer_comm, setter_comm
