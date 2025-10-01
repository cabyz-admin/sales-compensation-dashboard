"""
Test suite for business engine - locks down critical math
Run with: pytest modules/tests/test_engine.py -v
"""

import pytest
from modules.models import Channel, DealEconomics, CostMethod, Segment, CommissionPolicy, RoleCompensation
from modules.engine import (
    compute_channel_metrics, compute_gtm_aggregate,
    calculate_channel_spend, reverse_engineer_leads
)
from modules.engine_pnl import (
    calculate_unit_economics, calculate_commission_pools,
    calculate_pnl, calculate_ote_requirements
)
from modules.models import TeamStructure, OperatingCosts


# ============= FIXTURES =============

@pytest.fixture
def sample_deal():
    """Standard deal economics for testing"""
    return DealEconomics(
        avg_deal_value=50000,
        upfront_pct=70.0,
        contract_length_months=12,
        commission_policy=CommissionPolicy.UPFRONT,
        grr=0.90
    )


@pytest.fixture
def sample_channel():
    """Standard CPL channel"""
    return Channel(
        id="test_1",
        name="Test Channel",
        segment=Segment.SMB,
        monthly_leads=1000,
        contact_rate=0.65,
        meeting_rate=0.30,
        show_up_rate=0.70,
        close_rate=0.30,
        cost_method=CostMethod.CPL,
        cpl=50.0
    )


@pytest.fixture
def sample_roles():
    """Standard role compensation"""
    return {
        'closer': RoleCompensation(base=32000, variable=48000, commission_pct=20.0),
        'setter': RoleCompensation(base=16000, variable=24000, commission_pct=3.0),
        'manager': RoleCompensation(base=72000, variable=48000, commission_pct=5.0)
    }


# ============= GTM ENGINE TESTS =============

def test_cpl_spend_is_leads_times_price(sample_channel, sample_deal):
    """CPL method: spend = leads × CPL"""
    metrics = compute_channel_metrics(sample_channel, sample_deal)
    expected_spend = 1000 * 50.0  # 1000 leads × $50
    assert metrics.spend == expected_spend
    assert metrics.spend == 50000


def test_cpm_spend_is_meetings_held_times_price(sample_deal):
    """CPM method: spend = meetings_held × CPM"""
    channel = Channel(
        id="cpm_test",
        name="CPM Channel",
        segment=Segment.SMB,
        monthly_leads=183,  # Reverse engineered for 25 meetings
        contact_rate=0.65,
        meeting_rate=0.30,
        show_up_rate=0.70,
        close_rate=0.30,
        cost_method=CostMethod.CPM,
        cost_per_meeting=200.0
    )
    
    metrics = compute_channel_metrics(channel, sample_deal)
    
    # Should have ~25 meetings held
    assert round(metrics.meetings_held) == 25
    
    # Spend should be meetings × $200
    expected_spend = metrics.meetings_held * 200.0
    assert abs(metrics.spend - expected_spend) < 0.01
    assert abs(metrics.spend - 5000) < 100  # Roughly $5000


def test_cpa_spend_is_sales_times_price(sample_channel, sample_deal):
    """CPA method: spend = sales × CPA"""
    sample_channel.cost_method = CostMethod.CPA
    sample_channel.cost_per_sale = 1000.0
    sample_channel.cpl = None  # Should be ignored
    
    metrics = compute_channel_metrics(sample_channel, sample_deal)
    
    # Calculate expected sales
    expected_sales = 1000 * 0.65 * 0.30 * 0.70 * 0.30
    expected_spend = expected_sales * 1000.0
    
    assert abs(metrics.spend - expected_spend) < 0.01
    assert metrics.sales == expected_sales


def test_budget_spend_is_fixed(sample_deal):
    """Budget method: spend = fixed budget"""
    channel = Channel(
        id="budget_test",
        name="Budget Channel",
        segment=Segment.SMB,
        monthly_leads=1000,
        contact_rate=0.65,
        meeting_rate=0.30,
        show_up_rate=0.70,
        close_rate=0.30,
        cost_method=CostMethod.BUDGET,
        monthly_budget=25000.0
    )
    
    metrics = compute_channel_metrics(channel, sample_deal)
    assert metrics.spend == 25000.0


def test_sales_pipeline_monotonic_nonincreasing(sample_channel, sample_deal):
    """Pipeline stages should decrease: leads ≥ contacts ≥ meetings ≥ sales"""
    metrics = compute_channel_metrics(sample_channel, sample_deal)
    
    assert metrics.leads >= metrics.contacts
    assert metrics.contacts >= metrics.meetings_scheduled
    assert metrics.meetings_scheduled >= metrics.meetings_held
    assert metrics.meetings_held >= metrics.sales


