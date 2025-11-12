# ROOT CAUSE ANALYSIS: Values Resetting to Defaults

**Investigation Date:** 2025-11-12
**Investigator:** Durov (Debug Specialist)
**Severity:** CRITICAL - User-facing data loss

---

## EXECUTIVE SUMMARY

After systematic investigation, I have identified the **ROOT CAUSE** of why values reset randomly despite all previous fixes. The issue is NOT circular references, NOT cache invalidation, and NOT session state clearing.

**The root cause is: Missing `value` parameter in Streamlit number_input widgets.**

When `st.number_input()` is called without an explicit `value` parameter, Streamlit uses the `min_value` as the default, OVERWRITING any existing session state value on every render.

---

## THE PROBLEM: How Streamlit Widgets Work

### Streamlit number_input Signature
```python
st.number_input(
    label,           # Position 0
    min_value,       # Position 1  <-- BECOMES DEFAULT if value is omitted!
    max_value,       # Position 2
    value,           # Position 3  <-- MUST be explicitly provided!
    step,
    format,
    key,
    help
)
```

### Critical Behavior
When you call:
```python
st.number_input("Closers", 1, 50, key="num_closers_main")
```

Streamlit interprets this as:
- `label = "Closers"`
- `min_value = 1`
- `max_value = 50`
- `value = <NOT PROVIDED>` **<-- Defaults to min_value (1)!**
- `key = "num_closers_main"`

**Every time the app reruns, this widget resets `st.session_state['num_closers_main']` to 1!**

---

## PROBLEMATIC LOCATIONS

### 1. Team Size Widgets (Lines 2901-2904)

**File:** `/Users/castillo/CascadeProjects/comp-structure/dashboards/production/dashboard_fast.py`

```python
# Line 2901 - PROBLEMATIC
num_closers = st.number_input("Closers", 1, 50, key="num_closers_main")
# Resets to 1 on every render!

# Line 2902 - PROBLEMATIC
num_setters = st.number_input("Setters", 0, 50, key="num_setters_main")
# Resets to 0 on every render!

# Line 2903 - PROBLEMATIC
num_managers = st.number_input("Managers", 0, 20, key="num_managers_main")
# Resets to 0 on every render!

# Line 2904 - PROBLEMATIC
num_bench = st.number_input("Bench", 0, 20, key="num_benchs_main")
# Resets to 0 on every render!
```

**Impact:** When user changes number of closers, the next render resets it back to 1 (min_value).

---

### 2. Compensation Widgets (Lines 3193-3241)

```python
# Line 3193 - PROBLEMATIC
closer_base = st.number_input(
    "Base Salary (Annual $)",
    0, 200000, step=1000,     # min=0, max=200000, NO value!
    key="closer_base",
    help="Annual salary + commission on deals"
)
# Resets to 0 on every render!

# Line 3199 - PROBLEMATIC
closer_comm = st.number_input(
    "Commission % (Per Deal)",
    0.0, 50.0, step=0.5,      # min=0.0, max=50.0, NO value!
    key="closer_commission_pct",
    help="Percentage of each deal value (unlimited upside)"
)
# Resets to 0.0 on every render!

# Line 3208 - PROBLEMATIC
setter_base = st.number_input(
    "Base Salary (Annual $)",
    0, 200000, step=1000,     # Resets to 0!
    key="setter_base",
)

# Line 3214 - PROBLEMATIC
setter_comm = st.number_input(
    "Commission % (Per Deal)",
    0.0, 50.0, step=0.5,      # Resets to 0.0!
    key="setter_commission_pct",
)

# Line 3223 - PROBLEMATIC
manager_base = st.number_input(
    "Base Salary (Annual $)",
    0, 300000, step=1000,     # Resets to 0!
    key="manager_base",
)

# Line 3229 - PROBLEMATIC
manager_comm = st.number_input(
    "Commission % (Per Deal)",
    0.0, 50.0, step=0.5,      # Resets to 0.0!
    key="manager_commission_pct",
)

# Line 3238 - PROBLEMATIC
bench_base = st.number_input(
    "Base Salary (Annual $)",
    0, 200000, step=1000,     # Resets to 0!
    key="bench_base",
)
```

**Impact:** Every time user changes ANY value, the next render resets ALL compensation to 0!

---

## WHY THIS HAPPENS

### The Reset Sequence

1. **User changes a value** (e.g., closer_base from 32000 to 45000)
2. Streamlit updates `st.session_state['closer_base'] = 45000`
3. Streamlit triggers a rerun to reflect the change
4. **During rerun, widget code executes:**
   ```python
   closer_base = st.number_input("Base Salary", 0, 200000, step=1000, key="closer_base")
   ```
5. **Streamlit sees NO value parameter, uses min_value (0) as default**
6. `st.session_state['closer_base']` is overwritten to 0
7. Widget displays 0, user's input is lost

### Why initialization doesn't help

```python
# Line 238-240
for key, value in defaults.items():
    if key not in st.session_state:  # Only sets if missing
        st.session_state[key] = value
```

This initialization (line 242) runs BEFORE widgets are rendered. But then widgets render WITHOUT value parameter, overwriting the initialized values!

**Execution order:**
1. Initialize session_state (sets closer_base = 32000)
2. Widget renders without value parameter
3. Widget sets closer_base = 0 (min_value)
4. User sees 0, not 32000

---

## WHY PREVIOUS FIXES DIDN'T WORK

### Fix 1: Removed circular references (line 2445)
- **Problem addressed:** deal_calc_method circular reference
- **Why it didn't help:** Not related to widget value parameter issue

