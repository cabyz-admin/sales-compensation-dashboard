"""
Integración del Proceso de Ventas con Compensación
Visualización completa del flujo de ventas y su impacto en compensaciones
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_sales_process_view(config, calculator):
    """
    Crea una vista integrada del proceso de ventas con compensaciones
    """
    st.header("🔄 Proceso de Ventas Integrado con Compensación")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Flujo Completo", 
        "💰 Simulador de Compensación",
        "🎯 Escenarios What-If", 
        "📈 Optimización"
    ])
    
    with tab1:
        st.subheader("Flujo de Ventas End-to-End")
        
        # Crear visualización del embudo
        stages = [
            "🔍 Descubrimiento\n(Impressions/Leads)",
            "📚 Aprendizaje\n(MCL→MQL)",
            "⚖️ Evaluación\n(MQL→SAL→SQL)",
            "💼 Venta\n(SQL→Closed)",
            "🚀 Implementación\n(Onboarding)",
            "📊 Impacto\n(Retention)",
            "📈 Crecimiento\n(NRR)",
            "🎯 Expansión\n(Upsell)"
        ]
        
        # Calcular métricas para cada etapa
        funnel = calculator.simulate_monthly_funnel()
        
        # Datos del embudo
        funnel_data = [
            funnel['leads_mo'],  # Descubrimiento
            funnel['leads_mo'] * 0.5,  # MCL (50% de leads)
            funnel['contacts_mo'],  # Evaluación
            funnel['meetings_mo'],  # SAL/SQL
            funnel['sales_mo'],  # Venta
            funnel['sales_mo'] * 0.9,  # Implementación (90% success)
            funnel['sales_mo'] * 0.9 * config.PERSIST_18,  # Retention
            funnel['sales_mo'] * 0.9 * config.PERSIST_18 * 1.2  # Expansion
        ]
        
        # Crear gráfico de embudo
        fig = go.Figure(go.Funnel(
            y=stages,
            x=funnel_data,
            textposition="inside",
            textinfo="value+percent previous",
            opacity=0.65,
            marker={"color": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", 
                             "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]},
            connector={"line": {"color": "royalblue", "dash": "dot", "width": 3}}
        ))
        
        fig.update_layout(
            title="Embudo de Ventas Completo (Modelo Bowtie)",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas clave por etapa
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Leads → Ventas", f"{funnel['sales_mo']/funnel['leads_mo']*100:.2f}%")
        with col2:
            st.metric("Ventas/Mes", f"{funnel['sales_mo']:.0f}")
        with col3:
            st.metric("Persistencia 18m", f"{config.PERSIST_18:.0%}")
        with col4:
            st.metric("NRR Potencial", "120%")
    
    with tab2:
        st.subheader("💰 Simulador de Compensación por Rol")
        
        # Selector de escenario de venta
        col1, col2 = st.columns(2)
        
        with col1:
            pm_simulada = st.selectbox(
                "Prima Mensual a Simular",
                options=[2000, 3000, 4000, 5000],
                index=1  # Default 3000
            )
            
            attainment = st.select_slider(
                "Nivel de Attainment del Closer",
                options=["0-40%", "40-70%", "70-100%", "100-150%", "150%+"],
                value="70-100%"
            )
        
        with col2:
            tiene_speed = st.checkbox("Setter: Bono Velocidad (+10%)", value=True)
            tiene_followup = st.checkbox("Setter: Bono Seguimiento (+5%)", value=True)
        
        # Calcular compensaciones
        sale = calculator.calculate_sale_value(pm_simulada)
        dist_now = calculator.calculate_internal_distribution(
            sale['comp_now'], 
            attainment, 
            tiene_speed, 
            tiene_followup
        )
        dist_deferred = calculator.calculate_internal_distribution(
            sale['comp_deferred'], 
            attainment, 
            tiene_speed, 
            tiene_followup
        )
        
        # Mostrar resultados
        st.markdown("### 📊 Desglose de Compensación")
        
        # Tabla de compensaciones
        comp_data = {
            "Concepto": [
                "Compensación Total del Carrier",
                "├─ Pago Inmediato (70%)",
                "├─ Pago Diferido (30%)",
                "└─ Total Esperado",
                "",
                "Distribución Pago Inmediato",
                "├─ Closer",
                "├─ Setter",
                "└─ Margen Corporación",
                "",
                "Distribución Pago Diferido",
                "├─ Closer",
                "├─ Setter",
                "└─ Margen Corporación",
                "",
                "TOTALES POR ROL",
                "├─ Closer Total",
                "├─ Setter Total",
                "└─ Corporación Total"
            ],
            "Monto": [
                f"${sale['comp_total']:,.0f}",
                f"${sale['comp_now']:,.0f}",
                f"${sale['comp_deferred']:,.0f}",
                f"${sale['ltv_expected']:,.0f}",
                "",
                "",
                f"${dist_now['closer_pay']:,.0f}",
                f"${dist_now['setter_pay']:,.0f}",
                f"${dist_now['corp_margin']:,.0f}",
                "",
                "",
                f"${dist_deferred['closer_pay']:,.0f}",
                f"${dist_deferred['setter_pay']:,.0f}",
                f"${dist_deferred['corp_margin']:,.0f}",
                "",
                "",
                f"${dist_now['closer_pay'] + dist_deferred['closer_pay']:,.0f}",
                f"${dist_now['setter_pay'] + dist_deferred['setter_pay']:,.0f}",
                f"${dist_now['corp_margin'] + dist_deferred['corp_margin']:,.0f}"
            ],
            "% del Total": [
                "100%",
                "70%",
                "30%",
                f"{sale['ltv_expected']/sale['comp_total']*100:.1f}%",
                "",
                "",
                f"{dist_now['closer_pay']/sale['comp_total']*100:.1f}%",
                f"{dist_now['setter_pay']/sale['comp_total']*100:.1f}%",
                f"{dist_now['corp_margin']/sale['comp_total']*100:.1f}%",
                "",
                "",
                f"{dist_deferred['closer_pay']/sale['comp_total']*100:.1f}%",
                f"{dist_deferred['setter_pay']/sale['comp_total']*100:.1f}%",
                f"{dist_deferred['corp_margin']/sale['comp_total']*100:.1f}%",
                "",
                "",
                f"{(dist_now['closer_pay'] + dist_deferred['closer_pay'])/sale['comp_total']*100:.1f}%",
                f"{(dist_now['setter_pay'] + dist_deferred['setter_pay'])/sale['comp_total']*100:.1f}%",
                f"{(dist_now['corp_margin'] + dist_deferred['corp_margin'])/sale['comp_total']*100:.1f}%"
            ]
        }
        
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True, height=600)
        
        # Gráfico de distribución
        fig_dist = go.Figure(data=[
            go.Bar(name='Closer', x=['Inmediato', 'Diferido'], 
                   y=[dist_now['closer_pay'], dist_deferred['closer_pay']]),
            go.Bar(name='Setter', x=['Inmediato', 'Diferido'], 
                   y=[dist_now['setter_pay'], dist_deferred['setter_pay']]),
            go.Bar(name='Corporación', x=['Inmediato', 'Diferido'], 
                   y=[dist_now['corp_margin'], dist_deferred['corp_margin']])
        ])
        
        fig_dist.update_layout(
            barmode='stack',
            title=f"Distribución de Compensación - PM ${pm_simulada:,}",
            yaxis_title="Monto ($)",
            height=400
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with tab3:
        st.subheader("🎯 Análisis What-If: Impacto de Cambios en Compensación")
        
        # Parámetros ajustables
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_closer_pct = st.slider(
                "% Compensación para Closers",
                min_value=15.0,
                max_value=30.0,
                value=20.0,
                step=0.5,
                help="Actualmente: 20%"
            ) / 100
        
        with col2:
            new_setter_pct = st.slider(
                "% del Closer para Setter",
                min_value=10.0,
                max_value=25.0,
                value=15.0,
                step=0.5,
                help="Actualmente: 15%"
            ) / 100
        
        with col3:
            new_persist = st.slider(
                "Persistencia 18 meses (%)",
                min_value=70.0,
                max_value=95.0,
                value=config.PERSIST_18 * 100,
                step=1.0
            ) / 100
        
        # Simular escenarios
        scenarios = []
        pm_values = [2000, 3000, 4000, 5000]
        volumes = [20, 50, 20, 10]  # Distribución de volumen
        
        for pm, vol_pct in zip(pm_values, volumes):
            sale = calculator.calculate_sale_value(pm)
            
            # Escenario actual
            current_closer = config.PCT_CLOSER_POOL * sale['comp_now']
            current_setter = config.SETTER_OF_CLOSER * current_closer * 1.15  # Con bonos
            current_margin = sale['comp_now'] - current_closer - current_setter
            
            # Escenario nuevo
            new_closer = new_closer_pct * sale['comp_now']
            new_setter = new_setter_pct * new_closer * 1.15
            new_margin = sale['comp_now'] - new_closer - new_setter
            
            scenarios.append({
                'PM': f"${pm:,}",
                'Volumen': f"{vol_pct}%",
                'Closer Actual': f"${current_closer:,.0f}",
                'Closer Nuevo': f"${new_closer:,.0f}",
                'Δ Closer': f"${new_closer - current_closer:+,.0f}",
                'Setter Actual': f"${current_setter:,.0f}",
                'Setter Nuevo': f"${new_setter:,.0f}",
                'Δ Setter': f"${new_setter - current_setter:+,.0f}",
                'Margen Actual': f"${current_margin:,.0f}",
                'Margen Nuevo': f"${new_margin:,.0f}",
                'Δ Margen': f"${new_margin - current_margin:+,.0f}"
            })
        
        df_scenarios = pd.DataFrame(scenarios)
        st.dataframe(df_scenarios, use_container_width=True)
        
        # Impacto mensual
        st.markdown("### 📊 Impacto Mensual Proyectado")
        
        monthly_sales = funnel['sales_mo']
        avg_pm = np.average(pm_values, weights=volumes)
        
        # Calcular impacto total
        current_monthly_comp = monthly_sales * avg_pm * 8.1 * 0.7  # Solo inmediato
        current_closers = current_monthly_comp * config.PCT_CLOSER_POOL
        current_setters = current_closers * config.SETTER_OF_CLOSER * 1.15
        current_corp = current_monthly_comp - current_closers - current_setters
        
        new_closers = current_monthly_comp * new_closer_pct
        new_setters = new_closers * new_setter_pct * 1.15
        new_corp = current_monthly_comp - new_closers - new_setters
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Costo Closers/Mes",
                f"${new_closers:,.0f}",
                f"${new_closers - current_closers:+,.0f}"
            )
        
        with col2:
            st.metric(
                "Costo Setters/Mes",
                f"${new_setters:,.0f}",
                f"${new_setters - current_setters:+,.0f}"
            )
        
        with col3:
            st.metric(
                "Margen Corp/Mes",
                f"${new_corp:,.0f}",
                f"${new_corp - current_corp:+,.0f}",
                delta_color="inverse"  # Rojo si baja
            )
    
    with tab4:
        st.subheader("📈 Optimización de Estructura de Compensación")
        
        st.markdown("""
        ### 🎯 Recomendaciones Basadas en Datos
        
        Basado en tu configuración actual y las simulaciones:
        """)
        
        # Calcular métricas de optimización
        ue = calculator.calculate_unit_economics()
        
        # Recomendaciones
        recommendations = []
        
        # Check LTV:CAC ratio
        if ue['ltv_cac_ratio'] < 3:
            recommendations.append({
                "Área": "⚠️ LTV:CAC Ratio",
                "Actual": f"{ue['ltv_cac_ratio']:.1f}:1",
                "Objetivo": "3:1",
                "Acción": "Reducir CAC o aumentar LTV",
                "Impacto": "Alto"
            })
        else:
            recommendations.append({
                "Área": "✅ LTV:CAC Ratio",
                "Actual": f"{ue['ltv_cac_ratio']:.1f}:1",
                "Objetivo": "3:1",
                "Acción": "Mantener o mejorar",
                "Impacto": "Bajo"
            })
        
        # Check persistencia
        if config.PERSIST_18 < 0.85:
            recommendations.append({
                "Área": "⚠️ Persistencia",
                "Actual": f"{config.PERSIST_18:.0%}",
                "Objetivo": "90%",
                "Acción": "Mejorar onboarding y soporte",
                "Impacto": "Alto"
            })
        
        # Check conversion rates
        if funnel['sales_mo'] / funnel['leads_mo'] < 0.02:
            recommendations.append({
                "Área": "⚠️ Conversión Total",
                "Actual": f"{funnel['sales_mo']/funnel['leads_mo']*100:.2f}%",
                "Objetivo": "2-3%",
                "Acción": "Optimizar proceso de ventas",
                "Impacto": "Medio"
            })
        
        # Check margen
        avg_sale = calculator.calculate_sale_value(3000)
        dist = calculator.calculate_internal_distribution(avg_sale['comp_now'])
        if dist['margin_rate'] < 0.50:
            recommendations.append({
                "Área": "⚠️ Margen Corporación",
                "Actual": f"{dist['margin_rate']:.0%}",
                "Objetivo": ">50%",
                "Acción": "Revisar estructura de compensación",
                "Impacto": "Alto"
            })
        
        df_recommendations = pd.DataFrame(recommendations)
        st.dataframe(df_recommendations, use_container_width=True)
        
        # Simulación de optimización
        st.markdown("### 🚀 Escenario Optimizado")
        
        # Calcular escenario optimizado
        optimal_leads = funnel['leads_mo'] * 1.2  # +20% leads
        optimal_contact = config.CONTACT_RATE * 1.1  # +10% contact rate
        optimal_close = config.CLOSE_RATE * 1.15  # +15% close rate
        optimal_persist = 0.90  # Target 90%
        
        optimal_sales = optimal_leads * optimal_contact * config.MEETING_RATE * optimal_close
        optimal_revenue = optimal_sales * avg_pm * 8.1 * 0.7
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Ventas Optimizadas",
                f"{optimal_sales:.0f}/mes",
                f"+{optimal_sales - funnel['sales_mo']:.0f}"
            )
        
        with col2:
            st.metric(
                "Ingresos Optimizados",
                f"${optimal_revenue:,.0f}",
                f"+${optimal_revenue - (funnel['sales_mo'] * avg_pm * 8.1 * 0.7):,.0f}"
            )
        
        with col3:
            new_cac = (funnel['leads_mo'] * 1.2 * config.CPL + ue['monthly_costs']) / optimal_sales
            st.metric(
                "Nuevo CAC",
                f"${new_cac:,.0f}",
                f"${new_cac - ue['cac']:+,.0f}"
            )
        
        with col4:
            new_ltv_cac = ue['ltv'] / new_cac
            st.metric(
                "Nuevo LTV:CAC",
                f"{new_ltv_cac:.1f}:1",
                f"+{new_ltv_cac - ue['ltv_cac_ratio']:.1f}"
            )
        
        # Plan de acción
        st.markdown("""
        ### 📋 Plan de Acción Sugerido
        
        1. **Corto Plazo (1-2 meses)**
           - Implementar bonos por velocidad de respuesta
           - Mejorar tracking de persistencia
           - Ajustar targets por nivel de attainment
        
        2. **Mediano Plazo (3-6 meses)**
           - Optimizar proceso de onboarding
           - Implementar sistema de bench efectivo
           - Revisar estructura de compensación diferida
        
        3. **Largo Plazo (6-12 meses)**
           - Escalar equipo basado en métricas optimizadas
           - Implementar expansión/upsell sistemático
           - Alcanzar ratio LTV:CAC de 4:1+
        """)

# Función para integrar en el dashboard principal
def add_sales_process_integration(config, calculator):
    """
    Agrega la vista de integración al dashboard principal
    """
    create_sales_process_view(config, calculator)
