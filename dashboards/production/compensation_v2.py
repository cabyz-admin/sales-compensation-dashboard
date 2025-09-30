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
                base_pct = st.number_input(
                    "Base % of OTE",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=1.0,
                    key="custom_base_split"
                ) / 100
                closer_ote = st.number_input(
                    "Closer OTE ($)",
                    min_value=0.0,
                    value=80000.0,
                    step=5000.0,
                    key="custom_closer_ote"
                )
                setter_ote = st.number_input(
                    "Setter OTE ($)",
                    min_value=0.0,
                    value=40000.0,
                    step=2500.0,
                    key="custom_setter_ote"
                )
                closer_comm = st.number_input(
                    "Closer Commission Pool %",
                    min_value=0.0,
                    max_value=100.0,
                    value=20.0,
                    step=0.5,
                    key="custom_closer_pool"
                ) / 100
                setter_comm = st.number_input(
                    "Setter Commission Pool %",
                    min_value=0.0,
                    max_value=100.0,
                    value=3.0,
                    step=0.5,
                    key="custom_setter_pool"
                ) / 100
            
            manager_ote = st.number_input(
                "Manager OTE ($)",
                min_value=0.0,
                value=120000.0,
                step=5000.0,
                key="manager_ote_config"
            )
            
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
                commission_rate = (total_commission/actual_monthly_revenue)*100 if actual_monthly_revenue > 0 else 0
                st.metric("Commission Rate", f"{commission_rate:.1f}%")
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
    
    with comp_tabs[2]:  # Earnings Preview Tab
        st.markdown("#### **📅 Period-Based Earnings Preview**")
        
        working_days = 20
        
        # Calculate earnings for different periods
        period_data = []
        
        for role_name, role_data in comp_structure.items():
            if role_data['count'] > 0:
                base_daily = role_data['base'] / 365
                base_weekly = role_data['base'] / 52
                base_monthly = role_data['base'] / 12
                
                if role_name == 'closer':
                    comm_monthly = role_data['actual_commission']
                elif role_name == 'setter':
                    comm_monthly = role_data['actual_commission']
                else:
                    comm_monthly = 0
                
                comm_daily = comm_monthly / working_days
                comm_weekly = comm_monthly / 4.33
                comm_annual = comm_monthly * 12
                
                period_data.append({
                    'Role': role_name.capitalize(),
                    'Daily Base': f"${base_daily:.0f}",
                    'Daily Comm': f"${comm_daily:.0f}",
                    'Daily Total': f"${base_daily + comm_daily:.0f}",
                    'Weekly Total': f"${base_weekly + comm_weekly:.0f}",
                    'Monthly Total': f"${base_monthly + comm_monthly:.0f}",
                    'Annual Total': f"${role_data['base'] + comm_annual:.0f}",
                    'vs OTE': f"{((role_data['base'] + comm_annual)/role_data['ote']-1)*100:+.0f}%" if role_data['ote'] > 0 else "N/A"
                })
        
        if period_data:
            st.dataframe(pd.DataFrame(period_data), use_container_width=True, hide_index=True)
        
        # Performance tracking
        st.markdown("##### **🎯 Performance Requirements to Hit OTE**")
        perf_cols = st.columns(2)
        
        with perf_cols[0]:
            st.markdown("**Closer Targets**")
            if num_closers > 0 and closer_comm > 0:
                closer_var = comp_structure['closer']['variable']
                required_rev = (closer_var / closer_comm) * num_closers
                current_rev = actual_monthly_revenue * 12
                gap = required_rev - current_rev
                
                st.metric("Annual Revenue Needed", f"${required_rev:,.0f}")
                st.metric("Current Projection", f"${current_rev:,.0f}")
                
                if gap > 0:
                    st.warning(f"📈 Need ${gap:,.0f} more revenue ({(gap/required_rev)*100:.0f}% gap)")
                else:
                    st.success(f"✅ Exceeding target by ${-gap:,.0f}!")
        
        with perf_cols[1]:
            st.markdown("**Setter Targets**")
            if num_setters > 0 and setter_comm > 0:
                setter_var = comp_structure['setter']['variable']
                required_rev = (setter_var / setter_comm) * num_setters
                current_rev = actual_monthly_revenue * 12
                gap = required_rev - current_rev
                
                st.metric("Annual Revenue Needed", f"${required_rev:,.0f}")
                st.metric("Current Projection", f"${current_rev:,.0f}")
                
                if gap > 0:
                    st.warning(f"📈 Need ${gap:,.0f} more revenue ({(gap/required_rev)*100:.0f}% gap)")
                else:
                    st.success(f"✅ Exceeding target by ${-gap:,.0f}!")
    
    with comp_tabs[3]:  # Decision Matrix Tab
        st.markdown("#### **🎯 Compensation Decision Matrix**")
        
        # Create scenarios
        scenarios = {
            'Current': {
                'base_pct': base_pct,
                'closer_comm': closer_comm,
                'setter_comm': setter_comm,
                'closer_ote': closer_ote,
                'setter_ote': setter_ote
            },
            'Performance': {
                'base_pct': 0.30,
                'closer_comm': 0.25,
                'setter_comm': 0.04,
                'closer_ote': 90000,
                'setter_ote': 45000
            },
            'Balanced': {
                'base_pct': 0.40,
                'closer_comm': 0.20,
                'setter_comm': 0.03,
                'closer_ote': 80000,
                'setter_ote': 40000
            },
            'Stability': {
                'base_pct': 0.60,
                'closer_comm': 0.15,
                'setter_comm': 0.02,
                'closer_ote': 75000,
                'setter_ote': 35000
            }
        }
        
        # Calculate metrics for each scenario
        scenario_metrics = []
        
        for scenario_name, scenario_config in scenarios.items():
            # Calculate costs
            scenario_base = (
                num_closers * scenario_config['closer_ote'] * scenario_config['base_pct'] +
                num_setters * scenario_config['setter_ote'] * scenario_config['base_pct'] +
                num_managers * manager_ote * 0.6 +
                num_bench * 25000 * 0.5
            )
            
            scenario_commission = actual_monthly_revenue * (
                scenario_config['closer_comm'] + scenario_config['setter_comm']
            ) * 12
            
            scenario_total = scenario_base + scenario_commission
            
            scenario_metrics.append({
                'Scenario': scenario_name,
                'Base/Variable': f"{scenario_config['base_pct']:.0%}/{1-scenario_config['base_pct']:.0%}",
                'Annual Base': f"${scenario_base:,.0f}",
                'Annual Commission': f"${scenario_commission:,.0f}",
                'Total Cost': f"${scenario_total:,.0f}",
                'Cost/Revenue': f"{(scenario_total/(actual_monthly_revenue*12))*100:.1f}%" if actual_monthly_revenue > 0 else "N/A",
                'Risk Level': '🟢 Low' if scenario_config['base_pct'] >= 0.5 else '🟡 Medium' if scenario_config['base_pct'] >= 0.35 else '🔴 High'
            })
        
        # Display comparison table
        st.dataframe(pd.DataFrame(scenario_metrics), use_container_width=True, hide_index=True)
        
        # Scenario comparison chart
        st.markdown("##### **📊 Scenario Cost Comparison**")
        
        fig_comparison = go.Figure()
        
        for scenario in scenario_metrics:
            base_val = float(scenario['Annual Base'].replace('$', '').replace(',', ''))
            comm_val = float(scenario['Annual Commission'].replace('$', '').replace(',', ''))
            
            fig_comparison.add_trace(go.Bar(
                name=scenario['Scenario'],
                x=['Base Salary', 'Commission'],
                y=[base_val, comm_val]
            ))
        
        fig_comparison.update_layout(
            title="Annual Compensation by Component",
            barmode='group',
            height=400,
            yaxis_title="Annual Cost ($)",
            showlegend=True
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Decision recommendations
        st.markdown("##### **💡 Recommendations**")
        
        rec_cols = st.columns(3)
        
        with rec_cols[0]:
            st.info(
                "**🎯 Choose Performance Model if:**\n"
                "• High-growth phase\n"
                "• Strong product-market fit\n"
                "• Experienced sales team\n"
                "• Cash flow positive"
            )
        
        with rec_cols[1]:
            st.success(
                "**⚖️ Choose Balanced Model if:**\n"
                "• Steady growth\n"
                "• Mixed team experience\n"
                "• Moderate risk tolerance\n"
                "• Standard market"
            )
        
        with rec_cols[2]:
            st.warning(
                "**🛡️ Choose Stability Model if:**\n"
                "• Early stage/uncertain\n"
                "• New sales team\n"
                "• Conservative cash flow\n"
                "• Long sales cycles"
            )
    
    with comp_tabs[4]:  # Impact Analysis Tab
        st.markdown("#### **📈 Financial Impact Analysis**")
        
        # Current EBITDA calculation
        current_revenue = actual_monthly_revenue * 12
        current_comp_cost = total_base + total_commission * 12
        current_opex = deal_economics.get('monthly_opex', 35000) * 12
        current_marketing = deal_economics.get('monthly_marketing', 100000) * 12
        current_gov_fees = current_revenue * deal_economics.get('gov_fee_pct', 0.10)
        
        current_ebitda = current_revenue - current_comp_cost - current_opex - current_marketing - current_gov_fees
        current_margin = (current_ebitda / current_revenue) * 100 if current_revenue > 0 else 0
        
        # Display current state
        st.markdown("##### **Current Financial State**")
        current_cols = st.columns(5)
        
        current_cols[0].metric("Annual Revenue", f"${current_revenue:,.0f}")
        current_cols[1].metric("Comp Cost", f"${current_comp_cost:,.0f}")
        current_cols[2].metric("EBITDA", f"${current_ebitda:,.0f}")
        current_cols[3].metric("EBITDA Margin", f"{current_margin:.1f}%")
        current_cols[4].metric("Comp/Revenue", f"{(current_comp_cost/current_revenue)*100:.1f}%" if current_revenue > 0 else "0%")
        
        # What-if analysis
        st.markdown("##### **🔮 What-If Scenarios**")
        
        whatif_cols = st.columns(2)
        
        with whatif_cols[0]:
            st.markdown("**Adjust Variables**")
            revenue_change = st.slider("Revenue Change %", -30, 50, 0, 5, key="comp_rev_change")
            comm_change = st.slider("Commission Rate Change (pts)", -5, 5, 0, 1, key="comp_comm_change")
            team_change = st.slider("Team Size Change %", -30, 30, 0, 5, key="comp_team_change")
        
        with whatif_cols[1]:
            st.markdown("**Impact Results**")
            
            # Calculate new values
            new_revenue = current_revenue * (1 + revenue_change/100)
            new_comm_rate = (closer_comm + setter_comm) + comm_change/100
            new_commission = new_revenue * new_comm_rate
            new_base = total_base * (1 + team_change/100)
            new_comp_cost = new_base + new_commission
            
            new_ebitda = new_revenue - new_comp_cost - current_opex - current_marketing - (new_revenue * deal_economics.get('gov_fee_pct', 0.10))
            new_margin = (new_ebitda / new_revenue) * 100 if new_revenue > 0 else 0
            
            ebitda_change = new_ebitda - current_ebitda
            margin_change = new_margin - current_margin
            
            st.metric("New EBITDA", f"${new_ebitda:,.0f}", f"${ebitda_change:,.0f}")
            st.metric("New Margin", f"{new_margin:.1f}%", f"{margin_change:+.1f}%")
            st.metric("New Comp Cost", f"${new_comp_cost:,.0f}", f"${new_comp_cost - current_comp_cost:,.0f}")
        
        # Sensitivity analysis
        st.markdown("##### **📊 Sensitivity Analysis**")
        
        # Create heatmap for EBITDA sensitivity
        revenue_range = range(-20, 30, 5)
        comm_range = range(-3, 4, 1)
        
        ebitda_matrix = []
        for rev_chg in revenue_range:
            row = []
            for comm_chg in comm_range:
                test_revenue = current_revenue * (1 + rev_chg/100)
                test_comm = test_revenue * ((closer_comm + setter_comm) + comm_chg/100)
                test_ebitda = test_revenue - total_base - test_comm - current_opex - current_marketing - (test_revenue * 0.10)
                row.append(test_ebitda)
            ebitda_matrix.append(row)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=ebitda_matrix,
            x=[f"{c:+d}%" for c in comm_range],
            y=[f"{r:+d}%" for r in revenue_range],
            colorscale='RdYlGn',
            text=[[f"${val:,.0f}" for val in row] for row in ebitda_matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="EBITDA ($)")
        ))
        
        fig_heatmap.update_layout(
            title="EBITDA Sensitivity: Revenue vs Commission Changes",
            xaxis_title="Commission Rate Change",
            yaxis_title="Revenue Change",
            height=500
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Key insights
        st.markdown("##### **🔍 Key Insights**")
        
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            break_even_commission = current_ebitda / current_revenue if current_revenue > 0 else 0
            st.metric(
                "Max Commission for Break-Even",
                f"{(break_even_commission + (closer_comm + setter_comm))*100:.1f}%",
                help="Maximum total commission rate before EBITDA turns negative"
            )
        
        with insight_cols[1]:
            revenue_per_employee = current_revenue / (num_closers + num_setters + num_managers + num_bench) if (num_closers + num_setters + num_managers + num_bench) > 0 else 0
            st.metric(
                "Revenue per Employee",
                f"${revenue_per_employee:,.0f}",
                help="Annual revenue generated per team member"
            )
        
        with insight_cols[2]:
            comp_efficiency = current_revenue / current_comp_cost if current_comp_cost > 0 else 0
            st.metric(
                "Comp Efficiency Ratio",
                f"{comp_efficiency:.2f}x",
                help="Revenue generated per dollar of compensation"
            )
    
    return comp_structure, closer_comm, setter_comm
