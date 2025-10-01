"""
P&L Engine: Unit economics, commissions, and financial calculations
Single source of truth for all financial math
"""

from modules.models import (
    DealEconomics, UnitEconomics, CommissionBreakdown,
    PnLStatement, TeamStructure, OperatingCosts, RoleCompensation
)


def calculate_unit_economics(
    deal: DealEconomics,
    cost_per_sale: float
) -> UnitEconomics:
    """
    Calculate unit economics: LTV, CAC, payback period.
    Single source of truth for unit economics math.
    """
    upfront_cash = deal.upfront_cash
    deferred_cash = deal.deferred_cash
    
    # LTV = upfront + (deferred × retention rate)
    ltv = upfront_cash + (deferred_cash * deal.grr)
    
    # CAC = cost per sale
    cac = cost_per_sale
    
    # Payback = CAC / (upfront monthly cash flow)
    upfront_monthly = upfront_cash / 12
    payback_months = (cac / upfront_monthly) if upfront_monthly > 0 else 999
    
    return UnitEconomics(
        ltv=ltv,
        cac=cac,
        payback_months=payback_months,
        upfront_cash=upfront_cash,
        deferred_cash=deferred_cash
    )


def calculate_commission_pools(
    sales_count: float,
    closer_comp: RoleCompensation,
    setter_comp: RoleCompensation,
    manager_comp: RoleCompensation,
    deal: DealEconomics
) -> CommissionBreakdown:
    """
    Calculate commission pools based on policy.
    Single source of truth for commission math.
    """
    # Determine commission base (what we calculate commissions on)
    if deal.commission_policy.value == "upfront":
        commission_base = deal.upfront_cash
    else:  # full
        commission_base = deal.avg_deal_value
    
    # Monthly revenue this applies to
    total_commission_base = sales_count * commission_base
    
    # Calculate pools (% of commission base)
    closer_pool = total_commission_base * (closer_comp.commission_pct / 100)
    setter_pool = total_commission_base * (setter_comp.commission_pct / 100)
    manager_pool = total_commission_base * (manager_comp.commission_pct / 100)
    
    total_commission = closer_pool + setter_pool + manager_pool
    
    return CommissionBreakdown(
        closer_pool=closer_pool,
        setter_pool=setter_pool,
        manager_pool=manager_pool,
        total_commission=total_commission,
        commission_base=commission_base
    )


def calculate_pnl(
    gross_revenue: float,
    team_base_annual: float,
    commissions: float,
    marketing_spend: float,
    operating_costs: OperatingCosts,
    gov_cost_pct: float
) -> PnLStatement:
    """
    Calculate comprehensive P&L with proper COGS/OpEx categorization.
    Single source of truth for P&L math.
    
    Args:
        gross_revenue: Monthly revenue (upfront cash)
        team_base_annual: Total annual base salaries
        commissions: Monthly commission payments
        marketing_spend: Monthly marketing spend
        operating_costs: Monthly operating expenses
        gov_cost_pct: Government fees as % of gross revenue (0-100)
    """
    # Revenue
    gov_fees = gross_revenue * (gov_cost_pct / 100)
    net_revenue = gross_revenue - gov_fees
    
    # COGS (Cost of Goods Sold) - team compensation
    team_base_monthly = team_base_annual / 12
    cogs = team_base_monthly + commissions
    
    # Gross Profit
    gross_profit = net_revenue - cogs
    gross_margin = (gross_profit / net_revenue * 100) if net_revenue > 0 else 0
    
    # Operating Expenses
    marketing = marketing_spend
    opex = operating_costs.total
    total_opex = marketing + opex
    
    # EBITDA
    ebitda = gross_profit - total_opex
    ebitda_margin = (ebitda / net_revenue * 100) if net_revenue > 0 else 0
    
    return PnLStatement(
        gross_revenue=gross_revenue,
        gov_fees=gov_fees,
        net_revenue=net_revenue,
        team_base=team_base_monthly,
        commissions=commissions,
        cogs=cogs,
        gross_profit=gross_profit,
        gross_margin=gross_margin,
        marketing=marketing,
        opex=opex,
        total_opex=total_opex,
        ebitda=ebitda,
        ebitda_margin=ebitda_margin
    )