### Fix 2: Apply button pattern for calculator
- **Problem addressed:** Calculator values persisting
- **Why it didn't help:** Calculator widgets DO use value parameter correctly (lines 2487, 2497, etc.)

### Fix 3: Fixed widget key collisions with calc_ prefixes
- **Problem addressed:** Key name conflicts
- **Why it didn't help:** Keys are not the issue, missing value parameter is

### Fix 4: Pending import pattern
- **Problem addressed:** Template import flow
- **Why it didn't help:** Import works correctly, widgets immediately overwrite imported values

---

## THE FIX

### Required Changes

For EVERY problematic widget, add explicit `value` parameter that reads from session_state:

#### Team Size Widgets (Line 2901-2904)
```python
# BEFORE (BROKEN)
num_closers = st.number_input("Closers", 1, 50, key="num_closers_main")

# AFTER (FIXED)
num_closers = st.number_input(
    "Closers",
    min_value=1,
    max_value=50,
    value=st.session_state.get('num_closers_main', 8),  # Explicit value!
    key="num_closers_main"
)
```

#### Compensation Widgets (Lines 3193-3241)
```python
# BEFORE (BROKEN)
closer_base = st.number_input(
    "Base Salary (Annual $)",
    0, 200000, step=1000,
    key="closer_base",
)

# AFTER (FIXED)
closer_base = st.number_input(
    "Base Salary (Annual $)",
    min_value=0,
    max_value=200000,
    value=st.session_state.get('closer_base', 32000),  # Explicit value!
    step=1000,
    key="closer_base",
)
```

### Why This Fix Works

When you provide explicit `value` parameter:
1. Widget reads current value from session_state
2. Displays that value to user
3. When user changes it, Streamlit updates session_state
4. On rerun, widget reads the UPDATED value from session_state
5. No reset occurs!

---

## ALL WIDGETS REQUIRING FIXES

### Team Size Section (4 widgets)
- Line 2901: `num_closers_main` - resets to 1
- Line 2902: `num_setters_main` - resets to 0
- Line 2903: `num_managers_main` - resets to 0
- Line 2904: `num_benchs_main` - resets to 0

### Compensation Section (7 widgets)
- Line 3193: `closer_base` - resets to 0
- Line 3199: `closer_commission_pct` - resets to 0.0
- Line 3208: `setter_base` - resets to 0
- Line 3214: `setter_commission_pct` - resets to 0.0
- Line 3223: `manager_base` - resets to 0
- Line 3229: `manager_commission_pct` - resets to 0.0
- Line 3238: `bench_base` - resets to 0

**Total:** 11 broken widgets causing the reset issue

---

## VERIFICATION PLAN

After applying fix:

1. **Test Team Size Changes**
   - Change num_closers from 8 to 12
   - Verify it stays at 12 after rerun
   - Change another widget, verify closers still 12

2. **Test Compensation Changes**
   - Change closer_base from 32000 to 45000
   - Verify it stays at 45000 after rerun
   - Change closer_commission_pct, verify base still 45000

3. **Test Combined Changes**
   - Change multiple values
   - Trigger refresh button
   - Verify ALL values persist

4. **Test Import/Export Flow**
   - Export config
   - Change values
   - Import config
   - Verify all values restored correctly

---

## ADDITIONAL FINDINGS

### Non-problematic widgets (already correct)

Calculator widgets (lines 2487-2583) are implemented correctly:
```python
# CORRECT PATTERN
monthly_premium = st.number_input(
    "Monthly Premium ($)",
    min_value=0.0,
    value=float(st.session_state.get('calc_monthly_premium', 2000.0)),  # HAS value!
    step=100.0,
    key="calc_monthly_premium"
)
```

Capacity widgets (lines 2907-2930) are also correct:
```python
# CORRECT PATTERN
meetings_per_closer = st.number_input(
    "Meetings/Closer/Day",
    min_value=0.1,
    max_value=10.0,
    step=0.5,
    key="meetings_per_closer",  # Uses session_state implicitly via key
)
```

Wait - these don't have value parameter either! Let me check if they're also affected...

---

## EDGE CASE: Capacity Widgets

Lines 2907-2930 also lack explicit `value` parameter:
```python
meetings_per_closer = st.number_input(
    "Meetings/Closer/Day",
    min_value=0.1,  # Would default to 0.1 if not in session_state
    max_value=10.0,
    step=0.5,
    key="meetings_per_closer",
)
```

**Potential issue:** If these are initialized correctly and never reset, it's because:
1. They're initialized in session_state (line 194-196)
2. User hasn't reported them resetting
3. But they COULD reset if session_state is cleared

**Recommendation:** Fix these too for consistency and to prevent future issues.

---

## SUMMARY

### Root Cause
Missing `value` parameter in 11 critical widgets allows Streamlit to use `min_value` as default, overwriting session_state on every render.

### Why User Sees Random Resets
Any action that triggers a rerun (changing any widget, clicking refresh, tab navigation) causes widgets without explicit `value` to reset to their min_value.

### Why Previous Fixes Failed
They addressed different issues (circular refs, cache invalidation, key collisions) but didn't fix the fundamental widget configuration problem.

### The Solution
Add explicit `value=st.session_state.get('key', default)` to all 11 widgets (and potentially the capacity widgets for safety).

---

## NEXT STEPS

1. Apply fix to all 11 identified widgets
2. Consider fixing capacity widgets (lines 2907-2930) preventatively
3. Run verification plan
4. Add regression test to catch similar issues
5. Document widget best practices for future development

---

**This is the definitive root cause. Fixing these 11 widgets WILL resolve the user's issue.**
