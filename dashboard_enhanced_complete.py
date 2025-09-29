"""
Enhanced Sales Compensation Dashboard - Complete Version
Preserves ALL features from fixed_compensation_dashboard.py + adds requested enhancements
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Import modules
from modules.calculations_enhanced import (
    EnhancedRevenueCalculator, TeamMetricsCalculator,
    BottleneckAnalyzer, HealthScoreCalculator
)
from reverse_engineering_module import add_reverse_engineering_tab

# ============= CONFIGURACIÓN =============
st.set_page_config(
    page_title="🎯 Simulador Completo Optimaxx - Enhanced",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS (preserving original + enhancements)
st.markdown("""
    <style>
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .warning-box {
        background-color: #ffcc00;
        color: black;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .sensitivity-ribbon {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
        font-size: 14px;
    }
    .health-score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💰 Simulador Completo de Compensación - Modelo Optimaxx PLUS Enhanced")
st.markdown("**Control granular con validaciones, modelo Bowtie correcto y análisis de sensibilidad**")

# ============= FUNCIONES DE VALIDACIÓN (preserving original) =============
def validate_team_capacity(daily_leads, num_closers, num_setters, contact_rate, meeting_rate, close_rate):
    """Valida que el equipo tenga la capacidad correcta"""
    warnings = []
    suggestions = []
    
    # Calcular volúmenes esperados
    daily_contacts = daily_leads * contact_rate
    daily_meetings = daily_contacts * meeting_rate
    daily_sales = daily_meetings * close_rate
    
    # Validar capacidad de setters (30 contactos/día por setter)
    setter_capacity = num_setters * 30
    if daily_contacts > setter_capacity:
        warnings.append(f"⚠️ Setters sobrecargados: {daily_contacts:.0f} contactos vs {setter_capacity:.0f} capacidad")
        setters_needed = int(np.ceil(daily_contacts / 30))
        suggestions.append(f"💡 Necesitas {setters_needed - num_setters} setters adicionales")
    
    # Validar capacidad de closers (3 meetings/día por closer)
    closer_capacity = num_closers * 3
    if daily_meetings > closer_capacity:
        warnings.append(f"⚠️ Closers sobrecargados: {daily_meetings:.0f} meetings vs {closer_capacity:.0f} capacidad")
        closers_needed = int(np.ceil(daily_meetings / 3))
        suggestions.append(f"💡 Necesitas {closers_needed - num_closers} closers adicionales")
    
    return warnings, suggestions

# ============= SIDEBAR MEJORADO =============
st.sidebar.title("⚙️ Configuración del Modelo")
st.sidebar.markdown("---")

# SECCIÓN 1: REVENUE TARGETS (ENHANCED)
st.sidebar.header("🎯 1. Revenue Targets")

# Period selector
target_period = st.sidebar.radio(
    "Define tu target por:",
    ["Anual", "Trimestral", "Mensual", "Semanal", "Diario"],
    index=0,
    horizontal=True
)

# Input based on selection
if target_period == "Anual":
    annual_target = st.sidebar.number_input(
        "Revenue Target Anual ($)", 
        min_value=1000000, max_value=1000000000, 
        value=50000000, step=1000000
    )
elif target_period == "Trimestral":
    quarterly_input = st.sidebar.number_input(
        "Revenue Target Trimestral ($)",
        min_value=250000, max_value=250000000,
        value=12500000, step=250000
    )
    annual_target = quarterly_input * 4
elif target_period == "Mensual":
    monthly_input = st.sidebar.number_input(
        "Revenue Target Mensual ($)",
        min_value=100000, max_value=100000000,
        value=4166667, step=100000
    )
    annual_target = monthly_input * 12
elif target_period == "Semanal":
    weekly_input = st.sidebar.number_input(
        "Revenue Target Semanal ($)",
        min_value=25000, max_value=25000000,
        value=961538, step=25000
    )
    annual_target = weekly_input * 52
else:  # Diario
    daily_input = st.sidebar.number_input(
        "Revenue Target Diario ($)",
        min_value=5000, max_value=5000000,
        value=192308, step=5000
    )
    annual_target = daily_input * 260

# Calculate all breakdowns
revenue_targets = {
    'annual': annual_target,
    'quarterly': annual_target / 4,
    'monthly': annual_target / 12,
    'weekly': annual_target / 52,
    'daily': annual_target / 260
}

# Show breakdown
st.sidebar.info(f"""
**📊 Breakdown Completo:**
• Anual: ${revenue_targets['annual']:,.0f}
• Trimestral: ${revenue_targets['quarterly']:,.0f}
• Mensual: ${revenue_targets['monthly']:,.0f}
• Semanal: ${revenue_targets['weekly']:,.0f}
• Diario: ${revenue_targets['daily']:,.0f}
""")

# SECCIÓN 2: SALES CYCLE (NEW)
st.sidebar.header("⏱️ 2. Sales Cycle")

sales_cycle_days = st.sidebar.slider(
    "Ciclo de Ventas Promedio (días)",
    min_value=7, max_value=180, value=20, step=1,
    help="Impacta pipeline coverage, cash flow y capacity planning"
)

# Dynamic pipeline coverage based on cycle
if sales_cycle_days <= 30:
    suggested_coverage = 3.0
elif sales_cycle_days <= 60:
    suggested_coverage = 4.0
elif sales_cycle_days <= 90:
    suggested_coverage = 5.0
else:
    suggested_coverage = 6.0

pipeline_coverage = st.sidebar.slider(
    f"Pipeline Coverage Ratio (sugerido: {suggested_coverage}x)",
    min_value=2.0, max_value=8.0, value=suggested_coverage, step=0.5
)

# SECCIÓN 3: ESTRUCTURA DEL EMBUDO (preserving original)
st.sidebar.header("📊 3. Estructura del Embudo")

# Leads
daily_leads = st.sidebar.slider(
    "🎯 Leads Diarios", 
    min_value=10, max_value=500, value=155, step=5,
    help="Número de leads nuevos por día"
)

# Conversion rates
st.sidebar.markdown("##### Tasas de Conversión")
col1, col2 = st.sidebar.columns(2)
with col1:
    contact_rate = st.sidebar.slider("Contact Rate", 0.40, 0.80, 0.60, 0.05)
    meeting_rate = st.sidebar.slider("Meeting Rate", 0.20, 0.50, 0.35, 0.05)
with col2:
    close_rate = st.sidebar.slider("Close Rate", 0.15, 0.35, 0.25, 0.05)
    onboard_rate = st.sidebar.slider("Onboard Rate", 0.85, 1.00, 0.95, 0.01)

# Post-sale metrics
st.sidebar.markdown("##### Métricas Post-Venta")
grr_rate = st.sidebar.slider(
    "GRR @ 18 meses", 0.70, 0.95, 0.90, 0.05,
    help="Gross Revenue Retention - Persistencia"
)
nrr_rate = st.sidebar.slider(
    "NRR @ 18 meses", 0.90, 1.30, 1.10, 0.05,
    help="Net Revenue Retention - Expansión"
)

# SECCIÓN 4: DEAL ECONOMICS
st.sidebar.header("💰 4. Deal Economics")

avg_pm = st.sidebar.number_input(
    "Prima Mensual Promedio (MXN)",
    min_value=1000, max_value=10000, value=3000, step=100
)

# Automatic Optimaxx calculations
carrier_rate = 0.027  # 2.7%
contract_months = 300  # 25 years
comp_total = avg_pm * contract_months * carrier_rate
comp_immediate = comp_total * 0.7  # 70%
comp_deferred = comp_total * 0.3   # 30%

st.sidebar.success(f"""
**💎 Compensación por Venta:**
• Total: ${comp_total:,.0f}
• Inmediato (70%): ${comp_immediate:,.0f}
• Diferido mes 18 (30%): ${comp_deferred:,.0f}
• Con persistencia: ${comp_immediate + comp_deferred * grr_rate:,.0f}
""")

# SECCIÓN 5: EQUIPO Y CAPACIDAD
st.sidebar.header("👥 5. Equipo y Capacidad")

col1, col2 = st.sidebar.columns(2)
with col1:
    num_closers = st.sidebar.number_input("Closers", 0, 50, 8, 1)
    num_setters = st.sidebar.number_input("Setters", 0, 50, 4, 1)
with col2:
    num_bench = st.sidebar.number_input("En Banca", 0, 20, 2, 1)
    num_managers = st.sidebar.number_input("Managers", 0, 10, 2, 1)

# SECCIÓN 6: OTE POR POSICIÓN (NEW)
st.sidebar.header("💸 6. OTE por Posición")

st.sidebar.markdown("##### OTE Anual por Rol")
closer_ote = st.sidebar.number_input(
    "OTE Closer ($)", 30000, 200000, 80000, 5000
)
setter_ote = st.sidebar.number_input(
    "OTE Setter ($)", 20000, 100000, 40000, 2500
)
manager_ote = st.sidebar.number_input(
    "OTE Manager ($)", 50000, 300000, 120000, 10000
)
bench_ote = st.sidebar.number_input(
    "OTE Bench ($)", 15000, 50000, 25000, 2500
)

# Base vs Variable
base_salary_pct = st.sidebar.slider(
    "% Base (vs Variable)", 0.2, 0.6, 0.4, 0.05,
    help="Healthy range: 30-50% base"
)

# Calculate team OTE
team_ote_structure = TeamMetricsCalculator.calculate_ote_by_role(
    num_closers, num_setters, num_managers,
    closer_ote, setter_ote, manager_ote,
    base_salary_pct
)

# SECCIÓN 7: COMISIONES
st.sidebar.header("📊 7. Estructura de Comisiones")

closer_comm_pct = st.sidebar.slider(
    "% Pool para Closers", 0.10, 0.30, 0.20, 0.01,
    help="Del revenue inmediato"
)
setter_of_closer_pct = st.sidebar.slider(
    "% Setter del Closer", 0.10, 0.25, 0.15, 0.01,
    help="Del pago del closer"
)

# Bonuses
st.sidebar.markdown("##### Bonos Setters")
speed_bonus_pct = st.sidebar.slider(
    "Bonus Velocidad", 0.0, 0.20, 0.10, 0.01,
    help="Por respuesta <5min"
) 
followup_bonus_pct = st.sidebar.slider(
    "Bonus Seguimiento", 0.0, 0.10, 0.05, 0.01,
    help="Por 2+ seguimientos"
)

# SECCIÓN 8: COSTOS Y FEES
st.sidebar.header("💵 8. Costos y Fees")

cpl = st.sidebar.number_input("Cost per Lead ($)", 0, 500, 150, 10)

st.sidebar.markdown("##### Costos Fijos")
office_rent = st.sidebar.number_input("Renta Oficina", 0, 100000, 20000, 5000)
software_costs = st.sidebar.number_input("Software/Tools", 0, 50000, 10000, 1000)
other_opex = st.sidebar.number_input("Otros Gastos", 0, 50000, 5000, 1000)

# Government fees
gov_fee_pct = st.sidebar.slider(
    "🏛️ Fee Gubernamental (%)", 0.0, 20.0, 10.0, 0.5,
    help="ISR, IVA, etc sobre revenue"
) / 100

# SECCIÓN 9: PROYECCIÓN Y RAMP
st.sidebar.header("📈 9. Proyección y Ramp")

projection_months = st.sidebar.selectbox(
    "Horizonte de Proyección",
    [6, 12, 18, 24, 36],
    index=2
)

ramp_months = st.sidebar.slider(
    "Tiempo de Ramp (meses)", 1, 6, 3, 1,
    help="Meses para productividad completa"
)

attrition_rate = st.sidebar.slider(
    "Tasa de Attrition Anual (%)", 0, 50, 15, 5
) / 100

# ============= CÁLCULOS PRINCIPALES =============

# Monthly volumes
monthly_leads = daily_leads * 30
monthly_contacts = monthly_leads * contact_rate
monthly_meetings = monthly_contacts * meeting_rate
monthly_sales = monthly_meetings * close_rate
monthly_onboarded = monthly_sales * onboard_rate
monthly_grr = monthly_onboarded * grr_rate
monthly_nrr_value = monthly_grr * (nrr_rate / max(0.01, grr_rate))

# Revenue calculations (using enhanced module)
revenue_timeline = EnhancedRevenueCalculator.calculate_monthly_timeline(
    monthly_sales, avg_pm, projection_months,
    carrier_rate, 0.7, 0.3, grr_rate, 0.0
)

# Current month metrics
current_month = revenue_timeline.iloc[0] if len(revenue_timeline) > 0 else None
monthly_revenue_immediate = current_month['immediate_revenue']
monthly_revenue_deferred = current_month['deferred_revenue'] 
monthly_revenue_total = current_month['total_revenue']
cash_collected_today = current_month['cash_collected_today']
cash_pending_month_18 = current_month['cash_pending_month_18']

# Calculate costs
monthly_lead_cost = monthly_leads * cpl
closer_commission_total = monthly_revenue_immediate * closer_comm_pct
setter_commission_total = closer_commission_total * setter_of_closer_pct * (1 + speed_bonus_pct + followup_bonus_pct)

# Base salaries (monthly)
total_base_salaries = (
    num_closers * (closer_ote * base_salary_pct / 12) +
    num_setters * (setter_ote * base_salary_pct / 12) +
    num_bench * (bench_ote * 0.5 / 12) +  # Bench at 50% base
    num_managers * (manager_ote * 0.6 / 12)  # Managers at 60% base
)

# Total costs
total_marketing = monthly_lead_cost
total_compensation = closer_commission_total + setter_commission_total + total_base_salaries
total_fixed = office_rent + software_costs + other_opex
total_costs_before_fees = total_marketing + total_compensation + total_fixed
government_fees = monthly_revenue_total * gov_fee_pct
total_costs = total_costs_before_fees + government_fees

# EBITDA
monthly_ebitda = monthly_revenue_total - total_costs
ebitda_margin = monthly_ebitda / monthly_revenue_total if monthly_revenue_total > 0 else 0

# Unit economics
ltv = comp_immediate + (comp_deferred * grr_rate)
cac = (monthly_lead_cost + (total_compensation / 2)) / monthly_sales if monthly_sales > 0 else 0
ltv_cac_ratio = ltv / cac if cac > 0 else 0

# Validate capacity
warnings, suggestions = validate_team_capacity(
    daily_leads, num_closers, num_setters,
    contact_rate, meeting_rate, close_rate
)

# Health score calculation
health_scores = HealthScoreCalculator.calculate_health_metrics(
    {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
    {'utilization': monthly_meetings / (num_closers * 60) if num_closers > 0 else 0, 
     'attrition_rate': attrition_rate},
    {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin, 'growth_rate': 0.1}
)

# ============= SENSITIVITY RIBBON (NEW) =============
st.markdown('<div class="sensitivity-ribbon">', unsafe_allow_html=True)
st.markdown("### 🎯 What changes when I move X? - Impact Analysis")

sens_cols = st.columns(5)

with sens_cols[0]:
    st.markdown("**📈 Close Rate +10%**")
    new_sales = monthly_meetings * (close_rate * 1.1)
    new_revenue = new_sales * comp_immediate
    impact = new_revenue - monthly_revenue_immediate
    st.metric("Revenue Impact", f"${impact:,.0f}", f"+{(impact/monthly_revenue_immediate)*100:.1f}%")

with sens_cols[1]:
    st.markdown("**⏱️ Cycle -20%**")
    new_coverage = pipeline_coverage * 0.8
    cash_acceleration = sales_cycle_days * 0.2
    st.metric("Cash Acceleration", f"{cash_acceleration:.0f} days", f"-{20:.0f}%")

with sens_cols[2]:
    st.markdown("**💰 Deal +$500**")
    new_pm = avg_pm + 500
    new_comp = new_pm * 300 * carrier_rate * 0.7
    deal_impact = (new_comp - comp_immediate) * monthly_sales
    st.metric("Revenue Impact", f"${deal_impact:,.0f}", f"+{(deal_impact/monthly_revenue_immediate)*100:.1f}%")

with sens_cols[3]:
    st.markdown("**📉 CPL -30%**")
    new_cpl = cpl * 0.7
    cost_savings = (cpl - new_cpl) * monthly_leads
    st.metric("Cost Savings", f"${cost_savings:,.0f}", f"-30%")

with sens_cols[4]:
    st.markdown("**👥 +2 Closers**")
    new_capacity = (num_closers + 2) * 60  # meetings/month
    capacity_increase = new_capacity - (num_closers * 60)
    st.metric("Capacity +", f"{capacity_increase:.0f} mtgs", f"+{(2/num_closers)*100:.0f}%")

st.markdown('</div>', unsafe_allow_html=True)

# Show warnings if any
if warnings:
    st.warning("⚠️ **Alertas de Capacidad:**")
    for warning in warnings:
        st.write(warning)
    for suggestion in suggestions:
        st.info(suggestion)

# ============= MAIN TABS =============
tabs = st.tabs([
    "🎯 Bowtie",
    "📅 Timeline", 
    "💰 Costos Unit",
    "💵 Compensación",
    "📊 P&L",
    "🚀 Simulador",
    "👥 Team & Ramp",
    "📈 Health Metrics",
    "🔄 Ing. Inversa"
])

# TAB 1: BOWTIE MODEL (preserving original)
with tabs[0]:
    st.header("🎯 Modelo Bowtie - Winning by Design")
    
    # Payment structure info (from fixed)
    st.info(f"""
    💰 **ESTRUCTURA DE PAGOS OPTIMAXX ({projection_months} meses proyección):**
    - **70% INMEDIATO** = ${cash_collected_today:,.0f} cobrado HOY
    - **30% DIFERIDO** = ${cash_pending_month_18:,.0f} por cobrar en MES 18 (con {grr_rate:.0%} persistencia)
    - **Fee Gubernamental** = {gov_fee_pct:.1%} sobre revenue (${government_fees:,.0f}/mes)
    """)
    
    # Metrics row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Leads/Mes", f"{monthly_leads:,.0f}")
    with col2:
        st.metric("Contactados", f"{monthly_contacts:,.0f}")
    with col3:
        st.metric("Reuniones", f"{monthly_meetings:,.0f}")
    with col4:
        st.metric("Ventas", f"{monthly_sales:,.0f}")
    with col5:
        st.metric("Onboarded", f"{monthly_onboarded:,.0f}")
    with col6:
        st.metric("GRR→NRR", f"{monthly_grr:.0f}→{monthly_nrr_value:.0f}")
    
    # Funnel visualization
    fig = go.Figure(go.Funnel(
        y=['Leads', 'Contacted', 'Meetings', 'Sales', 'Onboarded', 'GRR (18m)'],
        x=[monthly_leads, monthly_contacts, monthly_meetings, monthly_sales, monthly_onboarded, monthly_grr],
        textposition="inside",
        textinfo="value+percent previous",
        marker={"color": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]},
        connector={"line": {"color": "royalblue", "dash": "dot", "width": 2}}
    ))
    
    fig.update_layout(
        title="Sales Funnel - Vista Mensual",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily Activities Required
    st.subheader("📊 Daily Activities Required")
    
    act_col1, act_col2, act_col3 = st.columns(3)
    
    with act_col1:
        st.markdown("**Por Setter (diario):**")
        if num_setters > 0:
            st.metric("Leads a contactar", f"{daily_leads/num_setters:.1f}")
            st.metric("Contactos efectivos", f"{(daily_leads * contact_rate)/num_setters:.1f}")
            st.metric("Meetings agendados", f"{(daily_leads * contact_rate * meeting_rate)/num_setters:.1f}")
    
    with act_col2:
        st.markdown("**Por Closer (diario):**")
        if num_closers > 0:
            st.metric("Meetings a atender", f"{(monthly_meetings/20)/num_closers:.1f}")
            st.metric("Ventas esperadas", f"{(monthly_sales/20)/num_closers:.2f}")
            st.metric("Revenue generado", f"${((monthly_sales/20) * comp_immediate)/num_closers:,.0f}")
    
    with act_col3:
        st.markdown("**Totales Equipo (diario):**")
        st.metric("Total Leads", f"{daily_leads:.0f}")
        st.metric("Total Meetings", f"{monthly_meetings/20:.1f}")
        st.metric("Total Sales", f"{monthly_sales/20:.1f}")

# TAB 2: TIMELINE
with tabs[1]:
    st.header("📅 Revenue Timeline - Proyección Detallada")
    
    # Key dates and amounts
    date_col1, date_col2, date_col3 = st.columns(3)
    
    with date_col1:
        st.success(f"""
        **📆 Fechas Clave:**
        • Hoy: {datetime.now().strftime('%B %Y')}
        • Primer diferido: {(datetime.now() + timedelta(days=18*30)).strftime('%B %Y')}
        • Fin proyección: {(datetime.now() + timedelta(days=projection_months*30)).strftime('%B %Y')}
        """)
    
    with date_col2:
        month_18_data = revenue_timeline[revenue_timeline['month'] == 18]
        if not month_18_data.empty:
            m18 = month_18_data.iloc[0]
            st.info(f"""
            **💰 Mes 18 - Inicio Diferidos:**
            • Revenue Total: ${m18['total_revenue']:,.0f}
            • Inmediato: ${m18['immediate_revenue']:,.0f}
            • Diferido: ${m18['deferred_revenue']:,.0f}
            """)
    
    with date_col3:
        final = revenue_timeline.iloc[-1]
        st.warning(f"""
        **📊 Mes {projection_months} - Final:**
        • Revenue Acumulado: ${final['cumulative_total']:,.0f}
        • Promedio Mensual: ${final['cumulative_total']/projection_months:,.0f}
        • Run Rate Anual: ${final['total_revenue']*12:,.0f}
        """)
    
    # Timeline chart
    fig_timeline = go.Figure()
    
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['immediate_revenue'],
        name='Inmediato (70%)',
        marker_color='#2E7D32'
    ))
    
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['deferred_revenue'],
        name='Diferido (30%)',
        marker_color='#1565C0'
    ))
    
    fig_timeline.add_trace(go.Scatter(
        x=revenue_timeline['month'],
        y=revenue_timeline['cumulative_total'],
        name='Acumulado Total',
        mode='lines+markers',
        line=dict(color='#FF6B00', width=3),
        yaxis='y2'
    ))
    
    # Add month 18 line
    fig_timeline.add_vline(x=18, line_dash="dash", line_color="red",
                          annotation_text="Inicio Pagos Diferidos")
    
    # Add quarterly markers
    for q in range(1, (projection_months // 3) + 1):
        fig_timeline.add_vline(x=q*3, line_dash="dot", line_color="gray", opacity=0.3)
    
    fig_timeline.update_layout(
        title="Revenue Timeline - 70% Inmediato vs 30% Diferido",
        xaxis_title="Mes",
        yaxis_title="Revenue Mensual ($)",
        yaxis2=dict(title="Revenue Acumulado ($)", overlaying='y', side='right'),
        barmode='stack',
        height=450
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# TAB 3: UNIT ECONOMICS
with tabs[2]:
    st.header("💰 Costos Unitarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Métricas de Costo")
        
        cpm = monthly_lead_cost / monthly_meetings if monthly_meetings > 0 else 0
        cpa = cpm
        
        metrics_df = pd.DataFrame({
            'Métrica': ['CPL', 'CPM', 'CPA', 'CAC', 'LTV', 'LTV:CAC'],
            'Valor': [
                f"${cpl:,.0f}",
                f"${cpm:,.0f}",
                f"${cpa:,.0f}",
                f"${cac:,.0f}",
                f"${ltv:,.0f}",
                f"{ltv_cac_ratio:.2f}:1"
            ],
            'Benchmark': ['$100-200', '$500-1000', '$500-1000', '$2000-5000', '$15000+', '3:1+'],
            'Status': [
                '✅' if 100 <= cpl <= 200 else '⚠️',
                '✅' if 500 <= cpm <= 1000 else '⚠️',
                '✅' if 500 <= cpa <= 1000 else '⚠️',
                '✅' if cac <= 5000 else '⚠️',
                '✅' if ltv >= 15000 else '⚠️',
                '✅' if ltv_cac_ratio >= 3 else '❌'
            ]
        })
        
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("💵 Efficiency Metrics")
        
        st.metric("EBITDA Margin", f"{ebitda_margin:.1%}", 
                 "Healthy" if ebitda_margin >= 0.25 else "Needs Improvement")
        st.metric("Payback Period", f"{cac/comp_immediate if comp_immediate > 0 else 0:.1f} deals")
        st.metric("Revenue per Lead", f"${(monthly_revenue_immediate/monthly_leads):.0f}")
        st.metric("Cost per Sale", f"${total_costs/monthly_sales if monthly_sales > 0 else 0:.0f}")

# TAB 4: COMPENSATION
with tabs[3]:
    st.header("💵 Estructura de Compensación")
    
    # OTE Structure
    st.subheader("💼 OTE Structure por Rol")
    
    ote_df = pd.DataFrame([
        {'Rol': 'Closer', 'Count': num_closers, 'OTE': closer_ote, 
         'Base': closer_ote * base_salary_pct, 'Variable': closer_ote * (1-base_salary_pct),
         'Total Cost': num_closers * closer_ote},
        {'Rol': 'Setter', 'Count': num_setters, 'OTE': setter_ote,
         'Base': setter_ote * base_salary_pct, 'Variable': setter_ote * (1-base_salary_pct),
         'Total Cost': num_setters * setter_ote},
        {'Rol': 'Manager', 'Count': num_managers, 'OTE': manager_ote,
         'Base': manager_ote * 0.6, 'Variable': manager_ote * 0.4,
         'Total Cost': num_managers * manager_ote},
        {'Rol': 'Bench', 'Count': num_bench, 'OTE': bench_ote,
         'Base': bench_ote * 0.5, 'Variable': bench_ote * 0.5,
         'Total Cost': num_bench * bench_ote}
    ])
    
    # Format columns
    for col in ['OTE', 'Base', 'Variable', 'Total Cost']:
        ote_df[col] = ote_df[col].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(ote_df, use_container_width=True, hide_index=True)
    
    # Attainment Tiers
    st.subheader("🏆 Attainment Tiers")
    
    tiers_df = pd.DataFrame([
        {'Tier': 'Below Threshold', 'Range': '0-40%', 'Multiplier': '0.6x', 'Example': '$0'},
        {'Tier': 'Developing', 'Range': '40-70%', 'Multiplier': '0.8x', 'Example': '$2,400'},
        {'Tier': 'At Target', 'Range': '70-100%', 'Multiplier': '1.0x', 'Example': '$4,000'},
        {'Tier': 'Exceeding', 'Range': '100-150%', 'Multiplier': '1.2x', 'Example': '$6,000'},
        {'Tier': 'Overachieving', 'Range': '150%+', 'Multiplier': '1.6x', 'Example': '$10,000'}
    ])
    
    st.dataframe(tiers_df, use_container_width=True, hide_index=True)

# TAB 5: P&L
with tabs[4]:
    st.header("📊 P&L Mensual Completo")
    
    # P&L Table
    pl_data = {
        'Concepto': [
            '📈 INGRESOS',
            'Ventas del Mes',
            'Ingresos Inmediatos (70%)',
            'Ingresos Diferidos (30%)*',
            'TOTAL INGRESOS',
            '',
            '💰 COSTOS OPERATIVOS',
            'Marketing (Leads)',
            'Comisiones Closers',
            'Comisiones Setters',
            'Salarios Base',
            'Renta Oficina',
            'Software',
            'Otros Gastos',
            'Subtotal Costos Op',
            '',
            '🏛️ FEES GUBERNAMENTALES',
            f'Fee {gov_fee_pct:.1%} sobre Revenue',
            '',
            'TOTAL COSTOS',
            '',
            '📊 RESULTADO',
            'EBITDA MENSUAL',
            'Margen EBITDA %',
            '',
            f'📅 PROYECCIÓN {projection_months} MESES',
            'Revenue Total Proyectado',
            'EBITDA Proyectado'
        ],
        'Monto': [
            '',
            f"{monthly_sales:.0f} ventas",
            f"${monthly_revenue_immediate:,.0f}",
            f"${monthly_revenue_deferred:,.0f}",
            f"${monthly_revenue_total:,.0f}",
            '',
            '',
            f"${total_marketing:,.0f}",
            f"${closer_commission_total:,.0f}",
            f"${setter_commission_total:,.0f}",
            f"${total_base_salaries:,.0f}",
            f"${office_rent:,.0f}",
            f"${software_costs:,.0f}",
            f"${other_opex:,.0f}",
            f"${total_costs_before_fees:,.0f}",
            '',
            '',
            f"${government_fees:,.0f}",
            '',
            f"${total_costs:,.0f}",
            '',
            '',
            f"${monthly_ebitda:,.0f}",
            f"{ebitda_margin:.1%}",
            '',
            '',
            f"${revenue_timeline['cumulative_total'].iloc[-1]:,.0f}",
            f"${revenue_timeline['cumulative_total'].iloc[-1] - (total_costs * projection_months):,.0f}"
        ]
    }
    
    df_pl = pd.DataFrame(pl_data)
    st.dataframe(df_pl, use_container_width=True, height=700)

# TAB 6: SIMULATOR (Enhanced from fixed)
with tabs[5]:
    st.header("🚀 Simulador de Escenarios MEJORADO")
    
    # Optimization selector
    opt_target = st.radio(
        "Qué quieres optimizar?",
        ["EBITDA", "Margen %", "Ventas", "CAC"],
        horizontal=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Estado Actual")
        st.code(f"""
Ventas/Mes: {monthly_sales:.0f}
Revenue: ${monthly_revenue_total:,.0f}
Costos: ${total_costs:,.0f}
EBITDA: ${monthly_ebitda:,.0f}
Margen: {ebitda_margin:.1%}
LTV:CAC: {ltv_cac_ratio:.1f}:1
        """)
    
    with col2:
        st.subheader("🎯 Simular Cambios")
        
        if opt_target == "EBITDA":
            target_ebitda = st.number_input(
                "EBITDA Objetivo",
                min_value=int(monthly_ebitda * 0.5),
                max_value=int(monthly_ebitda * 3),
                value=int(monthly_ebitda * 1.5)
            )
            
            # Calculate requirements
            revenue_needed = (target_ebitda + total_costs_before_fees) / (1 - gov_fee_pct)
            sales_needed = revenue_needed / comp_immediate
            meetings_needed = sales_needed / close_rate
            
            st.success(f"""
⚡ **Para EBITDA ${target_ebitda:,.0f}:**
• {sales_needed:.0f} ventas/mes
• {meetings_needed:.0f} reuniones/mes
• {int(meetings_needed/60):.0f} closers
• Revenue: ${revenue_needed:,.0f}
            """)
            
        elif opt_target == "Margen %":
            target_margin = st.slider("Margen Objetivo", 20, 60, 40, 5)
            cost_reduction = monthly_revenue_total * ((target_margin - ebitda_margin*100)/100)
            st.info(f"Reducir costos en ${cost_reduction:,.0f}")
    
    with col3:
        st.subheader("💡 Recomendaciones")
        if ltv_cac_ratio < 3:
            st.error("❌ LTV:CAC < 3:1")
            st.write("• Reduce CPL o mejora conversión")
        if ebitda_margin < 0.2:
            st.warning("⚠️ Margen bajo")
            st.write("• Optimiza costos fijos")

# TAB 7: TEAM & RAMP
with tabs[6]:
    st.header("👥 Team Planning & Ramp")
    
    # Ramp visualization
    st.subheader("📈 Ramp Schedule")
    
    new_hires = st.number_input("New Hires to Model", 1, 20, 5)
    
    ramp_data = TeamMetricsCalculator.calculate_ramp_impact(
        new_hires, ramp_months,
        [0.3, 0.6, 0.85, 1.0]  # Productivity curve
    )
    
    fig_ramp = go.Figure()
    fig_ramp.add_trace(go.Scatter(
        x=ramp_data['month'],
        y=ramp_data['productivity'] * 100,
        mode='lines+markers',
        name='Productivity %',
        line=dict(color='blue', width=3)
    ))
    
    fig_ramp.add_trace(go.Bar(
        x=ramp_data['month'],
        y=ramp_data['effective_capacity'],
        name='Effective Capacity',
        yaxis='y2',
        marker_color='lightblue'
    ))
    
    fig_ramp.update_layout(
        title="Ramp-up Schedule",
        xaxis_title="Month",
        yaxis_title="Productivity %",
        yaxis2=dict(title="Effective Capacity", overlaying='y', side='right'),
        height=400
    )
    
    st.plotly_chart(fig_ramp, use_container_width=True)
    
    st.dataframe(ramp_data, use_container_width=True)

# TAB 8: HEALTH METRICS
with tabs[7]:
    st.header("📊 Health Metrics Dashboard")
    
    # Health score card
    st.markdown('<div class="health-score-card">', unsafe_allow_html=True)
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    
    with health_col1:
        st.metric("Overall Health", f"{health_scores['overall_health']:.0f}/100", health_scores['status'])
    with health_col2:
        st.metric("Funnel Health", f"{health_scores['funnel_health']:.0f}/100")
    with health_col3:
        st.metric("Team Health", f"{health_scores['team_health']:.0f}/100")
    with health_col4:
        st.metric("Financial Health", f"{health_scores['financial_health']:.0f}/100")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bottlenecks
    st.subheader("🔍 Bottleneck Analysis")
    
    bottlenecks = BottleneckAnalyzer.find_bottlenecks(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {'closer_utilization': monthly_meetings / (num_closers * 60) if num_closers > 0 else 0},
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin}
    )
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            st.warning(f"""
            **{bottleneck['type']} Bottleneck: {bottleneck['issue']}**
            - Current: {bottleneck['current']:.2f}
            - Target: {bottleneck['target']:.2f}
            - Impact: {bottleneck['impact']}
            - Action: {bottleneck['action']}
            """)

# TAB 9: REVERSE ENGINEERING
with tabs[8]:
    add_reverse_engineering_tab(st.container())