def test_gtm_aggregation_equals_sum_channels(sample_deal):
    """Aggregate metrics should equal sum of channel metrics"""
    channels = [
        Channel(
            id=f"ch_{i}",
            name=f"Channel {i}",
            segment=Segment.SMB,
            monthly_leads=500,
            contact_rate=0.6,
            meeting_rate=0.3,
            show_up_rate=0.7,
            close_rate=0.25,
            cost_method=CostMethod.CPL,
            cpl=50.0
        )
        for i in range(3)
    ]
    
    per_channel, aggregate = compute_gtm_aggregate(channels, sample_deal)
    
    # Verify sums
    assert aggregate.leads == sum(m.leads for m in per_channel)
    assert aggregate.contacts == sum(m.contacts for m in per_channel)
    assert aggregate.sales == sum(m.sales for m in per_channel)
    assert aggregate.spend == sum(m.spend for m in per_channel)
    assert aggregate.revenue_upfront == sum(m.revenue_upfront for m in per_channel)


def test_disabled_channel_returns_zeros(sample_channel, sample_deal):
    """Disabled channels should contribute zero to metrics"""
    sample_channel.enabled = False
    metrics = compute_channel_metrics(sample_channel, sample_deal)
    
    assert metrics.leads == 0
    assert metrics.sales == 0
    assert metrics.spend == 0
    assert metrics.revenue_upfront == 0


# ============= UNIT ECONOMICS TESTS =============

def test_unit_econ_ltv_calculation(sample_deal):
    """LTV = upfront + (deferred × GRR)"""
    unit_econ = calculate_unit_economics(sample_deal, cost_per_sale=5000)
    
    upfront = 50000 * 0.70  # $35,000
    deferred = 50000 * 0.30  # $15,000
    expected_ltv = upfront + (deferred * 0.90)  # $35,000 + $13,500 = $48,500
    
    assert unit_econ.ltv == expected_ltv
    assert unit_econ.cac == 5000


def test_unit_econ_payback_matches_formula(sample_deal):
    """Payback = CAC / (upfront monthly cash flow)"""
    cac = 6000
    unit_econ = calculate_unit_economics(sample_deal, cost_per_sale=cac)
    
    upfront_monthly = (50000 * 0.70) / 12  # $2,916.67/month
    expected_payback = cac / upfront_monthly  # ~2.06 months
    
    assert abs(unit_econ.payback_months - expected_payback) < 0.01


def test_ltv_cac_ratio():
    """LTV:CAC should be LTV / CAC"""
    deal = DealEconomics(
        avg_deal_value=60000,
        upfront_pct=80.0,
        grr=0.95,
        commission_policy=CommissionPolicy.UPFRONT
    )
    
    unit_econ = calculate_unit_economics(deal, cost_per_sale=10000)
    
    # LTV = 48,000 + (12,000 × 0.95) = 59,400
    # CAC = 10,000
    # Ratio = 5.94
    expected_ratio = unit_econ.ltv / 10000
    assert abs(unit_econ.ltv_cac_ratio - expected_ratio) < 0.01


# ============= COMMISSION TESTS =============

def test_commission_policy_upfront_vs_full(sample_deal, sample_roles):
    """Commission base should differ based on policy"""
    sales = 10.0
    
    # Upfront policy
    sample_deal.commission_policy = CommissionPolicy.UPFRONT
    comm_upfront = calculate_commission_pools(
        sales, sample_roles['closer'], sample_roles['setter'],
        sample_roles['manager'], sample_deal
    )
    
    # Full policy
    sample_deal.commission_policy = CommissionPolicy.FULL
    comm_full = calculate_commission_pools(
        sales, sample_roles['closer'], sample_roles['setter'],
        sample_roles['manager'], sample_deal
    )
    
    # Full should be higher (70% vs 100%)
    assert comm_full.total_commission > comm_upfront.total_commission
    assert comm_full.commission_base == 50000
    assert comm_upfront.commission_base == 35000  # 70% of 50k


def test_commission_percentages_sum_correctly(sample_deal, sample_roles):
    """Commission pools should match percentages"""
    sales = 5.0
    comm = calculate_commission_pools(
        sales, sample_roles['closer'], sample_roles['setter'],
        sample_roles['manager'], sample_deal
    )
    
    commission_base = sales * sample_deal.upfront_cash  # 5 × 35,000
    
    # Verify each pool
    assert comm.closer_pool == commission_base * 0.20
    assert comm.setter_pool == commission_base * 0.03
    assert comm.manager_pool == commission_base * 0.05
    
    # Verify total
    expected_total = commission_base * (0.20 + 0.03 + 0.05)
    assert abs(comm.total_commission - expected_total) < 0.01


