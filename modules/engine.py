"""
GTM Engine: Single source of truth for all funnel and marketing calculations
Pure functions - no Streamlit dependencies
"""

from typing import List, Tuple
from modules.models import Channel, DealEconomics, GTMMetrics, CostMethod


def calculate_channel_spend(
    ch: Channel,
    contacts: float,
    meetings_held: float,
    sales: float
) -> float:
    """
    Calculate marketing spend for a channel using convergent cost model.
    Only ONE funnel stage is paid - the method's target stage blocks all upstream costs.
    """
    method = ch.cost_method
    
    if method == CostMethod.CPA:  # Cost per Sale
        return sales * float(ch.cost_per_sale or 0)
    
    elif method == CostMethod.CPM:  # Cost per Meeting
        return meetings_held * float(ch.cost_per_meeting or 0)
    
    elif method == CostMethod.CPC:  # Cost per Contact
        return contacts * float(ch.cost_per_contact or 0)
    
    elif method == CostMethod.BUDGET:  # Total Budget
        return float(ch.monthly_budget or 0)
    
    else:  # CPL - Cost per Lead (default)
        return ch.monthly_leads * float(ch.cpl or 0)


def compute_channel_metrics(ch: Channel, deal: DealEconomics) -> GTMMetrics:
    """
    Calculate complete funnel metrics for a single channel.
    This is the SINGLE SOURCE OF TRUTH for all channel math.
    """
    if not ch.enabled:
        # Return zeros for disabled channels
        return GTMMetrics(
            leads=0, contacts=0, meetings_scheduled=0, meetings_held=0,
            sales=0, revenue_upfront=0, spend=0, cost_per_sale=0,
            blended_close_rate=0
        )
    
    # Funnel cascade (bowtie model)
    leads = ch.monthly_leads
    contacts = leads * ch.contact_rate
    meetings_scheduled = contacts * ch.meeting_rate
    meetings_held = meetings_scheduled * ch.show_up_rate
    sales = meetings_held * ch.close_rate
    
    # Revenue (use deal economics upfront cash)
    revenue_upfront = sales * deal.upfront_cash
    
    # Spend (convergent cost model)
    spend = calculate_channel_spend(ch, contacts, meetings_held, sales)
    
    # Derived metrics
    cost_per_sale = (spend / sales) if sales > 0 else 0
    blended_close_rate = (sales / meetings_held) if meetings_held > 0 else 0
    
    return GTMMetrics(
        leads=leads,
        contacts=contacts,
        meetings_scheduled=meetings_scheduled,
        meetings_held=meetings_held,
        sales=sales,
        revenue_upfront=revenue_upfront,
        spend=spend,
        cost_per_sale=cost_per_sale,
        blended_close_rate=blended_close_rate
    )


def compute_gtm_aggregate(
    channels: List[Channel],
    deal: DealEconomics
) -> Tuple[List[GTMMetrics], GTMMetrics]:
    """
    Compute GTM metrics for all channels and aggregate totals.
    
    Returns:
        (per_channel_metrics, aggregate_totals)
    """
    # Calculate metrics for each channel
    per_channel = [compute_channel_metrics(ch, deal) for ch in channels]
    
    # Aggregate totals (simple summation)
    def sum_attr(attr: str) -> float:
        return sum(getattr(m, attr) for m in per_channel)
    
    total_leads = sum_attr("leads")
    total_contacts = sum_attr("contacts")
    total_meetings_scheduled = sum_attr("meetings_scheduled")
    total_meetings_held = sum_attr("meetings_held")
    total_sales = sum_attr("sales")
    total_revenue = sum_attr("revenue_upfront")
    total_spend = sum_attr("spend")
    
    # Blended metrics
    total_cost_per_sale = (total_spend / total_sales) if total_sales > 0 else 0
    blended_close_rate = (total_sales / total_meetings_held) if total_meetings_held > 0 else 0
    
    aggregate = GTMMetrics(
        leads=total_leads,
        contacts=total_contacts,
        meetings_scheduled=total_meetings_scheduled,
        meetings_held=total_meetings_held,
        sales=total_sales,
        revenue_upfront=total_revenue,
        spend=total_spend,
        cost_per_sale=total_cost_per_sale,
        blended_close_rate=blended_close_rate
    )
    
    return per_channel, aggregate


