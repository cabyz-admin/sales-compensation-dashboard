# 🎯 Capacity Planning: Supply vs Demand Analysis

## Current State: Naive Capacity Calculation

### What We Calculate Now (Supply-Side Only)

```python
# Team capacity (what they CAN handle)
monthly_closer_capacity = num_closers × meetings_per_closer × working_days
monthly_setter_capacity = num_setters × meetings_per_setter × working_days

# Actual demand (what they ARE handling)  
current_meetings = gtm_metrics['monthly_meetings_held']
current_bookings = gtm_metrics['monthly_meetings_scheduled']

# Utilization
closer_util = current_meetings / monthly_closer_capacity
```

**Example:**
- 8 closers × 3 meetings/day × 20 days = **480 meetings/month capacity**
- GTM generates 191 meetings/month
- Utilization = 191 / 480 = **40%** ✅

---

## The Problem: Missing Demand-Side Planning

### Scenario 1: Channel Growth Exceeds Capacity

```
Your Setup:
├─ Channels configured for 1,000 meetings/month
├─ Contact Rate: 65%
├─ Meeting Rate: 40%
├─ Show-up Rate: 70%
└─ Team capacity: 480 meetings/month

Math:
1,000 leads → 650 contacts → 260 mtgs scheduled → 182 mtgs held

Current Display:
✅ Closer Utilization: 38% (182/480)
✅ Looks healthy!

Reality Check:
❌ You're LOSING 78 meetings! (260 scheduled - 182 held)
❌ Could have 78 more meetings if you had capacity
❌ At 30% close = 23 lost sales
❌ At $50K/deal = $1.17M LOST REVENUE
```

### Scenario 2: Revenue Target Requires More Capacity

```
Revenue Target: $3M/month
Deal Size: $50K
Required Sales: 60/month
Close Rate: 30%
Required Meetings: 200/month

Current Team: 8 closers
Current Capacity: 480 meetings/month
Current Utilization: 40%

Hidden Issue:
✅ Team looks underutilized
❌ But GTM funnel only generates 182 meetings
❌ Need to either:
   - Fix funnel to generate 200+ meetings
   - Or downsize team to match demand
```

---

## What We Should Calculate

### 1. **Demand Forecast (Top-Down)**

```python
# From channel configuration
total_leads_planned = sum(channel.monthly_leads for channel in channels)

# Expected funnel flow
expected_contacts = total_leads_planned × blended_contact_rate
expected_scheduled = expected_contacts × blended_meeting_rate  
expected_held = expected_scheduled × blended_show_up_rate
expected_sales = expected_held × blended_close_rate

# This is what GTM WILL generate → Team must handle
```

### 2. **Supply Capacity (Bottom-Up)**

```python
# What team CAN handle
team_capacity_meetings = num_closers × meetings_per_closer × working_days
team_capacity_contacts = num_setters × contacts_per_setter × working_days

# Maximum possible sales
max_sales = team_capacity_meetings × close_rate
```

### 3. **Gap Analysis (Critical!)**

```python
# Meeting constraint
meeting_gap = expected_held - team_capacity_meetings
if meeting_gap > 0:
    # Need more closers
    additional_closers = ceil(meeting_gap / (meetings_per_closer × working_days))
    lost_sales = meeting_gap × close_rate
    lost_revenue = lost_sales × deal_value
    
# Contact constraint  
contact_gap = expected_contacts - team_capacity_contacts
if contact_gap > 0:
    # Need more setters
    additional_setters = ceil(contact_gap / (contacts_per_setter × working_days))
```

### 4. **Bottleneck Detection**

```python
# What's the limiting factor?
if expected_held > team_capacity_meetings:
    bottleneck = "Closers"
    constraint_impact = lost_revenue_from_missing_closers
elif expected_contacts > team_capacity_contacts:
    bottleneck = "Setters" 
    constraint_impact = lost_revenue_from_missing_setters
elif expected_sales < revenue_target / deal_value:
    bottleneck = "Funnel"
    constraint_impact = "Need more leads or better conversion"
else:
    bottleneck = None
    status = "Team properly sized"
```

---

## Smarter Capacity Metrics

### Current (Naive)
```
Closer Utilization: 40%
Status: ✅ Healthy
```