def calculate_per_person_earnings(
    commissions: CommissionBreakdown,
    team: TeamStructure,
    working_days: int = 20
) -> dict:
    """
    Calculate per-person earnings across different time periods.
    
    Returns dict with structure:
    {
        'closer': {'monthly_comm': X, 'daily_comm': Y, 'annual_comm': Z, 'ote_attainment': %},
        'setter': {...},
        'manager': {...}
    }
    """
    def calc_role(pool: float, count: int, role_comp: RoleCompensation):
        if count == 0:
            return {
                'monthly_comm': 0, 'daily_comm': 0, 'annual_comm': 0,
                'monthly_total': role_comp.base / 12, 'ote_attainment': 0
            }
        
        monthly_comm = pool / count
        daily_comm = monthly_comm / working_days
        annual_comm = monthly_comm * 12
        
        monthly_base = role_comp.base / 12
        monthly_total = monthly_base + monthly_comm
        
        # OTE attainment = actual commission / target variable
        ote_attainment = (annual_comm / role_comp.variable * 100) if role_comp.variable > 0 else 0
        
        return {
            'monthly_comm': monthly_comm,
            'daily_comm': daily_comm,
            'annual_comm': annual_comm,
            'monthly_base': monthly_base,
            'monthly_total': monthly_total,
            'ote': role_comp.ote,
            'ote_attainment': ote_attainment
        }
    
    return {
        'closer': calc_role(commissions.closer_pool, team.num_closers, team.closer),
        'setter': calc_role(commissions.setter_pool, team.num_setters, team.setter),
        'manager': calc_role(commissions.manager_pool, team.num_managers, team.manager),
        'bench': {
            'monthly_comm': 0,
            'daily_comm': 0,
            'annual_comm': 0,
            'monthly_base': team.bench.base / 12 if team.num_bench > 0 else 0,
            'monthly_total': team.bench.base / 12 if team.num_bench > 0 else 0,
            'ote': team.bench.ote,
            'ote_attainment': 0
        }
    }


def calculate_ote_requirements(
    target_variable: float,
    commission_pct: float,
    commission_base_per_deal: float
) -> dict:
    """
    Calculate what's needed to hit OTE.
    
    Returns:
    {
        'annual_deals_needed': X,
        'monthly_deals_needed': Y,
        'weekly_deals_needed': Z
    }
    """
    # How much commission revenue needed annually to hit variable target
    commission_revenue_needed = target_variable / (commission_pct / 100) if commission_pct > 0 else 0
    
    # How many deals is that?
    annual_deals = commission_revenue_needed / commission_base_per_deal if commission_base_per_deal > 0 else 0
    monthly_deals = annual_deals / 12
    weekly_deals = annual_deals / 52
    
    return {
        'annual_deals_needed': annual_deals,
        'monthly_deals_needed': monthly_deals,
        'weekly_deals_needed': weekly_deals,
        'commission_revenue_needed': commission_revenue_needed
    }


def project_financials(
    monthly_pnl: PnLStatement,
    months: int = 12
) -> dict:
    """
    Project annual financials from monthly run rate.
    
    Returns dict with annual projections.
    """
    return {
        'annual_revenue': monthly_pnl.gross_revenue * months,
        'annual_net_revenue': monthly_pnl.net_revenue * months,
        'annual_cogs': monthly_pnl.cogs * months,
        'annual_opex': monthly_pnl.total_opex * months,
        'annual_ebitda': monthly_pnl.ebitda * months,
        'annual_commissions': monthly_pnl.commissions * months,
        'annual_marketing': monthly_pnl.marketing * months,
    }
