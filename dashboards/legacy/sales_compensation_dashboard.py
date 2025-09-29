"""
Dashboard Corregido con Control Total y Validaciones
Modelo Bowtie (Winning by Design) + Compensación Optimaxx PLUS
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from reverse_engineering_module import add_reverse_engineering_tab

# Configuración
st.set_page_config(
    page_title="🎯 Simulador Completo Optimaxx - Bowtie WbD",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS mejorado
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
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💰 Simulador Completo de Compensación - Modelo Optimaxx PLUS")
st.markdown("**Control granular con validaciones y modelo Bowtie correcto**")

# ============= FUNCIONES DE VALIDACIÓN =============
def validate_team_capacity(daily_leads, num_closers, num_setters, contact_rate, meeting_rate, close_rate):
    """Valida que el equipo tenga la capacidad correcta"""
    warnings = []
    suggestions = []
    
    # Calcular volúmenes esperados
    daily_contacts = daily_leads * contact_rate
    daily_meetings = daily_contacts * meeting_rate
    daily_sales = daily_meetings * close_rate
    
    # Capacidad estándar por rol
    MAX_CONTACTS_PER_SETTER = 60
    MIN_CONTACTS_PER_SETTER = 20
    MAX_MEETINGS_PER_CLOSER = 6
    MIN_MEETINGS_PER_CLOSER = 2
    
    # Validar setters
    if num_setters > 0:
        contacts_per_setter = daily_contacts / num_setters
        if contacts_per_setter > MAX_CONTACTS_PER_SETTER:
            warnings.append(f"⚠️ Sobrecarga: Cada setter tendría {contacts_per_setter:.0f} contactos/día")
            needed = int(np.ceil(daily_contacts / MAX_CONTACTS_PER_SETTER))
            suggestions.append(f"💡 Necesitas al menos {needed} setters")
        elif contacts_per_setter < MIN_CONTACTS_PER_SETTER:
            warnings.append(f"⚠️ Subutilización: Cada setter solo tendría {contacts_per_setter:.0f} contactos/día")
            optimal = max(1, int(daily_contacts / 40))
            suggestions.append(f"💡 Podrías optimizar con {optimal} setters")
    
    # Validar closers
    if num_closers > 0:
        meetings_per_closer = daily_meetings / num_closers
        if meetings_per_closer > MAX_MEETINGS_PER_CLOSER:
            warnings.append(f"❌ Imposible: Cada closer tendría {meetings_per_closer:.0f} reuniones/día")
            needed = int(np.ceil(daily_meetings / MAX_MEETINGS_PER_CLOSER))
            suggestions.append(f"💡 Necesitas al menos {needed} closers")
        elif meetings_per_closer < MIN_MEETINGS_PER_CLOSER:
            warnings.append(f"⚠️ Desperdicio: Cada closer solo tendría {meetings_per_closer:.0f} reuniones/día")
            optimal = max(1, int(daily_meetings / 3))
            suggestions.append(f"💡 Podrías optimizar con {optimal} closers")
    
    # Validar ratio setter:closer
    if num_setters > 0 and num_closers > 0:
        ratio = num_setters / num_closers
        if ratio > 2:
            warnings.append(f"⚠️ Desbalance: Ratio setter:closer de {ratio:.1f}:1 (muy alto)")
        elif ratio < 0.5:
            warnings.append(f"⚠️ Desbalance: Ratio setter:closer de {ratio:.1f}:1 (muy bajo)")
    
    return warnings, suggestions

# ============= SIDEBAR - CONTROL GRANULAR =============
st.sidebar.header("⚙️ Panel de Control Completo")

# SECCIÓN 1: CONTROL GRANULAR DEL EQUIPO
st.sidebar.markdown("---")
st.sidebar.subheader("👥 1. Control Granular del Equipo")

col1, col2 = st.sidebar.columns(2)
with col1:
    num_closers = st.sidebar.number_input(
        "💼 # Closers Activos",
        min_value=0, max_value=50, value=8, step=1,
        help="Número exacto de closers en tu equipo"
    )
    num_setters = st.sidebar.number_input(
        "📞 # Setters Activos",
        min_value=0, max_value=50, value=6, step=1,
        help="Número exacto de setters en tu equipo"
    )

with col2:
    num_bench = st.sidebar.number_input(
        "🏈 # en Banca",
        min_value=0, max_value=20, value=4, step=1,
        help="Personas en recuperación (10 meetings para salir)"
    )
    num_managers = st.sidebar.number_input(
        "👔 # Managers/TLs",
        min_value=0, max_value=10, value=2, step=1,
        help="Supervisores y Team Leads"
    )

team_total = num_closers + num_setters + num_bench + num_managers
active_team = num_closers + num_setters

st.sidebar.info(f"""
**📊 Resumen del Equipo:**
- Total: {team_total} personas
- Activos: {active_team} ({active_team/max(1,team_total)*100:.0f}%)
- En Banca: {num_bench} ({num_bench/max(1,team_total)*100:.0f}%)
- Ratio S:C: {num_setters}:{num_closers} ({num_setters/max(1,num_closers):.1f}:1)
""")

# Alerta si hay demasiada gente en banca
if num_bench / max(1, team_total) > 0.25:
    st.sidebar.warning("⚠️ Más del 25% en banca indica problemas de reclutamiento/entrenamiento")

# SECCIÓN 2: VOLUMEN DE LEADS
st.sidebar.markdown("---")
st.sidebar.subheader("📈 2. Motor de Leads")

daily_leads = st.sidebar.number_input(
    "📥 Leads Diarios",
    min_value=0, max_value=2000, value=200, step=10,
    help="Nuevos prospectos por día (puede ser 0 para simular)"
)

cpl = st.sidebar.number_input(
    "💰 CPL - Costo por Lead (MXN)",
    min_value=0, max_value=200, value=25, step=5,
    help="Costo de marketing por cada lead"
)

# Mostrar costo mensual de leads
monthly_lead_cost = daily_leads * 30 * cpl
st.sidebar.metric("Gasto en Leads/Mes", f"${monthly_lead_cost:,.0f}")

# SECCIÓN 3: FUNNEL BOWTIE - LADO IZQUIERDO
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 3. Funnel Bowtie - Land (Izq)")

contact_rate = st.sidebar.slider(
    "📞 Contact Rate (%)",
    min_value=0.0, max_value=100.0, value=70.0, step=5.0,
    help="LEADS → CONTACTED"
) / 100

meeting_rate = st.sidebar.slider(
    "📅 Meeting/Appointment Rate (%)",
    min_value=0.0, max_value=100.0, value=35.0, step=5.0,
    help="CONTACTED → MEETINGS"
) / 100

close_rate = st.sidebar.slider(
    "💰 Close Rate (%)",
    min_value=0.0, max_value=100.0, value=25.0, step=5.0,
    help="MEETINGS → SALES"
) / 100

# SECCIÓN 4: FUNNEL BOWTIE - LADO DERECHO
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 4. Funnel Bowtie - Expand (Der)")

onboard_rate = st.sidebar.slider(
    "✅ Onboard Rate (%)",
    min_value=80.0, max_value=100.0, value=95.0, step=1.0,
    help="SALES → ONBOARDED (pólizas activas)"
) / 100

grr_rate = st.sidebar.slider(
    "📊 GRR 18m (%)",
    min_value=60.0, max_value=100.0, value=90.0, step=5.0,
    help="Gross Revenue Retention - Sin expansión"
) / 100

nrr_rate = st.sidebar.slider(
    "📈 NRR 18m (%)",
    min_value=80.0, max_value=150.0, value=120.0, step=5.0,
    help="Net Revenue Retention - Con upsell"
) / 100

# SECCIÓN 5: PRIMA MENSUAL (ÚNICA FUENTE)
st.sidebar.markdown("---")
st.sidebar.subheader("💳 5. Prima Mensual (PM)")

pm_mode = st.sidebar.radio(
    "Modo de Prima",
    ["Simple (Una Prima)", "Distribución (Mix)"]
)

if pm_mode == "Simple (Una Prima)":
    avg_pm = st.sidebar.number_input(
        "Prima Mensual (MXN)",
        min_value=1000, max_value=10000, value=3000, step=100,
        help="Prima mensual única para todos"
    )
    pm_distribution = {avg_pm: 1.0}
else:
    st.sidebar.markdown("##### Mix de Primas")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        pct_2k = st.sidebar.number_input("% PM $2,000", 0, 100, 20, 5)
        pct_3k = st.sidebar.number_input("% PM $3,000", 0, 100, 50, 5)
    with col2:
        pct_4k = st.sidebar.number_input("% PM $4,000", 0, 100, 20, 5)
        pct_5k = st.sidebar.number_input("% PM $5,000", 0, 100, 10, 5)
    
    total_pct = pct_2k + pct_3k + pct_4k + pct_5k
    if total_pct == 100:
        pm_values = [2000, 3000, 4000, 5000]
        pm_weights = [pct_2k/100, pct_3k/100, pct_4k/100, pct_5k/100]
        avg_pm = np.average(pm_values, weights=pm_weights)
        pm_distribution = dict(zip(pm_values, pm_weights))
    else:
        st.sidebar.error(f"❌ Suma debe ser 100% (actual: {total_pct}%)")
        avg_pm = 3000
        pm_distribution = {3000: 1.0}

# Mostrar resumen de compensación
comp_total = avg_pm * 8.1
comp_immediate = comp_total * 0.7
comp_deferred = comp_total * 0.3

st.sidebar.success(f"""
**💰 Resumen Compensación:**
- Prima Promedio: ${avg_pm:,.0f}
- Comp Total: ${comp_total:,.0f}
- Inmediato (70%): ${comp_immediate:,.0f}
- Diferido (30%): ${comp_deferred:,.0f}
""")

# SECCIÓN 6: ESTRUCTURA DE COMPENSACIÓN
st.sidebar.markdown("---")
st.sidebar.subheader("💵 6. Compensación Variable")

closer_comm_pct = st.sidebar.slider(
    "% Comisión Closers",
    min_value=10.0, max_value=30.0, value=20.0, step=1.0,
    help="% del ingreso que va a closers"
) / 100

setter_of_closer_pct = st.sidebar.slider(
    "% Setter (del closer)",
    min_value=10.0, max_value=30.0, value=15.0, step=1.0,
    help="Setter gana este % de lo que gana el closer"
) / 100

speed_bonus_pct = st.sidebar.slider(
    "⚡ Bono Velocidad (%)",
    min_value=0.0, max_value=20.0, value=10.0, step=5.0,
    help="Bonus por contactar en <15 min"
) / 100

followup_bonus_pct = st.sidebar.slider(
    "🔄 Bono Seguimiento (%)",
    min_value=0.0, max_value=15.0, value=5.0, step=5.0,
    help="Bonus por 2+ seguimientos"
) / 100

# SECCIÓN 7: SALARIOS BASE Y COSTOS FIJOS
st.sidebar.markdown("---")
st.sidebar.subheader("🏢 7. Costos Fijos")

st.sidebar.markdown("##### Salarios Base")
col1, col2 = st.sidebar.columns(2)
with col1:
    closer_base = st.sidebar.number_input("Base Closer", 0, 20000, 5000, 1000)
    setter_base = st.sidebar.number_input("Base Setter", 0, 15000, 3000, 1000)
with col2:
    bench_base = st.sidebar.number_input("Base Banca", 0, 10000, 3000, 500)
    manager_base = st.sidebar.number_input("Base Manager", 0, 50000, 15000, 2000)

st.sidebar.markdown("##### Otros Costos")
office_rent = st.sidebar.number_input("Renta Oficina", 0, 100000, 20000, 5000)
software_costs = st.sidebar.number_input("Software/Tools", 0, 50000, 10000, 1000)
other_opex = st.sidebar.number_input("Otros Gastos", 0, 50000, 5000, 1000)

# SECCIÓN 8: FEES Y PROYECCIÓN
st.sidebar.markdown("---")
st.sidebar.subheader("⚖️ 8. Fees y Proyección")

gov_fee_pct = st.sidebar.slider(
    "🏛️ Fee Gubernamental (%)",
    min_value=0.0, max_value=20.0, value=10.0, step=0.5,
    help="ISR, IVA u otros impuestos sobre revenue"
) / 100

projection_months = st.sidebar.selectbox(
    "📅 Horizonte de Proyección",
    options=[1, 3, 6, 12, 18, 24],
    index=4,  # Default a 18 meses
    help="Meses a proyectar (importante para pagos diferidos)"
)

# ============= CÁLCULOS DEL MODELO =============

# Calcular métricas del funnel (mensual)
monthly_leads = daily_leads * 30
monthly_contacts = monthly_leads * contact_rate
monthly_meetings = monthly_contacts * meeting_rate
monthly_sales = monthly_meetings * close_rate
monthly_onboarded = monthly_sales * onboard_rate
monthly_grr = monthly_onboarded * grr_rate
monthly_nrr_value = monthly_grr * (nrr_rate / max(0.01, grr_rate))

# Calcular ingresos CON CLARIDAD 70/30
revenue_per_sale_immediate = comp_immediate  # 70% cobrado HOY
revenue_per_sale_deferred = comp_deferred * grr_rate  # 30% en mes 18 (con persistencia)
revenue_per_sale_total = comp_immediate + (comp_deferred * grr_rate)

monthly_revenue_immediate = monthly_sales * revenue_per_sale_immediate
monthly_revenue_deferred = monthly_sales * revenue_per_sale_deferred

# PROYECCIÓN REAL A X MESES
if projection_months >= 18:
    # Si proyectamos 18+ meses, incluimos los pagos diferidos
    monthly_revenue_total = monthly_revenue_immediate + (monthly_revenue_deferred if projection_months == 18 else 0)
    # Para proyección completa: revenue acumulado incluyendo diferidos
    total_revenue_projection = (
        monthly_revenue_immediate * projection_months +  # Ingresos inmediatos cada mes
        monthly_revenue_deferred * max(0, projection_months - 17)  # Diferidos a partir del mes 18
    )
else:
    # Si proyectamos menos de 18 meses, solo inmediato
    monthly_revenue_total = monthly_revenue_immediate
    total_revenue_projection = monthly_revenue_immediate * projection_months

# Calcular costos unitarios
if monthly_meetings > 0:
    cpm = (monthly_lead_cost) / monthly_meetings  # Cost per Meeting
    cpa = cpm  # Cost per Appointment (mismo que meeting)
else:
    cpm = 0
    cpa = 0

if monthly_sales > 0:
    cac = (monthly_lead_cost + (active_team * 5000)) / monthly_sales  # CAC simplificado
else:
    cac = 0

# Calcular compensaciones
closer_commission_total = monthly_revenue_immediate * closer_comm_pct
setter_commission_total = closer_commission_total * setter_of_closer_pct * (1 + speed_bonus_pct + followup_bonus_pct)

# Salarios base totales
total_base_salaries = (
    num_closers * closer_base +
    num_setters * setter_base +
    num_bench * bench_base +
    num_managers * manager_base
)

# Costos totales
total_marketing = monthly_lead_cost
total_compensation = closer_commission_total + setter_commission_total + total_base_salaries
total_fixed = office_rent + software_costs + other_opex
total_costs_before_fees = total_marketing + total_compensation + total_fixed

# Aplicar FEE GUBERNAMENTAL
government_fees = monthly_revenue_total * gov_fee_pct
total_costs = total_costs_before_fees + government_fees

# EBITDA REAL (con fees)
monthly_ebitda = monthly_revenue_total - total_costs
daily_ebitda = monthly_ebitda / 30

# Métricas adicionales para claridad
pct_immediate = 0.7  # 70% inmediato
pct_deferred = 0.3   # 30% diferido
cash_collected_today = monthly_revenue_immediate  # Efectivo HOY
cash_pending_month_18 = monthly_revenue_deferred  # Por cobrar en mes 18

# LTV y ratios
ltv = revenue_per_sale_total
ltv_cac_ratio = ltv / cac if cac > 0 else 0

# Validaciones
warnings, suggestions = validate_team_capacity(
    daily_leads, num_closers, num_setters,
    contact_rate, meeting_rate, close_rate
)

# ============= VISUALIZACIÓN PRINCIPAL =============

# Mostrar alertas
if warnings:
    with st.expander("⚠️ **ALERTAS Y SUGERENCIAS**", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.error("### Problemas Detectados")
            for w in warnings:
                st.warning(w)
        with col2:
            st.info("### Sugerencias")
            for s in suggestions:
                st.success(s)

# Tabs principales
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Modelo Bowtie",
    "💰 Costos Unitarios",
    "💵 Compensación",
    "📊 P&L Completo",
    "🚀 Simulador",
    "🔄 Ingeniería Inversa"
])

with tab1:
    st.header("🎯 Modelo Bowtie - Winning by Design")
    
    # NUEVA SECCIÓN: Claridad 70/30
    st.info(f"""
    💰 **ESTRUCTURA DE PAGOS OPTIMAXX ({projection_months} meses proyección):**
    - **70% INMEDIATO** = ${cash_collected_today:,.0f} cobrado HOY
    - **30% DIFERIDO** = ${cash_pending_month_18:,.0f} por cobrar en MES 18 (con {grr_rate:.0%} persistencia)
    - **Fee Gubernamental** = {gov_fee_pct:.1%} sobre revenue (${government_fees:,.0f}/mes)
    """)
    
    # Métricas principales
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
    
    # Visualización del embudo
    fig = go.Figure(go.Funnel(
        y=['Leads', 'Contacted', 'Meetings', 'Sales', 'Onboarded', 'GRR (18m)'],
        x=[monthly_leads, monthly_contacts, monthly_meetings, monthly_sales, monthly_onboarded, monthly_grr],
        textposition="inside",
        textinfo="value+percent previous",
        marker={"color": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]},
        connector={"line": {"color": "royalblue", "dash": "dot", "width": 2}}
    ))
    
    fig.update_layout(
        title="Funnel Bowtie Mensual",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("💰 Análisis de Costos Unitarios")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CPL", f"${cpl:,.0f}", "Costo por Lead")
        if monthly_contacts > 0:
            cpc = monthly_lead_cost / monthly_contacts
            st.metric("CPC", f"${cpc:,.0f}", "Costo por Contacto")
    
    with col2:
        st.metric("CPM", f"${cpm:,.0f}", "Costo por Meeting")
        st.metric("CPA", f"${cpa:,.0f}", "Costo por Appointment")
    
    with col3:
        st.metric("CAC", f"${cac:,.0f}", "Costo de Adquisición")
        st.metric("LTV", f"${ltv:,.0f}", "Lifetime Value")
    
    with col4:
        color = "normal" if ltv_cac_ratio >= 3 else "inverse"
        st.metric(
            "LTV:CAC",
            f"{ltv_cac_ratio:.1f}:1",
            "✅ Saludable" if ltv_cac_ratio >= 3 else "❌ Bajo",
            delta_color=color
        )
        payback = cac / comp_immediate if comp_immediate > 0 else 999
        st.metric("Payback", f"{payback:.1f} meses")

with tab3:
    st.header("💵 Sistema de Compensación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💼 Compensación Closers")
        
        # Por venta
        closer_per_sale = comp_immediate * closer_comm_pct
        st.metric("Comisión por Venta", f"${closer_per_sale:,.0f}")
        
        # Por closer
        if num_closers > 0:
            sales_per_closer = monthly_sales / num_closers
            comm_per_closer_month = sales_per_closer * closer_per_sale
            total_closer_month = closer_base + comm_per_closer_month
            
            st.metric("Ventas/Closer/Mes", f"{sales_per_closer:.1f}")
            st.metric("Comisión Mensual", f"${comm_per_closer_month:,.0f}")
            st.metric("Total (Base+Com)", f"${total_closer_month:,.0f}")
    
    with col2:
        st.subheader("📞 Compensación Setters")
        
        # Por venta
        setter_per_sale = closer_per_sale * setter_of_closer_pct
        setter_with_bonuses = setter_per_sale * (1 + speed_bonus_pct + followup_bonus_pct)
        
        st.metric("Comisión por Venta", f"${setter_per_sale:,.0f}")
        st.metric("Con Bonos Máx", f"${setter_with_bonuses:,.0f}")
        
        # Por setter
        if num_setters > 0:
            sales_per_setter = monthly_sales / num_setters
            comm_per_setter_month = sales_per_setter * setter_with_bonuses
            total_setter_month = setter_base + comm_per_setter_month
            
            st.metric("Total (Base+Com+Bonos)", f"${total_setter_month:,.0f}")

with tab4:
    st.header("📊 P&L Mensual Completo")
    
    # Crear tabla P&L MEJORADA con fees
    pl_data = {
        'Concepto': [
            '📈 INGRESOS',
            'Ventas del Mes',
            'Ingresos Inmediatos (70%)',
            'Ingresos Diferidos (30%)*',
            'TOTAL INGRESOS (MES ACTUAL)',
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
            'EBITDA DIARIO',
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
            f"${daily_ebitda:,.0f}",
            f"{(monthly_ebitda/max(1,monthly_revenue_total))*100:.1f}%",
            '',
            '',
            f"${total_revenue_projection:,.0f}",
            f"${total_revenue_projection - (total_costs * projection_months):,.0f}"
        ]
    }
    
    df_pl = pd.DataFrame(pl_data)
    st.dataframe(df_pl, use_container_width=True, height=600)
    
    # Nota sobre pagos diferidos
    st.info("*Los ingresos diferidos se reciben en el mes 18 con persistencia del 90%")

with tab5:
    st.header("🚀 Simulador de Escenarios MEJORADO")
    
    # Selección de qué optimizar
    optimization_target = st.radio(
        "Qué quieres optimizar?",
        ["EBITDA", "Margen %", "Ventas", "CAC"],
        horizontal=True
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 Estado Actual")
        current_metrics = f"""
