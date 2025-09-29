"""
Dashboard Mejorado de Compensación con Tooltips y Control Total
Todos los inputs en el sidebar para mejor experiencia de usuario
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from optimaxx_plus_model import OptimaxPlusConfig, OptimaxPlusCalculator

# Configuración de página
st.set_page_config(
    page_title="🎯 Simulador Avanzado de Compensación Optimaxx PLUS",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para tooltips y mejor UI
st.markdown("""
    <style>
    .stAlert {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("💰 Simulador Avanzado de Compensación - Modelo Optimaxx PLUS")
st.markdown("**Control total sobre la estructura de compensación de tu equipo de ventas**")

# =============== SIDEBAR - TODOS LOS INPUTS ===============
st.sidebar.header("⚙️ Panel de Control Completo")
st.sidebar.markdown("---")

# SECCIÓN 1: ESTRUCTURA DEL EQUIPO
st.sidebar.subheader("👥 1. Estructura del Equipo")

team_size = st.sidebar.number_input(
    "📊 Tamaño Total del Equipo",
    min_value=5, max_value=100, value=20, step=1,
    help="""
    🎯 **¿Qué es?** El número total de personas en tu equipo comercial.
    
    💡 **Decisión:** Más personas = más capacidad pero más costo fijo.
    
    ⚠️ **Alerta:** Si tu EBITDA es negativo, considera reducir el equipo.
    """
)

st.sidebar.markdown("#### 🏈 Sistema de Banca (Bench)")
bench_pct = st.sidebar.number_input(
    "% en Banca",
    min_value=0.0, max_value=40.0, value=20.0, step=5.0,
    help="""
    🎯 **¿Qué es?** Personas en recuperación por bajo rendimiento.
    
    ⚽ **Sistema Football:** Como en los equipos deportivos, están en la banca.
    
    📈 **Para salir:** Deben lograr 10 reuniones agendadas.
    
    ⚠️ **Alerta:** >20% indica problemas de reclutamiento o entrenamiento.
    """
)

bench_base_salary = st.sidebar.number_input(
    "💵 Salario Base Banca (MXN)",
    min_value=2000, max_value=10000, value=3000, step=500,
    help="""
    🎯 **¿Qué es?** Salario mínimo mientras están en recuperación.
    
    💡 **Estrategia:** Suficiente para sobrevivir, pero motivador para salir.
    
    📊 **Benchmark:** $3,000-5,000 MXN es estándar en México.
    """
)

bench_meeting_bonus = st.sidebar.number_input(
    "🎁 Bono por Reunión Agendada",
    min_value=50, max_value=500, value=100, step=50,
    help="""
    🎯 **¿Qué es?** Pago extra por cada reunión que agendan.
    
    🎮 **Gamification:** Los motiva a salir rápido de la banca.
    
    💰 **ROI:** Cada reunión puede valer $500+ en comisiones futuras.
    """
)

bench_meetings_to_exit = st.sidebar.number_input(
    "🎯 Reuniones para Salir de Banca",
    min_value=5, max_value=20, value=10, step=1,
    help="""
    🏆 **Meta clara:** Al lograr este número, regresan como setters activos.
    
    ⚡ **Velocidad:** Un buen performer lo logra en 1-2 semanas.
    
    🚫 **Si no lo logran:** Considerar despido después de 30 días.
    """
)

# Distribución del equipo activo
active_team = int(team_size * (1 - bench_pct/100))
setter_pct = st.sidebar.number_input(
    "% Setters (del equipo activo)",
    min_value=30.0, max_value=70.0, value=40.0, step=5.0,
    help="""
    🎯 **¿Qué es?** Porcentaje de setters vs closers en el equipo ACTIVO.
    
    ⚖️ **Balance ideal:** 40% setters, 60% closers es común.
    
    📊 **Si tienes muchos leads:** Necesitas más setters.
    📉 **Si tienes pocos leads de calidad:** Necesitas más closers.
    """
)

# Mostrar distribución
bench_count = int(team_size * bench_pct/100)
setter_count = int(active_team * setter_pct/100)
closer_count = active_team - setter_count

st.sidebar.info(f"""
**📊 Distribución Actual:**
- 🏈 Banca: {bench_count} personas
- 📞 Setters: {setter_count} personas  
- 💼 Closers: {closer_count} personas
- ✅ Activos: {active_team} personas
""")

st.sidebar.markdown("---")

# SECCIÓN 2: GENERACIÓN DE LEADS
st.sidebar.subheader("🎯 2. Motor de Leads")

daily_leads = st.sidebar.number_input(
    "📈 Leads Diarios",
    min_value=50, max_value=1000, value=200, step=25,
    help="""
    🎯 **¿Qué es?** Nuevos prospectos que entran cada día.
    
    📊 **Cálculo rápido:** 200 leads × 30 días = 6,000 leads/mes
    
    💡 **Pro tip:** Es mejor tener 100 leads buenos que 500 malos.
    
    🚀 **Para escalar:** Primero mejora conversión, luego sube volumen.
    """
)

cpl = st.sidebar.number_input(
    "💰 Costo por Lead (MXN)",
    min_value=10, max_value=200, value=25, step=5,
    help="""
    🎯 **¿Qué es?** Lo que pagas en marketing por cada lead.
    
    📱 **Facebook:** $15-40 MXN típico
    🔍 **Google:** $30-80 MXN típico  
    📧 **Email frío:** $5-15 MXN típico
    
    ⚠️ **Alerta:** Si CPL > $50, revisa tu targeting.
    """
)

st.sidebar.markdown("---")

# SECCIÓN 3: TASAS DE CONVERSIÓN
st.sidebar.subheader("🔄 3. Tasas de Conversión del Funnel")

contact_rate = st.sidebar.slider(
    "📞 Tasa de Contacto (%)",
    min_value=40.0, max_value=90.0, value=70.0, step=5.0,
    help="""
    🎯 **¿Qué es?** % de leads con los que logras hablar.
    
    ⚡ **Velocidad importa:** Contactar en <5 min = 80%+ tasa
    🐌 **Lento mata:** Contactar en >1 hora = 40% tasa
    
    💡 **Para mejorar:** Implementa el bono de velocidad.
    """
) / 100

meeting_rate = st.sidebar.slider(
    "📅 Tasa de Reuniones (%)",
    min_value=20.0, max_value=60.0, value=35.0, step=5.0,
    help="""
    🎯 **¿Qué es?** % de contactados que agendan reunión.
    
    🎙️ **Script matters:** Un buen script puede doblar esta tasa.
    
    📊 **Benchmark:** 30-40% es bueno, 50%+ es excelente.
    
    💡 **Para mejorar:** Entrena objeciones y calificación.
    """
) / 100

close_rate = st.sidebar.slider(
    "💰 Tasa de Cierre (%)",
    min_value=10.0, max_value=50.0, value=25.0, step=5.0,
    help="""
    🎯 **¿Qué es?** % de reuniones que se convierten en venta.
    
    🏆 **La métrica reina:** Un 5% más aquí vale millones.
    
    📊 **Benchmark:** 20-30% es estándar, 40%+ es élite.
    
    💡 **Para mejorar:** Role-plays diarios y coaching 1:1.
    """
) / 100

st.sidebar.markdown("---")

# SECCIÓN 4: ESTRUCTURA DE COMPENSACIÓN
st.sidebar.subheader("💵 4. Estructura de Compensación")

st.sidebar.markdown("#### 💼 Compensación de Closers")

closer_base_pct = st.sidebar.slider(
    "% de Compensación Base para Closers",
    min_value=15.0, max_value=30.0, value=20.0, step=1.0,
    help="""
    🎯 **¿Qué es?** % del ingreso total que va a closers.
    
    📊 **Estándar industria:** 15-25%
    
    ⬆️ **Subir si:** Quieres atraer mejor talento
    ⬇️ **Bajar si:** Márgenes están muy apretados
    
    ⚖️ **Balance:** Muy alto = sin margen, muy bajo = sin motivación
    """
) / 100

# Multiplicadores simplificados
st.sidebar.markdown("##### 🎯 Multiplicadores por Attainment")
attainment_mult = {
    "0-40%": 0.6,
    "40-70%": 0.8,
    "70-100%": 1.0,
    "100-150%": 1.2,
    "150%+": 1.6
}

st.sidebar.markdown("#### 📞 Compensación de Setters")

setter_of_closer_pct = st.sidebar.slider(
    "% del Pago del Closer para Setter",
    min_value=10.0, max_value=30.0, value=15.0, step=1.0,
    help="""
    🎯 **¿Qué es?** El setter gana este % de lo que gana el closer.
    
    🤝 **Alineación:** Los conecta al éxito del closer.
    
    📊 **Estándar:** 10-20% es común
    
    💡 **Pro tip:** Súbelo si tienes problemas de calidad en agendamiento.
    """
) / 100

speed_bonus = st.sidebar.slider(
    "⚡ Bono Velocidad (%)",
    min_value=0.0, max_value=20.0, value=10.0, step=2.5,
    help="""
    🎯 **Trigger:** Contactar al lead en <15 minutos
    
    📈 **Impacto:** Puede doblar tu tasa de contacto
    
    💰 **ROI:** Cada contacto rápido vale 2-3x más
    
    🎮 **Gamification:** Crea competencia sana en el piso
    """
) / 100

followup_bonus = st.sidebar.slider(
    "🔄 Bono Seguimiento (%)",
    min_value=0.0, max_value=15.0, value=5.0, step=2.5,
    help="""
    🎯 **Trigger:** Hacer 2+ seguimientos antes de cerrar
    
    📊 **Dato:** 80% de ventas requieren 5+ toques
    
    💡 **Beneficio:** Reduce leads perdidos por falta de follow-up
    
    ⚠️ **Sin esto:** Pierdes 30%+ de oportunidades
    """
) / 100

st.sidebar.markdown("---")

# SECCIÓN 5: PRODUCTO OPTIMAXX PLUS
st.sidebar.subheader("🏦 5. Producto Optimaxx PLUS")

st.sidebar.markdown("#### 💳 Distribución de Primas Mensuales")
col1, col2 = st.sidebar.columns(2)

with col1:
    pm_2k_pct = st.number_input("% PM $2,000", 0, 100, 20, 5)
    pm_3k_pct = st.number_input("% PM $3,000", 0, 100, 50, 5)
    
with col2:
    pm_4k_pct = st.number_input("% PM $4,000", 0, 100, 20, 5)
    pm_5k_pct = st.number_input("% PM $5,000", 0, 100, 10, 5)

# Normalizar probabilidades
total_pm_pct = pm_2k_pct + pm_3k_pct + pm_4k_pct + pm_5k_pct
if total_pm_pct > 0:
    pm_probs = [pm_2k_pct/total_pm_pct, pm_3k_pct/total_pm_pct, 
                pm_4k_pct/total_pm_pct, pm_5k_pct/total_pm_pct]
else:
    pm_probs = [0.2, 0.5, 0.2, 0.1]

pm_values = [2000, 3000, 4000, 5000]
avg_pm = np.average(pm_values, weights=pm_probs)

persistencia_18m = st.sidebar.slider(
    "📈 Persistencia 18 meses (%)",
    min_value=70.0, max_value=95.0, value=90.0, step=5.0,
    help="""
    🎯 **¿Qué es?** % de clientes activos después de 18 meses.
    
    💰 **Impacto directo:** Afecta el 30% de tu ingreso (pago diferido).
    
    📊 **Benchmark:** <85% es preocupante, >90% es excelente.
    
    💡 **Para mejorar:** Mejor onboarding y customer success.
    """
) / 100

st.sidebar.info(f"""
**📊 Resumen de Prima:**
- Prima Promedio: ${avg_pm:,.0f} MXN
- Compensación Total: ${avg_pm * 8.1:,.0f} MXN
- Pago Inmediato: ${avg_pm * 8.1 * 0.7:,.0f} MXN
- Pago Diferido: ${avg_pm * 8.1 * 0.3:,.0f} MXN
""")

# =============== MAIN CONTENT - VISUALIZACIÓN ===============

# Crear configuración con todos los parámetros
config = OptimaxPlusConfig(
    LEADS_DAILY=daily_leads,
    CPL=cpl,
    CONTACT_RATE=contact_rate,
    MEETING_RATE=meeting_rate, 
    CLOSE_RATE=close_rate,
    PM_VALUES=pm_values,
    PM_PROBS=pm_probs,
    PERSIST_18=persistencia_18m,
    TEAM_SIZE=team_size,
    PCT_BENCH=bench_pct/100,
    BENCH_BASE=bench_base_salary,
    BENCH_PER_MEETING=bench_meeting_bonus,
    BENCH_TARGET_MEETINGS=bench_meetings_to_exit,
    PCT_CLOSER_POOL=closer_base_pct,
    SETTER_OF_CLOSER=setter_of_closer_pct,
    SETTER_SPEED_BONUS=speed_bonus,
    SETTER_FOLLOWUP_BONUS=followup_bonus,
    ATTAINMENT_BANDS=attainment_mult
)

calculator = OptimaxPlusCalculator(config)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Simulador de Compensación",
    "📊 Análisis del Funnel", 
    "🎯 What-If Scenarios",
    "📈 Plan de Acción"
])

