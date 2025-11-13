# System Consolidation Plan - v3.7

**Discovery:** The holistic GTM → Team workload calculations ALREADY EXIST!
**Location:** Tab 2, lines 1564-1600 ("📞 Setter Activities" section)
**Strategy:** Consolidate + Enhance existing code (not rebuild from scratch)

---

## 🎯 What Already Exists (Tab 2)

```python
# Lines 1564-1600: Already calculating holistically!

# 1. Pulls from GTM channels
for ch in st.session_state.gtm_channels:
    leads = ch.get('monthly_leads', 0)
    contacts = leads * ch.get('contact_rate', 0.6)
    meetings = contacts * ch.get('meeting_rate', 0.3)
    total_leads += leads
    total_contacts += contacts
    total_meetings += meetings

# 2. Calculates daily per person
daily_leads_per_setter = (total_leads / working_days) / num_setters
daily_contacts_per_setter = (total_contacts / working_days) / num_setters
daily_meetings_per_setter = (total_meetings / working_days) / num_setters

# 3. Shows results
st.metric("Leads to Contact/Day", f"{daily_leads_per_setter:.1f} per person")
st.metric("Contacts Made/Day", f"{daily_contacts_per_setter:.1f} per person")
st.metric("Meetings Scheduled/Day", f"{daily_meetings_per_setter:.1f} per person")
```

**This is PERFECT!** It's already:
- ✅ Connected to GTM channels
- ✅ Using actual conversion rates
- ✅ Calculating per-person workload
- ✅ Showing team totals

---

## ❌ What's Missing (Why you couldn't see it)

### 1. **No Capacity Validation**
```python
# Current: Shows "12.5 leads to contact/day"
# Missing: Is 12.5 leads/day realistic? Can setter handle it?
```

### 2. **No Sales Cadence Modeling**
```python
# Current: Assumes 1 contact = 1 call
# Reality: 1 contact might need 3-7 call attempts
```

### 3. **No Warning System**
```python
# Current: Shows metrics passively
# Missing: "⚠️ Setters would need 80 calls/day - IMPOSSIBLE!"
```

### 4. **Buried in Tab 2**
```python
# Current: Hidden in compensation tab
# Better: Should be prominent in GTM Command Center (Tab 1)
```

### 5. **Duplicate Logic**
```python
# Tab 2 (line 1564): Calculates GTM → Workload
# Tab 5 (line 3249): NEW code also calculates workload
# Problem: Two sources of truth!
```

---

## 🔧 Consolidation Strategy

### Phase 1: Extract to Shared Module (Week 1)

**Create:** `modules/holistic_calculator.py`

