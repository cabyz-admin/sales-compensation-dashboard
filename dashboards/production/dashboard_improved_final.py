"""
Improved Final Dashboard - All issues fixed
Deep integration, better inputs, proper math
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import json
import base64

# Import enhanced modules
try:
    from compensation_v2 import create_compensation_structure
except ImportError:
    create_compensation_structure = None

try:
    from business_performance_v2 import create_business_performance_dashboard
except ImportError:
    create_business_performance_dashboard = None

# Ensure project root and modules directory are on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARDS_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(DASHBOARDS_DIR)
MODULES_DIR = os.path.join(PROJECT_ROOT, "modules")

for path in [MODULES_DIR, PROJECT_ROOT, CURRENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import improved modules
try:
    from modules.calculations_improved import (
        ImprovedCostCalculator,
        ImprovedCompensationCalculator,
        ImprovedPnLCalculator,
        ImprovedReverseEngineering
    )
    from modules.calculations_enhanced import (
        EnhancedRevenueCalculator,
        BottleneckAnalyzer,
        HealthScoreCalculator
    )
    from modules.revenue_retention import (
        RevenueRetentionCalculator,
        MultiChannelGTM
    )
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.stop()

# Import Deal Economics Manager (single source of truth)
try:
    from deal_economics_manager import DealEconomicsManager, CommissionCalculator
except ImportError:
    st.error("⚠️ Could not import DealEconomicsManager. Please ensure deal_economics_manager.py is in the same directory.")
    st.stop()

# ============= TRANSLATION SYSTEM =============
TRANSLATIONS = {
    'en': {
        # Main titles
        'page_title': '🎯 Sales Compensation Model - Final Version',
        'language': 'Language',
        'model_summary': 'Model Summary',
        'revenue_target': 'Revenue Target',
        'revenue_targets': '🎯 Revenue Targets',
        'team_compensation_structure': '💵 Team & Compensation Structure',
        'team_configuration': '👥 Team Configuration',
        'compensation_configuration': '💵 Compensation Configuration',
        'deal_economics': '💰 Deal Economics & Payment Terms (Universal)',
        'operating_costs': '🏢 Operating Costs',
        'whatif_scenario': '🔮 What-If Scenario Analysis',
        'business_alerts': '🚨 Business Alerts',
        'gtm_command_center': '🎯 GTM Command Center',
        'configuration_center': '⚙️ Configuration Center',
        
        # Team labels
        'closers': 'Closers',
        'setters': 'Setters',
        'managers': 'Managers',
        'bench': 'Bench',
        'stakeholders': 'Stakeholders',
        'sales_team': 'Sales Team',
        'team_metrics': 'Team Metrics',
        
        # Metrics
        'total_team': 'Total Team',
        'active_ratio': 'Active Ratio',
        'capacity_analysis': 'Capacity Analysis',
        'monthly_base': 'Monthly Base',
        'monthly_ote': 'Monthly OTE',
        'annual_ote': 'Annual OTE',
        'expected_monthly': 'Expected Monthly',
        'monthly': 'Monthly',
        'annual': 'Annual',
        'daily': 'Daily',
        'weekly': 'Weekly',
        
        # Inputs
        'base_salary': 'Base Salary ($)',
        'variable_comp': 'Variable Comp ($)',
        'avg_deal_value': 'Average Deal Value ($)',
        'contract_length': 'Contract Length (months)',
        'upfront_payment_pct': 'Upfront Payment %',
        'deferred_payment_pct': 'Deferred Payment %',
        'input_period': 'Input Period',
        
        # Commission
        'commission_pct': 'Commission % of Revenue',
        'commission_flow': '💸 Commission Flow Visualization',
        'commission_base': 'Commission Base',
        'pay_commissions_from': 'Pay Commissions From',
        'upfront_cash_only': 'Upfront Cash Only',
        'full_deal_value': 'Full Deal Value',
        'total_commission': 'Total Commission',
        'commission_rate': 'Commission Rate',
        
        # Business types
        'business_type_template': 'Business Type Template',
        'custom': 'Custom',
        'insurance': 'Insurance',
        'saas': 'SaaS/Subscription',
        'consulting': 'Consulting/Services',
        'agency': 'Agency/Retainer',
        'one_time_sale': 'One-Time Sale',
        
        # Payment terms
        'deal_value': '💰 Deal Value',
        'payment_terms': '📅 Payment Terms (Modular)',
        'deal_breakdown': '📈 Deal Breakdown',
        'total_deal_value': 'Total Deal Value',
        'upfront_cash': 'Upfront Cash',
        'deferred_cash': 'Deferred Cash',
        
        # Common actions
        'configure': 'Configure',
        'calculate': 'Calculate',
        'view': 'View',
        'monthly_total': '📊 Monthly Total',
        'per_deal': '🎯 Per Deal (Unit Case)',
        
        # Capacity
        'capacity_settings': 'Capacity Settings',
        'meetings_per_closer_day': 'Meetings/Closer/Day',
        'working_days_month': 'Working Days/Month',
        'meetings_per_setter_day': 'Meetings Booked/Setter/Day',
        
        # Descriptions
        'configure_team': 'Configure team size, capacity, and compensation per role. Changes affect all calculations.',
        'universal_deal': 'Configure your deal structure - works for any business: SaaS, Services, Consulting, Insurance, etc.',
        'commission_policy': 'Commission Payment Policy: Choose whether commissions are paid from upfront cash (70%) or full deal value (100%)',
        
        # Alerts
        'all_systems_healthy': '✅ All Systems Healthy',
        'no_issues': 'No issues detected',
        'critical': 'CRITICAL',
        'warning': 'WARNING',
        'recommended_actions': '🎯 Recommended Actions',
        
        # Period earnings
        'period_earnings': '📅 Period-Based Earnings Preview',
        'role': 'Role',
        'count': 'Count',
        'vs_ote': 'vs OTE',
        
        # Compensation breakdown
        'compensation_breakdown': 'Compensation Breakdown',
        'total_ote': 'Total OTE',
        'base_pct': 'Base %',
        'variable_pct': 'Variable %',
        'team_cost_impact': 'Team Cost Impact',
        'team_count': 'Team Count',
        'monthly_base_cost': 'Monthly Base Cost',
        'monthly_ote_cost': 'Monthly OTE Cost',
        'annual_ote_cost': 'Annual OTE Cost',
        
        # Summary
        'total_compensation_summary': '📊 Total Compensation Summary',
        'stakeholder_annual': 'Stakeholder Annual',
        'stakeholder_share': 'Stakeholder Share',
        'ebitda_impact': '💰 EBITDA Impact',
        
        # Daily activities
        'daily_activities': '📊 Daily Activity Requirements (Visual)',
        'daily_activities_title': 'Daily Activities per Person by Role',
    },
    'es': {
        # Main titles
        'page_title': '🎯 Modelo de Compensación de Ventas - Versión Final',
        'language': 'Idioma',
        'model_summary': 'Resumen del Modelo',
        'revenue_target': 'Objetivo de Ingresos',
        'revenue_targets': '🎯 Objetivos de Ingresos',
        'team_compensation_structure': '💵 Estructura de Equipo y Compensación',
        'team_configuration': '👥 Configuración del Equipo',
        'compensation_configuration': '💵 Configuración de Compensación',
        'deal_economics': '💰 Economía del Negocio y Términos de Pago (Universal)',
        'operating_costs': '🏢 Costos Operativos',
        'whatif_scenario': '🔮 Análisis de Escenarios Hipotéticos',
        'business_alerts': '🚨 Alertas del Negocio',
        'gtm_command_center': '🎯 Centro de Comando GTM',
        'configuration_center': '⚙️ Centro de Configuración',
        
        # Team labels  
        'closers': 'Cerradores',
        'setters': 'Agendadores',
        'managers': 'Gerentes',
        'bench': 'Banca',
        'stakeholders': 'Accionistas',
        'sales_team': 'Equipo de Ventas',
        'team_metrics': 'Métricas del Equipo',
        
        # Metrics
        'total_team': 'Equipo Total',
        'active_ratio': 'Ratio Activo',
        'capacity_analysis': 'Análisis de Capacidad',
        'monthly_base': 'Base Mensual',
        'monthly_ote': 'OTE Mensual',
        'annual_ote': 'OTE Anual',
        'expected_monthly': 'Mensual Esperado',
        'monthly': 'Mensual',
        'annual': 'Anual',
        'daily': 'Diario',
        'weekly': 'Semanal',
        
        # Inputs
        'base_salary': 'Salario Base ($)',
        'variable_comp': 'Comp. Variable ($)',
        'avg_deal_value': 'Valor Promedio del Negocio ($)',
        'contract_length': 'Duración del Contrato (meses)',
        'upfront_payment_pct': 'Pago Inicial %',
        'deferred_payment_pct': 'Pago Diferido %',
        'input_period': 'Período de Entrada',
        
        # Commission
        'commission_pct': 'Comisión % de Ingresos',
        'commission_flow': '💸 Visualización de Flujo de Comisiones',
        'commission_base': 'Base de Comisión',
        'pay_commissions_from': 'Pagar Comisiones De',
        'upfront_cash_only': 'Solo Efectivo Inicial',
        'full_deal_value': 'Valor Total del Negocio',
        'total_commission': 'Comisión Total',
        'commission_rate': 'Tasa de Comisión',
        
        # Business types
        'business_type_template': 'Plantilla de Tipo de Negocio',
        'custom': 'Personalizado',
        'insurance': 'Seguros',
        'saas': 'SaaS/Suscripción',
        'consulting': 'Consultoría/Servicios',
        'agency': 'Agencia/Retainer',
        'one_time_sale': 'Venta Única',
        
        # Payment terms
        'deal_value': '💰 Valor del Negocio',
        'payment_terms': '📅 Términos de Pago (Modular)',
        'deal_breakdown': '📈 Desglose del Negocio',
        'total_deal_value': 'Valor Total del Negocio',
        'upfront_cash': 'Efectivo Inicial',
        'deferred_cash': 'Efectivo Diferido',
        
        # Common actions
        'configure': 'Configurar',
        'calculate': 'Calcular',
        'view': 'Ver',
        'monthly_total': '📊 Total Mensual',
        'per_deal': '🎯 Por Negocio (Caso Unitario)',
        
        # Capacity
        'capacity_settings': 'Configuración de Capacidad',
        'meetings_per_closer_day': 'Juntas/Cerrador/Día',
        'working_days_month': 'Días Laborables/Mes',
        'meetings_per_setter_day': 'Juntas Agendadas/Agendador/Día',
        
        # Descriptions
        'configure_team': 'Configure el tamaño del equipo, capacidad y compensación por rol. Los cambios afectan todos los cálculos.',
        'universal_deal': 'Configure su estructura de negocio - funciona para cualquier empresa: SaaS, Servicios, Consultoría, Seguros, etc.',
        'commission_policy': 'Política de Pago de Comisiones: Elija si las comisiones se pagan del efectivo inicial (70%) o del valor total del negocio (100%)',
        
        # Alerts
        'all_systems_healthy': '✅ Todos los Sistemas Saludables',
        'no_issues': 'No se detectaron problemas',
        'critical': 'CRÍTICO',
        'warning': 'ADVERTENCIA',
        'recommended_actions': '🎯 Acciones Recomendadas',
        
        # Period earnings
        'period_earnings': '📅 Vista Previa de Ganancias por Período',
        'role': 'Rol',
        'count': 'Cantidad',
        'vs_ote': 'vs OTE',
        
        # Compensation breakdown
        'compensation_breakdown': 'Desglose de Compensación',
        'total_ote': 'OTE Total',
        'base_pct': 'Base %',
        'variable_pct': 'Variable %',
        'team_cost_impact': 'Impacto de Costo del Equipo',
        'team_count': 'Cantidad de Equipo',
        'monthly_base_cost': 'Costo Base Mensual',
        'monthly_ote_cost': 'Costo OTE Mensual',
        'annual_ote_cost': 'Costo OTE Anual',
        
        # Summary
        'total_compensation_summary': '📊 Resumen Total de Compensación',
        'stakeholder_annual': 'Anual de Accionistas',
        'stakeholder_share': 'Participación de Accionistas',
        'ebitda_impact': '💰 Impacto en EBITDA',
        
        # Daily activities
        'daily_activities': '📊 Requisitos de Actividad Diaria (Visual)',
        'daily_activities_title': 'Actividades Diarias por Persona por Rol',
    }
}

def t(key, lang='en'):
    """Translation function - returns translated text based on selected language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# ============= CONFIGURACIÓN =============