💰 **FINANCIERO**
Ventas/Mes: {monthly_sales:.0f}
Ingreso Inmediato: ${cash_collected_today:,.0f}
Ingreso Total: ${monthly_revenue_total:,.0f}

💸 **COSTOS**
Operativos: ${total_costs_before_fees:,.0f}
Fees Gov: ${government_fees:,.0f}
Total: ${total_costs:,.0f}

📈 **RESULTADO**  
EBITDA: ${monthly_ebitda:,.0f}
Margen: {(monthly_ebitda/max(1,monthly_revenue_total))*100:.1f}%
LTV:CAC: {ltv_cac_ratio:.1f}:1
        """
        st.markdown(current_metrics)
    
    with col2:
        st.subheader("🎯 Simular Cambios")
        
        if optimization_target == "EBITDA":
            target_ebitda = st.number_input(
                "EBITDA Objetivo Mensual",
                min_value=int(monthly_ebitda * 0.5),
                max_value=int(monthly_ebitda * 3),
                value=int(monthly_ebitda * 1.5),
                step=10000
            )
            
            # Cálculos más realistas
            revenue_needed = (target_ebitda + total_costs_before_fees) / (1 - gov_fee_pct)
            sales_needed = revenue_needed / revenue_per_sale_immediate
            meetings_needed = sales_needed / close_rate
            leads_needed = meetings_needed / (contact_rate * meeting_rate)
            
            st.success(f"""