```python
class HolisticGTMCalculator:
    """
    Single source of truth for GTM → Team workload calculations
    Used by: Tab 1 (GTM Center), Tab 2 (Comp), Tab 5 (Config), Tab 6 (Performance)
    """

    @staticmethod
    def calculate_team_workload(gtm_channels, team_config, cadence_config=None):
        """
        Calculate realistic team workload from GTM channels

        Returns:
        {
            'daily_leads_per_setter': 12.5,
            'daily_contacts_per_setter': 8.1,
            'daily_meetings_per_setter': 3.2,
            'daily_calls_per_setter': 43.8,  # NEW: Based on cadence
            'daily_hours_per_setter': 5.8,   # NEW: Time required
            'capacity_status': 'OVERLOAD',   # NEW: Validation
            'warnings': ['Setters at 145% capacity'], # NEW: Alerts
            'suggestions': ['Hire 2 more setters OR reduce marketing by $12K']
        }
        """

        # 1. Calculate from GTM channels (existing logic from Tab 2)
        total_leads, total_contacts, total_meetings = 0, 0, 0
        for ch in gtm_channels:
            if ch.get('enabled', True):
                leads = ch.get('monthly_leads', 0)
                contacts = leads * ch.get('contact_rate', 0.6)
                meetings = contacts * ch.get('meeting_rate', 0.3)
                total_leads += leads
                total_contacts += contacts
                total_meetings += meetings

        # 2. Calculate per-setter daily (existing logic)
        working_days = team_config.get('working_days', 20)
        num_setters = team_config.get('num_setters', 4)

        daily_leads_per_setter = (total_leads / working_days) / num_setters
        daily_contacts_per_setter = (total_contacts / working_days) / num_setters
        daily_meetings_per_setter = (total_meetings / working_days) / num_setters

        # 3. NEW: Calculate call volume based on cadence
        if cadence_config:
            calls_per_lead = cadence_config.get('call_attempts', 3)
            daily_calls_per_setter = daily_leads_per_setter * calls_per_lead

            avg_call_duration = cadence_config.get('avg_call_duration_mins', 8)
            daily_call_time_mins = daily_calls_per_setter * avg_call_duration
            daily_hours_per_setter = daily_call_time_mins / 60
        else:
            # Default: Assume 1 call per contact
            daily_calls_per_setter = daily_contacts_per_setter
            daily_hours_per_setter = daily_calls_per_setter * 8 / 60

        # 4. NEW: Capacity validation
        max_calls_per_day = team_config.get('max_calls_per_setter_per_day', 40)
        max_hours_per_day = team_config.get('productive_hours_per_day', 6)

        call_capacity_pct = (daily_calls_per_setter / max_calls_per_day) * 100
        time_capacity_pct = (daily_hours_per_setter / max_hours_per_day) * 100

        capacity_pct = max(call_capacity_pct, time_capacity_pct)

        if capacity_pct > 100:
            capacity_status = 'OVERLOAD'
        elif capacity_pct > 85:
            capacity_status = 'WARNING'
        else:
            capacity_status = 'HEALTHY'

        # 5. NEW: Generate warnings and suggestions
        warnings = []
        suggestions = []

        if capacity_status == 'OVERLOAD':
            shortfall_pct = capacity_pct - 100
            warnings.append(f"Setters at {capacity_pct:.0f}% capacity ({shortfall_pct:.0f}% over limit)")

            # Calculate fixes
            setters_needed = math.ceil(num_setters * (capacity_pct / 85))  # Target 85%
            additional_setters = setters_needed - num_setters

            # Alternative: Reduce marketing
            sustainable_leads = (total_leads / capacity_pct) * 85
            leads_to_cut = total_leads - sustainable_leads
            avg_cpl = sum(ch.get('cpl', 50) for ch in gtm_channels) / len(gtm_channels)
            marketing_reduction = leads_to_cut * avg_cpl

            suggestions.append(f"Hire {additional_setters} more setter(s)")
            suggestions.append(f"OR reduce marketing by ${marketing_reduction:,.0f}")

        return {
            'daily_leads_per_setter': daily_leads_per_setter,
            'daily_contacts_per_setter': daily_contacts_per_setter,
            'daily_meetings_per_setter': daily_meetings_per_setter,
            'daily_calls_per_setter': daily_calls_per_setter,
            'daily_hours_per_setter': daily_hours_per_setter,
            'capacity_pct': capacity_pct,
            'capacity_status': capacity_status,
            'warnings': warnings,
            'suggestions': suggestions,
            'team_totals': {
                'daily_leads': daily_leads_per_setter * num_setters,
                'daily_contacts': daily_contacts_per_setter * num_setters,
                'daily_meetings': daily_meetings_per_setter * num_setters,
                'daily_calls': daily_calls_per_setter * num_setters,
            }
        }
```

---

### Phase 2: Surface in Tab 1 (Week 1)

**Enhance Tab 1 (GTM Command Center)** with prominent capacity warnings:

```python
# In Tab 1, after channel configuration
st.markdown("---")
st.markdown("### 🎯 Team Workload & Capacity Check")

# Calculate holistically
team_config = {
    'num_setters': st.session_state.get('num_setters_main', 4),
    'working_days': st.session_state.get('working_days', 20),
    'max_calls_per_setter_per_day': 40,
    'productive_hours_per_day': 6
}

cadence_config = {
    'call_attempts': st.session_state.get('cadence_call_attempts', 3),
    'avg_call_duration_mins': st.session_state.get('avg_call_duration_mins', 8)
}

workload = HolisticGTMCalculator.calculate_team_workload(
    st.session_state.gtm_channels,
    team_config,
    cadence_config
)

# Display with color-coded status
workload_cols = st.columns([2, 1])

with workload_cols[0]:
    st.markdown("**📊 Setter Workload (Per Person/Day)**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Leads to Contact", f"{workload['daily_leads_per_setter']:.1f}")
    with col2:
        st.metric("Calls Required", f"{workload['daily_calls_per_setter']:.1f}")
    with col3:
        st.metric("Hours Needed", f"{workload['daily_hours_per_setter']:.1f}h")

with workload_cols[1]:
    # Capacity gauge
    status = workload['capacity_status']
    if status == 'OVERLOAD':
        st.error(f"🚨 {workload['capacity_pct']:.0f}% Capacity")
        st.caption("CRITICAL: Team overloaded")
    elif status == 'WARNING':
        st.warning(f"⚠️ {workload['capacity_pct']:.0f}% Capacity")
        st.caption("High but manageable")
    else:
        st.success(f"✅ {workload['capacity_pct']:.0f}% Capacity")
        st.caption("Healthy workload")

# Show warnings
if workload['warnings']:
    for warning in workload['warnings']:
        st.warning(f"⚠️ {warning}")

# Show suggestions
if workload['suggestions']:
    st.info("💡 **Suggested Actions:**")
    for i, suggestion in enumerate(workload['suggestions'], 1):
        st.caption(f"{i}. {suggestion}")
```

---

### Phase 3: Add Sales Cadence Config (Week 2)

**Add to Tab 5 (Configuration):**