with tab1:
    st.header("💰 Simulador Interactivo de Compensación")
    
    # Controles adicionales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_pm = st.selectbox(
            "Prima Mensual a Simular",
            options=pm_values,
            index=1,  # Default $3,000
            format_func=lambda x: f"${x:,} MXN"
        )
    
    with col2:
        sim_attainment = st.select_slider(
            "Nivel de Attainment",
            options=list(attainment_mult.keys()),
            value="70-100%"
        )
    
    with col3:
        sim_role = st.radio(
            "Rol a Analizar",
            ["Closer", "Setter", "Banca", "Todos"]
        )
    
    # Checkboxes para bonos de setter
    col1, col2 = st.columns(2)
    with col1:
        has_speed = st.checkbox("✅ Setter logró bono velocidad", value=True)
    with col2:
        has_followup = st.checkbox("✅ Setter logró bono seguimiento", value=True)
    
    # Calcular compensaciones
    sale = calculator.calculate_sale_value(sim_pm)
    dist_now = calculator.calculate_internal_distribution(
        sale['comp_now'],
        sim_attainment,
        has_speed,
        has_followup
    )
    dist_deferred = calculator.calculate_internal_distribution(
        sale['comp_deferred'],
        sim_attainment,
        has_speed,
        has_followup
    )
    
    # Mostrar resultados
    st.markdown("---")
    st.subheader(f"📊 Análisis de Compensación - Prima ${sim_pm:,} MXN")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💼 Closer Gana",
            f"${dist_now['closer_pay'] + dist_deferred['closer_pay']:,.0f}",
            f"Multiplicador: {attainment_mult[sim_attainment]}x"
        )
    
    with col2:
        st.metric(
            "📞 Setter Gana",
            f"${dist_now['setter_pay'] + dist_deferred['setter_pay']:,.0f}",
            f"Bonos: +{(speed_bonus + followup_bonus)*100:.0f}%"
        )
    
    with col3:
        st.metric(
            "🏢 Margen Corp",
            f"${dist_now['corp_margin'] + dist_deferred['corp_margin']:,.0f}",
            f"{(dist_now['corp_margin'] + dist_deferred['corp_margin'])/sale['comp_total']*100:.0f}%"
        )
    
    with col4:
        st.metric(
            "🏈 Banca Gana",
            f"${bench_base_salary + 10*bench_meeting_bonus:,.0f}",
            "Al lograr 10 reuniones"
        )

