"""
Capacity Validator - Single source of truth for GTM → Team workload validation
Extracts and enhances existing Tab 2 logic (lines 1564-1600)
"""
import math

def validate_capacity(gtm_channels, num_setters, num_closers, working_days=20,
                      calls_per_lead=3, avg_call_mins=8, max_hours_per_day=6):
    """
    Calculate team workload from GTM channels and validate capacity.

    Args:
        gtm_channels: List of GTM channel configs
        num_setters: Number of setters
        num_closers: Number of closers
        working_days: Working days per month
        calls_per_lead: Sales cadence (call attempts per lead)
        avg_call_mins: Average call duration
        max_hours_per_day: Productive hours available per day

    Returns:
        dict: Workload metrics, capacity status, warnings, and fix suggestions
    """

    # 1. Calculate from GTM channels (existing Tab 2 logic)
    total_leads, total_contacts, total_meetings = 0, 0, 0
    for ch in gtm_channels:
        if ch.get('enabled', True):
            leads = ch.get('monthly_leads', 0)
            contact_rate = ch.get('contact_rate', 0.6)
            meeting_rate = ch.get('meeting_rate', 0.3)
            contacts = leads * contact_rate
            meetings = contacts * meeting_rate
            total_leads += leads
            total_contacts += contacts
            total_meetings += meetings

    # 2. Daily per-setter metrics
    daily_leads_per_setter = (total_leads / working_days / num_setters) if num_setters > 0 else 0
    daily_contacts_per_setter = (total_contacts / working_days / num_setters) if num_setters > 0 else 0
    daily_meetings_per_setter = (total_meetings / working_days / num_setters) if num_setters > 0 else 0

    # 3. Call volume with cadence
    daily_calls_per_setter = daily_leads_per_setter * calls_per_lead
    daily_call_hours_per_setter = (daily_calls_per_setter * avg_call_mins) / 60

    # 4. Setter capacity validation
    setter_capacity_pct = (daily_call_hours_per_setter / max_hours_per_day) * 100 if max_hours_per_day > 0 else 0

    if setter_capacity_pct > 100:
        setter_status = 'CRITICAL'
    elif setter_capacity_pct > 85:
        setter_status = 'WARNING'
    else:
        setter_status = 'HEALTHY'

    # 5. Closer capacity validation
    daily_meetings_per_closer = (total_meetings / working_days / num_closers) if num_closers > 0 else 0
    closer_capacity = num_closers * 3 * working_days  # 3 meetings/day capacity
    closer_utilization_pct = (total_meetings / closer_capacity * 100) if closer_capacity > 0 else 0

    if closer_utilization_pct > 90:
        closer_status = 'CRITICAL'
    elif closer_utilization_pct > 75:
        closer_status = 'WARNING'
    else:
        closer_status = 'HEALTHY'

    # 6. Generate warnings and suggestions
    warnings = []
    suggestions = []

    if setter_status == 'CRITICAL':
        shortfall_pct = setter_capacity_pct - 100
        warnings.append(f"🚨 Setters at {setter_capacity_pct:.0f}% capacity ({shortfall_pct:.0f}% over limit)")

        # Calculate fixes
        setters_needed = math.ceil(num_setters * (setter_capacity_pct / 85))
        additional_setters = setters_needed - num_setters

        # Marketing reduction option
        sustainable_leads = (total_leads / setter_capacity_pct) * 85
        leads_to_cut = total_leads - sustainable_leads
        avg_cpl = sum(ch.get('cpl', 50) for ch in gtm_channels if ch.get('enabled', True)) / max(len([ch for ch in gtm_channels if ch.get('enabled', True)]), 1)
        marketing_reduction = leads_to_cut * avg_cpl

        suggestions.append(f"Hire {additional_setters} setter(s) - adds {additional_setters * max_hours_per_day * working_days:.0f}h/mo capacity")
        suggestions.append(f"Reduce marketing by ${marketing_reduction:,.0f} - brings to 85% capacity")
        suggestions.append(f"Reduce cadence from {calls_per_lead} to {int(calls_per_lead * 85 / setter_capacity_pct)} calls/lead")

    if closer_status == 'CRITICAL':
        warnings.append(f"🚨 Closers at {closer_utilization_pct:.0f}% capacity")
        closers_needed = math.ceil(num_closers * (closer_utilization_pct / 75))
        suggestions.append(f"Hire {closers_needed - num_closers} closer(s)")

    # Check for underutilization
    if setter_capacity_pct < 50:
        warnings.append(f"💡 Setters underutilized at {setter_capacity_pct:.0f}% - can handle {100/setter_capacity_pct:.1f}x current volume")

    if closer_utilization_pct < 50:
        warnings.append(f"💡 Closers underutilized at {closer_utilization_pct:.0f}% - reduce to {math.ceil(num_closers * closer_utilization_pct / 65)} or increase marketing")

    return {
        # Per-setter metrics
        'daily_leads_per_setter': daily_leads_per_setter,
        'daily_contacts_per_setter': daily_contacts_per_setter,
        'daily_meetings_per_setter': daily_meetings_per_setter,
        'daily_calls_per_setter': daily_calls_per_setter,
        'daily_hours_per_setter': daily_call_hours_per_setter,

        # Per-closer metrics
        'daily_meetings_per_closer': daily_meetings_per_closer,

        # Capacity status
        'setter_capacity_pct': setter_capacity_pct,
        'setter_status': setter_status,
        'closer_utilization_pct': closer_utilization_pct,
        'closer_status': closer_status,

        # Alerts
        'warnings': warnings,
        'suggestions': suggestions,

        # Team totals
        'total_leads_monthly': total_leads,
        'total_contacts_monthly': total_contacts,
        'total_meetings_monthly': total_meetings,
        'total_calls_monthly': daily_calls_per_setter * num_setters * working_days,
    }