```python
# In Tab 5, before Team Configuration
with st.expander("📞 Sales Cadence Configuration", expanded=False):
    st.info("💡 Define how many times you call each lead")

    cadence_cols = st.columns(2)

    with cadence_cols[0]:
        cadence_type = st.selectbox(
            "Cadence Type",
            ["Light (3 calls)", "Standard (5 calls)", "Aggressive (7 calls)", "Custom"],
            key="cadence_type"
        )

        if cadence_type == "Custom":
            call_attempts = st.number_input(
                "Calls Per Lead",
                min_value=1,
                max_value=15,
                value=5,
                key="cadence_call_attempts"
            )
        else:
            call_attempts = {
                "Light (3 calls)": 3,
                "Standard (5 calls)": 5,
                "Aggressive (7 calls)": 7
            }[cadence_type]
            st.session_state['cadence_call_attempts'] = call_attempts

        st.metric("Total Calls Per Lead", f"{call_attempts}")

    with cadence_cols[1]:
        avg_call_duration = st.number_input(
            "Avg Call Duration (mins)",
            min_value=1,
            max_value=30,
            value=8,
            key="avg_call_duration_mins"
        )

        time_per_lead = call_attempts * avg_call_duration
        st.metric("Time Per Lead", f"{time_per_lead} mins")

    st.caption(f"📊 **Example:** 10 leads/day × {call_attempts} calls = {call_attempts * 10} dials/day ({time_per_lead * 10 / 60:.1f} hours)")
```

---

### Phase 4: Remove Duplicate Code (Week 2)

**Delete or redirect:**
1. Tab 5's "Setter Activity Planning" module (lines 3134-3458)
   - Replace with: "See GTM Command Center (Tab 1) for workload analysis"
   - Or: Keep as detailed view that calls `HolisticGTMCalculator`

2. Ensure all tabs use same calculator:
   - Tab 1: Workload validation
   - Tab 2: Activity targets (refactor to use module)
   - Tab 5: Configuration (sets params only)
   - Tab 6: Performance tracking (uses same calc)

---

## 🎯 Result: Single Source of Truth

### Before (Current):
```
Tab 1: GTM channels → No workload check
Tab 2: GTM channels → Calculate activities (isolated)
Tab 5: Static target → Calculate activities (different formula)
Tab 6: Performance tracking → Uses Tab 2's numbers?

❌ Three different calculations!
❌ No cross-validation!
```

### After (Consolidated):
```
HolisticGTMCalculator (single module)
    ↓
├─ Tab 1: Shows workload + warnings
├─ Tab 2: Shows daily activities
├─ Tab 5: Config only (no calculation)
└─ Tab 6: Performance vs holistic targets

✅ One calculation
✅ Always in sync
✅ Capacity validated
✅ Clear warnings
```

---

## 📊 Example Output (Tab 1)

```
┌─────────────────────────────────────────────────────┐
│ 🎯 Team Workload & Capacity Check                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Setter Workload (Per Person/Day):                   │
│   Leads to Contact: 12.5                             │
│   Calls Required: 37.5  (12.5 leads × 3 call attempts)
│   Hours Needed: 5.0h    (37.5 calls × 8 mins)      │
│                                                      │
│ Capacity: 🚨 125% - OVERLOAD                        │
│                                                      │
│ ⚠️ Setters at 125% capacity (25% over limit)       │
│                                                      │
│ 💡 Suggested Actions:                                │
│   1. Hire 2 more setters                            │
│   2. OR reduce marketing by $8,000                  │
│   3. OR reduce cadence to 2 calls per lead         │
│                                                      │
│ [Quick Fix ▼]                                       │
│   ○ Hire 2 setters ($96K/year)                     │
│   ● Reduce marketing to $22K (sustainable)         │
│   ○ Change to "Light" cadence (3→2 calls)         │
│                                                      │
│ [Apply Selected Fix]                                │
└─────────────────────────────────────────────────────┘
```

---

## ⏱️ Timeline

**Week 1:**
- Day 1-2: Create `HolisticGTMCalculator` module
- Day 3-4: Refactor Tab 2 to use module
- Day 4-5: Add capacity warnings to Tab 1

**Week 2:**
- Day 1-2: Add sales cadence configuration to Tab 5
- Day 3-4: Remove duplicate setter activity planning
- Day 5: Testing & bug fixes

**Total: 2 weeks** to consolidate and enhance existing system

---

## Summary

**Key Insight:** Don't rebuild - the holistic calculations ALREADY EXIST in Tab 2!

**Strategy:**
1. ✅ Extract existing logic to shared module
2. ✅ Surface warnings in Tab 1 (prominent placement)
3. ✅ Add sales cadence config
4. ✅ Remove duplicate code in Tab 5
5. ✅ Connect everything through one calculator

**Result:** Simpler, more maintainable, uses existing tested code

**Your instinct was right:** The system IS meant to be connected - and it already is! We just need to make it more visible and add validation.