### Proposed (Intelligent)
```
┌─────────────────────────────────────────────────────────┐
│ 🎯 Capacity Planning Analysis                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ DEMAND (GTM Funnel):                                    │
│   Meetings Scheduled: 260/month                         │
│   Meetings Held: 182/month (70% show-up)               │
│   Lost to No-Shows: 78 meetings                         │
│                                                          │
│ SUPPLY (Team Capacity):                                 │
│   Closer Capacity: 480 meetings/month                   │
│   Current Load: 182 meetings (38% util)                 │
│   Available Headroom: 298 meetings                      │
│                                                          │
│ GAP ANALYSIS:                                           │
│   ⚠️ BOTTLENECK: Show-up Rate (70%)                     │
│   Opportunity Cost: 78 lost meetings                    │
│   Revenue Impact: $1.17M/month                          │
│                                                          │
│ RECOMMENDATIONS:                                        │
│   1. Improve show-up rate 70% → 85%                    │
│      → Recover 39 meetings → +$585K revenue            │
│   2. Current team is OVERSIZED for demand               │
│      → Could reduce to 5 closers and save $96K/year    │
│   3. OR scale GTM to fill capacity                      │
│      → Add 480 leads to fill closer capacity            │
│                                                          │
│ DECISION:                                               │
│   [ ] Grow GTM to match team capacity                   │
│   [ ] Rightsize team to match GTM demand                │
│   [ ] Improve show-up rate to maximize efficiency       │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation: Demand-Aware Team Sizing

### Function 1: Calculate Required Team

```python
def calculate_required_team(
    monthly_leads: int,
    contact_rate: float,
    meeting_rate: float,
    show_up_rate: float,
    close_rate: float,
    revenue_target: float,
    deal_value: float,
    meetings_per_closer: int = 3,
    contacts_per_setter: int = 10,
    working_days: int = 20
) -> Dict:
    """
    Given GTM funnel metrics, calculate required team size.
    This is TOP-DOWN: Demand drives team size.
    """
    # Flow through funnel
    contacts = monthly_leads * contact_rate
    meetings_scheduled = contacts * meeting_rate
    meetings_held = meetings_scheduled * show_up_rate
    sales = meetings_held * close_rate
    revenue = sales * deal_value
    
    # Required team to handle this demand
    required_closers = ceil(meetings_held / (meetings_per_closer * working_days))
    required_setters = ceil(contacts / (contacts_per_setter * working_days))
    
    # If revenue target is higher, need more
    sales_for_target = revenue_target / deal_value
    if sales_for_target > sales:
        # Need more meetings
        meetings_for_target = sales_for_target / close_rate
        required_closers_for_target = ceil(meetings_for_target / (meetings_per_closer * working_days))
        required_closers = max(required_closers, required_closers_for_target)
    
    return {
        'required_closers': required_closers,
        'required_setters': required_setters,
        'expected_meetings': meetings_held,
        'expected_sales': sales,
        'expected_revenue': revenue,
        'meets_target': revenue >= revenue_target
    }
```

### Function 2: Detect Constraints

```python
def detect_constraints(
    current_team: Dict,
    gtm_demand: Dict,
    revenue_target: float
) -> Dict:
    """
    Find what's constraining growth: Team, Funnel, or Process.
    """
    constraints = []
    
    # Check if team can handle GTM demand
    if gtm_demand['expected_meetings'] > current_team['closer_capacity']:
        lost_meetings = gtm_demand['expected_meetings'] - current_team['closer_capacity']
        lost_sales = lost_meetings * gtm_demand['close_rate']
        lost_revenue = lost_sales * gtm_demand['deal_value']
        
        constraints.append({
            'type': 'TEAM_CAPACITY',
            'bottleneck': 'Closers',
            'impact': lost_revenue,
            'recommendation': f"Add {ceil(lost_meetings / (3 * 20))} closers to capture {lost_revenue:,.0f} revenue"
        })
    
    # Check if demand meets target
    if gtm_demand['expected_revenue'] < revenue_target:
        revenue_gap = revenue_target - gtm_demand['expected_revenue']
        sales_gap = revenue_gap / gtm_demand['deal_value']
        
        constraints.append({
            'type': 'DEMAND',
            'bottleneck': 'Funnel',
            'impact': revenue_gap,
            'recommendation': f"Need {sales_gap:.0f} more sales. Increase leads or conversion rates."
        })
    
    # Check process efficiency
    show_up_rate = gtm_demand.get('show_up_rate', 1.0)
    if show_up_rate < 0.8:
        potential_meetings = gtm_demand['meetings_scheduled'] * (0.85 - show_up_rate)
        potential_revenue = potential_meetings * gtm_demand['close_rate'] * gtm_demand['deal_value']
        
        constraints.append({
            'type': 'PROCESS',
            'bottleneck': 'Show-up Rate',
            'impact': potential_revenue,
            'recommendation': f"Improve show-up {show_up_rate:.0%} → 85% to gain ${potential_revenue:,.0f}"
        })
    
    return {
        'constraints': constraints,
        'primary_bottleneck': constraints[0] if constraints else None,
        'is_optimized': len(constraints) == 0
    }