⚡ **Para EBITDA ${target_ebitda:,.0f}:**

🎯 Necesitas:
• {sales_needed:.0f} ventas/mes (+{sales_needed - monthly_sales:.0f})
• {meetings_needed:.0f} reuniones/mes
• {leads_needed:.0f} leads/mes

👥 Equipo sugerido:
• {int(meetings_needed/15):.0f} closers (15 mtgs c/u)
• {int(leads_needed/600):.0f} setters (30 contactos/día)
            """)
            
        elif optimization_target == "Margen %":
            target_margin = st.slider(
                "Margen EBITDA Objetivo (%)",
                min_value=20,
                max_value=80,
                value=60,
                step=5
            )
            
            # Qué reducir para lograr el margen
            current_margin = (monthly_ebitda/max(1,monthly_revenue_total))*100
            if target_margin > current_margin:
                cost_reduction_needed = monthly_revenue_total * ((target_margin - current_margin)/100)
                st.info(f"""
💰 **Para Margen {target_margin}%:**

Opciones:
1️⃣ Reducir costos ${cost_reduction_needed:,.0f}/mes
2️⃣ Aumentar close rate a {(close_rate * 1.2):.1%}
3️⃣ Bajar CPL a ${cpl * 0.7:.0f}
4️⃣ Reducir comisiones 2-3%
                """)
        
        elif optimization_target == "CAC":
            target_cac = st.number_input(
                "CAC Objetivo",
                min_value=500,
                max_value=5000,
                value=1500,
                step=100
            )
            
            max_marketing_spend = target_cac * monthly_sales - (active_team * 5000)
            max_cpl = max_marketing_spend / monthly_leads if monthly_leads > 0 else 0
            
            st.warning(f"""
