"""
Módulo de Ingeniería Inversa Avanzada
Basado en análisis de mejores prácticas de compensación
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ReverseEngineeringCalculator:
    """Calculadora para diferentes escenarios de ingeniería inversa"""
    
    def __init__(self):
        self.scenarios = {
            'quota': 'Calcular Quota Individual',
            'headcount': 'Calcular Headcount Necesario',
            'activity': 'Calcular Actividades Requeridas',
            'compensation': 'Calcular Estructura de Comp Óptima',
            'territory': 'Calcular Territorios',
            'ramp': 'Calcular Plan de Ramp',
            'pipeline': 'Calcular Pipeline Coverage',
            'capacity': 'Calcular Capacity Planning'
        }
    
    def reverse_quota(self, revenue_target, num_reps, attainment_expected=0.9):
        """
        Dado un objetivo de revenue, calcular la quota por rep
        """
        total_quota_needed = revenue_target / attainment_expected
        quota_per_rep = total_quota_needed / num_reps
        
        return {
            'quota_per_rep': quota_per_rep,
            'quota_monthly': quota_per_rep / 12,
            'quota_quarterly': quota_per_rep / 4,
            'total_quota': total_quota_needed,
            'expected_achievement': revenue_target
        }
    
    def reverse_headcount(self, revenue_target, avg_quota_per_rep, productivity_ramp):
        """
        Dado un objetivo de revenue, calcular cuántos reps necesitas
        considerando ramp time
        """
        # Ajustar por productividad durante ramp
        effective_quota = avg_quota_per_rep * productivity_ramp
        headcount_needed = revenue_target / effective_quota
        
        # Considerar attrition (15% típico)
        attrition_rate = 0.15
        headcount_with_buffer = headcount_needed * (1 + attrition_rate)
        
        return {
            'headcount_base': int(np.ceil(headcount_needed)),
            'headcount_with_attrition': int(np.ceil(headcount_with_buffer)),
            'hiring_per_quarter': int(np.ceil(headcount_with_buffer / 4)),
            'effective_capacity': effective_quota * headcount_needed
        }
    
    def reverse_activity(self, sales_target, conversion_rates, avg_deal_size):
        """
        Dado un objetivo de ventas, calcular actividades diarias necesarias
        """
        # Trabajar hacia atrás desde sales
        deals_needed = sales_target / avg_deal_size
        
        # Calcular hacia atrás por el funnel
        meetings_needed = deals_needed / conversion_rates['close_rate']
        qualified_leads_needed = meetings_needed / conversion_rates['meeting_to_opp']
        leads_needed = qualified_leads_needed / conversion_rates['lead_to_qualified']
        calls_needed = leads_needed / conversion_rates['call_to_lead']
        
        # Convertir a métricas diarias (asumiendo 20 días laborales/mes)
        working_days = 20
        
        return {
            'daily_calls': int(np.ceil(calls_needed / working_days)),
            'daily_emails': int(np.ceil(calls_needed * 2 / working_days)),  # 2:1 email to call
            'daily_leads': int(np.ceil(leads_needed / working_days)),
            'weekly_meetings': int(np.ceil(meetings_needed / 4)),
            'monthly_deals': int(np.ceil(deals_needed)),
            'total_activities': int(np.ceil((calls_needed + calls_needed * 2) / working_days))
        }
    
    def reverse_compensation_structure(self, total_comp_budget, num_reps, market_ote):
        """
        Dado un presupuesto de compensación, calcular estructura óptima
        """
        budget_per_rep = total_comp_budget / num_reps
        
        # Estructura típica: 50/50 o 60/40 base/variable
        if budget_per_rep < market_ote * 0.8:
            # Presupuesto bajo: más variable
            base_salary_pct = 0.4
            variable_pct = 0.6
            message = "⚠️ Presupuesto bajo: Estructura agresiva 40/60"
        elif budget_per_rep > market_ote * 1.2:
            # Presupuesto alto: más base
            base_salary_pct = 0.6
            variable_pct = 0.4
            message = "✅ Presupuesto alto: Estructura conservadora 60/40"
        else:
            # Presupuesto normal
            base_salary_pct = 0.5
            variable_pct = 0.5
            message = "✅ Presupuesto estándar: Estructura balanceada 50/50"
        
        base_salary = budget_per_rep * base_salary_pct
        variable_comp = budget_per_rep * variable_pct
        
        # Calcular acceleradores
        accelerators = {
            '0-50%': 0.5,
            '50-75%': 0.75,
            '75-100%': 1.0,
            '100-125%': 1.5,
            '125-150%': 2.0,
            '150%+': 2.5
        }
        
        return {
            'base_salary': base_salary,
            'variable_target': variable_comp,
            'ote': budget_per_rep,
            'base_pct': base_salary_pct * 100,
            'variable_pct': variable_pct * 100,
            'accelerators': accelerators,
            'message': message,
            'cost_at_100_attainment': budget_per_rep,
            'cost_at_120_attainment': base_salary + (variable_comp * 1.5)
        }
    
    def reverse_pipeline_coverage(self, revenue_target, close_rate, sales_cycle_days):
        """
        Calcular pipeline necesario para hit revenue target
        """
        # Coverage típico: 3x-4x del target
        coverage_multiplier = 3.5
        
        pipeline_needed = revenue_target * coverage_multiplier
        opportunities_needed = pipeline_needed / (revenue_target / (revenue_target * close_rate))
        
        # Calcular por stage
        stage_multiples = {
            'Discovery': 5.0,
            'Qualification': 4.0,
            'Proposal': 2.5,
            'Negotiation': 1.5,
            'Closing': 1.1
        }
        
        pipeline_by_stage = {}
        for stage, multiple in stage_multiples.items():
            pipeline_by_stage[stage] = revenue_target * multiple
        
        return {
            'total_pipeline_needed': pipeline_needed,
            'coverage_ratio': coverage_multiplier,
            'opportunities_needed': int(opportunities_needed),
            'pipeline_by_stage': pipeline_by_stage,
            'monthly_pipeline_creation': pipeline_needed / 3,  # Para Q pipeline
            'weekly_pipeline_target': pipeline_needed / 12  # Weekly target
        }
    
    def reverse_ramp_plan(self, full_productivity_target, ramp_months=6):
        """
        Crear plan de ramp para nuevos reps
        """
        # Curva de productividad típica
        ramp_curve = {
            1: 0.25,  # Month 1: 25% productivity
            2: 0.40,  # Month 2: 40%
            3: 0.60,  # Month 3: 60%
            4: 0.75,  # Month 4: 75%
            5: 0.85,  # Month 5: 85%
            6: 1.00   # Month 6+: 100%
        }
        
        # Calcular quotas escalonadas
        monthly_targets = {}
        cumulative_target = 0
        
        for month, productivity in ramp_curve.items():
            monthly_target = full_productivity_target * productivity
            monthly_targets[f'Month {month}'] = monthly_target
            cumulative_target += monthly_target
        
        # Calcular draw/garantía necesaria
        full_ote = full_productivity_target * 0.2  # Asumiendo 20% commission rate
        draw_schedule = {}
        
        for month, productivity in ramp_curve.items():
            expected_earnings = full_ote * productivity
            guarantee = full_ote * 0.7  # 70% guarantee durante ramp
            draw_schedule[f'Month {month}'] = max(guarantee - expected_earnings, 0)
        
        return {
            'ramp_curve': ramp_curve,
            'monthly_targets': monthly_targets,
            'cumulative_target_6m': cumulative_target,
            'draw_schedule': draw_schedule,
            'total_draw_cost': sum(draw_schedule.values()),
            'breakeven_month': next((m for m, p in ramp_curve.items() if p >= 0.8), 6)
        }
    
    def reverse_territory_planning(self, total_tam, target_market_share, rep_capacity):
        """
        Planear territorios basado en TAM y capacidad
        """
        addressable_market = total_tam * target_market_share
        territories_needed = addressable_market / rep_capacity
        
        # Distribución por tier
        territory_tiers = {
            'Tier 1 (Enterprise)': {
                'count': int(territories_needed * 0.2),
                'tam_per_territory': rep_capacity * 1.5,
                'reps_per_territory': 2
            },
            'Tier 2 (Mid-Market)': {
                'count': int(territories_needed * 0.5),
                'tam_per_territory': rep_capacity * 1.0,
                'reps_per_territory': 1
            },
            'Tier 3 (SMB)': {
                'count': int(territories_needed * 0.3),
                'tam_per_territory': rep_capacity * 0.7,
                'reps_per_territory': 0.5
            }
        }
        
        total_reps_needed = sum(
            tier['count'] * tier['reps_per_territory'] 
            for tier in territory_tiers.values()
        )
        
        return {
            'territories_needed': int(np.ceil(territories_needed)),
            'addressable_market': addressable_market,
            'territory_tiers': territory_tiers,
            'total_reps_needed': int(np.ceil(total_reps_needed)),
            'avg_territory_value': addressable_market / territories_needed,
            'coverage_pct': (target_market_share * 100)
        }
    
    def reverse_spiff_structure(self, behavior_target, budget, num_reps):
        """
        Diseñar estructura de SPIFFs para incentivar comportamientos específicos
        """
        budget_per_rep = budget / num_reps
        
        # Tipos de SPIFFs comunes
        spiff_types = {
            'new_logo': {
                'amount': budget_per_rep * 0.3,
                'trigger': 'Primera venta a cuenta nueva',
                'frequency': 'Por deal'
            },
            'multi_year': {
                'amount': budget_per_rep * 0.25,
                'trigger': 'Contratos 2+ años',
                'frequency': 'Por deal'
            },
            'fast_close': {
                'amount': budget_per_rep * 0.2,
                'trigger': 'Cierre en <30 días',
                'frequency': 'Por deal'
            },
            'upsell': {
                'amount': budget_per_rep * 0.15,
                'trigger': 'Upsell >20% del contrato',
                'frequency': 'Por deal'
            },
            'reference': {
                'amount': budget_per_rep * 0.1,
                'trigger': 'Cliente acepta ser referencia',
                'frequency': 'Por cliente'
            }
        }
        
        # Calcular impacto esperado
        expected_impact = {
            'new_logo_increase': '15-20%',
            'deal_velocity': '+25% más rápido',
            'contract_length': '+6 meses promedio',
            'upsell_rate': '+10 puntos porcentuales'
        }
        
        return {
            'spiff_structure': spiff_types,
            'monthly_budget_per_rep': budget_per_rep,
            'annual_spiff_budget': budget,
            'expected_impact': expected_impact,
            'roi_expected': 2.5  # Típicamente 2.5x ROI en SPIFFs bien diseñados
        }


def add_reverse_engineering_tab(st_container):
    """
    Añade una pestaña de ingeniería inversa al dashboard principal
    """
    calculator = ReverseEngineeringCalculator()
    
    st.header("🔄 Ingeniería Inversa Avanzada")
    st.markdown("**Calcula hacia atrás desde tus objetivos de negocio**")
    
    # Selector de escenario
    scenario = st.selectbox(
        "Selecciona el tipo de cálculo inverso",
        options=list(calculator.scenarios.keys()),
        format_func=lambda x: calculator.scenarios[x]
    )
    
    st.markdown("---")
    
    if scenario == 'quota':
        st.subheader("🎯 Calculadora de Quota Individual")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            revenue_target = st.number_input(
                "Revenue Target Anual ($)", 
                min_value=100000, 
                max_value=100000000, 
                value=10000000,
                step=100000
            )
        with col2:
            num_reps = st.number_input(
                "Número de Reps",
                min_value=1,
                max_value=100,
                value=10
            )
        with col3:
            attainment = st.slider(
                "Attainment Esperado (%)",
                min_value=70,
                max_value=110,
                value=90
            ) / 100
        
        result = calculator.reverse_quota(revenue_target, num_reps, attainment)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Quota Anual/Rep", f"${result['quota_per_rep']:,.0f}")
        with col2:
            st.metric("Quota Mensual", f"${result['quota_monthly']:,.0f}")
        with col3:
            st.metric("Quota Trimestral", f"${result['quota_quarterly']:,.0f}")
        with col4:
            st.metric("Revenue Esperado", f"${result['expected_achievement']:,.0f}")
    
    elif scenario == 'headcount':
        st.subheader("👥 Calculadora de Headcount")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            revenue_target = st.number_input(
                "Revenue Target ($)",
                min_value=100000,
                max_value=100000000,
                value=10000000,
                step=100000
            )
        with col2:
            avg_quota = st.number_input(
                "Quota Promedio/Rep ($)",
                min_value=100000,
                max_value=5000000,
                value=1000000,
                step=50000
            )
        with col3:
            productivity = st.slider(
                "Productividad Promedio (%)",
                min_value=60,
                max_value=100,
                value=85
            ) / 100
        
        result = calculator.reverse_headcount(revenue_target, avg_quota, productivity)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Headcount Base", result['headcount_base'])
        with col2:
            st.metric("Con Buffer Attrition", result['headcount_with_attrition'])
        with col3:
            st.metric("Hiring/Quarter", result['hiring_per_quarter'])
        with col4:
            st.metric("Capacidad Efectiva", f"${result['effective_capacity']:,.0f}")
        
        # Mostrar plan de hiring
        st.subheader("📅 Plan de Contratación")
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        hiring_data = pd.DataFrame({
            'Quarter': quarters,
            'New Hires': [result['hiring_per_quarter']] * 4,
            'Cumulative': [result['hiring_per_quarter'] * (i+1) for i in range(4)],
            'Productive Capacity': [result['hiring_per_quarter'] * (i+1) * productivity * avg_quota for i in range(4)]
        })
        st.dataframe(hiring_data.style.format({
            'Productive Capacity': '${:,.0f}'
        }))
    
    elif scenario == 'activity':
        st.subheader("📊 Calculadora de Actividades")
        
        col1, col2 = st.columns(2)
        with col1:
            sales_target = st.number_input(
                "Target de Ventas Mensual ($)",
                min_value=10000,
                max_value=10000000,
                value=500000,
                step=10000
            )
            avg_deal = st.number_input(
                "Deal Size Promedio ($)",
                min_value=1000,
                max_value=100000,
                value=15000,
                step=1000
            )
        
        with col2:
            st.markdown("**Tasas de Conversión**")
            call_to_lead = st.slider("Call → Lead (%)", 5, 30, 15) / 100
            lead_to_qualified = st.slider("Lead → Qualified (%)", 20, 60, 40) / 100
            meeting_to_opp = st.slider("Meeting → Opp (%)", 30, 70, 50) / 100
            close_rate = st.slider("Opp → Close (%)", 15, 40, 25) / 100
        
        conversions = {
            'call_to_lead': call_to_lead,
            'lead_to_qualified': lead_to_qualified,
            'meeting_to_opp': meeting_to_opp,
            'close_rate': close_rate
        }
        
        result = calculator.reverse_activity(sales_target, conversions, avg_deal)
        
        # Mostrar métricas de actividad
        st.subheader("🎯 Actividades Diarias Requeridas")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Llamadas/Día", result['daily_calls'])
        with col2:
            st.metric("Emails/Día", result['daily_emails'])
        with col3:
            st.metric("Leads/Día", result['daily_leads'])
        with col4:
            st.metric("Meetings/Semana", result['weekly_meetings'])
        with col5:
            st.metric("Deals/Mes", result['monthly_deals'])
        with col6:
            st.metric("Total Act/Día", result['total_activities'])
        
        # Visualización del funnel
        fig = go.Figure(go.Funnel(
            y=['Calls', 'Leads', 'Qualified', 'Meetings', 'Opportunities', 'Closed'],
            x=[
                result['daily_calls'] * 20,  # Monthly
                result['daily_leads'] * 20,
                result['daily_leads'] * 20 * lead_to_qualified,
                result['weekly_meetings'] * 4,
                result['weekly_meetings'] * 4 * meeting_to_opp,
                result['monthly_deals']
            ],
            textposition="inside",
            textinfo="value+percent previous"
        ))
        fig.update_layout(title="Funnel de Actividades Mensual", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif scenario == 'compensation':
        st.subheader("💰 Calculadora de Estructura de Compensación")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            comp_budget = st.number_input(
                "Presupuesto Total Comp ($)",
                min_value=100000,
                max_value=10000000,
                value=1000000,
                step=50000
            )
        with col2:
            num_reps = st.number_input(
                "Número de Reps",
                min_value=1,
                max_value=100,
                value=10
            )
        with col3:
            market_ote = st.number_input(
                "OTE de Mercado ($)",
                min_value=50000,
                max_value=500000,
                value=120000,
                step=5000
            )
        
        result = calculator.reverse_compensation_structure(comp_budget, num_reps, market_ote)
        
        # Mostrar estructura
        st.info(result['message'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Base Salary", f"${result['base_salary']:,.0f}")
        with col2:
            st.metric("Variable Target", f"${result['variable_target']:,.0f}")
        with col3:
            st.metric("OTE", f"${result['ote']:,.0f}")
        with col4:
            st.metric("Mix", f"{result['base_pct']:.0f}/{result['variable_pct']:.0f}")
        
        # Tabla de acceleradores
        st.subheader("🚀 Estructura de Aceleradores")
        accel_df = pd.DataFrame({
            'Attainment': list(result['accelerators'].keys()),
            'Multiplicador': list(result['accelerators'].values()),
            'Pago Variable': [result['variable_target'] * m for m in result['accelerators'].values()],
            'Comp Total': [result['base_salary'] + result['variable_target'] * m for m in result['accelerators'].values()]
        })
        st.dataframe(accel_df.style.format({
            'Multiplicador': '{:.1f}x',
            'Pago Variable': '${:,.0f}',
            'Comp Total': '${:,.0f}'
        }))
    
    elif scenario == 'pipeline':
        st.subheader("📈 Calculadora de Pipeline Coverage")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            revenue_target = st.number_input(
                "Revenue Target Trimestral ($)",
                min_value=100000,
                max_value=50000000,
                value=2500000,
                step=100000
            )
        with col2:
            close_rate = st.slider(
                "Close Rate (%)",
                min_value=10,
                max_value=40,
                value=25
            ) / 100
        with col3:
            cycle_days = st.number_input(
                "Sales Cycle (días)",
                min_value=30,
                max_value=365,
                value=90
            )
        
        result = calculator.reverse_pipeline_coverage(revenue_target, close_rate, cycle_days)
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pipeline Total Necesario", f"${result['total_pipeline_needed']:,.0f}")
        with col2:
            st.metric("Coverage Ratio", f"{result['coverage_ratio']:.1f}x")
        with col3:
            st.metric("# Oportunidades", result['opportunities_needed'])
        
        # Pipeline por stage
        st.subheader("Pipeline por Etapa")
        stages_df = pd.DataFrame({
            'Stage': list(result['pipeline_by_stage'].keys()),
            'Pipeline Requerido': list(result['pipeline_by_stage'].values()),
            'Multiple': [v/revenue_target for v in result['pipeline_by_stage'].values()]
        })
        
        fig = go.Figure(go.Bar(
            x=stages_df['Stage'],
            y=stages_df['Pipeline Requerido'],
            text=stages_df['Multiple'].apply(lambda x: f'{x:.1f}x'),
            textposition='auto'
        ))
        fig.update_layout(title="Pipeline Requerido por Stage", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif scenario == 'ramp':
        st.subheader("📈 Calculadora de Plan de Ramp")
        
        col1, col2 = st.columns(2)
        with col1:
            full_quota = st.number_input(
                "Quota Full Productivity ($)",
                min_value=100000,
                max_value=5000000,
                value=1000000,
                step=50000
            )
        with col2:
            ramp_months = st.slider(
                "Meses de Ramp",
                min_value=3,
                max_value=12,
                value=6
            )
        
        result = calculator.reverse_ramp_plan(full_quota, ramp_months)
        
        # Métricas clave
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Target 6 Meses", f"${result['cumulative_target_6m']:,.0f}")
        with col2:
            st.metric("Draw Total", f"${result['total_draw_cost']:,.0f}")
        with col3:
            st.metric("Breakeven", f"Mes {result['breakeven_month']}")
        
        # Curva de ramp
        ramp_df = pd.DataFrame({
            'Mes': list(result['ramp_curve'].keys()),
            'Productividad (%)': [p*100 for p in result['ramp_curve'].values()],
            'Quota': list(result['monthly_targets'].values()),
            'Draw': list(result['draw_schedule'].values())
        })
        
        # Gráfico de doble eje
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(name='Quota Mensual', x=ramp_df['Mes'], y=ramp_df['Quota']),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(name='Productividad %', x=ramp_df['Mes'], y=ramp_df['Productividad (%)'], mode='lines+markers'),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Mes")
        fig.update_yaxes(title_text="Quota ($)", secondary_y=False)
        fig.update_yaxes(title_text="Productividad (%)", secondary_y=True)
        fig.update_layout(title="Plan de Ramp", height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif scenario == 'territory':
        st.subheader("🗺️ Calculadora de Territorios")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_tam = st.number_input(
                "TAM Total ($)",
                min_value=1000000,
                max_value=1000000000,
                value=100000000,
                step=1000000
            )
        with col2:
            market_share = st.slider(
                "Target Market Share (%)",
                min_value=1,
                max_value=30,
                value=5
            ) / 100
        with col3:
            rep_capacity = st.number_input(
                "Capacidad por Rep ($)",
                min_value=500000,
                max_value=10000000,
                value=2000000,
                step=100000
            )
        
        result = calculator.reverse_territory_planning(total_tam, market_share, rep_capacity)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Territorios Totales", result['territories_needed'])
        with col2:
            st.metric("Reps Necesarios", result['total_reps_needed'])
        with col3:
            st.metric("Mercado Addressable", f"${result['addressable_market']/1000000:.1f}M")
        with col4:
            st.metric("Coverage", f"{result['coverage_pct']:.1f}%")
        
        # Distribución por tier
        st.subheader("Distribución por Tier")
        tiers_data = []
        for tier_name, tier_data in result['territory_tiers'].items():
            tiers_data.append({
                'Tier': tier_name,
                'Territorios': tier_data['count'],
                'TAM/Territorio': f"${tier_data['tam_per_territory']/1000000:.1f}M",
                'Reps/Territorio': tier_data['reps_per_territory'],
                'Reps Totales': tier_data['count'] * tier_data['reps_per_territory']
            })
        
        tiers_df = pd.DataFrame(tiers_data)
        st.dataframe(tiers_df)
    
    elif scenario == 'capacity':
        st.subheader("📅 Capacity Planning")
        st.info("🚧 En construcción - Próximamente: Planificación de capacidad con seasonality y ramp time")


# Función para integrar con el dashboard principal
def integrate_reverse_engineering(main_app):
    """
    Integra el módulo de ingeniería inversa con el dashboard principal
    """
    return add_reverse_engineering_tab
