"""
Modelo Optimaxx PLUS - Módulo de Compensación para Seguros
Especificaciones exactas del producto de seguros con pagos diferidos
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class OptimaxPlusConfig:
    """Configuración del modelo Optimaxx PLUS"""
    # Parámetros del Carrier
    TERM_MO: int = 300  # Plazo en meses (25 años)
    CARRIER_RATE: float = 0.027  # 2.7% sobre prima total
    UPFRONT_PCT: float = 0.70  # 70% pago inmediato
    DEFERRED_PCT: float = 0.30  # 30% pago diferido
    PERSIST_18: float = 0.90  # Probabilidad de persistencia a 18 meses
    
    # Distribución interna de compensaciones
    PCT_CLOSER_POOL: float = 0.20  # 20% de la compensación para closers
    SETTER_OF_CLOSER: float = 0.15  # 15% del pago del closer para setter
    SETTER_SPEED_BONUS: float = 0.10  # +10% por respuesta rápida
    SETTER_FOLLOWUP_BONUS: float = 0.05  # +5% por seguimiento completo
    
    # Multiplicadores por nivel de attainment
    ATTAINMENT_BANDS: Dict[str, float] = None
    
    # Parámetros del funnel
    LEADS_DAILY: int = 200
    CPL: float = 25  # Costo por lead
    CONTACT_RATE: float = 0.70
    MEETING_RATE: float = 0.35
    CLOSE_RATE: float = 0.25
    
    # Distribución de primas mensuales
    PM_VALUES: List[float] = None  # [2000, 3000, 4000, 5000]
    PM_PROBS: List[float] = None  # [0.2, 0.5, 0.2, 0.1]
    
    # Equipo y costos fijos
    TEAM_SIZE: int = 20
    PCT_BENCH: float = 0.20
    BENCH_BASE: float = 3000  # Salario base banco
    BENCH_PER_MEETING: float = 100
    BENCH_TARGET_MEETINGS: int = 5
    OPEX_FIXED: float = 10000  # Otros gastos fijos mensuales
    DAYS: int = 30  # Días operativos por mes
    
    def __post_init__(self):
        if self.ATTAINMENT_BANDS is None:
            self.ATTAINMENT_BANDS = {
                "0-40%": 0.60,
                "40-70%": 0.80,
                "70-100%": 1.00,
                "100-150%": 1.20,
                "150%+": 1.60
            }
        if self.PM_VALUES is None:
            self.PM_VALUES = [2000, 3000, 4000, 5000]
        if self.PM_PROBS is None:
            self.PM_PROBS = [0.2, 0.5, 0.2, 0.1]


class OptimaxPlusCalculator:
    """Calculadora para el modelo Optimaxx PLUS"""
    
    def __init__(self, config: OptimaxPlusConfig):
        self.config = config
        self.deferred_payments_schedule = {}  # Calendario de pagos diferidos
    
    def calculate_sale_value(self, pm: float) -> Dict[str, float]:
        """
        Calcula el valor de una venta individual
        
        Args:
            pm: Prima mensual de la póliza
            
        Returns:
            Dict con compensación total, pago inmediato y diferido
        """
        # Compensación total del carrier
        comp_total = self.config.CARRIER_RATE * pm * self.config.TERM_MO
        
        # Pagos
        comp_now = self.config.UPFRONT_PCT * comp_total
        comp_deferred = self.config.DEFERRED_PCT * comp_total
        
        # LTV esperado para la corporación
        ltv_expected = comp_now + (comp_deferred * self.config.PERSIST_18)
        
        return {
            'pm': pm,
            'comp_total': comp_total,
            'comp_now': comp_now,
            'comp_deferred': comp_deferred,
            'ltv_expected': ltv_expected,
            'formula': f"PM({pm:,.0f}) × {self.config.TERM_MO} × {self.config.CARRIER_RATE:.1%} = {comp_total:,.0f}"
        }
    
    def calculate_internal_distribution(self, comp_amount: float, 
                                       attainment_level: str = "70-100%",
                                       has_speed_bonus: bool = True,
                                       has_followup_bonus: bool = True) -> Dict[str, float]:
        """
        Calcula la distribución interna de compensaciones
        
        Args:
            comp_amount: Monto de compensación a distribuir
            attainment_level: Nivel de cumplimiento del closer
            has_speed_bonus: Si el setter obtiene bono de velocidad
            has_followup_bonus: Si el setter obtiene bono de seguimiento
            
        Returns:
            Dict con pagos para closer, setter y margen corporación
        """
        # Multiplicador por attainment
        mult = self.config.ATTAINMENT_BANDS.get(attainment_level, 1.0)
        
        # Pago del closer
        closer_pay = self.config.PCT_CLOSER_POOL * comp_amount * mult
        
        # Pago base del setter
        setter_base = self.config.SETTER_OF_CLOSER * closer_pay
        
        # Bonos del setter
        setter_multiplier = 1.0
        if has_speed_bonus:
            setter_multiplier += self.config.SETTER_SPEED_BONUS
        if has_followup_bonus:
            setter_multiplier += self.config.SETTER_FOLLOWUP_BONUS
        
        setter_pay = setter_base * setter_multiplier
        
        # Margen para la corporación
        corp_margin = comp_amount - closer_pay - setter_pay
        
        return {
            'closer_pay': closer_pay,
            'setter_pay': setter_pay,
            'corp_margin': corp_margin,
            'closer_rate': closer_pay / comp_amount,
            'setter_rate': setter_pay / comp_amount,
            'margin_rate': corp_margin / comp_amount
        }
    
    def simulate_monthly_funnel(self) -> Dict[str, float]:
        """
        Simula el funnel mensual determinístico
        
        Returns:
            Dict con métricas del funnel
        """
        leads_mo = self.config.LEADS_DAILY * self.config.DAYS
        contacts_mo = leads_mo * self.config.CONTACT_RATE
        meetings_mo = contacts_mo * self.config.MEETING_RATE
        sales_mo = meetings_mo * self.config.CLOSE_RATE
        
        return {
            'leads_mo': leads_mo,
            'contacts_mo': contacts_mo,
            'meetings_mo': meetings_mo,
            'sales_mo': sales_mo,
            'conversion_rate': sales_mo / leads_mo if leads_mo > 0 else 0
        }
    
    def calculate_monthly_revenue(self, sales_current_month: List[float],
                                 sales_18_months_ago: List[float] = None) -> Dict[str, float]:
        """
        Calcula los ingresos del mes considerando pagos diferidos
        
        Args:
            sales_current_month: Lista de primas mensuales vendidas este mes
            sales_18_months_ago: Lista de primas vendidas hace 18 meses
            
        Returns:
            Dict con ingresos inmediatos, diferidos y totales
        """
        # Ingresos por ventas del mes actual (70% inmediato)
        immediate_revenue = 0
        for pm in sales_current_month:
            sale = self.calculate_sale_value(pm)
            immediate_revenue += sale['comp_now']
        
        # Ingresos por pagos diferidos (30% de ventas hace 18 meses)
        deferred_revenue = 0
        if sales_18_months_ago:
            for pm in sales_18_months_ago:
                sale = self.calculate_sale_value(pm)
                # Aplicar persistencia
                if np.random.random() < self.config.PERSIST_18:
                    deferred_revenue += sale['comp_deferred']
        
        return {
            'immediate_revenue': immediate_revenue,
            'deferred_revenue': deferred_revenue,
            'total_revenue': immediate_revenue + deferred_revenue,
            'sales_count': len(sales_current_month),
            'deferred_count': sum(1 for _ in sales_18_months_ago if np.random.random() < self.config.PERSIST_18) if sales_18_months_ago else 0
        }
    
    def calculate_monthly_costs(self, sales_mo: int, revenue_data: Dict) -> Dict[str, float]:
        """
        Calcula los costos mensuales
        
        Args:
            sales_mo: Número de ventas en el mes
            revenue_data: Datos de ingresos del mes
            
        Returns:
            Dict con todos los costos desglosados
        """
        funnel = self.simulate_monthly_funnel()
        
        # Marketing/Leads
        ad_spend = funnel['leads_mo'] * self.config.CPL
        
        # Compensaciones (simplificado - en realidad depende de cada venta)
        avg_pm = np.average(self.config.PM_VALUES, weights=self.config.PM_PROBS)
        avg_sale = self.calculate_sale_value(avg_pm)
        
        # Distribuir compensaciones sobre los ingresos del mes
        total_revenue = revenue_data['total_revenue']
        dist = self.calculate_internal_distribution(total_revenue)
        
        closers_cost = dist['closer_pay']
        setters_cost = dist['setter_pay']
        
        # Costos del banco
        bench_count = int(self.config.TEAM_SIZE * self.config.PCT_BENCH)
        bench_cost = bench_count * self.config.BENCH_BASE
        bench_cost += bench_count * self.config.BENCH_TARGET_MEETINGS * self.config.BENCH_PER_MEETING
        
        # Otros fijos
        opex_fixed = self.config.OPEX_FIXED
        
        return {
            'ad_spend': ad_spend,
            'closers_cost': closers_cost,
            'setters_cost': setters_cost,
            'bench_cost': bench_cost,
            'opex_fixed': opex_fixed,
            'total_costs': ad_spend + closers_cost + setters_cost + bench_cost + opex_fixed
        }
    
    def calculate_unit_economics(self) -> Dict[str, float]:
        """
        Calcula CAC, LTV y ratio LTV:CAC
        
        Returns:
            Dict con métricas de unit economics
        """
        # Simular un mes típico
        funnel = self.simulate_monthly_funnel()
        
        # Generar ventas sintéticas
        sales = []
        for _ in range(int(funnel['sales_mo'])):
            pm = np.random.choice(self.config.PM_VALUES, p=self.config.PM_PROBS)
            sales.append(pm)
        
        # Calcular ingresos
        revenue_data = self.calculate_monthly_revenue(sales)
        
        # Calcular costos
        costs = self.calculate_monthly_costs(int(funnel['sales_mo']), revenue_data)
        
        # CAC
        cac = costs['total_costs'] / funnel['sales_mo'] if funnel['sales_mo'] > 0 else 0
        
        # LTV promedio por cliente
        avg_pm = np.average(self.config.PM_VALUES, weights=self.config.PM_PROBS)
        avg_sale = self.calculate_sale_value(avg_pm)
        ltv = avg_sale['ltv_expected']
        
        # Ratio
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        
        return {
            'cac': cac,
            'ltv': ltv,
            'ltv_cac_ratio': ltv_cac_ratio,
            'avg_pm': avg_pm,
            'monthly_sales': funnel['sales_mo'],
            'monthly_revenue': revenue_data['total_revenue'],
            'monthly_costs': costs['total_costs'],
            'monthly_ebitda': revenue_data['total_revenue'] - costs['total_costs']
        }
    
    def run_monte_carlo(self, n_simulations: int = 1000, horizon_months: int = 1) -> pd.DataFrame:
        """
        Ejecuta simulación Monte Carlo
        
        Args:
            n_simulations: Número de simulaciones
            horizon_months: Horizonte temporal en meses
            
        Returns:
            DataFrame con resultados de todas las simulaciones
        """
        results = []
        
        for sim in range(n_simulations):
            # Variar parámetros estocásticamente
            leads_daily = np.random.normal(self.config.LEADS_DAILY, self.config.LEADS_DAILY * 0.1)
            contact_rate = np.random.beta(7, 3) * 0.9  # Media ~0.7
            meeting_rate = np.random.beta(4, 6) * 0.6  # Media ~0.4
            close_rate = np.random.beta(3, 9) * 0.4    # Media ~0.25
            
            # Calcular ventas
            leads_mo = leads_daily * self.config.DAYS
            contacts_mo = leads_mo * contact_rate
            meetings_mo = contacts_mo * meeting_rate
            sales_mo = meetings_mo * close_rate
            
            # Generar ventas con primas variables
            sales = []
            for _ in range(int(sales_mo)):
                pm = np.random.choice(self.config.PM_VALUES, p=self.config.PM_PROBS)
                sales.append(pm)
            
            # Calcular métricas
            revenue_data = self.calculate_monthly_revenue(sales)
            costs = self.calculate_monthly_costs(int(sales_mo), revenue_data)
            
            ebitda = revenue_data['total_revenue'] - costs['total_costs']
            
            # Calcular CAC y LTV
            cac = costs['total_costs'] / sales_mo if sales_mo > 0 else 0
            avg_pm = np.mean(sales) if sales else np.average(self.config.PM_VALUES, weights=self.config.PM_PROBS)
            ltv = self.calculate_sale_value(avg_pm)['ltv_expected']
            
            results.append({
                'simulation': sim + 1,
                'leads_daily': leads_daily,
                'contact_rate': contact_rate,
                'meeting_rate': meeting_rate,
                'close_rate': close_rate,
                'leads_mo': leads_mo,
                'contacts_mo': contacts_mo,
                'meetings_mo': meetings_mo,
                'sales_mo': sales_mo,
                'avg_pm': avg_pm,
                'immediate_revenue': revenue_data['immediate_revenue'],
                'deferred_revenue': revenue_data['deferred_revenue'],
                'total_revenue': revenue_data['total_revenue'],
                'ad_spend': costs['ad_spend'],
                'closers_cost': costs['closers_cost'],
                'setters_cost': costs['setters_cost'],
                'bench_cost': costs['bench_cost'],
                'total_costs': costs['total_costs'],
                'ebitda': ebitda,
                'cac': cac,
                'ltv': ltv,
                'ltv_cac_ratio': ltv / cac if cac > 0 else 0
            })
        
        return pd.DataFrame(results)


# Ejemplo de uso y validación
if __name__ == "__main__":
    # Crear configuración
    config = OptimaxPlusConfig()
    calculator = OptimaxPlusCalculator(config)
    
    # Validación con ejemplo del documento
    print("=== VALIDACIÓN EJEMPLO PM=3,000 ===")
    sale = calculator.calculate_sale_value(3000)
    print(f"Compensación Total: ${sale['comp_total']:,.0f} (esperado: $24,300)")
    print(f"Pago Inmediato: ${sale['comp_now']:,.0f} (esperado: $17,010)")
    print(f"Pago Diferido: ${sale['comp_deferred']:,.0f} (esperado: $7,290)")
    print(f"LTV Esperado: ${sale['ltv_expected']:,.0f} (esperado: $23,571)")
    print(f"Fórmula: {sale['formula']}")
    
    print("\n=== DISTRIBUCIÓN INTERNA ===")
    dist = calculator.calculate_internal_distribution(sale['comp_now'])
    print(f"Closer (20% × ${sale['comp_now']:,.0f} × 1.0): ${dist['closer_pay']:,.0f}")
    print(f"Setter (15% × ${dist['closer_pay']:,.0f} × 1.15): ${dist['setter_pay']:,.0f}")
    print(f"Margen Corporación: ${dist['corp_margin']:,.0f}")
    
    print("\n=== UNIT ECONOMICS ===")
    ue = calculator.calculate_unit_economics()
    print(f"CAC: ${ue['cac']:,.0f}")
    print(f"LTV: ${ue['ltv']:,.0f}")
    print(f"LTV:CAC Ratio: {ue['ltv_cac_ratio']:.1f}:1")
    print(f"EBITDA Mensual: ${ue['monthly_ebitda']:,.0f}")