with tab2:
    st.header("📊 Análisis del Funnel de Ventas")
    
    funnel = calculator.simulate_monthly_funnel()
    ue = calculator.calculate_unit_economics()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📥 Leads/Mes", f"{funnel['leads_mo']:,.0f}")
    with col2:
        st.metric("💰 Ventas/Mes", f"{funnel['sales_mo']:.0f}")
    with col3:
        st.metric("🎯 CAC", f"${ue['cac']:,.0f}")
    with col4:
        st.metric("📈 LTV:CAC", f"{ue['ltv_cac_ratio']:.1f}:1")

with tab3:
    st.header("🎯 Escenarios What-If")
    
    st.info("🚀 Experimenta con los controles en el sidebar para ver cómo afectan tus métricas")
    
    # Comparación antes/después
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Configuración Actual")
        st.code(f"""
Equipo: {team_size} personas
- Banca: {bench_count}
- Setters: {setter_count}
- Closers: {closer_count}

Compensación:
- Closers: {closer_base_pct*100:.0f}%
- Setters: {setter_of_closer_pct*100:.0f}%
- Bonos: +{(speed_bonus+followup_bonus)*100:.0f}%

EBITDA Proyectado:
${ue['monthly_ebitda']:,.0f}/mes
${ue['monthly_ebitda']/30:,.0f}/día
        """)
    
    with col2:
        st.subheader("💡 Sugerencias")
        if ue['ltv_cac_ratio'] < 3:
            st.warning("⚠️ Tu LTV:CAC es bajo. Considera reducir compensaciones o mejorar persistencia.")
        if bench_pct > 25:
            st.error("❌ Demasiada gente en banca. Mejora entrenamiento o despide.")
        if ue['monthly_ebitda'] < 0:
            st.error("❌ EBITDA negativo. Reduce costos urgentemente.")

with tab4:
    st.header("📈 Plan de Acción Recomendado")
    
    st.markdown("""
    ### 🎯 Acciones Inmediatas (Esta Semana)
    
    1. **Si CAC > $1,500:** Implementa bono de velocidad al máximo
    2. **Si Persistencia < 85%:** Auditoría urgente de onboarding
    3. **Si Banca > 25%:** Plan de recuperación o despidos
    
    ### 📊 Acciones a 30 Días
    
    1. Optimizar estructura de compensación basado en simulaciones
    2. Implementar tracking detallado por vendedor
    3. Ajustar quotas basado en capacidad real
    
    ### 🚀 Acciones a 90 Días
    
    1. Escalar equipo si LTV:CAC > 4:1
    2. Implementar automatizaciones para reducir CAC
    3. Expandir a nuevos productos/mercados
    """)