🎯 **Para CAC ${target_cac}:**

Límites:
• CPL máximo: ${max_cpl:.0f}
• Marketing máx: ${max_marketing_spend:,.0f}
• O aumentar close rate a {(monthly_sales/monthly_meetings * 1.3):.1%}
            """)
    
    with col3:
        st.subheader("💡 Análisis Inteligente")
        
        if ltv_cac_ratio < 3:
            st.error("❌ LTV:CAC < 3:1")
            st.write("• Reduce CPL o mejora conversión")
        
        if num_bench / max(1, team_total) > 0.25:
            st.warning("⚠️ Mucha gente en banca")
            st.write("• Mejora entrenamiento")
        
        if monthly_ebitda < 0:
            st.error("❌ EBITDA Negativo")
            st.write("• Reduce costos urgentemente")

with tab6:
    # Añadir el módulo de ingeniería inversa con CONTEXTO del dashboard
    st.header("🔄 Ingeniería Inversa CONECTADA")
    
    # Crear un diccionario con todos los valores actuales del dashboard
    current_context = {
        'monthly_sales': monthly_sales,
        'monthly_revenue': monthly_revenue_total,
        'monthly_ebitda': monthly_ebitda,
        'num_closers': num_closers,
        'num_setters': num_setters,
        'close_rate': close_rate,
        'meeting_rate': meeting_rate,
        'contact_rate': contact_rate,
        'cpl': cpl,
        'avg_pm': avg_pm,
        'comp_immediate': comp_immediate,
        'gov_fee_pct': gov_fee_pct,
        'projection_months': projection_months
    }
    
    # Mostrar contexto actual
    with st.expander("📊 Valores actuales del dashboard (usados en cálculos)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ventas/mes actual", f"{monthly_sales:.0f}")
            st.metric("EBITDA actual", f"${monthly_ebitda:,.0f}")
        with col2:
            st.metric("Closers actuales", num_closers)
            st.metric("Close rate actual", f"{close_rate:.0%}")
        with col3:
            st.metric("Revenue/venta", f"${comp_immediate:,.0f}")
            st.metric("Fee Gov", f"{gov_fee_pct:.1%}")
    
    # Llamar al módulo con contexto
    add_reverse_engineering_tab(st.container())