def reverse_engineer_leads(
    target_value: float,
    target_stage: str,
    contact_rate: float,
    meeting_rate: float,
    show_up_rate: float,
    close_rate: float
) -> float:
    """
    Reverse engineer how many leads are needed to hit a target at a specific funnel stage.
    
    Args:
        target_value: Desired output (e.g., 25 meetings, 5 sales)
        target_stage: "contacts", "meetings", "sales"
        contact_rate, meeting_rate, show_up_rate, close_rate: Conversion rates
    
    Returns:
        Number of leads required
    """
    if target_stage == "sales":
        conversion = contact_rate * meeting_rate * show_up_rate * close_rate
        return target_value / conversion if conversion > 0 else 0
    
    elif target_stage == "meetings":
        conversion = contact_rate * meeting_rate * show_up_rate
        return target_value / conversion if conversion > 0 else 0
    
    elif target_stage == "contacts":
        conversion = contact_rate
        return target_value / conversion if conversion > 0 else 0
    
    else:  # leads
        return target_value


def calculate_effective_cpl(
    cost_method: CostMethod,
    cost_value: float,
    contact_rate: float,
    meeting_rate: float,
    show_up_rate: float,
    close_rate: float
) -> float:
    """
    Calculate effective CPL for any cost method.
    Useful for displaying "what you're really paying per lead" regardless of input method.
    """
    if cost_method == CostMethod.CPL:
        return cost_value
    
    elif cost_method == CostMethod.CPC:
        return cost_value / contact_rate if contact_rate > 0 else 0
    
    elif cost_method == CostMethod.CPM:
        conversion_to_meeting = contact_rate * meeting_rate * show_up_rate
        return cost_value / conversion_to_meeting if conversion_to_meeting > 0 else 0
    
    elif cost_method == CostMethod.CPA:
        full_conversion = contact_rate * meeting_rate * show_up_rate * close_rate
        return cost_value / full_conversion if full_conversion > 0 else 0
    
    return 0  # Budget method doesn't have a fixed CPL


def validate_channel(ch: Channel) -> List[str]:
    """
    Validate channel configuration and return list of issues.
    Empty list = valid.
    """
    issues = []
    
    # Check rates are between 0-1
    if not (0 <= ch.contact_rate <= 1):
        issues.append(f"Contact rate must be 0-1, got {ch.contact_rate}")
    if not (0 <= ch.meeting_rate <= 1):
        issues.append(f"Meeting rate must be 0-1, got {ch.meeting_rate}")
    if not (0 <= ch.show_up_rate <= 1):
        issues.append(f"Show-up rate must be 0-1, got {ch.show_up_rate}")
    if not (0 <= ch.close_rate <= 1):
        issues.append(f"Close rate must be 0-1, got {ch.close_rate}")
    
    # Check cost configuration matches method
    if ch.cost_method == CostMethod.CPL and (not ch.cpl or ch.cpl <= 0):
        issues.append("CPL method requires valid 'cpl' value")
    elif ch.cost_method == CostMethod.CPC and (not ch.cost_per_contact or ch.cost_per_contact <= 0):
        issues.append("CPC method requires valid 'cost_per_contact' value")
    elif ch.cost_method == CostMethod.CPM and (not ch.cost_per_meeting or ch.cost_per_meeting <= 0):
        issues.append("CPM method requires valid 'cost_per_meeting' value")
    elif ch.cost_method == CostMethod.CPA and (not ch.cost_per_sale or ch.cost_per_sale <= 0):
        issues.append("CPA method requires valid 'cost_per_sale' value")
    elif ch.cost_method == CostMethod.BUDGET and (not ch.monthly_budget or ch.monthly_budget <= 0):
        issues.append("Budget method requires valid 'monthly_budget' value")
    
    # Check for completeness
    if ch.monthly_leads <= 0:
        issues.append("Monthly leads must be > 0")
    
    return issues
