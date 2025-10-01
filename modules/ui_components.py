"""
Reusable UI components for the dashboard
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Any


def render_kpi_row(metrics: Dict[str, Dict[str, Any]], columns: int = 6):
    """
    Render a row of KPI metrics.
    
    Args:
        metrics: Dict of {label: {value, delta, help, format}}
        columns: Number of columns to display
    """
    cols = st.columns(columns)
    
    for idx, (label, data) in enumerate(metrics.items()):
        if idx >= columns:
            break
        
        with cols[idx]:
            value = data.get('value', 0)
            delta = data.get('delta')
            help_text = data.get('help')
            fmt = data.get('format', ',.0f')
            delta_color = data.get('delta_color', 'normal')
            
            # Format value
            if isinstance(fmt, str) and fmt.startswith('$'):
                display_value = f"${value:{fmt[1:]}}"
            elif isinstance(fmt, str) and fmt.endswith('%'):
                display_value = f"{value:.{fmt[:-1]}}%"
            else:
                display_value = f"{value:{fmt}}"
            
            st.metric(
                label=label,
                value=display_value,
                delta=delta,
                delta_color=delta_color,
                help=help_text
            )


def render_dependency_inspector(
    inputs: Dict[str, float],
    intermediates: Dict[str, float],
    outputs: Dict[str, float]
):
    """
    Render a dependency/traceability panel showing how inputs flow to outputs.
    
    Args:
        inputs: Input variables and their current values
        intermediates: Calculated intermediate values
        outputs: Final output metrics
    """
    with st.expander("🔍 Dependency Inspector - See How Numbers Flow", expanded=False):
        st.markdown("### 📊 Input → Intermediate → Output Flow")
        st.caption("See exactly how your inputs affect the business metrics")
        
        # Three columns for the flow
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎛️ INPUTS**")
            for key, value in inputs.items():
                if isinstance(value, float):
                    if value < 1:  # Probably a rate
                        st.caption(f"• {key}: {value:.1%}")
                    elif value > 100:
                        st.caption(f"• {key}: ${value:,.0f}")
                    else:
                        st.caption(f"• {key}: {value:.2f}")
                else:
                    st.caption(f"• {key}: {value}")
        
        with col2:
            st.markdown("**⚙️ CALCULATIONS**")
            for key, value in intermediates.items():
                if isinstance(value, (int, float)):
                    if key.lower().endswith('rate') or key.lower().endswith('pct'):
                        st.caption(f"• {key}: {value:.1%}")
                    elif 'spend' in key.lower() or 'revenue' in key.lower() or 'cost' in key.lower():
                        st.caption(f"• {key}: ${value:,.0f}")
                    else:
                        st.caption(f"• {key}: {value:.1f}")
                else:
                    st.caption(f"• {key}: {value}")
        
        with col3:
            st.markdown("**📈 OUTPUTS**")
            for key, value in outputs.items():
                if isinstance(value, (int, float)):
                    if 'margin' in key.lower() or 'rate' in key.lower():
                        st.caption(f"• {key}: {value:.1f}%")
                    elif 'ratio' in key.lower():
                        st.caption(f"• {key}: {value:.2f}:1")
                    else:
                        st.caption(f"• {key}: ${value:,.0f}")
                else:
                    st.caption(f"• {key}: {value}")
        
        # Show formulas
        st.markdown("---")
        st.markdown("**📐 Key Formulas**")
        
        formulas = [
            "**Pipeline**: `Leads → Contacts (× contact_rate) → Meetings Sched (× meeting_rate) → Meetings Held (× show_up_rate) → Sales (× close_rate)`",
            "**Spend**: Depends on cost method - e.g., CPM: `meetings_held × cost_per_meeting`",
            "**Revenue**: `Sales × upfront_cash_per_deal`",
            "**CAC**: `Total marketing spend / sales`",
            "**LTV**: `upfront_cash + (deferred_cash × GRR)`",
            "**EBITDA**: `(Net Revenue - COGS) - (Marketing + OpEx)`",
        ]
        
        for formula in formulas:
            st.markdown(f"- {formula}")


def render_sensitivity_chart(
    sensitivities: Dict[str, Dict[str, float]],
    metric_name: str,
    top_n: int = 8
):
    """
    Render a sensitivity analysis chart.
    
    Args:
        sensitivities: Output from scenario.calculate_sensitivity
        metric_name: Name of the metric being analyzed
        top_n: Show top N drivers
    """
    # Sort by absolute sensitivity
    sorted_items = sorted(
        sensitivities.items(),
        key=lambda x: x[1].get('abs_sensitivity', 0),
        reverse=True
    )[:top_n]
    
    # Create bar chart
    labels = [item[0].replace('_', ' ').title() for item, _ in sorted_items]
    values = [data['sensitivity'] * 100 for _, data in sorted_items]  # Convert to %
    colors = ['#ef4444' if v < 0 else '#10b981' for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:+.1f}%" for v in values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Sensitivity: %{x:+.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Top Drivers of {metric_name} (% change per 1% input change)",
        xaxis_title="Sensitivity (%)",
        yaxis_title="Input Variable",
        height=400,
        showlegend=False,
        margin=dict(l=150, r=50, t=60, b=50)
    )
    
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show interpretation
    if sorted_items:
        top_driver = sorted_items[0]
        top_name = top_driver[0].replace('_', ' ').title()
        top_sens = top_driver[1]['sensitivity'] * 100
        
        if abs(top_sens) > 0.5:
            direction = "increases" if top_sens > 0 else "decreases"
            st.info(f"💡 **Key Insight**: {metric_name} is most sensitive to **{top_name}**. "
                   f"A 1% increase in {top_name} {direction} {metric_name} by {abs(top_sens):.1f}%.")


def render_scenario_comparison(
    baseline: Dict[str, float],
    scenario: Dict[str, float],
    scenario_name: str = "Scenario"
):
    """
    Render a side-by-side comparison of baseline vs scenario.
    
    Args:
        baseline: Baseline metrics
        scenario: Scenario metrics
        scenario_name: Name of the scenario
    """
    st.markdown(f"### 📊 Baseline vs {scenario_name}")
    
    # Calculate deltas
    metrics_data = []
    for key in baseline.keys():
        base_val = baseline[key]
        scen_val = scenario.get(key, 0)
        delta = scen_val - base_val
        delta_pct = (delta / base_val * 100) if base_val != 0 else 0
        
        metrics_data.append({
            'Metric': key.replace('_', ' ').title(),
            'Baseline': base_val,
            'Scenario': scen_val,
            'Delta': delta,
            'Delta %': delta_pct
        })
    
    # Create comparison table
    import pandas as pd
    df = pd.DataFrame(metrics_data)
    
    # Format display
    st.dataframe(
        df.style.format({
            'Baseline': '${:,.0f}',
            'Scenario': '${:,.0f}',
            'Delta': '${:+,.0f}',
            'Delta %': '{:+.1f}%'
        }).applymap(
            lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else 'color: red',
            subset=['Delta', 'Delta %']
        ),
        use_container_width=True
    )


def render_channel_card(
    channel_name: str,
    metrics: Dict[str, Any],
    enabled: bool = True
):
    """
    Render a compact channel performance card.
    
    Args:
        channel_name: Channel name
        metrics: Channel metrics (leads, sales, spend, roas, etc.)
        enabled: Whether channel is enabled
    """
    with st.container():
        # Header
        status = "✅" if enabled else "⚪"
        st.markdown(f"### {status} {channel_name}")
        
        if not enabled:
            st.caption("_Channel disabled_")
            return
        
        # Key metrics in columns
        cols = st.columns(4)
        
        with cols[0]:
            st.metric("📊 Leads", f"{metrics.get('leads', 0):,.0f}")
        with cols[1]:
            st.metric("✅ Sales", f"{metrics.get('sales', 0):.1f}")
        with cols[2]:
            st.metric("💰 Spend", f"${metrics.get('spend', 0):,.0f}")
        with cols[3]:
            roas = metrics.get('roas', 0)
            roas_color = "normal" if roas >= 3 else "inverse"
            st.metric("📊 ROAS", f"{roas:.1f}x", delta_color=roas_color)


def render_funnel_chart(
    leads: float,
    contacts: float,
    meetings_sched: float,
    meetings_held: float,
    sales: float,
    title: str = "Sales Funnel"
):
    """Render a funnel chart for the sales pipeline"""
    fig = go.Figure(go.Funnel(
        y=['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales'],
        x=[leads, contacts, meetings_sched, meetings_held, sales],
        textinfo="value+percent initial",
        marker=dict(color='#3b82f6', line=dict(width=2, color='#1e40af'))
    ))
    
    fig.update_layout(
        title=title,
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_health_score(
    ltv_cac: float,
    payback_months: float,
    ebitda_margin: float,
    gross_margin: float
):
    """
    Render an overall business health score.
    
    Health Score = weighted average of key metrics vs benchmarks
    """
    # Score each dimension (0-100)
    scores = {}
    
    # LTV:CAC (benchmark: >3 is good, >5 is excellent)
    if ltv_cac >= 5:
        scores['ltv_cac'] = 100
    elif ltv_cac >= 3:
        scores['ltv_cac'] = 70
    elif ltv_cac >= 1.5:
        scores['ltv_cac'] = 40
    else:
        scores['ltv_cac'] = 0
    
    # Payback (benchmark: <6mo excellent, <12mo good)
    if payback_months <= 6:
        scores['payback'] = 100
    elif payback_months <= 12:
        scores['payback'] = 70
    elif payback_months <= 18:
        scores['payback'] = 40
    else:
        scores['payback'] = 0
    
    # EBITDA Margin (benchmark: >30% excellent, >15% good)
    if ebitda_margin >= 30:
        scores['ebitda'] = 100
    elif ebitda_margin >= 15:
        scores['ebitda'] = 70
    elif ebitda_margin >= 0:
        scores['ebitda'] = 40
    else:
        scores['ebitda'] = 0
    
    # Gross Margin (benchmark: >70% excellent, >60% good)
    if gross_margin >= 70:
        scores['gross'] = 100
    elif gross_margin >= 60:
        scores['gross'] = 70
    elif gross_margin >= 50:
        scores['gross'] = 40
    else:
        scores['gross'] = 0
    
    # Overall health (weighted average)
    overall = (
        scores['ltv_cac'] * 0.35 +
        scores['payback'] * 0.25 +
        scores['ebitda'] * 0.25 +
        scores['gross'] * 0.15
    )
    
    # Color based on score
    if overall >= 80:
        color = "green"
        emoji = "🟢"
        status = "Excellent"
    elif overall >= 60:
        color = "blue"
        emoji = "🔵"
        status = "Good"
    elif overall >= 40:
        color = "orange"
        emoji = "🟠"
        status = "Fair"
    else:
        color = "red"
        emoji = "🔴"
        status = "Poor"
    
    # Display
    st.markdown(f"### {emoji} Business Health Score: {overall:.0f}/100 - {status}")
    
    # Show breakdown
    with st.expander("📊 Score Breakdown"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Unit Economics (LTV:CAC)", f"{scores['ltv_cac']:.0f}/100")
            st.metric("EBITDA Margin", f"{scores['ebitda']:.0f}/100")
        
        with col2:
            st.metric("Payback Period", f"{scores['payback']:.0f}/100")
            st.metric("Gross Margin", f"{scores['gross']:.0f}/100")