st.set_page_config(
    page_title="🎯 Sales Compensation Model - Final Version",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stNumberInput > div > div > input {
        background-color: #f0f2f6;
    }
    .compensation-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        padding: 10px;
        background: #f0f2f6;
        border-radius: 10px;
    }
    .alert-box {
        padding: 25px 30px;
        border-radius: 15px;
        margin: 20px 0;
        border: 3px solid;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        font-size: 16px;
        font-weight: 600;
    }
    .alert-critical {
        background: linear-gradient(135deg, #ff5252 0%, #f44336 100%);
        border-color: #d32f2f;
        color: white;
        animation: pulse-critical 2s infinite;
    }
    .alert-warning {
        background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%);
        border-color: #f57c00;
        color: white;
        animation: pulse-warning 3s infinite;
    }
    .alert-success {
        background: linear-gradient(135deg, #66bb6a 0%, #4caf50 100%);
        border-color: #388e3c;
        color: white;
    }
    .alert-critical::before {
        content: '🚨';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
        animation: bounce 1s infinite;
    }
    .alert-warning::before {
        content: '⚠️';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
        animation: shake 2s infinite;
    }
    .alert-success::before {
        content: '✅';
        font-size: 24px;
        position: absolute;
        top: 15px;
        right: 20px;
    }
    @keyframes pulse-critical {
        0% { box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(244, 67, 54, 0.6); }
        100% { box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3); }
    }
    @keyframes pulse-warning {
        0% { box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3); }
        50% { box-shadow: 0 12px 35px rgba(255, 152, 0, 0.5); }
        100% { box-shadow: 0 8px 25px rgba(255, 152, 0, 0.3); }
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    .alert-title {
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .alert-message {
        font-size: 16px;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .alert-action {
        background: rgba(255,255,255,0.2);
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 4px solid rgba(255,255,255,0.5);
        font-size: 15px;
        font-weight: 700;
        margin-top: 15px;
    }
    .sensitivity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for dynamic values
st.session_state.setdefault('cost_input_type', 'CPL')
st.session_state.setdefault('compensation_mode', 'simple')
st.session_state.setdefault('reverse_target', None)
st.session_state.setdefault('theme_light', False)
st.session_state.setdefault('gtm_channels', [
    {
        'id': 'channel_1',
        'name': 'Primary Channel',
        'segment': 'SMB',
        'lead_source': 'Inbound Marketing',
        'monthly_leads': 1000,
        'cpl': 50,
        'contact_rate': 0.65,
        'meeting_rate': 0.4,
        'show_up_rate': 0.7,
        'close_rate': 0.3,
        'avg_deal_value': 15000,
        'sales_cycle_days': 21,
        'icon': '🏢'
    }
])

# ============= HEADER =============
header_cols = st.columns([0.8, 0.2])
with header_cols[0]:
    st.title("💎 Sales Compensation Model - Improved Final Version")
    st.markdown("**Complete integration with proper calculations and flexible inputs**")
with header_cols[1]:
    light_selected = st.toggle(
        "Light background",
        value=st.session_state.theme_light,
        help="Switch to a lighter UI palette if you prefer higher contrast on cards and tables."
    )
    if light_selected != st.session_state.theme_light:
        st.session_state.theme_light = light_selected

if st.session_state.theme_light:
    st.markdown(
        """
        <style>
            body, .stApp, .block-container {
                background-color: #f8fafc !important;
                color: #0f172a !important;
            }
            .stMetric label, .stMetric span, .stMarkdown p, .stMarkdown li, .stMarkdown h1,
            .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {
                color: #0f172a !important;
            }
            .alert-box { color: #0f172a; }
            div[data-testid="stMetricValue"], div[data-testid="stMetricDelta"] {
                color: #0f172a !important;
            }
            .compensation-grid {
                background: #ffffff !important;
                border: 1px solid #e2e8f0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Sidebar is now visible and used for model summary
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# ============= BASELINE INPUT DEFAULTS (legacy sidebar removed) =============
monthly_revenue_target = st.session_state.get('monthly_revenue_target_value', 4_166_667)
annual_revenue = st.session_state.get('annual_revenue_value', monthly_revenue_target * 12)

num_closers = st.session_state.get('closers_value', 8)
num_setters = st.session_state.get('setters_value', 4)
num_bench = st.session_state.get('bench_value', 2)
num_managers = st.session_state.get('managers_value', 2)

team_total = num_closers + num_setters + num_bench + num_managers

cost_type = st.session_state.get('lead_cost_type', 'CPL')
cost_value = st.session_state.get('lead_cost_value', 150)
daily_leads = st.session_state.get('lead_volume_daily', 155)
monthly_leads = st.session_state.get('lead_volume_monthly', daily_leads * 30)

contact_rate = st.session_state.get('default_contact_rate', 0.60)
meeting_rate = st.session_state.get('default_meeting_rate', 0.35)
show_up_rate = st.session_state.get('default_showup_rate', 0.75)
close_rate = st.session_state.get('default_close_rate', 0.25)
onboard_rate = st.session_state.get('default_onboard_rate', 0.95)

grr_rate = st.session_state.get('grr_rate_main', 0.90)

# ============= DEAL ECONOMICS - SINGLE SOURCE OF TRUTH =============
# Get current deal economics from Deal Economics Manager
# This replaces all hardcoded deal values and uses actual user inputs
deal_econ = DealEconomicsManager.get_current_deal_economics()

# Extract values for backward compatibility
avg_deal_value = deal_econ['avg_deal_value']
upfront_pct = deal_econ['upfront_pct']
deferred_pct = deal_econ['deferred_pct']
comp_immediate = deal_econ['upfront_cash']
comp_deferred = deal_econ['deferred_cash']
contract_length_months = deal_econ['contract_length_months']

# Legacy values (kept for compatibility with old code that references them)
avg_pm = avg_deal_value / contract_length_months if contract_length_months > 0 else avg_deal_value
contract_years = contract_length_months / 12
carrier_rate = 1.0  # Not applicable in new model, kept for compatibility
total_contract_value = avg_deal_value
total_comp = avg_deal_value

default_roles_comp = {
    'closer': {'count': num_closers, 'base': 32000, 'variable': 48000, 'ote': 80000, 'label': 'Closer'},
    'setter': {'count': num_setters, 'base': 16000, 'variable': 24000, 'ote': 40000, 'label': 'Setter'},
    'manager': {'count': num_managers, 'base': 72000, 'variable': 48000, 'ote': 120000, 'label': 'Manager'},
    'bench': {'count': num_bench, 'base': 12500, 'variable': 12500, 'ote': 25000, 'label': 'Bench'}
}

comp_inputs_state = st.session_state.get('team_compensation_inputs')
if not comp_inputs_state:
    comp_inputs_state = {
        'comp_mode': 'Simple (% split)',
        'roles_comp': default_roles_comp,
        'closer_comm_pct': 0.20,
        'setter_comm_pct': 0.03
    }
    st.session_state['team_compensation_inputs'] = comp_inputs_state

roles_comp = comp_inputs_state['roles_comp']
closer_comm_pct = comp_inputs_state['closer_comm_pct']
setter_comm_pct = comp_inputs_state['setter_comm_pct']
comp_structure = ImprovedCompensationCalculator.calculate_custom_compensation(roles_comp)

st.session_state.setdefault('team_compensation_structure', {
    'comp_structure': comp_structure,
    'closer_comm_pct': closer_comm_pct,
    'setter_comm_pct': setter_comm_pct
})

office_rent = st.session_state.get('rent_value', 20000)
software_costs = st.session_state.get('software_value', 10000)
other_opex = st.session_state.get('opex_value', 5000)
gov_fee_pct = st.session_state.get('gov_fee_pct_value', 0.10)

projection_months = st.session_state.get('projection_months_value', 18)
sales_cycle_days = st.session_state.get('sales_cycle_value', 20)

# ============= CALCULATIONS =============
# ============= CALCULATIONS =============
# ============= CALCULATIONS =============

# Initialize with zeros - will be calculated from channels
monthly_contacts = 0
monthly_meetings_scheduled = 0
monthly_meetings_held = 0
monthly_sales = 0
monthly_onboarded = 0
monthly_meetings = 0

# These will be overridden by channel calculations
# Only use legacy calculations if no channels are defined
if 'gtm_channels' not in st.session_state or len(st.session_state.gtm_channels) == 0:
    # Fallback to simple calculations for initial state
    monthly_contacts = monthly_leads * contact_rate
    monthly_meetings_scheduled = monthly_contacts * meeting_rate
    monthly_meetings_held = monthly_meetings_scheduled * show_up_rate
    monthly_sales = monthly_meetings_held * close_rate
    monthly_onboarded = monthly_sales * onboard_rate
    monthly_meetings = monthly_meetings_held

# Cost calculations
volume_metrics = {
    'leads': monthly_leads,
    'contact_rate': contact_rate,
    'meeting_rate': meeting_rate,
    'show_up_rate': show_up_rate,
    'close_rate': close_rate,
    'avg_deal_value': comp_immediate
}

cost_breakdown = ImprovedCostCalculator.calculate_acquisition_costs(
    cost_type, cost_value, volume_metrics
)

# Revenue calculations - safe calculation even during configuration
try:
    revenue_timeline = EnhancedRevenueCalculator.calculate_monthly_timeline(
        max(monthly_sales, 0), avg_pm, projection_months,
        carrier_rate, 0.7, 0.3, grr_rate, 0.0
    )
except:
    revenue_timeline = []

# Current month values - using Deal Economics Manager
rev_calc = DealEconomicsManager.calculate_monthly_revenue(
    max(monthly_sales, 0), 
    deal_econ, 
    include_deferred=False, 
    month_number=1
)
monthly_revenue_immediate = rev_calc['upfront_revenue']
monthly_revenue_deferred = rev_calc['deferred_revenue']
monthly_revenue_total = rev_calc['total_revenue']

# Month 18 values (if applicable) - using Deal Economics Manager
if projection_months >= 18:
    rev_calc_18 = DealEconomicsManager.calculate_monthly_revenue(
        max(monthly_sales, 0),
        deal_econ,
        include_deferred=True,
        month_number=18
    )
    month_18_revenue_immediate = rev_calc_18['upfront_revenue']
    month_18_revenue_deferred = rev_calc_18['deferred_revenue'] * grr_rate
    month_18_revenue_total = month_18_revenue_immediate + month_18_revenue_deferred
else:
    month_18_revenue_immediate = monthly_revenue_immediate
    month_18_revenue_deferred = 0
    month_18_revenue_total = monthly_revenue_total

# Cost structure for P&L - using Deal Economics Manager for commissions
monthly_marketing = cost_breakdown.get('total_marketing_spend', cost_breakdown.get('cost_per_lead', 0) * monthly_leads)

# Calculate commissions using Deal Economics Manager
comm_calc = DealEconomicsManager.calculate_monthly_commission(max(monthly_sales, 0), roles_comp, deal_econ)
monthly_commissions = comm_calc['total_commission']

monthly_base_salaries = comp_structure['monthly_base']
monthly_opex = office_rent + software_costs + other_opex
monthly_costs_before_fees = monthly_marketing + monthly_commissions + monthly_base_salaries + monthly_opex
monthly_gov_fees = monthly_revenue_total * gov_fee_pct
monthly_total_costs = monthly_costs_before_fees + monthly_gov_fees

# EBITDA
monthly_ebitda = monthly_revenue_total - monthly_total_costs
ebitda_margin = monthly_ebitda / monthly_revenue_total if monthly_revenue_total > 0 else 0

# Unit Economics
ltv = comp_immediate + (comp_deferred * grr_rate)
cac = cost_breakdown['cost_per_sale'] + (monthly_commissions / monthly_sales if monthly_sales > 0 else 0)
ltv_cac_ratio = ltv / cac if cac > 0 else 0
payback_months = cac / (comp_immediate / 12) if comp_immediate > 0 else 999  # Months to recover CAC
roas = monthly_revenue_target / monthly_marketing if monthly_marketing > 0 else 0  # Return on Ad Spend

# Current state for reverse engineering
current_state = {
    'monthly_revenue': monthly_revenue_total,
    'monthly_sales': monthly_sales,
    'monthly_meetings': monthly_meetings,
    'monthly_leads': monthly_leads,
    'monthly_ebitda': monthly_ebitda,
    'ebitda_margin': ebitda_margin,
    'num_closers': num_closers,
    'num_setters': num_setters,
    'close_rate': close_rate,
    'meeting_rate': meeting_rate,
    'contact_rate': contact_rate,
    'avg_deal_value': comp_immediate,
    'cost_per_lead': cost_breakdown['cost_per_lead'],
    'ltv': ltv,
    'cac': cac,
    'total_costs': monthly_total_costs
}

# ============= MAIN DASHBOARD =============

# Top metrics moved to consolidated Business Performance Dashboard section
# All metrics are now displayed in the aggregated section below


@st.cache_data(ttl=60)
def get_capacity_metrics(default_closers, default_setters, fallback_working_days=20, fallback_closer_meetings=3.0, fallback_setter_meetings=2.0):
    """Return capacity configuration and derived totals based on stored settings."""
    settings = st.session_state.get('team_capacity_settings', {})
    working_days = settings.get('working_days', fallback_working_days)
    meetings_per_closer = settings.get('meetings_per_closer', fallback_closer_meetings)
    meetings_per_setter = settings.get('meetings_per_setter', fallback_setter_meetings)
    per_closer_monthly_capacity = meetings_per_closer * working_days
    per_setter_monthly_capacity = meetings_per_setter * working_days
    monthly_closer_capacity = settings.get('monthly_closer_capacity', default_closers * per_closer_monthly_capacity)
    monthly_setter_capacity = settings.get('monthly_setter_capacity', default_setters * per_setter_monthly_capacity)
    return {
        'working_days': working_days,
        'meetings_per_closer': meetings_per_closer,
        'meetings_per_setter': meetings_per_setter,
        'per_closer_monthly_capacity': per_closer_monthly_capacity,
        'per_setter_monthly_capacity': per_setter_monthly_capacity,
        'monthly_closer_capacity': monthly_closer_capacity,
        'monthly_setter_capacity': monthly_setter_capacity
    }

# ============= ALERTS AND SUGGESTIONS (Improved) =============

# Dynamic alerts based on current state
alerts = []
suggestions = []

# Check revenue gap with enhanced urgency
revenue_gap = monthly_revenue_target - monthly_revenue_total
if revenue_gap > 0:
    gap_pct = (revenue_gap / monthly_revenue_target) * 100
    if gap_pct > 30:
        alert_type = 'critical'
        urgency = '🔥 CRITICAL SHORTFALL'
    elif gap_pct > 15:
        alert_type = 'critical' 
        urgency = '⚠️ MAJOR GAP'
    else:
        alert_type = 'warning'
        urgency = '📊 BELOW TARGET'
    
    # Calculate required metrics safely
    required_sales = revenue_gap / comp_immediate if comp_immediate > 0 else 0
    required_close_rate = (monthly_sales * monthly_revenue_target / max(monthly_revenue_total, 1)) / max(monthly_meetings, 1)
    
    alerts.append({
        'type': alert_type,
        'message': f'{urgency}: Revenue shortfall of ${revenue_gap:,.0f} ({gap_pct:.1f}% below target) - Missing {required_sales:.0f} sales',
        'action': f'URGENT: Increase sales by {required_sales:.0f} units/month OR improve close rate to {required_close_rate:.1%}'
    })

cap_settings_global = get_capacity_metrics(num_closers, num_setters)
working_days_effective = max(cap_settings_global['working_days'], 1)
monthly_closer_capacity_global = cap_settings_global['monthly_closer_capacity']
monthly_setter_capacity_global = cap_settings_global['monthly_setter_capacity']
per_closer_capacity = max(cap_settings_global['per_closer_monthly_capacity'], 1)
per_setter_capacity = max(cap_settings_global['per_setter_monthly_capacity'], 1)
capacity_util = monthly_meetings / monthly_closer_capacity_global if monthly_closer_capacity_global > 0 else 0
setter_util_global = monthly_meetings_scheduled / monthly_setter_capacity_global if monthly_setter_capacity_global > 0 else 0

# Check team capacity with multiple thresholds
if capacity_util > 0.95:
    high_capacity_target = per_closer_capacity * num_closers * 0.8
    excess_meetings_high = monthly_meetings - high_capacity_target
    additional_closers_high = np.ceil(max(excess_meetings_high, 0) / per_closer_capacity) if per_closer_capacity > 0 else 0
    meeting_reduction_high = (max(excess_meetings_high, 0) / monthly_meetings * 100) if monthly_meetings > 0 else 0
    alerts.append({
        'type': 'critical',
        'message': f'🚨 TEAM OVERLOAD: {capacity_util:.0%} capacity - Quality degradation imminent, burnout risk HIGH',
        'action': f'IMMEDIATE: Hire {additional_closers_high:.0f} closers OR cut meetings by {meeting_reduction_high:.0f}%'
    })
elif capacity_util > 0.85:
    warn_capacity_target = per_closer_capacity * num_closers * 0.75
    excess_meetings_warn = monthly_meetings - warn_capacity_target
    additional_closers_warn = np.ceil(max(excess_meetings_warn, 0) / per_closer_capacity) if per_closer_capacity > 0 else 0
    alerts.append({
        'type': 'warning',
        'message': f'⚠️ HIGH UTILIZATION: {capacity_util:.0%} capacity - Approaching danger zone',
        'action': f'Plan hiring: Need {additional_closers_warn:.0f} closers within 30 days to maintain quality'
    })

# Check LTV:CAC with severity levels
if ltv_cac_ratio < 2:
    alerts.append({
        'type': 'critical',
        'message': f'💀 UNSUSTAINABLE ECONOMICS: LTV:CAC {ltv_cac_ratio:.1f}:1 - Business model failing, immediate action required',
        'action': f'EMERGENCY: Reduce CAC by ${cac - ltv/3:.0f} ({((cac - ltv/3)/cac)*100:.0f}%) OR increase LTV by ${ltv*3/ltv_cac_ratio - ltv:.0f}'
    })
elif ltv_cac_ratio < 3:
    target_cac = ltv / 3
    cac_reduction = cac - target_cac
    alerts.append({
        'type': 'warning',
        'message': f'📉 POOR UNIT ECONOMICS: LTV:CAC {ltv_cac_ratio:.1f}:1 below healthy 3:1 benchmark',
        'action': f'Optimize: Reduce CAC by ${cac_reduction:.0f} through better targeting, conversion, or pricing'
    })

# Check conversion rates with benchmarks
if close_rate < 0.15:
    alerts.append({
        'type': 'critical',
        'message': f'💔 CRITICAL CONVERSION: {close_rate:.1%} close rate - Massive efficiency loss, wasting {(1-close_rate)*100:.0f}% of meetings',
        'action': f'URGENT: Sales training + lead quality audit. Target: 25% close rate (+{(0.25-close_rate)*100:.1f} points)'
    })
elif close_rate < 0.2:
    alerts.append({
        'type': 'warning',
        'message': f'📊 BELOW BENCHMARK: {close_rate:.1%} close rate under industry standard (20-25%)',
        'action': f'Improve sales process: Need +{(0.22-close_rate)*100:.1f} percentage points to reach 22% benchmark'
    })

# Check contact rate
if contact_rate < 0.5:
    wasted_leads = monthly_leads * (1 - contact_rate)
    alerts.append({
        'type': 'warning',
        'message': f'📞 POOR LEAD CONTACT: {contact_rate:.1%} contact rate - Wasting {wasted_leads:.0f} leads/month (${wasted_leads * cost_breakdown["cost_per_lead"]:,.0f})',
        'action': f'Fix lead routing/quality OR increase setter capacity. Target: 60% contact rate'
    })

# Check EBITDA margin
if ebitda_margin < 0:
    alerts.append({
        'type': 'critical',
        'message': f'🔴 LOSING MONEY: {ebitda_margin:.1%} EBITDA margin - Business is unprofitable',
        'action': f'EMERGENCY: Cut costs by ${abs(monthly_ebitda):,.0f}/month OR increase revenue by ${abs(monthly_ebitda)/0.25:,.0f}/month'
    })
elif ebitda_margin < 0.15:
    alerts.append({
        'type': 'warning',
        'message': f'📉 THIN MARGINS: {ebitda_margin:.1%} EBITDA margin below healthy 20-25% range',
        'action': f'Optimize operations: Improve margin by {(0.2 - ebitda_margin)*100:.1f} percentage points'
    })

# Check pipeline coverage
pipeline_coverage = (monthly_meetings * comp_immediate / close_rate) / monthly_revenue_target if monthly_revenue_target > 0 else 0
if pipeline_coverage < 2:
    alerts.append({
        'type': 'critical',
        'message': f'🔍 INSUFFICIENT PIPELINE: {pipeline_coverage:.1f}x coverage - High risk of missing targets',
        'action': f'URGENT: Increase pipeline to {monthly_revenue_target * 3 / comp_immediate:.0f} opportunities (need {(3 - pipeline_coverage) * monthly_revenue_target / comp_immediate:.0f} more)'
    })

# Check show-up rate
if show_up_rate < 0.7:
    no_shows_monthly = monthly_meetings_scheduled * (1 - show_up_rate)
    wasted_cost = no_shows_monthly * cost_breakdown.get('cost_per_meeting_scheduled', 0)
    alerts.append({
        'type': 'warning',
        'message': f'😞 POOR SHOW-UP RATE: {show_up_rate:.1%} attendance - Wasting {no_shows_monthly:.0f} meetings/month',
        'action': f'Implement confirmation system, reschedule policies, or meeting incentives. Potential savings: ${wasted_cost:,.0f}/month'
    })

# Sort alerts by severity (critical first)
alerts.sort(key=lambda x: 0 if x['type'] == 'critical' else 1)

# Build recommended actions based on metrics
recommended_actions = []
achievement_rate_calc = (monthly_revenue_total / monthly_revenue_target * 100) if monthly_revenue_target > 0 else 0
if achievement_rate_calc < 80:
    recommended_actions.append("📈 Increase lead generation by 25%")
    recommended_actions.append("🎯 Review and optimize close rates")

if ebitda_margin < 15:
    recommended_actions.append("💰 Reduce operational costs by 10%")
    recommended_actions.append("📊 Optimize marketing spend efficiency")

if ltv_cac_ratio < 3:
    recommended_actions.append("🔄 Focus on customer retention")
    recommended_actions.append("💵 Consider pricing optimization")

if capacity_util > 0.85:
    recommended_actions.append("👥 Plan team expansion to prevent burnout")

if close_rate < 0.2:
    recommended_actions.append("📚 Invest in sales training programs")

# Alerts moved to sidebar for better visibility

# ============= HEALTH MONITORING (Moved from Critical Alerts) =============

# This section shows health metrics and recommendations in a calmer way
# Actual critical alerts logic is preserved but displayed differently in the main tab

# ============= SIDEBAR: LANGUAGE SELECTOR & MODEL SUMMARY =============
with st.sidebar:
    # Language Selector at the very top
    st.markdown("### 🌐 Language / Idioma")
    lang = st.selectbox(
        "",
        options=['en', 'es'],
        format_func=lambda x: '🇺🇸 English' if x == 'en' else '🇪🇸 Español',
        key='language_selector',
        label_visibility='collapsed'
    )
    st.markdown("---")
    
    st.markdown(f"## 📋 {t('model_summary', lang)}")
    st.markdown("---")
    
    # Revenue Target Section
    st.markdown(f"### {t('revenue_target', lang)}")
    monthly_target_display = st.session_state.get('monthly_revenue_target_main', monthly_revenue_target)
    st.metric(t('monthly', lang), f"${monthly_target_display:,.0f}")
    st.metric(t('annual', lang), f"${monthly_target_display*12:,.0f}")
    
    st.markdown("---")
    
    # Team Configuration
    st.markdown("### 👥 Sales Team")
    closers_display = st.session_state.get('num_closers_main', num_closers)
    setters_display = st.session_state.get('num_setters_main', num_setters)
    managers_display = st.session_state.get('num_managers_main', num_managers)
    bench_display = st.session_state.get('num_bench_main', num_bench)
    
    st.text(f"Closers: {closers_display}")
    st.text(f"Setters: {setters_display}")
    st.text(f"Managers: {managers_display}")
    st.text(f"Bench: {bench_display}")
    st.metric("Total Team", f"{closers_display + setters_display + managers_display + bench_display}")
    
    st.markdown("---")
    
    # Compensation Model
    st.markdown("### 💰 Compensation")
    comp_mode_display = st.session_state.get('comp_model_selection', '⚖️ Balanced (40/60)')
    st.text(f"Model: {comp_mode_display.split(' ')[0]}")
    
    # Deal Economics
    avg_pm_display = st.session_state.get('avg_pm_main', avg_pm)
    contract_years_display = st.session_state.get('contract_years_main', contract_years)
    st.metric("Avg Premium", f"${avg_pm_display:,.0f} MXN/mo")
    st.metric("Contract", f"{contract_years_display} years")
    
    st.markdown("---")
    
    # Financial Health
    st.markdown("### 💵 Financial Health")
    cash_balance_display = st.session_state.get('cash_balance_main', 0)
    st.metric("Cash on Hand", f"${cash_balance_display:,.0f}")
    
    st.markdown("---")
    
    # Compact Alerts Section
    st.markdown(f"### {t('business_alerts', lang)}")
    
    if alerts:
        critical_count = sum(1 for alert in alerts if alert['type'] == 'critical')
        warning_count = len(alerts) - critical_count
        
        # Status badge
        if critical_count > 0:
            st.markdown(f"**<span style='color: #f87171;'>●</span> {critical_count} Critical | <span style='color: #fbbf24;'>●</span> {warning_count} Warning**", unsafe_allow_html=True)
        elif warning_count > 0:
            st.markdown(f"**<span style='color: #fbbf24;'>●</span> {warning_count} Warning**", unsafe_allow_html=True)
        
        for alert in alerts:
            icon = "🔴" if alert['type'] == 'critical' else "⚠️"
            bg_color = "#2d1618" if alert['type'] == 'critical' else "#2d2418"
            border_color = "#f87171" if alert['type'] == 'critical' else "#fbbf24"
            
            st.markdown(
                f"""
                <div style="background: {bg_color}; border-left: 3px solid {border_color}; 
                            padding: 10px; margin: 8px 0; border-radius: 6px; font-size: 12px;">
                    <div style="font-weight: 600; margin-bottom: 4px;">{icon} {alert['type'].upper()}</div>
                    <div style="color: #e2e8f0; margin-bottom: 6px; line-height: 1.4;">{alert['message']}</div>
                    <div style="color: #94a3b8; font-size: 11px; line-height: 1.3;">
                        <strong>Action:</strong> {alert['action']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.success(t('all_systems_healthy', lang))
        st.caption(t('no_issues', lang))
    
    # Recommended Actions Section
    if recommended_actions:
        st.markdown(f"**{t('recommended_actions', lang)}**")
        for action in recommended_actions[:5]:  # Show top 5
            st.markdown(
                f"""
                <div style="background: #1e293b; border-left: 3px solid #3b82f6; 
                            padding: 8px; margin: 6px 0; border-radius: 4px; font-size: 12px;">
                    <div style="color: #e2e8f0; line-height: 1.4;">{action}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # Save/Load Configuration
    st.markdown("### 💾 Save/Load Model")
    
    # Collect current configuration (including all new business-specific fields)
    current_config = {
        "revenue": {
            "monthly_target": monthly_target_display,
            "annual_target": monthly_target_display * 12
        },
        "team": {
            "closers": closers_display,
            "setters": setters_display,
            "managers": managers_display,
            "bench": bench_display
        },
        "compensation": {
            "model": comp_mode_display,
            "avg_premium_mxn": avg_pm_display,
            "contract_years": contract_years_display
        },
        "deal_economics": {
            # Insurance fields
            "monthly_premium_mxn": st.session_state.get('monthly_premium_mxn', 3000),
            "insurance_contract_years": st.session_state.get('insurance_contract_years', 18),
            "carrier_commission_rate": st.session_state.get('carrier_commission_rate', 2.7),
            
            # SaaS fields
            "monthly_mrr": st.session_state.get('monthly_mrr', 5000),
            "saas_contract_months": st.session_state.get('saas_contract_months', 12),
            
            # Consulting fields
            "project_value": st.session_state.get('project_value', 50000),
            "project_duration_months": st.session_state.get('project_duration_months', 3),
            
            # Agency/Retainer fields
            "monthly_retainer": st.session_state.get('monthly_retainer', 10000),
            "retainer_duration_months": st.session_state.get('retainer_duration_months', 6),
            
            # One-time sale fields
            "sale_price": st.session_state.get('sale_price', 10000),
            
            # Universal fields
            "avg_deal_value": st.session_state.get('avg_deal_value', 50000),
            "contract_length_months": st.session_state.get('contract_length_months', 12),
            "upfront_payment_pct": st.session_state.get('upfront_payment_pct', 70.0),
            "deferred_timing_months": st.session_state.get('deferred_timing_months', 18),
            
            # Business type selection
            "business_type": st.session_state.get('business_type_template_display', 'Custom')
        },
        "commission_policy": {
            "commission_base_policy": st.session_state.get('commission_base_policy', 'Upfront Cash Only (70%)'),
            "commission_multiplier": st.session_state.get('commission_multiplier', 0.70)
        },
        "financial": {
            "cash_balance": cash_balance_display
        },
        "timestamp": datetime.now().isoformat()
    }
    
    # Export as JSON
    config_json = json.dumps(current_config, indent=2)
    
    # Download button
    st.download_button(
        label="📥 Download Config",
        data=config_json,
        file_name=f"model_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download current model configuration as JSON file"
    )
    
    # Copy to clipboard
    if st.button("📋 Copy Config", help="Copy configuration to clipboard"):
        st.code(config_json, language="json")
        st.success("✅ Configuration displayed above - copy from code block")
    
    # Load configuration
    st.markdown("**Load Config**")
    uploaded_file = st.file_uploader(
        "Upload JSON config",
        type=['json'],
        help="Upload a previously saved configuration file",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            loaded_config = json.load(uploaded_file)
            
            # Apply loaded configuration to session state
            if st.button("✅ Apply Loaded Config"):
                if 'revenue' in loaded_config:
                    st.session_state['monthly_revenue_target_main'] = loaded_config['revenue'].get('monthly_target', monthly_revenue_target)
                
                if 'team' in loaded_config:
                    st.session_state['num_closers_main'] = loaded_config['team'].get('closers', num_closers)
                    st.session_state['num_setters_main'] = loaded_config['team'].get('setters', num_setters)
                    st.session_state['num_managers_main'] = loaded_config['team'].get('managers', num_managers)
                    st.session_state['num_bench_main'] = loaded_config['team'].get('bench', num_bench)
                
                if 'compensation' in loaded_config:
                    st.session_state['avg_pm_main'] = loaded_config['compensation'].get('avg_premium_mxn', avg_pm)
                    st.session_state['contract_years_main'] = loaded_config['compensation'].get('contract_years', contract_years)
                
                # Load new deal economics fields
                if 'deal_economics' in loaded_config:
                    deal_econ = loaded_config['deal_economics']
                    # Insurance
                    st.session_state['monthly_premium_mxn'] = deal_econ.get('monthly_premium_mxn', 3000)
                    st.session_state['insurance_contract_years'] = deal_econ.get('insurance_contract_years', 18)
                    st.session_state['carrier_commission_rate'] = deal_econ.get('carrier_commission_rate', 2.7)
                    # SaaS
                    st.session_state['monthly_mrr'] = deal_econ.get('monthly_mrr', 5000)
                    st.session_state['saas_contract_months'] = deal_econ.get('saas_contract_months', 12)
                    # Consulting
                    st.session_state['project_value'] = deal_econ.get('project_value', 50000)
                    st.session_state['project_duration_months'] = deal_econ.get('project_duration_months', 3)
                    # Agency
                    st.session_state['monthly_retainer'] = deal_econ.get('monthly_retainer', 10000)
                    st.session_state['retainer_duration_months'] = deal_econ.get('retainer_duration_months', 6)
                    # One-time
                    st.session_state['sale_price'] = deal_econ.get('sale_price', 10000)
                    # Universal
                    st.session_state['avg_deal_value'] = deal_econ.get('avg_deal_value', 50000)
                    st.session_state['contract_length_months'] = deal_econ.get('contract_length_months', 12)
                    st.session_state['upfront_payment_pct'] = deal_econ.get('upfront_payment_pct', 70.0)
                    st.session_state['deferred_timing_months'] = deal_econ.get('deferred_timing_months', 18)
                    
                    # Convert English business type to localized display
                    business_type_loaded = deal_econ.get('business_type', 'Custom')
                    # Reverse map: English -> Translated
                    reverse_map = {
                        'Custom': t('custom', lang),
                        'Insurance': t('insurance', lang),
                        'SaaS/Subscription': t('saas', lang),
                        'Consulting/Services': t('consulting', lang),
                        'Agency/Retainer': t('agency', lang),
                        'One-Time Sale': t('one_time_sale', lang)
                    }
                    st.session_state['business_type_template_display'] = reverse_map.get(business_type_loaded, t('custom', lang))
                
                # Load commission policy
                if 'commission_policy' in loaded_config:
                    st.session_state['commission_base_policy'] = loaded_config['commission_policy'].get('commission_base_policy', 'Upfront Cash Only (70%)')
                    st.session_state['commission_multiplier'] = loaded_config['commission_policy'].get('commission_multiplier', 0.70)
                
                if 'financial' in loaded_config:
                    st.session_state['cash_balance_main'] = loaded_config['financial'].get('cash_balance', 0)
                
                st.success("✅ Configuration loaded! Refresh to see changes.")
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading config: {str(e)}")
    
    # Paste JSON config
    with st.expander("📝 Or Paste JSON Config"):
        pasted_config = st.text_area(
            "Paste configuration JSON",
            height=150,
            placeholder='{"revenue": {"monthly_target": 4166667}, ...}',
            label_visibility="collapsed"
        )
        
        if st.button("✅ Apply Pasted Config") and pasted_config:
            try:
                loaded_config = json.loads(pasted_config)
                
                # Apply configuration
                if 'revenue' in loaded_config:
                    st.session_state['monthly_revenue_target_main'] = loaded_config['revenue'].get('monthly_target', monthly_revenue_target)
                
                if 'team' in loaded_config:
                    st.session_state['num_closers_main'] = loaded_config['team'].get('closers', num_closers)
                    st.session_state['num_setters_main'] = loaded_config['team'].get('setters', num_setters)
                    st.session_state['num_managers_main'] = loaded_config['team'].get('managers', num_managers)
                    st.session_state['num_bench_main'] = loaded_config['team'].get('bench', num_bench)
                
                if 'compensation' in loaded_config:
                    st.session_state['avg_pm_main'] = loaded_config['compensation'].get('avg_premium_mxn', avg_pm)
                    st.session_state['contract_years_main'] = loaded_config['compensation'].get('contract_years', contract_years)
                
                # Load new deal economics fields
                if 'deal_economics' in loaded_config:
                    deal_econ = loaded_config['deal_economics']
                    # Insurance
                    st.session_state['monthly_premium_mxn'] = deal_econ.get('monthly_premium_mxn', 3000)
                    st.session_state['insurance_contract_years'] = deal_econ.get('insurance_contract_years', 18)
                    st.session_state['carrier_commission_rate'] = deal_econ.get('carrier_commission_rate', 2.7)
                    # SaaS
                    st.session_state['monthly_mrr'] = deal_econ.get('monthly_mrr', 5000)
                    st.session_state['saas_contract_months'] = deal_econ.get('saas_contract_months', 12)
                    # Consulting
                    st.session_state['project_value'] = deal_econ.get('project_value', 50000)
                    st.session_state['project_duration_months'] = deal_econ.get('project_duration_months', 3)
                    # Agency
                    st.session_state['monthly_retainer'] = deal_econ.get('monthly_retainer', 10000)
                    st.session_state['retainer_duration_months'] = deal_econ.get('retainer_duration_months', 6)
                    # One-time
                    st.session_state['sale_price'] = deal_econ.get('sale_price', 10000)
                    # Universal
                    st.session_state['avg_deal_value'] = deal_econ.get('avg_deal_value', 50000)
                    st.session_state['contract_length_months'] = deal_econ.get('contract_length_months', 12)
                    st.session_state['upfront_payment_pct'] = deal_econ.get('upfront_payment_pct', 70.0)
                    st.session_state['deferred_timing_months'] = deal_econ.get('deferred_timing_months', 18)
                    
                    # Convert English business type to localized display
                    business_type_loaded = deal_econ.get('business_type', 'Custom')
                    # Reverse map: English -> Translated
                    reverse_map = {
                        'Custom': t('custom', lang),
                        'Insurance': t('insurance', lang),
                        'SaaS/Subscription': t('saas', lang),
                        'Consulting/Services': t('consulting', lang),
                        'Agency/Retainer': t('agency', lang),
                        'One-Time Sale': t('one_time_sale', lang)
                    }
                    st.session_state['business_type_template_display'] = reverse_map.get(business_type_loaded, t('custom', lang))
                
                # Load commission policy
                if 'commission_policy' in loaded_config:
                    st.session_state['commission_base_policy'] = loaded_config['commission_policy'].get('commission_base_policy', 'Upfront Cash Only (70%)')
                    st.session_state['commission_multiplier'] = loaded_config['commission_policy'].get('commission_multiplier', 0.70)
                
                if 'financial' in loaded_config:
                    st.session_state['cash_balance_main'] = loaded_config['financial'].get('cash_balance', 0)
                
                st.success("✅ Configuration applied! Refresh to see changes.")
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error parsing JSON: {str(e)}")

# ============= MAIN TABS =============

tabs = st.tabs([
    "🎯 GTM Command Center",
    "💰 Costos Unit",
    "📊 P&L Detallado",
    "🚀 Simulador",
    "🔄 Ingeniería Inversa"
])

# TAB 1: BOWTIE & MULTI-CHANNEL GTM INTEGRATED
with tabs[0]:
    st.header(t('gtm_command_center', lang))
    st.markdown("**Unified view of your Go-to-Market strategy with all KPIs**" if lang == 'en' else "**Vista unificada de su estrategia de salida al mercado con todos los KPIs**")
    
    # Configuration Sections - All inputs in main view
    st.markdown(f"### {t('configuration_center', lang)}")
    st.markdown("Configure all parameters directly in the main view with immediate feedback" if lang == 'en' else "Configure todos los parámetros directamente en la vista principal con retroalimentación inmediata")
    
    # Revenue Targets Configuration
    with st.expander(f"{t('revenue_targets', lang)}", expanded=True):
        rev_col1, rev_col2, rev_col3 = st.columns(3)
        
        with rev_col1:
            target_period_main = st.selectbox(
                "Input Period",
                ["Annual", "Monthly", "Weekly", "Daily"],
                index=1,
                key="target_period_main"
            )
            
            # Get current monthly target from session state or use default
            current_monthly_target = st.session_state.get('monthly_revenue_target_main', 4166667)
            
            if target_period_main == "Annual":
                default_annual = st.session_state.get('rev_annual_main', current_monthly_target * 12)
                revenue_input_main = st.number_input("Annual Target ($)", value=int(default_annual), step=1000000, key="rev_annual_main")
                monthly_revenue_target_main = revenue_input_main / 12
            elif target_period_main == "Monthly":
                default_monthly = st.session_state.get('rev_monthly_main', current_monthly_target)
                revenue_input_main = st.number_input("Monthly Target ($)", value=int(default_monthly), step=100000, key="rev_monthly_main")
                monthly_revenue_target_main = revenue_input_main
            elif target_period_main == "Weekly":
                default_weekly = st.session_state.get('rev_weekly_main', current_monthly_target / 4.33)
                revenue_input_main = st.number_input("Weekly Target ($)", value=int(default_weekly), step=25000, key="rev_weekly_main")
                monthly_revenue_target_main = revenue_input_main * 4.33
            else:  # Daily
                default_daily = st.session_state.get('rev_daily_main', current_monthly_target / 21.67)
                revenue_input_main = st.number_input("Daily Target ($)", value=int(default_daily), step=5000, key="rev_daily_main")
                monthly_revenue_target_main = revenue_input_main * 21.67
            
            # Store in session state for sidebar
            st.session_state['monthly_revenue_target_main'] = monthly_revenue_target_main
        
        with rev_col2:
            st.markdown("**📊 Revenue Breakdown**")
            annual_revenue_main = monthly_revenue_target_main * 12
            st.metric("Annual", f"${annual_revenue_main:,.0f}")
            st.metric("Monthly", f"${monthly_revenue_target_main:,.0f}")
            st.metric("Daily", f"${monthly_revenue_target_main/21.67:,.0f}")
        
        with rev_col3:
            st.markdown("**🎯 Impact Metrics**")
            effective_revenue_per_sale = comp_immediate + (comp_deferred * grr_rate)
            sales_needed = monthly_revenue_target_main / effective_revenue_per_sale if effective_revenue_per_sale > 0 else 0
            st.metric(
                "Sales Needed",
                f"{sales_needed:.0f}/mo",
                help="Monthly deals required based on actual per-sale cash (immediate + retained month-18)."
            )
            st.metric("Revenue/Sale", f"${comp_immediate:,.0f}")
            st.metric("Target vs Current", f"{(monthly_revenue_total/monthly_revenue_target_main*100):.0f}%")
    
    # Pull latest GTM metrics (updates set after channel aggregation)
    gtm_metrics = st.session_state.get('gtm_metrics', {})
    gtm_monthly_leads = gtm_metrics.get('monthly_leads', monthly_leads)
    gtm_monthly_meetings_scheduled = gtm_metrics.get('monthly_meetings_scheduled', monthly_meetings_scheduled)
    gtm_monthly_meetings = gtm_metrics.get('monthly_meetings', monthly_meetings)
    gtm_monthly_sales = gtm_metrics.get('monthly_sales', monthly_sales)
    gtm_monthly_revenue_immediate = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate)
    gtm_blended_contact_rate = gtm_metrics.get('blended_contact_rate', contact_rate)

    # Multi-Channel GTM is now the primary funnel configuration
    # Legacy conversion funnel removed - all configuration happens through channels
    
    # Compensation Structure Configuration - Fully Customizable (with Team Structure integrated)
    with st.expander(f"{t('team_compensation_structure', lang)}", expanded=True):
        st.info(f"💡 {t('configure_team', lang)}")
        
        # Team Structure Section (moved from above)
        st.markdown(f"### {t('team_configuration', lang)}")
        team_col1, team_col2, team_col3 = st.columns(3)
        
        with team_col1:
            st.markdown(f"**{t('sales_team', lang)}**")
            num_closers_main = st.number_input(f"💼 {t('closers', lang)}", min_value=0, max_value=50, value=num_closers, step=1, key="closers_main")
            num_setters_main = st.number_input(f"📞 {t('setters', lang)}", min_value=0, max_value=50, value=num_setters, step=1, key="setters_main")
            num_bench_main = st.number_input(f"🏋 {t('bench', lang)}", min_value=0, max_value=20, value=num_bench, step=1, key="bench_main")
            num_managers_main = st.number_input(f"👔 {t('managers', lang)}", min_value=0, max_value=10, value=num_managers, step=1, key="managers_main")
            st.markdown(f"**{t('capacity_settings', lang)}**")
            meetings_per_closer = st.number_input(
                "Meetings/Closer/Day",
                min_value=0.0,
                value=st.session_state.get('meetings_per_closer', 3.0),
                step=0.1,
                help="Average meetings each closer can run per working day"
            )
            working_days = st.number_input(
                "Working Days/Month",
                min_value=10,
                max_value=26,
                value=st.session_state.get('working_days', 20),
                step=1,
                help="Number of active selling days per month"
            )
            meetings_per_setter = st.number_input(
                "Meetings Booked/Setter/Day",
                min_value=0.0,
                value=st.session_state.get('meetings_per_setter', 2.0),
                step=0.1,
                help="Average meetings each setter confirms and books per day"
            )
        
        with team_col2:
            st.markdown(f"**{t('team_metrics', lang)}**")
            team_total_main = num_closers_main + num_setters_main + num_bench_main + num_managers_main
            active_ratio_main = (num_closers_main + num_setters_main) / max(1, team_total_main)
            setter_closer_ratio_main = num_setters_main / max(1, num_closers_main)
            st.metric(t('total_team', lang), f"{team_total_main}")
            st.metric(t('active_ratio', lang), f"{active_ratio_main:.0%}")
            st.metric("S:C Ratio", f"{setter_closer_ratio_main:.1f}:1")
        
        with team_col3:
            st.markdown(f"**{t('capacity_analysis', lang)}**")
            monthly_closer_capacity = num_closers_main * meetings_per_closer * working_days
            capacity_util_main = gtm_monthly_meetings / monthly_closer_capacity if monthly_closer_capacity > 0 else 0
            monthly_setter_capacity = num_setters_main * meetings_per_setter * working_days
            setter_util = gtm_monthly_meetings_scheduled / monthly_setter_capacity if monthly_setter_capacity > 0 else 0
            
            # Simple capacity comparison visualization
            import plotly.graph_objects as go
            
            # Calculate target meetings needed for revenue goal
            target_meetings = monthly_revenue_target_main / comp_immediate * (1 / close_rate) if comp_immediate > 0 and close_rate > 0 else gtm_monthly_meetings
            
            # Calculate gaps
            closer_headroom = monthly_closer_capacity - gtm_monthly_meetings
            setter_headroom = monthly_setter_capacity - gtm_monthly_meetings_scheduled
            
            # Determine status colors
            closer_status_color = "#22c55e" if capacity_util_main < 0.75 else "#f59e0b" if capacity_util_main < 0.9 else "#ef4444"
            setter_status_color = "#22c55e" if setter_util < 0.75 else "#f59e0b" if setter_util < 1.0 else "#ef4444"
            
            fig_capacity = go.Figure()
            
            # Closers - Stacked bar
            fig_capacity.add_trace(go.Bar(
                name='Used',
                x=['Closers'],
                y=[gtm_monthly_meetings],
                text=[f"{gtm_monthly_meetings:.0f}"],
                textposition='inside',
                marker_color='#3b82f6',
                hovertemplate='<b>Current Load</b><br>%{y:.0f} meetings<extra></extra>'
            ))
            
            fig_capacity.add_trace(go.Bar(
                name='Available',
                x=['Closers'],
                y=[closer_headroom if closer_headroom > 0 else 0],
                text=[f"{closer_headroom:.0f}" if closer_headroom > 0 else "OVERLOAD"],
                textposition='inside',
                marker_color=closer_status_color,
                hovertemplate='<b>Headroom</b><br>%{y:.0f} meetings<extra></extra>'
            ))
            
            # Setters - Stacked bar
            fig_capacity.add_trace(go.Bar(
                name='Used',
                x=['Setters'],
                y=[gtm_monthly_meetings_scheduled],
                text=[f"{gtm_monthly_meetings_scheduled:.0f}"],
                textposition='inside',
                marker_color='#3b82f6',
                showlegend=False,
                hovertemplate='<b>Current Load</b><br>%{y:.0f} bookings<extra></extra>'
            ))
            
            fig_capacity.add_trace(go.Bar(
                name='Available',
                x=['Setters'],
                y=[setter_headroom if setter_headroom > 0 else 0],
                text=[f"{setter_headroom:.0f}" if setter_headroom > 0 else "OVERLOAD"],
                textposition='inside',
                marker_color=setter_status_color,
                showlegend=False,
                hovertemplate='<b>Headroom</b><br>%{y:.0f} bookings<extra></extra>'
            ))
            
            # Add target line
            fig_capacity.add_trace(go.Scatter(
                x=['Closers', 'Setters'],
                y=[target_meetings, target_meetings / (show_up_rate if show_up_rate > 0 else 0.7)],
                mode='markers+text',
                name='Target',
                marker=dict(size=12, symbol='diamond', color='#fbbf24'),
                text=['Target', ''],
                textposition='top center',
                hovertemplate='<b>Target Needed</b><br>%{y:.0f}<extra></extra>'
            ))
            
            fig_capacity.update_layout(
                barmode='stack',
                title={
                    'text': 'Team Capacity Analysis',
                    'font': {'size': 14, 'color': '#e2e8f0'}
                },
                height=320,
                margin=dict(t=50, b=30, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=11, color='#e2e8f0'),
                xaxis=dict(
                    showgrid=False,
                    title='',
                    tickfont=dict(size=13, color='#e2e8f0')
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(148, 163, 184, 0.1)',
                    title='Meetings/Month',
                    tickfont=dict(size=11, color='#94a3b8')
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    font=dict(size=10)
                )
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True, key="capacity_comparison")
            
            # Decision-focused recommendations
            st.markdown("---")
            st.markdown("**⚡ Actions Needed:**")
            
            # Closer recommendations
            if capacity_util_main > 0.9:
                additional_closers_needed = np.ceil((gtm_monthly_meetings - monthly_closer_capacity * 0.85) / (meetings_per_closer * working_days))
                st.error(f"🔴 **URGENT**: Closers at {capacity_util_main:.0%} - Hire **{additional_closers_needed:.0f} more closers** immediately")
            elif capacity_util_main > 0.75:
                additional_closers_needed = np.ceil((gtm_monthly_meetings - monthly_closer_capacity * 0.75) / (meetings_per_closer * working_days))
                st.warning(f"🟡 **PLAN**: Closers at {capacity_util_main:.0%} - Prepare to hire **{additional_closers_needed:.0f} closers** within 30 days")
            else:
                st.success(f"✅ Closers healthy at {capacity_util_main:.0%} - Headroom: **{closer_headroom:.0f} meetings/mo**")
            
            # Setter recommendations
            if setter_util > 1.0:
                overload = gtm_monthly_meetings_scheduled - monthly_setter_capacity
                additional_setters_needed = np.ceil(overload / (meetings_per_setter * working_days))
                st.error(f"🔴 **CRITICAL**: Setters at {setter_util:.0%} ({overload:.0f} over capacity) - Hire **{additional_setters_needed:.0f} setters** NOW")
            elif setter_util > 0.85:
                additional_setters_needed = np.ceil((gtm_monthly_meetings_scheduled - monthly_setter_capacity * 0.85) / (meetings_per_setter * working_days))
                st.warning(f"🟡 **PLAN**: Setters at {setter_util:.0%} - Prepare to hire **{additional_setters_needed:.0f} setters** soon")
            else:
                st.success(f"✅ Setters healthy at {setter_util:.0%} - Headroom: **{setter_headroom:.0f} bookings/mo**")

            st.session_state['team_capacity_settings'] = {
                'meetings_per_closer': meetings_per_closer,
                'meetings_per_setter': meetings_per_setter,
                'working_days': working_days,
                'monthly_closer_capacity': monthly_closer_capacity,
                'monthly_setter_capacity': monthly_setter_capacity
            }
        
        # Compensation Configuration Section
        st.markdown("---")
        st.markdown(f"### {t('compensation_configuration', lang)}")
        
        # Commission Base Setting (critical for cash flow)
        st.info(f"⚙️ **{t('commission_policy', lang)}**")
        comm_policy_cols = st.columns([2, 2, 3])
        
        with comm_policy_cols[0]:
            commission_base_options = [
                f"{t('upfront_cash_only', lang)} (70%)",
                f"{t('full_deal_value', lang)} (100%)"
            ]
            commission_base = st.selectbox(
                t('pay_commissions_from', lang),
                commission_base_options,
                index=0,
                key="commission_base_policy",
                help="Upfront = Conservative, protects cash flow. Full = Aggressive, better margins but cash risk"
            )
        
        with comm_policy_cols[1]:
            # Show the multiplier being used
            if "Upfront" in commission_base:
                comm_multiplier = 0.70
                st.metric(t('commission_base', lang), "70%", t('upfront_cash_only', lang).replace(' (70%)', ''))
            else:
                comm_multiplier = 1.0
                st.metric(t('commission_base', lang), "100%", t('full_deal_value', lang).replace(' (100%)', ''))
            st.session_state['commission_multiplier'] = comm_multiplier
        
        with comm_policy_cols[2]:
            # Show example calculation using modular upfront percentage
            upfront_pct_val = st.session_state.get('upfront_payment_pct', 70.0)
            example_deal_value = st.session_state.get('avg_deal_value', 50000)
            example_upfront = example_deal_value * (upfront_pct_val / 100)
            
            st.markdown("**💡 Example Calculation:**")
            if comm_multiplier < 1.0:
                # Paying from upfront only
                st.caption(f"Deal: ${example_deal_value:,.0f} → Upfront: ${example_upfront:,.0f} ({upfront_pct_val:.0f}%)")
                st.caption(f"20% commission = ${example_upfront * 0.20:,.0f} (from upfront only)")
            else:
                # Paying from full deal
                st.caption(f"Deal: ${example_deal_value:,.0f} → Commission base: ${example_deal_value:,.0f}")
                st.caption(f"20% commission = ${example_deal_value * 0.20:,.0f} (from full deal)")
        
        st.markdown("---")
        
        # Initialize roles_comp in session state if not exists
        if 'roles_comp_custom' not in st.session_state:
            st.session_state.roles_comp_custom = default_roles_comp.copy()
        
        roles_comp = st.session_state.roles_comp_custom
        
        # Display each role's compensation
        role_tabs = st.tabs([
            f"💼 {t('closers', lang)}",
            f"📞 {t('setters', lang)}",
            f"👔 {t('managers', lang)}",
            f"🏋 {t('bench', lang)}",
            f"👔 {t('stakeholders', lang)}"
        ])
        
        for idx, (role_key, tab) in enumerate(zip(['closer', 'setter', 'manager', 'bench', 'stakeholder'], role_tabs)):
            with tab:
                if role_key == 'stakeholder':
                    # Stakeholders Tab
                    st.markdown("### 👔 Stakeholders (Profit Distribution)")
                    st.info("💡 Stakeholders receive a percentage of EBITDA after all operating costs")
                    
                    stake_cols = st.columns([2, 2])
                    
                    with stake_cols[0]:
                        stakeholder_pct = st.number_input(
                            "Stakeholder Profit Share (%)",
                            min_value=0.0,
                            max_value=50.0,
                            value=st.session_state.get('stakeholder_pct', 10.0),
                            step=0.5,
                            key="stakeholder_pct_input",
                            help="Percentage of EBITDA distributed to stakeholders/owners"
                        )
                        st.session_state['stakeholder_pct'] = stakeholder_pct
                        
                        st.markdown("**📊 Distribution Source:**")
                        st.caption("✅ Comes from EBITDA (after all team costs + OpEx)")
                        st.caption("✅ Remaining EBITDA stays in business for growth")
                        st.caption("✅ Typical range: 5-25% for healthy businesses")
                    
                    with stake_cols[1]:
                        st.markdown("**💰 Projected Distribution:**")
                        
                        # Calculate stakeholder payout (need to get EBITDA from main calculations)
                        # For now, show placeholder - will be calculated in summary
                        if 'monthly_ebitda' in locals() and monthly_ebitda > 0:
                            stakeholder_monthly = monthly_ebitda * (stakeholder_pct / 100)
                            ebitda_after_stake = monthly_ebitda - stakeholder_monthly
                            
                            st.metric("Monthly Distribution", f"${stakeholder_monthly:,.0f}")
                            st.metric("Annual Distribution", f"${stakeholder_monthly * 12:,.0f}")
                            st.metric("EBITDA After Distribution", f"${ebitda_after_stake:,.0f}")
                            
                            # Show as % of revenue
                            if 'monthly_revenue_total' in locals() and monthly_revenue_total > 0:
                                stake_pct_rev = (stakeholder_monthly / monthly_revenue_total * 100)
                                st.metric("As % of Revenue", f"{stake_pct_rev:.1f}%")
                        else:
                            st.caption("💡 EBITDA will be calculated from revenue and costs")
                            st.caption("Distribution amounts will appear here once data is available")
                else:
                    # Regular role tabs (Closer, Setter, Manager, Bench)
                    role_config = roles_comp[role_key]
                    
                    comp_col1, comp_col2, comp_col3 = st.columns(3)
                    
                    with comp_col1:
                        st.markdown(f"**Monthly Compensation**")
                        
                        base_salary = st.number_input(
                            t('base_salary', lang),
                            min_value=0,
                            max_value=200000,
                            value=int(role_config.get('base', 32000)),
                            step=1000,
                            key=f"{role_key}_base",
                            help="Fixed monthly salary regardless of performance" if lang == 'en' else "Salario mensual fijo sin importar el rendimiento"
                        )
                        
                        # Variable comp as percentage of revenue
                        default_pct = role_config.get('commission_pct', 20.0 if role_key == 'closer' else 3.0 if role_key == 'setter' else 5.0)
                        # Get commission base policy
                        comm_base_policy = st.session_state.get('commission_base_policy', 'Upfront Cash Only (70%)')
                        
                        commission_pct = st.number_input(
                            t('commission_pct', lang),
                            min_value=0.0,
                            max_value=50.0,
                            value=float(default_pct),
                            step=0.5,
                            key=f"{role_key}_commission_pct",
                            help=f"Percentage of {'upfront cash (70%)' if 'Upfront' in comm_base_policy else 'full deal value (100%)'} paid as commission"
                        )
                        
                        # Calculate variable comp based on projected revenue
                        actual_revenue = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate) if 'gtm_metrics' in locals() else monthly_revenue_immediate
                        comm_multiplier = st.session_state.get('commission_multiplier', 1.0)
                        upfront_pct_val = st.session_state.get('upfront_payment_pct', 70.0) / 100
                        
                        # Commission base (either upfront portion or full deal)
                        if comm_multiplier < 1.0:
                            # Using upfront only - revenue already represents upfront (comp_immediate)
                            commission_base_amount = actual_revenue
                        else:
                            # Using full deal value
                            commission_base_amount = actual_revenue / upfront_pct_val if upfront_pct_val > 0 else actual_revenue
                        
                        variable_comp = (commission_base_amount * (commission_pct / 100)) / max(1, st.session_state.get(f'num_{role_key}s_main', 1))
                        
                        # Show what this means
                        upfront_pct_display = st.session_state.get('upfront_payment_pct', 70.0)
                        st.caption(f"💰 Estimated: ${variable_comp:,.0f}/mo per person")
                        st.caption(f"📊 From {commission_pct}% of {'upfront (' + str(int(upfront_pct_display)) + '%)' if comm_multiplier < 1.0 else 'full (100%)'} revenue")
                        
                        ote = base_salary + variable_comp
                        
                        # Update role config
                        role_config['base'] = base_salary
                        role_config['commission_pct'] = commission_pct
                        role_config['variable'] = variable_comp
                        role_config['ote'] = ote
                    
                    with comp_col2:
                        st.markdown(f"**{t('compensation_breakdown', lang)}**")
                        
                        # Show pie chart of base vs variable
                        base_pct = (base_salary / ote * 100) if ote > 0 else 50
                        variable_pct = (variable_comp / ote * 100) if ote > 0 else 50
                        
                        st.metric(t('total_ote', lang), f"${ote:,.0f}/mo", f"${ote*12:,.0f}/yr")
                        st.metric(t('base_pct', lang), f"{base_pct:.0f}%")
                        st.metric(t('variable_pct', lang), f"{variable_pct:.0f}%")
                        
                        # Show risk profile
                        if base_pct >= 75:
                            st.success("🟢 Low Risk (High Base)")
                        elif base_pct >= 50:
                            st.info("🔵 Balanced Risk")
                        else:
                            st.warning("🟡 High Risk (High Variable)")
                    
                    with comp_col3:
                        st.markdown(f"**{t('team_cost_impact', lang)}**")
                        
                        # Get count from main team inputs
                        role_count = st.session_state.get(f'num_{role_key}s_main', role_config.get('count', 0))
                        
                        monthly_base_cost = base_salary * role_count
                        monthly_ote_cost = ote * role_count
                        annual_ote_cost = monthly_ote_cost * 12
                        
                        st.metric(t('team_count', lang), f"{role_count}")
                        st.metric(t('monthly_base_cost', lang), f"${monthly_base_cost:,.0f}")
                        st.metric(t('monthly_ote_cost', lang), f"${monthly_ote_cost:,.0f}")
                        st.metric(t('annual_ote_cost', lang), f"${annual_ote_cost:,.0f}")
                    
                    # Add per-deal commission preview
                    st.markdown("---")
                    st.markdown(f"**💰 {'Comisión por Negocio' if lang == 'es' else 'Per-Deal Commission'}**")
                    
                    per_deal_cols = st.columns(3)
                    
                    # Get deal economics
                    avg_deal_value_calc = st.session_state.get('avg_deal_value', 50000)
                    upfront_pct_calc = st.session_state.get('upfront_payment_pct', 70.0) / 100
                    comm_mult_calc = st.session_state.get('commission_multiplier', 1.0)
                    
                    # Calculate commission base
                    if comm_mult_calc < 1.0:
                        # Commission on upfront only
                        comm_base_per_deal = avg_deal_value_calc * upfront_pct_calc
                    else:
                        # Commission on full deal
                        comm_base_per_deal = avg_deal_value_calc
                    
                    # Calculate this role's commission per deal
                    role_comm_per_deal = comm_base_per_deal * (commission_pct / 100)
                    
                    with per_deal_cols[0]:
                        st.metric("Deal Value" if lang == 'en' else "Valor del Negocio", f"${avg_deal_value_calc:,.0f}")
                    with per_deal_cols[1]:
                        st.metric("Commission Base" if lang == 'en' else "Base de Comisión", 
                                 f"${comm_base_per_deal:,.0f}",
                                 f"{int(upfront_pct_calc*100)}%" if comm_mult_calc < 1.0 else "100%")
                    with per_deal_cols[2]:
                        st.metric(f"{t(role_key+'s', lang)} Commission" if lang == 'en' else f"Comisión de {t(role_key+'s', lang)}", 
                                 f"${role_comm_per_deal:,.0f}",
                                 f"{commission_pct}%")
                    
                    st.caption(f"📊 Formula: ${comm_base_per_deal:,.0f} × {commission_pct}% = ${role_comm_per_deal:,.0f}")
                    
                    # Add Performance Requirements to Hit OTE
                    st.markdown("---")
                    st.markdown(f"**🎯 {'Requisitos de Desempeño' if lang == 'es' else 'Performance Requirements to Hit OTE'}**")
                    
                    # Calculate how many deals needed to earn the variable comp
                    if role_comm_per_deal > 0:
                        deals_needed_monthly = variable_comp / role_comm_per_deal
                        deals_needed_weekly = deals_needed_monthly / 4.33
                        deals_needed_daily = deals_needed_monthly / working_days if working_days > 0 else 0
                        
                        # Calculate revenue quota
                        revenue_quota_monthly = deals_needed_monthly * avg_deal_value_calc
                        revenue_quota_annual = revenue_quota_monthly * 12
                        
                        quota_cols = st.columns(4)
                        with quota_cols[0]:
                            st.metric("Monthly Quota" if lang == 'en' else "Cuota Mensual",
                                     f"{deals_needed_monthly:.1f} deals",
                                     f"${revenue_quota_monthly:,.0f}")
                        with quota_cols[1]:
                            st.metric("Weekly" if lang == 'en' else "Semanal",
                                     f"{deals_needed_weekly:.1f} deals")
                        with quota_cols[2]:
                            st.metric("Daily" if lang == 'en' else "Diario",
                                     f"{deals_needed_daily:.2f} deals")
                        with quota_cols[3]:
                            st.metric("Annual Quota" if lang == 'en' else "Cuota Anual",
                                     f"{deals_needed_monthly*12:.0f} deals",
                                     f"${revenue_quota_annual:,.0f}")
                        
                        # Show performance scenarios
                        st.markdown("**📈 " + ("Escenarios de Desempeño" if lang == 'es' else "Performance Scenarios") + "**")
                        scenario_cols = st.columns(3)
                        
                        with scenario_cols[0]:
                            st.info(f"**80% Attainment**\n\n"
                                   f"Deals: {deals_needed_monthly*0.8:.1f}/mo\n\n"
                                   f"Earnings: ${base_salary + (variable_comp*0.8):,.0f}/mo\n\n"
                                   f"({(base_salary + (variable_comp*0.8))/ote*100:.0f}% of OTE)")
                        
                        with scenario_cols[1]:
                            st.success(f"**100% Attainment (OTE)**\n\n"
                                      f"Deals: {deals_needed_monthly:.1f}/mo\n\n"
                                      f"Earnings: ${ote:,.0f}/mo\n\n"
                                      f"(Target)")
                        
                        with scenario_cols[2]:
                            st.warning(f"**120% Attainment**\n\n"
                                      f"Deals: {deals_needed_monthly*1.2:.1f}/mo\n\n"
                                      f"Earnings: ${base_salary + (variable_comp*1.2):,.0f}/mo\n\n"
                                      f"({(base_salary + (variable_comp*1.2))/ote*100:.0f}% of OTE)")
                        
                        # Reality check against capacity
                        st.markdown("---")
                        st.markdown("**⚠️ " + ("Verificación de Realidad" if lang == 'es' else "Reality Check") + "**")
                        
                        # Get close rate and capacity
                        close_rate = st.session_state.get('close_rate', 0.30)
                        meetings_per_closer_day = st.session_state.get('meetings_per_closer', 3.0)
                        meetings_capacity_monthly = meetings_per_closer_day * working_days if working_days > 0 else 60
                        
                        # Calculate required meetings for quota
                        meetings_needed_for_quota = deals_needed_monthly / close_rate if close_rate > 0 else deals_needed_monthly / 0.30
                        capacity_utilization = (meetings_needed_for_quota / meetings_capacity_monthly * 100) if meetings_capacity_monthly > 0 else 0
                        
                        reality_cols = st.columns(3)
                        with reality_cols[0]:
                            st.metric("Meetings Needed" if lang == 'en' else "Reuniones Necesarias",
                                     f"{meetings_needed_for_quota:.0f}/mo",
                                     f"{meetings_needed_for_quota/working_days:.1f}/day" if working_days > 0 else "")
                        with reality_cols[1]:
                            st.metric("Capacity" if lang == 'en' else "Capacidad",
                                     f"{meetings_capacity_monthly:.0f}/mo",
                                     f"{meetings_per_closer_day:.1f}/day")
                        with reality_cols[2]:
                            capacity_color = "🟢" if capacity_utilization <= 80 else "🟡" if capacity_utilization <= 100 else "🔴"
                            st.metric("Utilization" if lang == 'en' else "Utilización",
                                     f"{capacity_utilization:.0f}%",
                                     capacity_color)
                        
                        # Warning if over capacity
                        if capacity_utilization > 100:
                            st.error(f"⚠️ {'ALERTA' if lang == 'es' else 'WARNING'}: Quota requires {capacity_utilization:.0f}% capacity utilization. "
                                    f"This rep needs {meetings_needed_for_quota:.0f} meetings/month but only has capacity for {meetings_capacity_monthly:.0f}. "
                                    f"{'Considere aumentar equipo o ajustar compensación.' if lang == 'es' else 'Consider increasing team size or adjusting compensation.'}")
                        elif capacity_utilization > 80:
                            st.warning(f"⚡ High utilization ({capacity_utilization:.0f}%). "
                                      f"{'Poco margen para error.' if lang == 'es' else 'Limited margin for error.'}")
                    else:
                        st.warning("⚠️ Set commission % to see performance requirements")
        
        # Get stakeholder percentage
        stakeholder_pct = st.session_state.get('stakeholder_pct', 10.0)
        
        # Summary section
        st.markdown("---")
        st.markdown(f"### {t('total_compensation_summary', lang)}")
        
        summary_cols = st.columns(5)
        
        # Calculate totals
        total_monthly_base = sum([
            roles_comp[role]['base'] * st.session_state.get(f'num_{role}s_main', roles_comp[role].get('count', 0))
            for role in ['closer', 'setter', 'manager', 'bench']
        ])
        
        total_monthly_ote = sum([
            roles_comp[role]['ote'] * st.session_state.get(f'num_{role}s_main', roles_comp[role].get('count', 0))
            for role in ['closer', 'setter', 'manager', 'bench']
        ])
        
        total_annual_ote = total_monthly_ote * 12
        
        # Calculate expected variable payout (assume 80% attainment)
        total_monthly_variable_target = total_monthly_ote - total_monthly_base
        expected_monthly_variable = total_monthly_variable_target * 0.8
        expected_monthly_total = total_monthly_base + expected_monthly_variable
        
        with summary_cols[0]:
            st.metric(t('monthly_base', lang), f"${total_monthly_base:,.0f}")
        with summary_cols[1]:
            st.metric(t('monthly_ote', lang), f"${total_monthly_ote:,.0f}")
        with summary_cols[2]:
            st.metric(t('expected_monthly', lang), f"${expected_monthly_total:,.0f}", "80% attainment" if lang == 'en' else "80% alcanzado")
        with summary_cols[3]:
            st.metric(t('annual_ote', lang), f"${total_annual_ote:,.0f}")
        with summary_cols[4]:
            if 'monthly_ebitda' in locals() and monthly_ebitda > 0:
                stakeholder_annual = monthly_ebitda * (stakeholder_pct / 100) * 12
                st.metric(t('stakeholder_annual', lang), f"${stakeholder_annual:,.0f}", f"{stakeholder_pct}% EBITDA")
            else:
                st.metric(t('stakeholder_share', lang), f"{stakeholder_pct:.1f}%")
        
        # Show EBITDA impact
        st.markdown(f"**{t('ebitda_impact', lang)}:**")
        if 'monthly_revenue_total' in locals():
            comp_as_pct_revenue = (total_monthly_ote / monthly_revenue_total * 100) if monthly_revenue_total > 0 else 0
            st.caption(f"Team comp is **{comp_as_pct_revenue:.1f}%** of revenue (target: <40% for healthy margins)")
        
        # Commission Flow Visualization
        st.markdown("---")
        st.markdown(f"### {t('commission_flow', lang)}")
        
        import plotly.graph_objects as go
        
        # Toggle between monthly and per-deal view
        flow_view = st.radio(
            t('view', lang),
            [t('monthly_total', lang), t('per_deal', lang)],
            horizontal=True,
            key="commission_flow_view"
        )
        
        flow_cols = st.columns([2, 1])
        
        with flow_cols[0]:
            # ✅ FIXED: Use Deal Economics Manager for all calculations
            actual_revenue = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate) if 'gtm_metrics' in locals() else monthly_revenue_immediate
            actual_sales_count = gtm_metrics.get('monthly_sales', monthly_sales) if 'gtm_metrics' in locals() else monthly_sales
            
            # Get current deal economics
            current_deal_econ = DealEconomicsManager.get_current_deal_economics()
            
            # Per-deal or monthly
            if "Per Deal" in flow_view or "Por Negocio" in flow_view:
                # ✅ Unit case - per deal using Deal Economics Manager
                per_deal_comm = DealEconomicsManager.calculate_per_deal_commission(roles_comp, current_deal_econ)
                
                closer_pool = per_deal_comm['closer_pool']
                setter_pool = per_deal_comm['setter_pool']
                manager_pool = per_deal_comm['manager_pool']
                deal_for_commission = per_deal_comm['commission_base']
                stakeholder_pool = 0  # Stakeholders get EBITDA, not per-deal commission
                
                avg_deal_value_calculated = current_deal_econ['avg_deal_value']
                revenue_per_deal = current_deal_econ['upfront_cash']
                upfront_pct_display = int(current_deal_econ['upfront_pct'])
                
                policy_display = "Upfront (" + str(upfront_pct_display) + "%)" if per_deal_comm['policy'] == 'upfront' else "Full (100%)"
                title_text = f"Per Deal: ${avg_deal_value_calculated:,.0f} ({policy_display}) → Commissions"
            else:
                # ✅ Monthly total using Deal Economics Manager
                monthly_comm = DealEconomicsManager.calculate_monthly_commission(
                    actual_sales_count, roles_comp, current_deal_econ
                )
                
                closer_pool = monthly_comm['closer_pool']
                setter_pool = monthly_comm['setter_pool']
                manager_pool = monthly_comm['manager_pool']
                revenue_for_commission = monthly_comm['commission_base']
                stakeholder_pool = 0  # Placeholder
                
                upfront_pct_display = int(current_deal_econ['upfront_pct'])
                policy_display = "Upfront (" + str(upfront_pct_display) + "%)" if monthly_comm['per_deal']['policy'] == 'upfront' else "Full (100%)"
                title_text = f"Revenue → Pools → Per Person ({policy_display} Base)"
            
            # Create flow diagram
            fig_flow = go.Figure()
            
            # Revenue box - show appropriate value based on view
            if "Per Deal" in flow_view or "Por Negocio" in flow_view:
                revenue_display = avg_deal_value_calculated
                revenue_label = f"Deal Value<br>${avg_deal_value_calculated:,.0f}"
                hover_label = 'Deal Value'
            else:
                revenue_display = actual_revenue
                revenue_label = f"Revenue<br>${actual_revenue:,.0f}"
                hover_label = 'Monthly Revenue'
            
            fig_flow.add_trace(go.Scatter(
                x=[1], y=[3],
                mode='markers+text',
                marker=dict(size=100, color='#3b82f6'),
                text=[revenue_label],
                textfont=dict(color='white', size=12),
                textposition="middle center",
                showlegend=False,
                hovertemplate=f'<b>{hover_label}</b><br>${revenue_display:,.0f}<extra></extra>'
            ))
            
            # Commission pools
            fig_flow.add_trace(go.Scatter(
                x=[2.5, 2.5, 2.5], y=[4, 3, 2],
                mode='markers+text',
                marker=dict(size=[80, 80, 70], color='#f59e0b'),
                text=[f"Closer Pool<br>${closer_pool:,.0f}", 
                      f"Setter Pool<br>${setter_pool:,.0f}",
                      f"Manager Pool<br>${manager_pool:,.0f}"],
                textfont=dict(color='white', size=10),
                textposition="middle center",
                showlegend=False
            ))
            
            # Per-person amounts
            num_closers_calc = st.session_state.get('num_closers_main', num_closers)
            num_setters_calc = st.session_state.get('num_setters_main', num_setters)
            num_managers_calc = st.session_state.get('num_managers_main', num_managers)
            
            if num_closers_calc > 0:
                fig_flow.add_trace(go.Scatter(
                    x=[4], y=[4],
                    mode='markers+text',
                    marker=dict(size=60, color='#22c55e'),
                    text=[f"Per Closer<br>${closer_pool/num_closers_calc:,.0f}"],
                    textfont=dict(color='white', size=10),
                    textposition="middle center",
                    showlegend=False
                ))
            
            if num_setters_calc > 0:
                fig_flow.add_trace(go.Scatter(
                    x=[4], y=[3],
                    mode='markers+text',
                    marker=dict(size=60, color='#22c55e'),
                    text=[f"Per Setter<br>${setter_pool/num_setters_calc:,.0f}"],
                    textfont=dict(color='white', size=10),
                    textposition="middle center",
                    showlegend=False
                ))
            
            if num_managers_calc > 0:
                fig_flow.add_trace(go.Scatter(
                    x=[4], y=[2],
                    mode='markers+text',
                    marker=dict(size=60, color='#22c55e'),
                    text=[f"Per Manager<br>${manager_pool/num_managers_calc:,.0f}"],
                    textfont=dict(color='white', size=10),
                    textposition="middle center",
                    showlegend=False
                ))
            
            # Add arrows
            for y_pos in [4, 3, 2]:
                fig_flow.add_annotation(
                    x=2, y=y_pos, ax=1.3, ay=3,
                    xref="x", yref="y", axref="x", ayref="y",
                    arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#94a3b8"
                )
                fig_flow.add_annotation(
                    x=3.5, y=y_pos, ax=2.8, ay=y_pos,
                    xref="x", yref="y", axref="x", ayref="y",
                    arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#94a3b8"
                )
            
            fig_flow.update_layout(
                height=350,
                showlegend=False,
                xaxis=dict(visible=False, range=[0, 5]),
                yaxis=dict(visible=False, range=[1.5, 4.5]),
                margin=dict(l=0, r=0, t=20, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title=dict(text=title_text, font=dict(size=14, color='#e2e8f0'))
            )
            
            st.plotly_chart(fig_flow, use_container_width=True, key="commission_flow")
        
        with flow_cols[1]:
            if "Per Deal" in flow_view or "Por Negocio" in flow_view:
                st.markdown("**🎯 " + (t('per_deal', lang) if lang == 'es' else "Per Deal Economics") + "**")
                total_commission = closer_pool + setter_pool + manager_pool
                commission_rate = (total_commission/deal_for_commission)*100 if deal_for_commission > 0 else 0
                
                st.metric("Deal Value" if lang == 'en' else "Valor del Negocio", f"${avg_deal_value_calculated:,.0f}")
                st.metric(t('upfront_cash', lang), f"${revenue_per_deal:,.0f}", f"{int(upfront_pct_val*100)}%")
                st.metric(t('total_commission', lang), f"${total_commission:,.0f}")
                st.metric(t('commission_rate', lang), f"{commission_rate:.1f}%")
                
                st.markdown("---")
                st.markdown("**" + ("Desglose por Rol" if lang == 'es' else "Per-Role Breakdown") + "**")
                
                # Show per-role breakdown with per-person amounts in formatted markdown
                breakdown_text = ""
                if num_closers_calc > 0:
                    breakdown_text += f"💼 **{t('closers', lang)}**: ${closer_pool:,.0f} total  \n→ ${closer_pool/num_closers_calc:,.0f} each ({num_closers_calc}x)  \n\n"
                if num_setters_calc > 0:
                    breakdown_text += f"📞 **{t('setters', lang)}**: ${setter_pool:,.0f} total  \n→ ${setter_pool/num_setters_calc:,.0f} each ({num_setters_calc}x)  \n\n"
                if num_managers_calc > 0:
                    breakdown_text += f"👔 **{t('managers', lang)}**: ${manager_pool:,.0f} total  \n→ ${manager_pool/num_managers_calc:,.0f} each ({num_managers_calc}x)"
                
                st.markdown(breakdown_text)
            else:
                st.markdown("**📊 Monthly Total**")
                total_commission = closer_pool + setter_pool + manager_pool
                commission_rate = (total_commission/actual_revenue)*100 if actual_revenue > 0 else 0
                
                st.metric("Total Commission", f"${total_commission:,.0f}")
                st.metric("Commission Rate", f"{commission_rate:.1f}%")
                st.metric("Commission/Employee", 
                         f"${total_commission/(num_closers_calc+num_setters_calc+num_managers_calc):,.0f}" 
                         if (num_closers_calc+num_setters_calc+num_managers_calc) > 0 else "$0")
        
        # Period-Based Earnings Preview
        st.markdown("---")
        st.markdown(f"### {t('period_earnings', lang)}")
        
        working_days = st.session_state.get('working_days', 20)
        
        # ✅ FIXED: Use CommissionCalculator from Deal Economics Manager
        actual_sales_for_period = gtm_metrics.get('monthly_sales', monthly_sales) if 'gtm_metrics' in locals() else monthly_sales
        team_counts = {
            'closer': num_closers_calc,
            'setter': num_setters_calc,
            'manager': num_managers_calc,
            'bench': st.session_state.get('num_benchs_main', num_bench)
        }
        
        period_data = CommissionCalculator.calculate_period_earnings(
            roles_comp, actual_sales_for_period, team_counts, working_days
        )
        
        # ✅ Add stakeholder earnings (EBITDA-based) - simplified
        stakeholder_pct = st.session_state.get('stakeholder_pct', 10.0)
        
        # Calculate EBITDA using current values
        actual_revenue_for_ebitda = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate) if 'gtm_metrics' in locals() else monthly_revenue_immediate
        
        # Use already calculated commission from Deal Economics Manager
        monthly_comm_total = comm_calc['total_commission']
        total_monthly_base = comp_structure['monthly_base']
        cogs = total_monthly_base + monthly_comm_total
        gross_profit = actual_revenue_for_ebitda - cogs
        monthly_opex_calc = office_rent + software_costs + other_opex
        ebitda = gross_profit - monthly_opex_calc
        
        if ebitda > 0:
            stake_monthly = ebitda * (stakeholder_pct / 100)
            stake_daily = stake_monthly / 30
            stake_weekly = stake_monthly / 4.33
            stake_annual = stake_monthly * 12
            
            period_data.append({
                'Role': 'Stakeholders',
                'Count': 1,
                'Daily': f"${stake_daily:,.0f}",
                'Weekly': f"${stake_weekly:,.0f}",
                'Monthly': f"${stake_monthly:,.0f}",
                'Annual': f"${stake_annual:,.0f}",
                'vs OTE': f"{stakeholder_pct:.1f}% EBITDA"
            })
        
        if period_data:
            st.dataframe(
                pd.DataFrame(period_data), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Role": st.column_config.TextColumn("Role", width="small"),
                    "Count": st.column_config.NumberColumn("Count", width="small"),
                    "vs OTE": st.column_config.TextColumn("vs OTE", width="small")
                }
            )
        
        # Visual Daily Activity Requirements per Role
        st.markdown("---")
        st.markdown(f"### {t('daily_activities', lang)}")
        
        daily_leads = gtm_monthly_leads / working_days if working_days > 0 and 'gtm_monthly_leads' in locals() else 0
        daily_contacts = daily_leads * gtm_blended_contact_rate if 'gtm_blended_contact_rate' in locals() else 0
        daily_meetings_sched = gtm_monthly_meetings_scheduled / working_days if working_days > 0 and 'gtm_monthly_meetings_scheduled' in locals() else 0
        daily_meetings = gtm_monthly_meetings / working_days if working_days > 0 and 'gtm_monthly_meetings' in locals() else 0
        daily_sales = gtm_monthly_sales / working_days if working_days > 0 and 'gtm_monthly_sales' in locals() else 0
        
        # Create bar chart per role
        fig_daily = go.Figure()
        
        roles_visual = []
        leads_per_role = []
        contacts_per_role = []
        meetings_per_role = []
        sales_per_role = []
        
        if num_setters_calc > 0:
            roles_visual.append('Setters')
            leads_per_role.append(daily_leads / num_setters_calc)
            contacts_per_role.append(daily_contacts / num_setters_calc)
            meetings_per_role.append(daily_meetings_sched / num_setters_calc)
            sales_per_role.append(0)
        
        if num_closers_calc > 0:
            roles_visual.append('Closers')
            leads_per_role.append(0)
            contacts_per_role.append(0)
            meetings_per_role.append(daily_meetings / num_closers_calc)
            sales_per_role.append(daily_sales / num_closers_calc)
        
        fig_daily.add_trace(go.Bar(name='Leads', x=roles_visual, y=leads_per_role, marker_color='#3b82f6'))
        fig_daily.add_trace(go.Bar(name='Contacts', x=roles_visual, y=contacts_per_role, marker_color='#8b5cf6'))
        fig_daily.add_trace(go.Bar(name='Meetings', x=roles_visual, y=meetings_per_role, marker_color='#f59e0b'))
        fig_daily.add_trace(go.Bar(name='Sales', x=roles_visual, y=sales_per_role, marker_color='#22c55e'))
        
        fig_daily.update_layout(
            title=t('daily_activities_title', lang),
            barmode='group',
            height=300,
            xaxis_title="Role",
            yaxis_title="Activities per Day",
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0')
        )
        
        st.plotly_chart(fig_daily, use_container_width=True, key="daily_activities")
        
        # Save to session state
        st.session_state.roles_comp_custom = roles_comp
    
    # Deal Economics Configuration - Modular for Any Business Type
    with st.expander(f"{t('deal_economics', lang)}", expanded=False):
        st.info(f"🌐 {t('universal_deal', lang)}")
        
        # Business Type Selector with Templates
        biz_type_col1, biz_type_col2 = st.columns([1, 2])
        
        with biz_type_col1:
            business_type_options = [t('custom', lang), t('insurance', lang), t('saas', lang), t('consulting', lang), t('agency', lang), t('one_time_sale', lang)]
            business_type_map = {t('custom', lang): 'Custom', t('insurance', lang): 'Insurance', t('saas', lang): 'SaaS/Subscription', t('consulting', lang): 'Consulting/Services', t('agency', lang): 'Agency/Retainer', t('one_time_sale', lang): 'One-Time Sale'}
            
            business_type_display = st.selectbox(
                t('business_type_template', lang),
                business_type_options,
                key="business_type_template_display"
            )
            business_type = business_type_map.get(business_type_display, 'Custom')
        
        with biz_type_col2:
            # Show template description
            template_descriptions = {
                "Insurance": "🛡️ Upfront commission (70%) + Deferred at renewal (30%)",
                "SaaS/Subscription": "💻 Upfront commission (60%) + Monthly residuals (40%)",
                "Consulting/Services": "📈 Deposit upfront (50%) + Balance on completion (50%)",
                "Agency/Retainer": "🎯 Monthly retainer (100% upfront) or milestone-based",
                "One-Time Sale": "💵 Full payment upfront (100%)",
                "Custom": "⚙️ Define your own payment terms"
            }
            st.info(template_descriptions.get(business_type, ""))
        
        st.markdown("---")
        
        # Smart inputs based on business type
        deal_structure_cols = st.columns(3)
        
        with deal_structure_cols[0]:
            st.markdown(f"**{t('deal_value', lang)}**")
            
            # INSURANCE-SPECIFIC INPUTS (like Allianz)
            if business_type == "Insurance":
                st.markdown("📋 **Insurance Configuration**" if lang == 'en' else "📋 **Configuración de Seguros**")
                
                monthly_premium_mxn = st.number_input(
                    "Monthly Premium (MXN)" if lang == 'en' else "Prima Mensual (MXN)",
                    min_value=0,
                    value=int(st.session_state.get('monthly_premium_mxn', 3000)),
                    step=100,
                    key="monthly_premium_mxn",
                    help="Monthly premium charged to customer (e.g., 3,000 MXN for Allianz)"
                )
                
                contract_years = st.number_input(
                    "Contract Years" if lang == 'en' else "Años de Contrato",
                    min_value=1,
                    max_value=30,
                    value=int(st.session_state.get('insurance_contract_years', 18)),
                    step=1,
                    key="insurance_contract_years",
                    help="Duration of insurance policy"
                )
                
                carrier_commission_rate = st.slider(
                    "Carrier Commission Rate %" if lang == 'en' else "Tasa de Comisión Aseguradora %",
                    min_value=1.0,
                    max_value=5.0,
                    value=float(st.session_state.get('carrier_commission_rate', 2.7)),
                    step=0.1,
                    key="carrier_commission_rate",
                    help="Commission rate paid by insurance carrier (e.g., 2.7% for Allianz)"
                )
                
                # AUTO-CALCULATE deal value
                total_premium_value = monthly_premium_mxn * contract_years * 12
                avg_deal_value = int(total_premium_value * (carrier_commission_rate / 100))
                contract_length_months = contract_years * 12
                
                st.success(f"✅ Auto-calculated: ${avg_deal_value:,.0f} deal value")
                st.caption(f"Formula: {monthly_premium_mxn:,} MXN/mo × {contract_years} years × {carrier_commission_rate}% = ${avg_deal_value:,.0f}")
            
            # SAAS-SPECIFIC INPUTS
            elif business_type == "SaaS/Subscription":
                st.markdown("📋 **SaaS Configuration**" if lang == 'en' else "📋 **Configuración SaaS**")
                
                monthly_mrr = st.number_input(
                    "Monthly Recurring Revenue (MRR)" if lang == 'en' else "Ingreso Recurrente Mensual (MRR)",
                    min_value=0,
                    value=int(st.session_state.get('monthly_mrr', 5000)),
                    step=100,
                    key="monthly_mrr"
                )
                
                contract_length_months = st.number_input(
                    "Contract Length (months)" if lang == 'en' else "Duración de Contrato (meses)",
                    min_value=1,
                    max_value=36,
                    value=int(st.session_state.get('saas_contract_months', 12)),
                    step=1,
                    key="saas_contract_months"
                )
                
                # AUTO-CALCULATE
                avg_deal_value = monthly_mrr * contract_length_months
                st.success(f"✅ Auto-calculated: ${avg_deal_value:,.0f} ACV")
                st.caption(f"Formula: ${monthly_mrr:,}/mo × {contract_length_months} months")
            
            # CONSULTING/SERVICES
            elif business_type == "Consulting/Services":
                st.markdown("📋 **Project Configuration**" if lang == 'en' else "📋 **Configuración de Proyecto**")
                
                avg_deal_value = st.number_input(
                    "Average Project Value" if lang == 'en' else "Valor Promedio del Proyecto",
                    min_value=0,
                    value=int(st.session_state.get('project_value', 50000)),
                    step=1000,
                    key="project_value"
                )
                
                contract_length_months = st.number_input(
                    "Project Duration (months)" if lang == 'en' else "Duración del Proyecto (meses)",
                    min_value=1,
                    max_value=24,
                    value=int(st.session_state.get('project_duration_months', 3)),
                    step=1,
                    key="project_duration_months"
                )
            
            # ONE-TIME SALE
            elif business_type == "One-Time Sale":
                st.markdown("📋 **Sale Configuration**" if lang == 'en' else "📋 **Configuración de Venta**")
                
                avg_deal_value = st.number_input(
                    "Average Sale Price" if lang == 'en' else "Precio Promedio de Venta",
                    min_value=0,
                    value=int(st.session_state.get('sale_price', 10000)),
                    step=500,
                    key="sale_price"
                )
                contract_length_months = 1  # One-time sale
            
            # AGENCY/RETAINER
            elif business_type == "Agency/Retainer":
                st.markdown("📋 **Retainer Configuration**" if lang == 'en' else "📋 **Configuración de Retainer**")
                
                monthly_retainer = st.number_input(
                    "Monthly Retainer" if lang == 'en' else "Retainer Mensual",
                    min_value=0,
                    value=int(st.session_state.get('monthly_retainer', 10000)),
                    step=500,
                    key="monthly_retainer"
                )
                
                contract_length_months = st.number_input(
                    "Retainer Duration (months)" if lang == 'en' else "Duración del Retainer (meses)",
                    min_value=1,
                    max_value=24,
                    value=int(st.session_state.get('retainer_duration_months', 6)),
                    step=1,
                    key="retainer_duration_months"
                )
                
                # AUTO-CALCULATE
                avg_deal_value = monthly_retainer * contract_length_months
                st.success(f"✅ Auto-calculated: ${avg_deal_value:,.0f} total value")
            
            # CUSTOM (original universal inputs)
            else:
                avg_deal_value = st.number_input(
                    t('avg_deal_value', lang),
                    min_value=0,
                    value=int(st.session_state.get('avg_deal_value', 50000)),
                    step=1000,
                    key="avg_deal_value",
                    help="Total value of an average deal/contract"
                )
                
                contract_length_months = st.number_input(
                    t('contract_length', lang),
                    min_value=1,
                    max_value=120,
                    value=st.session_state.get('contract_length_months', 12),
                    step=1,
                    key="contract_length_months",
                    help="Duration of contract/engagement (1 for one-time sales)"
                )
        
        with deal_structure_cols[1]:
            st.markdown("**📅 Payment Terms (Modular)**")
            
            # Upfront percentage
            default_upfront_pct = 70.0 if business_type == "Insurance" else 60.0 if business_type == "SaaS/Subscription" else 50.0 if business_type == "Consulting/Services" else 100.0
            upfront_pct = st.slider(
                "Upfront Payment %",
                0.0,
                100.0,
                st.session_state.get('upfront_payment_pct', default_upfront_pct),
                1.0,
                key="upfront_payment_pct",
                help="% of deal value received upfront/immediately"
            )
            
            deferred_pct = 100.0 - upfront_pct
            st.metric(t('deferred_payment_pct', lang), f"{deferred_pct:.0f}%")
            
            # Deferred payment timing
            if deferred_pct > 0:
                deferred_timing_months = st.number_input(
                    "Deferred Payment After (months)",
                    min_value=1,
                    max_value=60,
                    value=st.session_state.get('deferred_timing_months', 18 if business_type == "Insurance" else 1),
                    step=1,
                    key="deferred_timing_months",
                    help="When deferred payment is received (e.g., 18 months for insurance renewal)"
                )
        
        with deal_structure_cols[2]:
            st.markdown(f"**{t('deal_breakdown', lang)}**")
            
            # Calculate upfront and deferred amounts
            comp_immediate_val = avg_deal_value * (upfront_pct / 100)
            comp_deferred_val = avg_deal_value * (deferred_pct / 100)
            
            st.metric(t('total_deal_value', lang), f"${avg_deal_value:,.0f}")
            st.metric(t('upfront_cash', lang), f"${comp_immediate_val:,.0f}", f"{upfront_pct:.0f}%")
            
            if deferred_pct > 0:
                st.metric(
                    t('deferred_cash', lang), 
                    f"${comp_deferred_val:,.0f}",
                    f"{deferred_pct:.0f}% at month {deferred_timing_months if 'deferred_timing_months' in locals() else 1}"
                )
            else:
                st.metric(t('deferred_cash', lang), "$0", "No deferred payment" if lang == 'en' else "Sin pago diferido")
        
        # Commission Payment Policy
        st.markdown("---")
        st.markdown("**💰 Commission Payment Policy**")
        st.info(f"🎯 {t('commission_policy', lang)}")
        
        policy_cols = st.columns([2, 1])
        with policy_cols[0]:
            commission_policy = st.radio(
                t('pay_commissions_from', lang),
                [t('upfront_cash_only', lang), t('full_deal_value', lang)],
                index=0 if st.session_state.get('commission_policy', 'upfront') == 'upfront' else 1,
                horizontal=True,
                key="commission_policy_selector",
                help="Choose whether commissions are calculated on upfront cash only or full deal value"
            )
            
            # Store policy in session state
            if "Upfront" in commission_policy or "Inicial" in commission_policy:
                st.session_state['commission_policy'] = 'upfront'
            else:
                st.session_state['commission_policy'] = 'full'
        
        with policy_cols[1]:
            # Show commission base amount
            policy_val = st.session_state.get('commission_policy', 'upfront')
            if policy_val == 'upfront':
                comm_base_amount = comp_immediate_val
                comm_base_label = f"${comm_base_amount:,.0f} ({upfront_pct:.0f}%)"
            else:
                comm_base_amount = avg_deal_value
                comm_base_label = f"${comm_base_amount:,.0f} (100%)"
            
            st.metric(t('commission_base', lang), comm_base_label)
            st.caption("This is the base amount for commission calculations")
        
        # Additional context
        st.markdown("---")
        st.markdown("**💡 Use Cases by Business Type:**")
        
        use_case_cols = st.columns(3)
        
        with use_case_cols[0]:
            st.caption("👉 **Insurance**: 70/30 split, deferred at renewal (18mo)")
            st.caption("👉 **SaaS**: 60% upfront, 40% as monthly residuals")
        
        with use_case_cols[1]:
            st.caption("👉 **Consulting**: 50% deposit, 50% on completion")
            st.caption("👉 **Agency**: 100% upfront monthly retainer")
        
        with use_case_cols[2]:
            st.caption("👉 **Milestone-based**: Custom splits (e.g., 25/50/25)")
            st.caption("👉 **One-time**: 100% upfront, no deferred")
        
        # Store values for use in calculations
        total_comp_main = avg_deal_value
        avg_pm_main = avg_deal_value / contract_length_months if contract_length_months > 0 else avg_deal_value
        contract_years_main = contract_length_months / 12
    
    # Operating Costs Configuration (Marketing moved to channels)
    with st.expander(f"{t('operating_costs', lang)}", expanded=False):
        ops_col1, ops_col2, ops_col3 = st.columns(3)
        
        with ops_col1:
            st.markdown("**Fixed Costs**")
            office_rent_main = st.number_input("Office Rent ($)", value=office_rent, step=500, key="rent_main")
            software_costs_main = st.number_input("Software ($)", value=software_costs, step=100, key="software_main")
            other_opex_main = st.number_input("Other OpEx ($)", value=other_opex, step=500, key="opex_main")
        
        with ops_col2:
            st.markdown("**Cost Summary**")
            total_opex_main = office_rent_main + software_costs_main + other_opex_main
            st.metric("Total OpEx", f"${total_opex_main:,.0f}/mo")
            st.metric("Annual OpEx", f"${total_opex_main*12:,.0f}")
            st.metric("Per Employee", f"${total_opex_main/max(1,team_total):.0f}")
        
        with ops_col3:
            st.markdown("**Efficiency Metrics**")
            opex_per_sale = total_opex_main / max(1, monthly_sales)
            opex_ratio = total_opex_main / max(1, monthly_revenue_total)
            st.metric("OpEx per Sale", f"${opex_per_sale:.0f}")
            st.metric("OpEx Ratio", f"{opex_ratio*100:.1f}%")
            if opex_ratio > 0.3:
                st.warning("🟡 High OpEx ratio")
            else:
                st.success("✅ Healthy OpEx")

            st.markdown("**Liquidity**")
            default_cash_balance = st.session_state.get(
                "cash_balance_main",
                float(total_opex_main * 3)
            )
            cash_balance_main = st.number_input(
                "Cash on Hand ($)",
                min_value=0.0,
                value=float(default_cash_balance),
                step=50000.0,
                key="cash_balance_input"
            )
            st.session_state["cash_balance_main"] = cash_balance_main
    
    # What-If Analysis Configuration
    with st.expander(f"{t('whatif_scenario', lang)}", expanded=False):
        whatif_col1, whatif_col2 = st.columns(2)
        
        with whatif_col1:
            st.markdown("**Adjust Variables**")
            close_change = st.number_input("Close Rate Change (%)", min_value=-50, max_value=50, value=st.session_state.get('close_change_main', 0), step=5, key="close_change_main")
            deal_change = st.number_input("Deal Size Change (%)", min_value=-50, max_value=50, value=st.session_state.get('deal_change_main', 0), step=5, key="deal_change_main")
            cost_change = st.number_input("Cost Reduction (%)", min_value=0, max_value=50, value=st.session_state.get('cost_change_main', 0), step=5, key="cost_change_main")
            team_change = st.number_input("Add Closers", min_value=0, max_value=10, value=st.session_state.get('team_change_main', 0), step=1, key="team_change_main")
        
        with whatif_col2:
            st.markdown("**Impact Results**")
            
            # Close rate impact
            if close_change != 0:
                new_close = close_rate * (1 + close_change/100)
                new_sales = monthly_meetings * new_close
                impact_revenue = (new_sales - monthly_sales) * comp_immediate
                st.metric("Revenue from Close Rate", f"${impact_revenue:,.0f}", f"{close_change:+d}%")
            
            # Deal size impact
            if deal_change != 0:
                new_deal = comp_immediate * (1 + deal_change/100)
                impact_revenue = monthly_sales * (new_deal - comp_immediate)
                st.metric("Revenue from Deal Size", f"${impact_revenue:,.0f}", f"{deal_change:+d}%")
            
            # Cost reduction impact
            if cost_change != 0:
                cost_savings = monthly_costs_before_fees * (cost_change/100)
                new_ebitda = monthly_ebitda + cost_savings
                st.metric("EBITDA Improvement", f"${cost_savings:,.0f}", f"{cost_change}% saved")
            
            # Team expansion impact (uses current capacity settings)
            if team_change != 0:
                cap_settings = get_capacity_metrics(num_closers_main if 'num_closers_main' in locals() else num_closers,
                                                   num_setters_main if 'num_setters_main' in locals() else num_setters)
                meetings_per_closer_change = cap_settings['meetings_per_closer']
                working_days_change = cap_settings['working_days']
                capacity_increase = team_change * meetings_per_closer_change * working_days_change
                potential_sales = capacity_increase * close_rate
                potential_revenue = potential_sales * comp_immediate
                st.metric("Sales Potential", f"+{potential_sales:.0f} sales", f"${potential_revenue:,.0f}")
    
    # Use the main page values if they exist, otherwise use sidebar values
    if 'target_period_main' in locals():
        monthly_revenue_target = monthly_revenue_target_main
        annual_revenue = annual_revenue_main
    if 'num_closers_main' in locals():
        num_closers = num_closers_main
        num_setters = num_setters_main
        num_bench = num_bench_main
        num_managers = num_managers_main
        team_total = team_total_main
        active_ratio = active_ratio_main
    if 'contact_rate_main' in locals():
        contact_rate = contact_rate_main
        meeting_rate = meeting_rate_main
        show_up_rate = show_up_rate_main
        close_rate = close_rate_main
    if 'avg_pm_main' in locals():
        avg_pm = avg_pm_main
        if 'total_comp_main' in locals():
            total_comp = total_comp_main
            comp_immediate = comp_immediate_val
            comp_deferred = comp_deferred_val
    if 'office_rent_main' in locals():
        office_rent = office_rent_main
        software_costs = software_costs_main
        other_opex = other_opex_main
    
    # MULTI-CHANNEL GTM INTEGRATION
    st.markdown("### 🚀 Multi-Channel GTM Configuration")
    
    # Initialize session state for channels
    if 'gtm_channels' not in st.session_state:
        st.session_state.gtm_channels = [
            {
                'id': 'channel_1',
                'name': 'Primary Channel',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            }
        ]
    
    # Channel management in compact form
    ch_col1, ch_col2, ch_col3, ch_col4 = st.columns([1.5, 1.5, 2, 3])
    with ch_col1:
        if st.button("➕ Add Channel", use_container_width=True, key="add_channel_main"):
            new_id = f"channel_{len(st.session_state.gtm_channels) + 1}"
            st.session_state.gtm_channels.append({
                'id': new_id,
                'name': f'Channel {len(st.session_state.gtm_channels) + 1}',
                'segment': 'SMB',
                'lead_source': 'Inbound Marketing',
                'icon': '🏢'
            })
            st.rerun()
    
    with ch_col2:
        if len(st.session_state.gtm_channels) > 1:
            if st.button("🗑️ Remove Last", use_container_width=True, key="remove_channel_main"):
                st.session_state.gtm_channels.pop()
                st.rerun()
    
    with ch_col3:
        template = st.selectbox(
            "Templates:",
            options=['Custom', 'SMB+MID+ENT', 'Inbound+Outbound'],
            key="gtm_template_main"
        )
    
    with ch_col4:
        st.info(f"Managing {len(st.session_state.gtm_channels)} channel(s)")
    
    # Configure channels in expandable sections
    channels = []
    for idx, channel_config in enumerate(st.session_state.gtm_channels):
        with st.expander(f"{channel_config.get('icon', '📊')} **{channel_config.get('name', f'Channel {idx+1}')}**", expanded=(idx == 0)):
            # Quick configuration in columns
            cfg_col1, cfg_col2, cfg_col3 = st.columns(3)
            
            with cfg_col1:
                channel_name = st.text_input("Name", value=channel_config['name'], key=f"main_{channel_config['id']}_name")
                segment = st.selectbox("Segment", ['SMB', 'MID', 'ENT'], key=f"main_{channel_config['id']}_segment")
                
                # Dynamic cost input method per channel
                cost_point = st.selectbox(
                    "Cost Input Point",
                    ["Cost per Lead", "Cost per Contact", "Cost per Meeting", "Cost per Sale", "Total Budget"],
                    key=f"main_{channel_config['id']}_cost_point"
                )
                
                # Dynamic quantity input based on cost point
                # Input the quantity that matches the cost point
                if cost_point == "Cost per Lead":
                    cpl = st.number_input("Cost per Lead ($)", value=channel_config.get('cpl', 50), step=10, key=f"main_{channel_config['id']}_cpl_direct")
                    leads = st.number_input("Monthly Leads", value=channel_config.get('monthly_leads', 1000), step=100, key=f"main_{channel_config['id']}_leads")
                    
                elif cost_point == "Cost per Contact":
                    cost_per_contact = st.number_input("Cost per Contact ($)", value=channel_config.get('cost_per_contact', 75), step=10, key=f"main_{channel_config['id']}_cpc")
                    contacts_target = st.number_input("Monthly Contacts Target", value=channel_config.get('contacts_target', 650), step=50, key=f"main_{channel_config['id']}_contacts")
                    # Leads will be calculated after we get contact rate
                    leads = contacts_target  # Temporary, will recalculate with actual rate
                    cpl = cost_per_contact  # Temporary
                    
                elif cost_point == "Cost per Meeting":
                    cost_per_meeting = st.number_input("Cost per Meeting ($)", value=channel_config.get('cost_per_meeting', 200), step=25, key=f"main_{channel_config['id']}_cpm")
                    meetings_target = st.number_input("Monthly Meetings Target", value=channel_config.get('meetings_target', 20), step=5, key=f"main_{channel_config['id']}_meetings")
                    # Leads will be calculated after we get conversion rates
                    leads = meetings_target * 5  # Rough estimate
                    cpl = cost_per_meeting / 5  # Temporary
                    
                elif cost_point == "Cost per Sale":
                    cost_per_sale = st.number_input("Cost per Sale ($)", value=channel_config.get('cost_per_sale', 500), step=50, key=f"main_{channel_config['id']}_cps")
                    sales_target = st.number_input("Monthly Sales Target", value=channel_config.get('sales_target', 5), step=1, key=f"main_{channel_config['id']}_sales")
                    # Leads will be calculated after we get conversion rates
                    leads = sales_target * 20  # Rough estimate
                    cpl = cost_per_sale / 20  # Temporary
                    
                else:  # Total Budget
                    total_budget = st.number_input("Total Budget ($)", value=channel_config.get('total_budget', 10000), step=1000, key=f"main_{channel_config['id']}_budget")
                    # For budget, still ask for estimated leads
                    leads = st.number_input("Estimated Monthly Leads", value=channel_config.get('monthly_leads', 1000), step=100, key=f"main_{channel_config['id']}_leads_budget")
                    cpl = total_budget / leads if leads > 0 else 0
            
            with cfg_col2:
                contact_rt = st.slider("Contact %", 0, 100, int(channel_config.get('contact_rate', 0.65) * 100), 5, key=f"main_{channel_config['id']}_contact") / 100
                meeting_rt = st.slider("Meeting %", 0, 100, int(channel_config.get('meeting_rate', 0.40) * 100), 5, key=f"main_{channel_config['id']}_meeting") / 100
                showup_rt = st.slider("Show-up %", 0, 100, int(channel_config.get('show_up_rate', 0.70) * 100), 5, key=f"main_{channel_config['id']}_showup") / 100
                close_rt = st.slider("Close %", 0, 100, int(channel_config.get('close_rate', 0.25) * 100), 5, key=f"main_{channel_config['id']}_close") / 100
                
                # Now calculate actual leads needed based on target quantities and rates
                if cost_point == "Cost per Contact":
                    # Calculate leads from contact target
                    leads = contacts_target / contact_rt if contact_rt > 0 else contacts_target
                    cpl = cost_per_contact / contact_rt if contact_rt > 0 else cost_per_contact
                    st.info(f"📊 Need {leads:.0f} leads to get {contacts_target} contacts")
                    
                elif cost_point == "Cost per Meeting":
                    # Calculate leads from meeting target
                    conversion_to_meeting = contact_rt * meeting_rt * showup_rt
                    leads = meetings_target / conversion_to_meeting if conversion_to_meeting > 0 else meetings_target * 5
                    cpl = cost_per_meeting / conversion_to_meeting if conversion_to_meeting > 0 else cost_per_meeting
                    st.info(f"📊 Need {leads:.0f} leads to get {meetings_target} meetings")
                    
                elif cost_point == "Cost per Sale":
                    # Calculate leads from sales target
                    full_conversion = contact_rt * meeting_rt * showup_rt * close_rt
                    leads = sales_target / full_conversion if full_conversion > 0 else sales_target * 20
                    cpl = cost_per_sale / full_conversion if full_conversion > 0 else cost_per_sale
                    st.info(f"📊 Need {leads:.0f} leads to get {sales_target} sales")
                    
                elif cost_point == "Total Budget":
                    cpl = total_budget / leads if leads > 0 else 0
                    st.info(f"📊 Effective CPL: ${cpl:.2f}")
            
            with cfg_col3:
                # Use the deal value from insurance model
                st.markdown("**Deal Value (from Insurance Model)**")
                st.info(f"💰 Deal Value: ${total_comp:,.0f}")
                st.caption(f"• Contract: ${total_contract_value:,.0f} MXN")
                st.caption(f"• Commission: {carrier_rate*100:.1f}%")
                st.caption(f"• Upfront: ${comp_immediate:,.0f}")
                st.caption(f"• Month 18: ${comp_deferred:,.0f}")
                
                cycle_days = st.slider("Sales Cycle", 7, 180, 30, 7, key=f"main_{channel_config['id']}_cycle")
                source = st.selectbox("Source", ['Inbound', 'Outbound', 'Partner', 'Events'], key=f"main_{channel_config['id']}_source")
            
            # Calculate channel metrics with proper cost point handling
            # The key is to calculate total marketing cost correctly based on selected method
            if cost_point == "Cost per Lead":
                total_marketing_cost = leads * cpl
            elif cost_point == "Cost per Contact":
                contacts_needed = leads * contact_rt
                total_marketing_cost = contacts_needed * cost_per_contact
            elif cost_point == "Cost per Meeting":
                meetings_from_channel = leads * contact_rt * meeting_rt * showup_rt
                total_marketing_cost = meetings_from_channel * cost_per_meeting
            elif cost_point == "Cost per Sale":
                sales_from_channel = leads * contact_rt * meeting_rt * showup_rt * close_rt
                total_marketing_cost = sales_from_channel * cost_per_sale
            elif cost_point == "Total Budget":
                total_marketing_cost = total_budget
            
            # Now define channel with corrected metrics - using deal value from insurance model
            channel = MultiChannelGTM.define_channel(
                name=channel_name,
                lead_source=source,
                segment=segment,
                monthly_leads=leads,
                contact_rate=contact_rt,
                meeting_rate=meeting_rt,
                show_up_rate=showup_rt,
                close_rate=close_rt,
                avg_deal_value=total_comp,  # Use total compensation from insurance model
                cpl=total_marketing_cost / leads if leads > 0 else 0,  # Effective CPL
                sales_cycle_days=cycle_days
            )
            
            # Add comprehensive cost info to channel
            channel['cost_point'] = cost_point
            channel['total_marketing_cost'] = total_marketing_cost
            channel['effective_cpl'] = total_marketing_cost / leads if leads > 0 else 0
            
            # Recalculate CAC based on actual total cost
            channel['cac'] = total_marketing_cost / channel['sales'] if channel['sales'] > 0 else 0
            
            # Calculate proper LTV and metrics using insurance model
            channel['ltv'] = total_comp  # Use full deal value from insurance model
            channel['ltv_cac'] = channel['ltv'] / channel['cac'] if channel['cac'] > 0 else 0
            channel['roas'] = channel['revenue'] / total_marketing_cost if total_marketing_cost > 0 else 0
            
            channels.append(channel)
            
            # Show channel metrics (without duplicate ROAS)
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
    
    # Aggregate all channels and show comprehensive funnel breakdown
    if channels:
        aggregated = MultiChannelGTM.aggregate_channels(channels)

        cap_settings = get_capacity_metrics(num_closers, num_setters)
        working_days_effective = max(cap_settings['working_days'], 1)
        monthly_closer_capacity = cap_settings['monthly_closer_capacity']
        monthly_setter_capacity = cap_settings['monthly_setter_capacity']

        # Update global metrics from channels (use aggregated values)
        monthly_leads = aggregated.get('total_leads', monthly_leads)
        monthly_sales = aggregated.get('total_sales', monthly_sales)
        monthly_revenue_total = aggregated.get('total_revenue', monthly_revenue_total)
        monthly_contacts = aggregated.get('total_contacts', 0)
        monthly_meetings_scheduled = aggregated.get('total_meetings_scheduled', 0)
        monthly_meetings = aggregated.get('total_meetings_held', 0)
        blended_contact_rate = aggregated.get('blended_contact_rate', 0)
        blended_meeting_rate = aggregated.get('blended_meeting_rate', 0)
        blended_showup_rate = aggregated.get('blended_show_up_rate', 0)
        blended_close_rate = aggregated.get('blended_close_rate', 0)
        
        # Recalculate revenue components based on channel sales
        monthly_revenue_immediate = monthly_sales * comp_immediate
        monthly_revenue_deferred = monthly_sales * comp_deferred
        monthly_revenue_total = monthly_revenue_immediate + monthly_revenue_deferred
        
        # Persist GTM metrics for team capacity section
        st.session_state['gtm_metrics'] = {
            'monthly_leads': monthly_leads,
            'monthly_meetings_scheduled': monthly_meetings_scheduled,
            'monthly_meetings': monthly_meetings,
            'monthly_sales': monthly_sales,
            'monthly_revenue_immediate': monthly_revenue_immediate,
            'monthly_revenue_total': monthly_revenue_total,
            'blended_contact_rate': blended_contact_rate
        }

        # Recalculate financial metrics with updated values
        # Total costs (marketing + compensation + opex)
        total_marketing_costs = aggregated.get('total_cost', sum(ch.get('total_marketing_cost', 0) for ch in channels))
        total_sales_comp = monthly_sales * (comp_immediate + comp_deferred) * 0.3  # Assume 30% goes to sales team
        monthly_total_costs = total_marketing_costs + total_sales_comp + monthly_opex
        
        # EBITDA calculation
        monthly_ebitda = monthly_revenue_total - monthly_total_costs
        ebitda_margin = monthly_ebitda / monthly_revenue_total if monthly_revenue_total > 0 else 0
        
        # CAC and other metrics
        cac = total_marketing_costs / monthly_sales if monthly_sales > 0 else 0
        ltv = total_comp  # Use insurance model value
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        roas = monthly_revenue_total / total_marketing_costs if total_marketing_costs > 0 else 0
        # Update global spend & payback with channel-derived values
        monthly_marketing = total_marketing_costs
        payback_months = cac / (comp_immediate / 12) if comp_immediate > 0 else 999
        
        # ENHANCED BUSINESS PERFORMANCE DASHBOARD V2
        if create_business_performance_dashboard:
            # Get actual revenue for calculations
            actual_revenue_for_dash = gtm_metrics.get('monthly_revenue_immediate', monthly_revenue_immediate)
            
            # Calculate monthly compensation safely
            if comp_structure and isinstance(comp_structure, dict) and 'monthly_base' in comp_structure:
                monthly_base_comp = comp_structure['monthly_base']
            else:
                monthly_base_comp = (num_closers * 32000 + num_setters * 16000 + num_managers * 72000 + num_bench * 12500) / 12
            
            # Get commission rates safely
            closer_comm_safe = closer_comm_pct if 'closer_comm_pct' in locals() else 0.20
            setter_comm_safe = setter_comm_pct if 'setter_comm_pct' in locals() else 0.03
            
            # Prepare metrics for the enhanced dashboard
            cash_balance_value = st.session_state.get("cash_balance_main", float(monthly_opex * 3))

            financial_metrics = {
                'monthly_revenue_target': monthly_revenue_target,
                'monthly_marketing': cost_breakdown.get('total_marketing_spend', monthly_marketing) if 'cost_breakdown' in locals() else monthly_marketing,
                'monthly_opex': monthly_opex,
                'monthly_compensation': monthly_base_comp + (actual_revenue_for_dash * (closer_comm_safe + setter_comm_safe)),
                'cac': cac,
                'ltv': ltv,
                'payback_months': payback_months,
                'cash_balance': cash_balance_value,
                'gov_fee_pct': gov_fee_pct
            }
            
            team_metrics_dash = {
                'total_team': team_total,
                'num_closers': num_closers,
                'num_setters': num_setters
            }
            
            operational_metrics = {
                'monthly_leads': monthly_leads,
                'monthly_meetings': monthly_meetings,
                'monthly_sales': monthly_sales,
                'close_rate': blended_close_rate,
                'sales_cycle_days': sales_cycle_days
            }
            
            # Call the enhanced business performance module
            create_business_performance_dashboard(
                gtm_metrics=gtm_metrics,
                financial_metrics=financial_metrics,
                team_metrics=team_metrics_dash,
                operational_metrics=operational_metrics
            )
        else:
            # Fallback to standard dashboard if module not available
            st.markdown("### 📊 Business Performance Dashboard")
            st.warning("⚠️ Enhanced Business Performance module not available. Using standard dashboard.")
            
            # Primary KPIs - Most Important (First Row)
            st.markdown("**Primary Business Metrics**")
            primary_cols = st.columns(6)
            
            with primary_cols[0]:
                st.metric("💵 Monthly Revenue", f"${monthly_revenue_total:,.0f}", f"{(monthly_revenue_total/monthly_revenue_target - 1)*100:.1f}% vs target")
            with primary_cols[1]:
                st.metric("💰 EBITDA", f"${monthly_ebitda:,.0f}", f"{ebitda_margin:.1%} margin")
            with primary_cols[2]:
                st.metric("🎯 LTV:CAC", f"{ltv_cac_ratio:.1f}:1", "Target: >3:1")
            with primary_cols[3]:
                st.metric("🚀 ROAS", f"{roas:.1f}x", f"Target: >4x")
            with primary_cols[4]:
                cap_settings = get_capacity_metrics(num_closers, num_setters)
                monthly_closer_capacity = cap_settings['monthly_closer_capacity']
                capacity_util = monthly_meetings / monthly_closer_capacity if monthly_closer_capacity > 0 else 0
                st.metric("📅 Capacity Used", f"{capacity_util:.0%}", "OK" if capacity_util < 0.9 else "Overloaded")
            with primary_cols[5]:
                if monthly_meetings > 0 and blended_close_rate > 0:
                    pipeline_value = monthly_meetings * comp_immediate / blended_close_rate
                    pipeline_coverage = pipeline_value / monthly_revenue_target if monthly_revenue_target > 0 else 0
                else:
                    pipeline_coverage = 0
                st.metric("📊 Pipeline Coverage", f"{pipeline_coverage:.1f}x", "Good" if pipeline_coverage >= 3 else "Low")
        
        # Sales Activity Metrics (Second Row)
        st.markdown("**Sales Activity**")
        activity_cols = st.columns(5)
        
        with activity_cols[0]:
            st.metric("👥 Leads", f"{monthly_leads:,.0f}/mo", f"{daily_leads:.0f}/day")
        with activity_cols[1]:
            st.metric("🤝 Meetings", f"{monthly_meetings:,.0f}/mo", f"{monthly_meetings/working_days_effective:.0f}/day")
        with activity_cols[2]:
            per_closer_daily_capacity = per_closer_capacity / working_days_effective if working_days_effective > 0 else 0
            st.metric("✅ Monthly Sales", f"{monthly_sales:.0f}",
                    f"{monthly_sales/num_closers:.1f} per closer" if num_closers > 0 else "N/A")
        with activity_cols[3]:
            st.metric("📈 Close Rate", f"{blended_close_rate:.0%}", f"Show-up: {blended_showup_rate:.0%}")
        with activity_cols[4]:
            st.metric("🕒 Sales Cycle", f"{sales_cycle_days} days", f"Velocity: {monthly_sales/sales_cycle_days*30:.0f}/mo" if sales_cycle_days > 0 else "-")
        
        # Financial Details (Third Row)
        st.markdown("**Financial Performance**")
        finance_cols = st.columns(5)
        
        with finance_cols[0]:
            st.metric("💳 CAC", f"${cac:,.0f}", f"LTV: ${ltv:,.0f}")
        with finance_cols[1]:
            st.metric("⏱️ Payback", f"{payback_months:.1f} mo", "Target: <18m")
        with finance_cols[2]:
            st.metric(
                "📈 Revenue (Imm)",
                f"${monthly_revenue_immediate:,.0f}",
                "70% split",
                help="Cash collected upfront in month 1 from current sales (immediate commission portion)."
            )
        with finance_cols[3]:
            st.metric(
                "📅 Revenue (Def)",
                f"${monthly_revenue_deferred:,.0f}",
                "30% split",
                help="Deferred revenue scheduled for month 18 based on retained deals (deferred commission portion)."
            )
        with finance_cols[4]:
            st.metric("🏢 Team", f"{team_total} people", f"Burn: ${monthly_opex:,.0f}/mo")
        
        # Sales Process Timeline - Moved from Analytics section
        st.markdown("**Sales Process & Pipeline Stages**")
        
        # Create a visual timeline of the sales process
        timeline_data = [
            {"stage": "Lead Generated", "day": 0, "icon": "👥", "count": monthly_leads},
            {"stage": "First Contact", "day": 1, "icon": "📞", "count": monthly_contacts},
            {"stage": "Meeting Scheduled", "day": 3, "icon": "📅", "count": monthly_meetings_scheduled},
            {"stage": "Meeting Held", "day": 5, "icon": "🤝", "count": monthly_meetings},
            {"stage": "Deal Closed", "day": sales_cycle_days, "icon": "✅", "count": monthly_sales},
        ]
        
        # Create compact timeline visualization
        timeline_cols = st.columns(len(timeline_data))
        
        for idx, stage_data in enumerate(timeline_data):
            with timeline_cols[idx]:
                # Calculate conversion rate from previous stage
                if idx > 0:
                    prev_count = timeline_data[idx-1]['count']
                    conversion = (stage_data['count'] / prev_count * 100) if prev_count > 0 else 0
                    color = "#4CAF50" if conversion >= 70 else "#FF9800" if conversion >= 50 else "#F44336"
                else:
                    conversion = 100
                    color = "#2196F3"
                
                st.metric(
                    stage_data['icon'] + " " + stage_data['stage'],
                    f"{stage_data['count']:.0f}",
                    f"Day {stage_data['day']} | {conversion:.0f}%" if idx > 0 else f"Day {stage_data['day']}"
                )
        
        # Timing metrics row
        timing_metrics = st.columns(4)
        with timing_metrics[0]:
            st.metric("🕒 Lead to Meeting", "5 days")
        with timing_metrics[1]:
            st.metric("⏱️ Meeting to Close", f"{sales_cycle_days - 5} days")
        with timing_metrics[2]:
            velocity = monthly_sales / sales_cycle_days * 30 if sales_cycle_days > 0 else 0
            st.metric("🚀 Sales Velocity", f"{velocity:.1f} deals/mo", help="Projection of monthly deal throughput based on current closes and sales cycle length.")
        with timing_metrics[3]:
            st.metric("🎯 Win Rate", f"{blended_close_rate:.1%}")
        
        # Channel-specific metrics
        st.markdown("**Channel Performance**")
        channel_summary = st.columns(4)
        with channel_summary[0]:
            st.metric("Total Channel Leads", f"{monthly_leads:,.0f}")
        with channel_summary[1]:
            st.metric("Total Channel Sales", f"{monthly_sales:,.0f}")
        with channel_summary[2]:
            st.metric("Blended CAC", f"${aggregated.get('blended_cac', cac):,.0f}")
        with channel_summary[3]:
            st.metric("Blended Close Rate", f"{blended_close_rate:.1%}")
        
        # Channel comparison table
        st.markdown("### 📈 Channel Performance Breakdown")
        
        channel_data = []
        for ch in channels:
            efficiency = MultiChannelGTM.calculate_channel_efficiency(ch)
            channel_data.append({
                'Channel': ch['name'],
                'Segment': ch['segment'],
                'Leads': ch['monthly_leads'],
                'Meetings Held': f"{ch['meetings_held']:.0f}",
                'Sales': f"{ch['sales']:.0f}",
                'Revenue': f"${ch['revenue']:,.0f}",
                'CAC': f"${ch['cac']:,.0f}",
                'LTV:CAC': f"{ch['ltv_cac']:.1f}x",
                'Payback': f"{efficiency['payback_months']:.1f} mo"
            })
        
        channel_df = pd.DataFrame(channel_data)
        st.dataframe(
            channel_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Revenue": st.column_config.TextColumn("Revenue", width="medium"),
                "LTV:CAC": st.column_config.TextColumn("LTV:CAC", width="small")
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
    
    # Health Monitoring Section in Expandable Format
    with st.expander("🌱 **System Health & Recommendations**", expanded=False):
        # Check various health metrics
        health_issues = []
        
        # Check revenue gap
        revenue_gap = monthly_revenue_target - monthly_revenue_total
        if revenue_gap > 0:
            gap_pct = (revenue_gap / monthly_revenue_target) * 100
            if gap_pct > 30:
                health_issues.append({
                'severity': 'high',
                'category': 'Revenue',
                'issue': f'Revenue {gap_pct:.0f}% below target',
                'recommendation': f'Increase sales by {revenue_gap/comp_immediate:.0f} or improve close rate to {(monthly_sales * monthly_revenue_target / monthly_revenue_total) / monthly_meetings:.1%}'
            })
            elif gap_pct > 15:
                health_issues.append({
                'severity': 'medium',
                'category': 'Revenue',
                'issue': f'Revenue gap of ${revenue_gap:,.0f}',
                'recommendation': f'Focus on closing {revenue_gap/comp_immediate:.0f} additional sales'
            })
    
        
        # Check capacity utilization
        health_capacity_settings = get_capacity_metrics(num_closers, num_setters)
        capacity_util = monthly_meetings / health_capacity_settings['monthly_closer_capacity'] if health_capacity_settings['monthly_closer_capacity'] > 0 else 0
        setter_utilization = monthly_meetings_scheduled / health_capacity_settings['monthly_setter_capacity'] if health_capacity_settings['monthly_setter_capacity'] > 0 else 0
        if capacity_util > 0.9:
            health_issues.append({
                'severity': 'high',
                'category': 'Capacity',
                'issue': f'Team at {capacity_util:.0%} capacity',
                'recommendation': f'Hire {np.ceil(max(monthly_meetings - health_capacity_settings["per_closer_monthly_capacity"] * num_closers * 0.8, 0) / health_capacity_settings["per_closer_monthly_capacity"]):.0f} closers to reduce load'
            })
        
        # Check LTV:CAC ratio
        if ltv_cac_ratio < 3:
            health_issues.append({
                'severity': 'medium',
                'category': 'Unit Economics',
                'issue': f'LTV:CAC ratio {ltv_cac_ratio:.1f}:1 below target',
                'recommendation': f'Reduce CAC by ${cac - ltv/3:.0f} or increase LTV'
            })
    
        # Display health issues in a friendly way
        if health_issues:
            health_cols = st.columns(len(health_issues[:3]))  # Show up to 3 issues
            for idx, issue in enumerate(health_issues[:3]):
                with health_cols[idx]:
                    if issue['severity'] == 'high':
                        st.warning(f"""
                        **{issue['category']}**  
                        🟡 {issue['issue']}  
                        💡 {issue['recommendation']}
                        """)
                    else:
                        st.info(f"""
                        **{issue['category']}**  
                        ℹ️ {issue['issue']}  
                        💡 {issue['recommendation']}
                        """)
        else:
            st.success("✅ All systems healthy! No major issues detected.")
    
    # Integrated Health Metrics & Bottleneck Analysis in Expandable Format
    with st.expander("🔍 **Bottleneck Analysis & Health Scores**", expanded=False):
        # Calculate health scores
        funnel_health = HealthScoreCalculator.calculate_health_metrics(
            {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
            {'utilization': capacity_util, 'attrition_rate': 0.15},
            {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin, 'growth_rate': 0.1}
        )
        
        # Display health scores in columns
        health_col1, health_col2, health_col3, health_col4 = st.columns(4)
        
        with health_col1:
            score = funnel_health['overall_health']
            if score >= 80:
                color = "normal"
                emoji = "🚀"
            elif score >= 60:
                color = "normal"
                emoji = "⚠️"
            else:
                color = "inverse"
                emoji = "🔴"
            st.metric(
                "Overall Health",
                f"{score:.0f}/100 {emoji}",
                funnel_health['status'],
                delta_color=color
            )
    
    with health_col2:
        score = funnel_health['funnel_health']
        st.metric(
            "Funnel Health",
            f"{score:.0f}/100",
            "Conversion flow" if score > 70 else "Needs attention"
        )
    
    with health_col3:
        score = funnel_health['team_health']
        st.metric(
            "Team Health",
            f"{score:.0f}/100",
            "Capacity OK" if score > 70 else "Overloaded"
        )
    
    with health_col4:
        score = funnel_health['financial_health']
        st.metric(
            "Financial Health",
            f"{score:.0f}/100",
            "Profitable" if score > 70 else "Review costs"
        )
    
    # Bottleneck identification
    bottlenecks = BottleneckAnalyzer.find_bottlenecks(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {
            'closer_utilization': capacity_util,
            'setter_utilization': setter_util_global
        },
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin}
    )
    
    if bottlenecks:
        st.markdown("**🎯 Identified Bottlenecks:**")
        bottleneck_cols = st.columns(min(len(bottlenecks), 3))
        
        for idx, bottleneck in enumerate(bottlenecks[:3]):
            with bottleneck_cols[idx]:
                # Color code by type
                if bottleneck['type'] == 'Financial':
                    st.error(f"""
                    **{bottleneck['type']}**  
                    🔴 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
                elif bottleneck['type'] == 'Capacity':
                    st.warning(f"""
                    **{bottleneck['type']}**  
                    🟡 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
                else:
                    st.info(f"""
                    **{bottleneck['type']}**  
                    🔵 {bottleneck['issue']}  
                    Current: {bottleneck['current']:.2f} | Target: {bottleneck['target']:.2f}  
                    👉 {bottleneck['action']}
                    """)
        else:
            st.success("🎆 No bottlenecks detected! System running smoothly.")
    
    # Charts Section - Consolidating visual analytics
    st.markdown("### 📈 Analytics & Charts")
    
    # Revenue Retention Metrics in expandable format
    with st.expander("💹 **Revenue Retention Analysis**", expanded=False):
        retention_col1, retention_col2 = st.columns(2)
    
    with retention_col1:
        # Retention inputs in expandable section
        with st.expander("📊 **Configure Retention Metrics**", expanded=False):
            # Use actual current MRR from business metrics
            starting_mrr = monthly_revenue_total  # Use actual monthly revenue
            st.info(f"💵 Using Current MRR: ${starting_mrr:,.0f}")
            
            # Retention components
            churn_pct = st.slider("Monthly Churn %", 0.0, 20.0, 3.0, 0.5, key="retention_churn") / 100
            downgrade_pct = st.slider("Monthly Downgrade %", 0.0, 10.0, 2.0, 0.5, key="retention_downgrade") / 100
            expansion_pct = st.slider("Monthly Expansion %", 0.0, 20.0, 5.0, 0.5, key="retention_expansion") / 100
            new_customer_pct = st.slider("New Customer Growth %", 0.0, 50.0, 10.0, 1.0, key="retention_new") / 100
    
    # Calculate absolute values
    churned_mrr = starting_mrr * churn_pct
    downgrade_mrr = starting_mrr * downgrade_pct
    expansion_mrr = starting_mrr * expansion_pct
    new_mrr = starting_mrr * new_customer_pct
    ending_mrr = starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr + new_mrr
    
    # Calculate GRR and NRR
    retention_metrics = RevenueRetentionCalculator.calculate_grr_nrr(
        starting_mrr=starting_mrr,
        ending_mrr=ending_mrr,
        churned_mrr=churned_mrr,
        downgrade_mrr=downgrade_mrr,
        expansion_mrr=expansion_mrr,
        new_mrr=new_mrr
    )
    
    # Display retention metrics
    ret_metric_cols = st.columns(4)
    
    with ret_metric_cols[0]:
        grr_status = "Excellent" if retention_metrics['grr_percentage'] >= 95 else "Good" if retention_metrics['grr_percentage'] >= 90 else "Needs Work"
        st.metric(
            "Gross Revenue Retention",
            f"{retention_metrics['grr_percentage']:.1f}%",
            grr_status
        )
    
    with ret_metric_cols[1]:
        nrr_status = "Excellent" if retention_metrics['nrr_percentage'] >= 120 else "Good" if retention_metrics['nrr_percentage'] >= 110 else "Review"
        st.metric(
            "Net Revenue Retention",
            f"{retention_metrics['nrr_percentage']:.1f}%",
            nrr_status
        )
    
    with ret_metric_cols[2]:
        st.metric(
            "Expansion Rate",
            f"{retention_metrics['expansion_rate']:.1f}%",
            f"+${expansion_mrr:,.0f}/mo"
        )
    
    with ret_metric_cols[3]:
        churn_status = "Healthy" if retention_metrics['churn_rate'] <= 3 else "Watch" if retention_metrics['churn_rate'] <= 5 else "High"
        st.metric(
            "Monthly Churn",
            f"{retention_metrics['churn_rate']:.1f}%",
            churn_status
        )
    
    # Revenue Waterfall Chart
    with retention_col2:
        st.markdown("**💧 Revenue Movement Waterfall**")
        
        waterfall_data = {
            'measure': ['absolute', 'relative', 'relative', 'relative', 'relative', 'total'],
            'x': ['Starting MRR', 'Churned', 'Downgrades', 'Expansion', 'New Customers', 'Ending MRR'],
            'y': [starting_mrr, -churned_mrr, -downgrade_mrr, expansion_mrr, new_mrr, ending_mrr]
        }
        
        fig_waterfall = go.Figure(go.Waterfall(
            measure=waterfall_data['measure'],
            x=waterfall_data['x'],
            y=waterfall_data['y'],
            text=[f"${abs(val):,.0f}" for val in waterfall_data['y']],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#4CAF50"}},
            decreasing={"marker": {"color": "#F44336"}},
            totals={"marker": {"color": "#2196F3"}}
        ))
        
        fig_waterfall.update_layout(
            height=350,
            margin=dict(t=20, b=20),
            showlegend=False
        )
        
        st.plotly_chart(fig_waterfall, use_container_width=True, key="retention_waterfall")
    
    # Sales Process Timeline removed - data available in other metrics

# TAB 2: UNIT COSTS (10x Better One-Pager Design)
with tabs[1]:
    # Import dynamic benchmarks
    from modules.dynamic_benchmarks import DynamicBenchmarks
    
    # Header with dramatic styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 20px; margin-bottom: 30px; color: white; text-align: center;">
        <h1 style="margin: 0; font-size: 36px; font-weight: 900;">💰 UNIT ECONOMICS COMMAND CENTER</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Complete cost analysis with dynamic benchmarks</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get dynamic benchmarks
    cost_benchmarks = DynamicBenchmarks.get_cost_benchmarks("insurance", "digital", "mexico")
    financial_benchmarks = DynamicBenchmarks.get_financial_benchmarks("insurance", "recurring")
    
    # Key metrics with show-up rate impact
    no_show_cost = cost_breakdown.get('no_show_cost', 0)
    no_show_rate = cost_breakdown.get('no_show_rate', 0)
    
    # TOP METRICS DASHBOARD
    st.markdown("### 🎯 KEY PERFORMANCE INDICATORS")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cpl_status, cpl_color, cpl_emoji = DynamicBenchmarks.get_performance_status(
            cost_breakdown['cost_per_lead'], cost_benchmarks['cpl']
        )
        st.markdown(f"""
        <div style="background: {cpl_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{cpl_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">${cost_breakdown['cost_per_lead']:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Cost per Lead</div>
            <div style="font-size: 12px; margin-top: 5px;">{cpl_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cac_status, cac_color, cac_emoji = DynamicBenchmarks.get_performance_status(
            cac, cost_benchmarks['cac']
        )
        st.markdown(f"""
        <div style="background: {cac_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{cac_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">${cac:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Total CAC</div>
            <div style="font-size: 12px; margin-top: 5px;">{cac_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ltv_cac_status, ltv_cac_color, ltv_cac_emoji = DynamicBenchmarks.get_performance_status(
            ltv_cac_ratio, financial_benchmarks['ltv_cac_ratio']
        )
        st.markdown(f"""
        <div style="background: {ltv_cac_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{ltv_cac_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">{ltv_cac_ratio:.1f}:1</div>
            <div style="font-size: 14px; opacity: 0.9;">LTV:CAC Ratio</div>
            <div style="font-size: 12px; margin-top: 5px;">{ltv_cac_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        payback_months = cac / (comp_immediate * ebitda_margin) if (comp_immediate * ebitda_margin) > 0 else 999
        # For payback, we need to invert the logic (lower is better)
        if payback_months <= financial_benchmarks['payback_months']['excellent']:
            payback_status, payback_color, payback_emoji = "Excellent", "#4CAF50", "🟢"
        elif payback_months <= financial_benchmarks['payback_months']['good']:
            payback_status, payback_color, payback_emoji = "Good", "#8BC34A", "🟡"
        elif payback_months <= financial_benchmarks['payback_months']['min']:
            payback_status, payback_color, payback_emoji = "Acceptable", "#FF9800", "🟠"
        else:
            payback_status, payback_color, payback_emoji = "Below Standard", "#F44336", "🔴"
        st.markdown(f"""
        <div style="background: {payback_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">{payback_emoji}</div>
            <div style="font-size: 28px; font-weight: 900;">{payback_months:.1f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Payback Months</div>
            <div style="font-size: 12px; margin-top: 5px;">{payback_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        revenue_per_lead = monthly_revenue_immediate / monthly_leads if monthly_leads > 0 else 0
        rpl_color = "#4CAF50" if revenue_per_lead > cost_breakdown['cost_per_lead'] * 3 else "#FF9800" if revenue_per_lead > cost_breakdown['cost_per_lead'] else "#F44336"
        st.markdown(f"""
        <div style="background: {rpl_color}; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <div style="font-size: 24px;">💰</div>
            <div style="font-size: 28px; font-weight: 900;">${revenue_per_lead:,.0f}</div>
            <div style="font-size: 14px; opacity: 0.9;">Revenue/Lead</div>
            <div style="font-size: 12px; margin-top: 5px;">{"Excellent" if revenue_per_lead > cost_breakdown['cost_per_lead'] * 3 else "Good" if revenue_per_lead > cost_breakdown['cost_per_lead'] else "Poor"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # FUNNEL COST BREAKDOWN
    st.markdown("### 🔄 COMPLETE FUNNEL COST ANALYSIS")
    
    # Create comprehensive funnel visualization
    funnel_data = {
        'Stage': ['Leads', 'Contacts', 'Meetings Scheduled', 'Meetings Held', 'Sales', 'Onboarded'],
        'Volume': [monthly_leads, monthly_contacts, monthly_meetings_scheduled, monthly_meetings_held, monthly_sales, monthly_onboarded],
        'Cost_Per_Unit': [
            cost_breakdown.get('cost_per_lead', 0),
            cost_breakdown.get('cost_per_contact', 0),
            cost_breakdown.get('cost_per_meeting_scheduled', 0),
            cost_breakdown.get('cost_per_meeting_held', 0),
            cost_breakdown.get('cost_per_sale', 0),
            cost_breakdown.get('cost_per_sale', 0) / onboard_rate if onboard_rate > 0 else 0
        ],
        'Conversion_Rate': [
            1.0,
            contact_rate,
            meeting_rate,
            show_up_rate,
            close_rate,
            onboard_rate
        ],
        'Total_Cost': [
            cost_breakdown.get('cost_per_lead', 0) * monthly_leads,
            cost_breakdown.get('cost_per_contact', 0) * monthly_contacts,
            cost_breakdown.get('cost_per_meeting_scheduled', 0) * monthly_meetings_scheduled,
            cost_breakdown.get('cost_per_meeting_held', 0) * monthly_meetings_held,
            cost_breakdown.get('cost_per_sale', 0) * monthly_sales,
            (cost_breakdown.get('cost_per_sale', 0) / onboard_rate if onboard_rate > 0 else 0) * monthly_onboarded
        ]
    }
    
    funnel_df = pd.DataFrame(funnel_data)
    
    # Display as professional OG table like compensation tables
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3 style="color: white; margin: 0; text-align: center; font-weight: 900;">
            📊 COMPLETE FUNNEL BREAKDOWN
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create the professional table
    st.dataframe(
        funnel_df.style.format({
            'Volume': '{:,.0f}',
            'Cost_Per_Unit': '${:,.0f}',
            'Conversion_Rate': '{:.1%}',
            'Total_Cost': '${:,.0f}'
        }).set_properties(**{
            'background-color': '#f8f9fa',
            'color': '#333',
            'border': '1px solid #dee2e6',
            'text-align': 'center',
            'font-weight': '600'
        }).set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', '#495057'),
                    ('color', 'white'),
                    ('font-weight', '900'),
                    ('text-align', 'center'),
                    ('padding', '12px'),
                    ('border', '1px solid #495057')
                ]
            },
            {
                'selector': 'tbody td',
                'props': [
                    ('padding', '10px'),
                    ('border', '1px solid #dee2e6'),
                    ('text-align', 'center')
                ]
            },
            {
                'selector': 'tbody tr:nth-child(even)',
                'props': [
                    ('background-color', '#ffffff')
                ]
            },
            {
                'selector': 'tbody tr:hover',
                'props': [
                    ('background-color', '#e9ecef'),
                    ('cursor', 'pointer')
                ]
            }
        ]),
        use_container_width=True,
        hide_index=True
    )
    
    # NO-SHOW IMPACT ANALYSIS
    if no_show_cost > 0:
        st.markdown("### 🚫 NO-SHOW IMPACT ANALYSIS")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">😞</div>
                <div style="font-size: 24px; font-weight: 900;">{no_show_rate:.1%}</div>
                <div style="font-size: 14px; opacity: 0.9;">No-Show Rate</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    {monthly_meetings_scheduled * (1-show_up_rate):.0f} missed meetings/month
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffa726 0%, #ff9800 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">💸</div>
                <div style="font-size: 24px; font-weight: 900;">${no_show_cost:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">Wasted Cost/Month</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    ${no_show_cost * 12:,.0f} annually
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            potential_sales = monthly_meetings_scheduled * (1-show_up_rate) * close_rate
            potential_revenue = potential_sales * comp_immediate
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ab47bc 0%, #9c27b0 100%); 
                        padding: 25px; border-radius: 15px; color: white; text-align: center;">
                <div style="font-size: 32px; margin-bottom: 10px;">📉</div>
                <div style="font-size: 24px; font-weight: 900;">${potential_revenue:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">Lost Revenue/Month</div>
                <div style="font-size: 12px; margin-top: 10px;">
                    {potential_sales:.0f} lost sales
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # OPTIMIZATION RECOMMENDATIONS
    st.markdown("### 🎯 OPTIMIZATION RECOMMENDATIONS")
    
    recommendations = []
    
    # Check each metric against benchmarks
    if cost_breakdown['cost_per_lead'] > cost_benchmarks['cpl']['good']:
        reduction_needed = cost_breakdown['cost_per_lead'] - cost_benchmarks['cpl']['good']
        recommendations.append({
            'priority': 'HIGH',
            'metric': 'Cost per Lead',
            'issue': f"${cost_breakdown['cost_per_lead']:,.0f} is ${reduction_needed:.0f} above benchmark",
            'action': f"Optimize targeting or channels to reduce CPL by {(reduction_needed/cost_breakdown['cost_per_lead'])*100:.0f}%",
            'impact': f"Save ${reduction_needed * monthly_leads:,.0f}/month"
        })
    
    if ltv_cac_ratio < financial_benchmarks['ltv_cac_ratio']['good']:
        recommendations.append({
            'priority': 'CRITICAL',
            'metric': 'LTV:CAC Ratio',
            'issue': f"{ltv_cac_ratio:.1f}:1 below {financial_benchmarks['ltv_cac_ratio']['good']:.1f}:1 benchmark",
            'action': f"Reduce CAC by ${cac - ltv/financial_benchmarks['ltv_cac_ratio']['good']:,.0f} or increase LTV",
            'impact': f"Improve unit economics sustainability"
        })
    
    if no_show_rate > 0.3:
        recommendations.append({
            'priority': 'MEDIUM',
            'metric': 'Show-up Rate',
            'issue': f"{no_show_rate:.1%} no-show rate is high",
            'action': f"Implement confirmation calls, better scheduling, or penalties",
            'impact': f"Recover ${no_show_cost:,.0f}/month in wasted costs"
        })
    
    # Display recommendations
    for i, rec in enumerate(recommendations):
        priority_color = {"CRITICAL": "#f44336", "HIGH": "#ff9800", "MEDIUM": "#2196f3"}[rec['priority']]
        st.markdown(f"""
        <div style="background: {priority_color}; padding: 20px; border-radius: 15px; 
                    margin: 10px 0; color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 18px; font-weight: 900;">
                        {rec['priority']} PRIORITY: {rec['metric']}
                    </div>
                    <div style="font-size: 14px; margin: 5px 0; opacity: 0.9;">
                        {rec['issue']}
                    </div>
                    <div style="font-size: 14px; font-weight: 600;">
                        🎯 Action: {rec['action']}
                    </div>
                </div>
                <div style="text-align: right; font-size: 12px; opacity: 0.8;">
                    💰 {rec['impact']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: P&L (Deep analysis)
with tabs[2]:
    st.header("📊 P&L Detallado - Análisis Profundo")
    
    # Prepare P&L data
    revenue_dict = {
        'monthly_sales': monthly_sales,
        'immediate_revenue': monthly_revenue_immediate,
        'deferred_revenue': monthly_sales * comp_deferred,
        'total_projected': revenue_timeline['cumulative_total'].iloc[-1] if len(revenue_timeline) > 0 else 0
    }
    
    # Handle case where comp_structure might be None or from different sources
    if comp_structure and isinstance(comp_structure, dict) and 'monthly_base' in comp_structure:
        monthly_base_salaries = comp_structure['monthly_base']
    else:
        # Fallback calculation if comp_structure is not available
        monthly_base_salaries = (num_closers * 32000 + num_setters * 16000 + num_managers * 72000 + num_bench * 12500) / 12
    
    costs_dict = {
        'cogs': 0,
        'marketing_costs': monthly_marketing,
        'commissions': monthly_commissions,
        'sales_base_salaries': monthly_base_salaries,
        'office_rent': office_rent,
        'software': software_costs,
        'other_opex': other_opex,
        'gov_fee_pct': gov_fee_pct
    }
    
    pnl_df = ImprovedPnLCalculator.calculate_detailed_pnl(
        revenue_dict, costs_dict, projection_months
    )
    
    # Format P&L display - include format column for processing
    display_pnl = pnl_df.copy()
    
    # Format columns
    for col in ['month_1', 'month_18', 'total_projection']:
        display_pnl[col] = display_pnl.apply(
            lambda x: f"${x[col]:,.0f}" if x['format'] in ['currency', 'currency_bold'] 
            else f"{x[col]:.0f}" if x['format'] == 'units'
            else f"{x[col]:.1%}" if x['format'] == 'percentage'
            else x[col],
            axis=1
        )
    
    display_pnl['pct_of_revenue'] = display_pnl['pct_of_revenue'].apply(
        lambda x: f"{x:.1%}" if pd.notna(x) and x != 0 else ""
    )
    
    # Select and display only the key columns
    final_pnl = display_pnl[['line_item', 'month_1', 'month_18', 'total_projection', 'pct_of_revenue']].copy()
    final_pnl.columns = ['Line Item', 'Month 1', 'Month 18', f'{projection_months}M Total', '% of Rev']
    
    st.dataframe(final_pnl, use_container_width=True, height=600, hide_index=True)

# TAB 4: SIMULATOR (was TAB 6)
with tabs[3]:  # Simulator tab
    st.header("📅 Revenue Timeline - Proyección Detallada")
    
    # Key milestone dates
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0; color: #64B5F6;">📆 Key Dates</h4>
            <div style="margin-top: 10px; line-height: 1.8;">
                • <b>Today:</b> {datetime.now().strftime('%B %Y')}<br>
                • <b>Month 18:</b> {(datetime.now() + timedelta(days=540)).strftime('%B %Y')}<br>
                • <b>End:</b> {(datetime.now() + timedelta(days=projection_months*30)).strftime('%B %Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if projection_months >= 18:
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h4 style="margin: 0; color: #81C784;">💰 Month 18 Revenue</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Immediate:</b> ${month_18_revenue_immediate:,.0f}<br>
                    • <b>Deferred:</b> ${month_18_revenue_deferred:,.0f}<br>
                    • <b>Total:</b> ${month_18_revenue_total:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        total_projection = revenue_timeline['cumulative_total'].iloc[-1] if len(revenue_timeline) > 0 else 0
        st.markdown(f"""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
            <h4 style="margin: 0; color: #FFB74D;">📊 {projection_months}M Projection</h4>
            <div style="margin-top: 10px; line-height: 1.8;">
                • <b>Total Revenue:</b> ${total_projection:,.0f}<br>
                • <b>Avg Monthly:</b> ${total_projection/projection_months:,.0f}<br>
                • <b>Run Rate:</b> ${(total_projection/projection_months)*12:,.0f}/yr
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Timeline visualization
    fig_timeline = go.Figure()
    
    # Immediate revenue
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['immediate_revenue'],
        name='Immediate (70%)',
        marker_color='#2ecc71'
    ))
    
    # Deferred revenue
    fig_timeline.add_trace(go.Bar(
        x=revenue_timeline['month'],
        y=revenue_timeline['deferred_revenue'],
        name='Deferred (30%)',
        marker_color='#3498db'
    ))
    
    # Cumulative line
    fig_timeline.add_trace(go.Scatter(
        x=revenue_timeline['month'],
        y=revenue_timeline['cumulative_total'],
        name='Cumulative',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=3),
        yaxis='y2'
    ))
    
    # Add month 18 marker
    if projection_months >= 18:
        fig_timeline.add_vline(
            x=18, line_dash="dash", line_color="red",
            annotation_text="Deferred Payments Start"
        )
    
    # Add quarters
    for q in range(1, (projection_months // 3) + 1):
        fig_timeline.add_vline(x=q*3, line_dash="dot", line_color="gray", opacity=0.3)
    
    fig_timeline.update_layout(
        title="Revenue Timeline with 70/30 Split",
        xaxis_title="Month",
        yaxis_title="Monthly Revenue ($)",
        yaxis2=dict(title="Cumulative ($)", overlaying='y', side='right'),
        barmode='stack',
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# TAB 5: REVERSE ENGINEERING (was TAB 7)
with tabs[4]:  # Reverse Engineering tab
    st.header("🚀 Simulador Avanzado")
    
    # Optimization target
    opt_col1, opt_col2 = st.columns([1, 3])
    
    with opt_col1:
        optimize_for = st.radio(
            "Optimize for:",
            ["Revenue", "EBITDA", "LTV:CAC", "Margin %"],
            index=1
        )
    
    with opt_col2:
        if optimize_for == "Revenue":
            target_revenue = st.number_input(
                "Target Monthly Revenue ($)",
                value=int(monthly_revenue_target * 1.5),
                step=100000
            )
            
            # Calculate requirements
            sales_needed = target_revenue / comp_immediate
            meetings_needed = sales_needed / close_rate
            leads_needed = meetings_needed / (contact_rate * meeting_rate)
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h4 style="margin: 0; color: #81C784;">🎯 Requirements for ${target_revenue:,.0f}/month</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>{sales_needed:.0f} sales</b> ({sales_needed - monthly_sales:+.0f})<br>
                    • <b>{meetings_needed:.0f} meetings</b> ({meetings_needed - monthly_meetings:+.0f})<br>
                    • <b>{leads_needed:.0f} leads</b> ({leads_needed - monthly_leads:+.0f})<br>
                    • <b>{np.ceil(meetings_needed/per_closer_capacity):.0f} closers needed</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif optimize_for == "EBITDA":
            target_ebitda = st.number_input(
                "Target Monthly EBITDA ($)",
                value=int(monthly_ebitda * 2),
                step=50000
            )
            
            # Calculate options
            revenue_for_ebitda = (target_ebitda + monthly_costs_before_fees) / (1 - gov_fee_pct)
            cost_reduction = monthly_ebitda - target_ebitda
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;">
                <h4 style="margin: 0; color: #64B5F6;">🎯 Options for ${target_ebitda:,.0f} EBITDA</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Option 1:</b> Increase revenue to ${revenue_for_ebitda:,.0f}<br>
                    • <b>Option 2:</b> Reduce costs by ${abs(cost_reduction):,.0f}<br>
                    • <b>Option 3:</b> Combination approach
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif optimize_for == "LTV:CAC":
            target_ratio = st.number_input(
                "Target LTV:CAC Ratio",
                value=5.0,
                step=0.5,
                min_value=3.0,
                max_value=10.0
            )
            
            # Calculate requirements
            target_cac = ltv / target_ratio
            cac_reduction = cac - target_cac
            
            st.markdown(f"""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0; color: #FFB74D;">🎯 To achieve {target_ratio:.1f}:1 ratio</h4>
                <div style="margin-top: 10px; line-height: 1.8;">
                    • <b>Reduce CAC</b> from ${cac:,.0f} to ${target_cac:,.0f}<br>
                    • <b>Reduction needed:</b> ${cac_reduction:,.0f} (-{(cac_reduction/cac)*100:.0f}%)<br>
                    • <b>Or increase LTV</b> by {((target_ratio * cac) - ltv)/ltv*100:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

# REMOVED - Now only 6 tabs
# Old TAB 7 content removed
if False:  # This code is no longer used
    st.header("🔄 Ingeniería Inversa - Integrada")
    st.markdown("**Single source of truth - uses current dashboard values**")
    
    # Select target
    rev_col1, rev_col2 = st.columns([1, 2])
    
    with rev_col1:
        target_type = st.selectbox(
            "Start from:",
            ["Revenue Target", "EBITDA Target", "LTV:CAC Target", "Sales Target"]
        )
    
    with rev_col2:
        if target_type == "Revenue Target":
            target_value = st.number_input(
                "Monthly Revenue Target ($)",
                value=int(monthly_revenue_target),
                step=100000
            )
            
            # Use integrated reverse engineering
            results = ImprovedReverseEngineering.calculate_from_target(
                'revenue', target_value, current_state
            )
            
        elif target_type == "EBITDA Target":
            target_value = st.number_input(
                "Monthly EBITDA Target ($)",
                value=int(monthly_ebitda * 1.5),
                step=50000
            )
            
            results = ImprovedReverseEngineering.calculate_from_target(
                'ebitda', target_value, current_state
            )
            
        elif target_type == "LTV:CAC Target":
            target_value = st.number_input(
                "Target Ratio",
                value=5.0,
                step=0.5,
                min_value=3.0,
                max_value=10.0
            )
            
            results = ImprovedReverseEngineering.calculate_from_target(
                'ltv_cac', target_value, current_state
            )
        else:
            target_value = st.number_input(
                "Monthly Sales Target",
                value=int(monthly_sales * 1.5),
                step=10
            )
            
            # Convert sales target to revenue and calculate
            revenue_target = target_value * comp_immediate
            results = ImprovedReverseEngineering.calculate_from_target(
                'revenue', revenue_target, current_state
            )
    
    # Display results
    if 'results' in locals():
        st.markdown("### 📊 Results")
        
        # Show required changes
        if results['required_changes']:
            change_col1, change_col2 = st.columns(2)
            
            with change_col1:
                st.markdown("**🔄 Required Changes:**")
                for key, value in results['required_changes'].items():
                    if 'additional' in key or 'total' in key:
                        if isinstance(value, (int, float)):
                            if 'cost' in key or 'spend' in key or 'revenue' in key:
                                st.write(f"• {key.replace('_', ' ').title()}: ${value:,.0f}")
                            else:
                                st.write(f"• {key.replace('_', ' ').title()}: {value:.0f}")
            
            with change_col2:
                st.markdown("**🎯 Action Items:**")
                for action in results['actions']:
                    st.write(f"✅ {action}")
        
        # Show warnings
        if results['warnings']:
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;">
                <h4 style="margin: 0; color: #FFB74D;">⚠️ Warnings</h4>
            </div>
            """, unsafe_allow_html=True)
            for warning in results['warnings']:
                st.write(f"• {warning}")
        
        # Feasibility indicator
        if results['feasibility'] == 'feasible':
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; display: flex; align-items: center;">
                <div style="font-size: 24px; margin-right: 10px;">✅</div>
                <div style="font-weight: bold;">Target is achievable with current resources</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #F44336; display: flex; align-items: center;">
                <div style="font-size: 24px; margin-right: 10px;">❌</div>
                <div style="font-weight: bold;">Target requires significant changes</div>
            </div>
            """, unsafe_allow_html=True)

# REMOVED - Health metrics integrated into GTM Command Center
if False:  # Old Health Metrics tab
    st.header("📈 Health Metrics Dashboard")
    
    # Calculate health scores
    funnel_health = HealthScoreCalculator.calculate_health_metrics(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {'utilization': capacity_util, 'attrition_rate': 0.15},
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin, 'growth_rate': 0.1}
    )
    
    # Display scores
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    
    with health_col1:
        st.metric(
            "Overall Health",
            f"{funnel_health['overall_health']:.0f}/100",
            funnel_health['status']
        )
    
    with health_col2:
        st.metric(
            "Funnel Health",
            f"{funnel_health['funnel_health']:.0f}/100"
        )
    
    with health_col3:
        st.metric(
            "Team Health",
            f"{funnel_health['team_health']:.0f}/100"
        )
    
    with health_col4:
        st.metric(
            "Financial Health",
            f"{funnel_health['financial_health']:.0f}/100"
        )
    
    # Bottleneck analysis
    st.subheader("🔍 Bottleneck Analysis")
    
    bottlenecks = BottleneckAnalyzer.find_bottlenecks(
        {'contact_rate': contact_rate, 'meeting_rate': meeting_rate, 'close_rate': close_rate},
        {'closer_utilization': capacity_util, 'setter_utilization': monthly_contacts / (num_setters * 600) if num_setters > 0 else 0},
        {'ltv_cac_ratio': ltv_cac_ratio, 'ebitda_margin': ebitda_margin}
    )
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            bottleneck_type = 'alert-critical' if bottleneck['type'] == 'Financial' else 'alert-warning'
            st.markdown(
                f'<div class="alert-box {bottleneck_type}">' +
                f'<strong>{bottleneck["type"]} Issue: {bottleneck["issue"]}</strong><br>' +
                f'Current: {bottleneck["current"]:.2f} | Target: {bottleneck["target"]:.2f}<br>' +
                f'Impact: {bottleneck["impact"]}<br>' +
                f'👉 Action: {bottleneck["action"]}' +
                '</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown("""
        <div style="background: #121212; color: white; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50; display: flex; align-items: center;">
            <div style="font-size: 24px; margin-right: 10px;">✅</div>
            <div style="font-weight: bold;">No major bottlenecks detected!</div>
        </div>
        """, unsafe_allow_html=True)

# REMOVED - Revenue retention integrated into GTM Command Center
if False:  # Old Revenue Retention tab
    st.header("📈 Revenue Retention Metrics (GRR & NRR)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Input Retention Data")
        
        # MRR inputs
        starting_mrr = st.number_input(
            "Starting MRR ($)", 
            value=float(monthly_revenue_total),
            step=10000.0,
            help="Monthly Recurring Revenue at start of period"
        )
        
        # Retention components
        churn_pct = st.slider("Monthly Churn %", 0.0, 20.0, 3.0, 0.5) / 100
        downgrade_pct = st.slider("Monthly Downgrade %", 0.0, 10.0, 2.0, 0.5) / 100
        expansion_pct = st.slider("Monthly Expansion %", 0.0, 20.0, 5.0, 0.5) / 100
        
        # Calculate absolute values
        churned_mrr = starting_mrr * churn_pct
        downgrade_mrr = starting_mrr * downgrade_pct
        expansion_mrr = starting_mrr * expansion_pct
        
        # New customer MRR
        new_customer_pct = st.slider("New Customer Growth %", 0.0, 50.0, 10.0, 1.0) / 100
        new_mrr = starting_mrr * new_customer_pct
        
        # Calculate ending MRR
        ending_mrr = starting_mrr - churned_mrr - downgrade_mrr + expansion_mrr + new_mrr
        
    with col2:
        st.subheader("📈 Retention Analysis")
        
        # Calculate GRR and NRR
        retention_metrics = RevenueRetentionCalculator.calculate_grr_nrr(
            starting_mrr=starting_mrr,
            ending_mrr=ending_mrr,
            churned_mrr=churned_mrr,
            downgrade_mrr=downgrade_mrr,
            expansion_mrr=expansion_mrr,
            new_mrr=new_mrr
        )
        
        # Display key metrics
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            grr_color = "#4CAF50" if retention_metrics['grr_percentage'] >= 90 else "#FF9800" if retention_metrics['grr_percentage'] >= 80 else "#F44336"
            st.markdown(f"""
            <div style="background: {grr_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['grr_percentage']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Gross Revenue Retention</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    Retained: ${retention_metrics['retained_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[1]:
            nrr_color = "#4CAF50" if retention_metrics['nrr_percentage'] >= 110 else "#2196F3" if retention_metrics['nrr_percentage'] >= 100 else "#FF9800"
            st.markdown(f"""
            <div style="background: {nrr_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['nrr_percentage']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Net Revenue Retention</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    Total: ${retention_metrics['total_retention_revenue']:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[2]:
            st.markdown(f"""
            <div style="background: #9C27B0; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['expansion_rate']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Expansion Rate</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    +${expansion_mrr:,.0f}/mo
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with metric_cols[3]:
            churn_color = "#4CAF50" if retention_metrics['churn_rate'] <= 3 else "#FF9800" if retention_metrics['churn_rate'] <= 5 else "#F44336"
            st.markdown(f"""
            <div style="background: {churn_color}; padding: 20px; border-radius: 10px; color: white; text-align: center;">
                <div style="font-size: 32px; font-weight: bold;">{retention_metrics['churn_rate']:.1f}%</div>
                <div style="font-size: 14px; margin-top: 5px;">Monthly Churn</div>
                <div style="font-size: 12px; margin-top: 10px; opacity: 0.9;">
                    -${churned_mrr:,.0f}/mo
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Revenue Waterfall Chart
    st.subheader("💧 Revenue Waterfall")
    
    waterfall_data = {
        'Category': ['Starting MRR', 'Churned', 'Downgraded', 'Expanded', 'New Customers', 'Ending MRR'],
        'Amount': [starting_mrr, -churned_mrr, -downgrade_mrr, expansion_mrr, new_mrr, ending_mrr],
        'Type': ['Start', 'Negative', 'Negative', 'Positive', 'Positive', 'End']
    }
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="Revenue Movement",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=waterfall_data['Category'],
        text=[f"${v:,.0f}" for v in waterfall_data['Amount']],
        y=waterfall_data['Amount'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#4CAF50"}},
        decreasing={"marker": {"color": "#F44336"}},
        totals={"marker": {"color": "#2196F3"}}
    ))
    
    fig_waterfall.update_layout(
        title="Monthly Revenue Movement",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Projection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 12-Month Projection")
        projections = RevenueRetentionCalculator.project_retention_impact(
            current_mrr=starting_mrr,
            monthly_churn_rate=churn_pct,
            monthly_expansion_rate=expansion_pct,
            months_forward=12
        )
        
        projection_df = pd.DataFrame({
            'Month': projections['month'],
            'GRR MRR': projections['grr_mrr'],
            'NRR MRR': projections['nrr_mrr']
        })
        
        fig_projection = go.Figure()
        fig_projection.add_trace(go.Scatter(
            x=projection_df['Month'],
            y=projection_df['GRR MRR'],
            name='GRR Projection',
            line=dict(color='#FF9800', width=2)
        ))
        fig_projection.add_trace(go.Scatter(
            x=projection_df['Month'],
            y=projection_df['NRR MRR'],
            name='NRR Projection',
            line=dict(color='#4CAF50', width=2)
        ))
        
        fig_projection.update_layout(
            title="MRR Projection (GRR vs NRR)",
            xaxis_title="Month",
            yaxis_title="MRR ($)",
            height=350
        )
        
        st.plotly_chart(fig_projection, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Retention Benchmarks")
        
        benchmark_data = {
            'Metric': ['GRR', 'NRR', 'Churn Rate', 'Expansion Rate'],
            'Your Value': [
                f"{retention_metrics['grr_percentage']:.1f}%",
                f"{retention_metrics['nrr_percentage']:.1f}%",
                f"{retention_metrics['churn_rate']:.1f}%",
                f"{retention_metrics['expansion_rate']:.1f}%"
            ],
            'Best in Class': ['95%+', '120%+', '<2%', '15%+'],
            'Good': ['90-95%', '105-120%', '2-3%', '10-15%'],
            'Average': ['80-90%', '95-105%', '3-5%', '5-10%'],
            'Status': [
                '🟢' if retention_metrics['grr_percentage'] >= 95 else '🟡' if retention_metrics['grr_percentage'] >= 90 else '🔴',
                '🟢' if retention_metrics['nrr_percentage'] >= 120 else '🟡' if retention_metrics['nrr_percentage'] >= 105 else '🔴',
                '🟢' if retention_metrics['churn_rate'] <= 2 else '🟡' if retention_metrics['churn_rate'] <= 3 else '🔴',
                '🟢' if retention_metrics['expansion_rate'] >= 15 else '🟡' if retention_metrics['expansion_rate'] >= 10 else '🔴'
            ]
        }
        
        benchmark_df = pd.DataFrame(benchmark_data)
        st.dataframe(
            benchmark_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )

# Old Multi-Channel GTM tab removed - now integrated into main GTM Command Center tab
# Archived code moved to: dashboards/production/ARCHIVED_CODE.md