def test_ote_requirements_calculation():
    """OTE requirements should calculate deals needed correctly"""
    target_variable = 48000  # Annual variable comp
    commission_pct = 20.0
    commission_base = 35000  # Per deal
    
    req = calculate_ote_requirements(target_variable, commission_pct, commission_base)
    
    # Need $48k in commission = $240k in commission base (48k / 0.20)
    # At $35k per deal = 6.86 deals annually
    expected_annual = 240000 / 35000
    assert abs(req['annual_deals_needed'] - expected_annual) < 0.01
    assert abs(req['monthly_deals_needed'] - expected_annual/12) < 0.01


# ============= P&L TESTS =============

def test_pnl_gross_margin_calculation():
    """Gross margin = (gross_profit / net_revenue) × 100"""
    team_base = 400000  # Annual
    opex = OperatingCosts(office_rent=20000, software_costs=10000, other_opex=5000)
    
    pnl = calculate_pnl(
        gross_revenue=200000,
        team_base_annual=team_base,
        commissions=40000,
        marketing_spend=30000,
        operating_costs=opex,
        gov_cost_pct=10.0
    )
    
    # Net revenue = 200k - 20k (10% gov) = 180k
    # COGS = 400k/12 + 40k = 73,333
    # Gross profit = 180k - 73,333 = 106,667
    # Gross margin = 106,667 / 180k = 59.26%
    
    assert abs(pnl.net_revenue - 180000) < 1
    assert abs(pnl.gross_margin - 59.26) < 0.1


def test_pnl_ebitda_calculation():
    """EBITDA = gross_profit - total_opex"""
    team_base = 480000
    opex = OperatingCosts(office_rent=15000, software_costs=8000, other_opex=2000)
    
    pnl = calculate_pnl(
        gross_revenue=250000,
        team_base_annual=team_base,
        commissions=50000,
        marketing_spend=40000,
        operating_costs=opex,
        gov_cost_pct=12.0
    )
    
    # Expected EBITDA = (Net Revenue - COGS) - (Marketing + OpEx)
    expected_net = 250000 * 0.88  # 220,000
    expected_cogs = 480000/12 + 50000  # 90,000
    expected_gross_profit = expected_net - expected_cogs  # 130,000
    expected_opex = 40000 + 25000  # 65,000
    expected_ebitda = expected_gross_profit - expected_opex  # 65,000
    
    assert abs(pnl.ebitda - expected_ebitda) < 1


# ============= REVERSE ENGINEERING TESTS =============

def test_reverse_engineer_leads_for_sales():
    """Should calculate leads needed to hit sales target"""
    target_sales = 10.0
    leads_needed = reverse_engineer_leads(
        target_value=target_sales,
        target_stage="sales",
        contact_rate=0.6,
        meeting_rate=0.3,
        show_up_rate=0.7,
        close_rate=0.25
    )
    
    # Full conversion = 0.6 × 0.3 × 0.7 × 0.25 = 0.0315
    # Leads needed = 10 / 0.0315 = 317.46
    expected = target_sales / (0.6 * 0.3 * 0.7 * 0.25)
    assert abs(leads_needed - expected) < 0.01


def test_reverse_engineer_leads_for_meetings():
    """Should calculate leads needed to hit meeting target"""
    target_meetings = 25.0
    leads_needed = reverse_engineer_leads(
        target_value=target_meetings,
        target_stage="meetings",
        contact_rate=0.65,
        meeting_rate=0.30,
        show_up_rate=0.70,
        close_rate=0.30
    )
    
    # Conversion to meetings = 0.65 × 0.30 × 0.70 = 0.1365
    # Leads = 25 / 0.1365 = 183.15
    expected = target_meetings / (0.65 * 0.30 * 0.70)
    assert abs(leads_needed - expected) < 0.01
    assert abs(leads_needed - 183.15) < 0.1


# ============= EDGE CASES =============

def test_zero_sales_no_divide_by_zero(sample_channel, sample_deal):
    """Zero sales shouldn't cause division by zero"""
    sample_channel.close_rate = 0.0  # Force zero sales
    metrics = compute_channel_metrics(sample_channel, sample_deal)
    
    assert metrics.sales == 0
    assert metrics.cost_per_sale == 0  # Not infinity
    assert metrics.blended_close_rate == 0


def test_zero_cac_ltv_ratio_safe():
    """Zero CAC should handle gracefully"""
    deal = DealEconomics(
        avg_deal_value=50000,
        upfront_pct=70.0,
        grr=0.9,
        commission_policy=CommissionPolicy.UPFRONT
    )
    
    unit_econ = calculate_unit_economics(deal, cost_per_sale=0)
    # LTV:CAC with zero CAC is technically infinite, but we should return 0
    # This depends on how the model property handles it
    assert unit_econ.ltv_cac_ratio >= 0  # No crash


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