```

### Function 3: Team Sizing Scenarios

```python
def generate_team_scenarios(
    base_metrics: Dict,
    revenue_target: float
) -> List[Dict]:
    """
    Generate 3 scenarios: Current, Optimized, Target-Aligned
    """
    scenarios = []
    
    # Scenario 1: Current State
    scenarios.append({
        'name': 'Current',
        'closers': base_metrics['current_closers'],
        'setters': base_metrics['current_setters'],
        'capacity': base_metrics['closer_capacity'],
        'utilization': base_metrics['utilization'],
        'revenue': base_metrics['revenue'],
        'cost': base_metrics['team_cost']
    })
    
    # Scenario 2: Right-sized for Current Demand
    optimal = calculate_required_team(
        base_metrics['leads'],
        base_metrics['contact_rate'],
        base_metrics['meeting_rate'],
        base_metrics['show_up_rate'],
        base_metrics['close_rate'],
        base_metrics['revenue'],  # Current, not target
        base_metrics['deal_value']
    )
    scenarios.append({
        'name': 'Optimized for Current Demand',
        'closers': optimal['required_closers'],
        'setters': optimal['required_setters'],
        'capacity': optimal['required_closers'] * 3 * 20,
        'utilization': 75,  # Target 75%
        'revenue': optimal['expected_revenue'],
        'cost': calculate_team_cost(optimal['required_closers'], optimal['required_setters'])
    })
    
    # Scenario 3: Sized for Revenue Target
    target_aligned = calculate_required_team(
        # ... calculate leads needed for target ...
    )
    scenarios.append({
        'name': 'Target-Aligned',
        'closers': target_aligned['required_closers'],
        'setters': target_aligned['required_setters'],
        'capacity': target_aligned['capacity'],
        'utilization': target_aligned['utilization'],
        'revenue': revenue_target,
        'cost': target_aligned['cost']
    })
    
    return scenarios
```

---

## UI Enhancements Needed

### 1. **Demand vs Supply Chart**

```
     DEMAND (GTM)         SUPPLY (Team)
    
260 mtgs scheduled  →  480 mtgs capacity
182 mtgs held       →  [||||||||40%  util]
                        298 headroom
                    
⚠️ 78 meetings lost to no-shows
💡 Opportunity: $1.17M/month
```

### 2. **Constraint Alert**

```
⚠️ PRIMARY BOTTLENECK: Show-up Rate

Current: 70% → Only 182 of 260 meetings happen
If improved to 85%: → 221 meetings (+39)
Revenue Impact: +$585K/month

Actions:
[ ] Implement confirmation sequences
[ ] Add calendar reminders  
[ ] Require double opt-in
```

### 3. **Team Sizing Recommendation**

```
📊 Based on your GTM funnel:

Current: 8 closers, 4 setters
Status: OVERSIZED for demand

Recommendations:
1️⃣ Match current demand:
   → 5 closers, 3 setters
   → Save $96K/year
   → Same revenue output

2️⃣ Grow GTM to match team:
   → Need 800 more leads/month
   → Would generate $2.1M more revenue
   → Team would reach 75% utilization

3️⃣ Hit revenue target ($3M):
   → Keep 8 closers
   → Add 600 leads
   → Improve show-up to 85%
```

---

## Recommended Implementation Order

### Phase 1: Add Constraint Detection (High Priority)
- Show if team is over/undersized for GTM demand
- Show bottlenecks (team, funnel, or process)
- Show revenue impact of constraints

### Phase 2: Add Required Team Calculator (Medium Priority)  
- "What team do you need?" widget
- Input: Revenue target
- Output: Required closers/setters

### Phase 3: Add Scenario Comparison (Medium Priority)
- Side-by-side: Current vs Optimized vs Target
- Show cost, revenue, utilization for each

### Phase 4: Add Demand Forecasting (Low Priority)
- Predict meetings based on channel changes
- Warn if changes will exceed team capacity
- Suggest team adjustments proactively

---

## Example: Complete Capacity Analysis

```python
{
    'demand': {
        'leads': 1000,
        'contacts': 650,
        'meetings_scheduled': 260,
        'meetings_held': 182,
        'sales': 54.6,
        'revenue': 2_730_000
    },
    'supply': {
        'closers': 8,
        'closer_capacity': 480,
        'setters': 4,
        'setter_capacity': 800,
        'cost': 489_000
    },
    'utilization': {
        'closer': 0.38,
        'setter': 0.81,
        'status': 'Closers UNDERUTILIZED, Setters HEALTHY'
    },
    'constraints': [
        {
            'type': 'PROCESS',
            'bottleneck': 'Show-up Rate (70%)',
            'lost_meetings': 78,
            'lost_revenue': 1_170_000,
            'recommendation': 'Improve show-up 70% → 85%'
        }
    ],
    'optimal_team': {
        'closers': 5,
        'setters': 4,
        'cost_savings': 96_000,
        'maintains_revenue': True
    }
}
```

---

## Summary

**Current State:**
- ❌ Only tracks supply (team capacity)
- ❌ Doesn't consider demand (GTM funnel)
- ❌ No constraint detection
- ❌ No team sizing recommendations

**Needed:**
- ✅ Demand-aware capacity planning
- ✅ Constraint detection (team, funnel, process)
- ✅ Team sizing recommendations
- ✅ Scenario comparison
- ✅ Revenue impact analysis

**Next Step:** Implement Phase 1 (Constraint Detection) in Team Configuration section.
