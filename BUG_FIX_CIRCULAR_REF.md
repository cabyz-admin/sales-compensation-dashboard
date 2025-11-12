# Bug Fix: Calculator Circular Reference Issue

**Date:** 2025-11-12
**Issue:** Values resetting, Apply button not working, insurance premium changing randomly
**Root Cause:** Circular reference in calculator method dropdown

---

## Problem Description

User reported three symptoms:
1. **"comp is resetting"** - Compensation values resetting unexpectedly
2. **"apply button concept not working"** - Apply button not properly committing values
3. **"insurance monthly premium changes randomly"** - Premium field value changing without user input

## Root Cause Analysis

### The Circular Reference

**Location:** [dashboard_fast.py:2445](dashboards/production/dashboard_fast.py#L2445)

```python
# BEFORE (BROKEN)
calc_method = st.selectbox(
    "Calculation Method",
    calc_methods,
    index=default_index,
    key="calc_deal_calc_method",  # Widget uses calc_ prefix
    help="..."
)

# ❌ PROBLEM: Syncs on EVERY render, not just on Apply
st.session_state['deal_calc_method'] = calc_method
```

### Why This Broke Everything

The Apply Button pattern requires:
1. Widget keys use `calc_` prefix (temporary state)
2. Widgets show preview values
3. **Only Apply button** commits to actual session state keys
4. Actual keys (`avg_deal_value`, `deal_calc_method`, etc.) drive the calculation engine

But line 2445 violated rule #3 by syncing `deal_calc_method` on **every render** instead of only when Apply is clicked.

### The Circular Reference Chain

```
User Action: Load Insurance Template
    ↓
Template sets: calc_deal_calc_method = "🏥 Insurance (Premium-Based)"
                calc_monthly_premium = 2000
                calc_insurance_commission_rate = 2.7
    ↓
Page Reruns → Widgets Render
    ↓
Dropdown renders with key="calc_deal_calc_method"
    ↓
❌ Line 2445 IMMEDIATELY syncs: st.session_state['deal_calc_method'] = calc_method
    ↓
This triggers cache invalidation (deal_calc_method is NOT in cache key, but mutation triggers rerun)
    ↓
Rerun occurs BEFORE user clicks Apply
    ↓
Calculator inputs reset to defaults
    ↓
User sees: "insurance monthly premium changes randomly"
```

### Why Compensation Reset

The same circular reference affected the entire session state:
1. Dropdown syncs → triggers rerun
2. Rerun before Apply → calculator preview values lost
3. User thinks they clicked Apply but values reverted
4. Team compensation calculations used stale/wrong deal values

## The Fix

### Change 1: Remove Auto-Sync from Dropdown

**File:** [dashboard_fast.py:2444-2445](dashboards/production/dashboard_fast.py#L2444-L2445)

```python
# AFTER (FIXED)
calc_method = st.selectbox(
    "Calculation Method",
    calc_methods,
    index=default_index,
    key="calc_deal_calc_method",  # Widget uses calc_ prefix
    help="..."
)

# ✅ DON'T sync on every render - only sync when Apply button is clicked
# This prevents circular reference issues where changing method resets other values
```

### Change 2: Sync Method on Apply Button Click

**File:** [dashboard_fast.py:2625-2632](dashboards/production/dashboard_fast.py#L2625-L2632)

```python
if st.button("✅ Apply Calculator Values", ...):
    # NOW we commit to the actual session state keys
    st.session_state['avg_deal_value'] = calculated_deal_value
    st.session_state['contract_length_months'] = calculated_contract_length
    st.session_state['deal_calc_method'] = calc_method  # ✅ Sync method on Apply
    st.cache_data.clear()
    st.success(f"✅ Deal value set to ${calculated_deal_value:,.0f}!")
    st.rerun()
```

## Why This Works

### Proper Apply Button Flow (Fixed)

```
User Action: Load Insurance Template
    ↓
Template sets: calc_deal_calc_method = "🏥 Insurance (Premium-Based)"
                calc_monthly_premium = 2000
                calc_insurance_commission_rate = 2.7
    ↓
Page Reruns → Widgets Render
    ↓
Dropdown shows "🏥 Insurance (Premium-Based)" (from calc_ key)
Calculator inputs show 2000, 2.7, 25 years (from calc_ keys)
Preview shows: $16,200 commission (calculated, not committed)
    ↓
✅ NO AUTO-SYNC - session_state['deal_calc_method'] unchanged
✅ NO RERUN - page stays stable
    ↓
User reviews preview values
    ↓
User clicks "✅ Apply Calculator Values"
    ↓
Apply button commits ALL values at once:
    - avg_deal_value = 16200
    - contract_length_months = 300
    - deal_calc_method = "🏥 Insurance (Premium-Based)"
    ↓
Cache cleared, rerun triggered
    ↓
All tabs now use new committed values
    ↓
✅ Values persist across reruns
✅ Compensation calculations correct
✅ No random changes
```

## Other Auto-Sync Values (Not Bugs)

These values sync on every render by design because they're **not part of the calculator preview**:

1. **Payment Terms** (line 2664):
   ```python
   st.session_state['upfront_payment_pct'] = upfront_pct
   ```
   ✅ Correct - payment splits should update immediately

2. **Deferred Timing** (line 2685):
   ```python
   st.session_state['deferred_timing_months'] = deferred_timing
   ```
   ✅ Correct - timing should update immediately

3. **Commission Policy** (lines 2702, 2706):
   ```python
   st.session_state['commission_policy'] = 'upfront' or 'full'
   ```
   ✅ Correct - policy should update immediately

4. **Government Costs** (line 2724):
   ```python
   st.session_state['government_cost_pct'] = gov_cost
   ```
   ✅ Correct - gov costs should update immediately

5. **GRR** (line 2738):
   ```python
   st.session_state['grr_rate'] = grr
   ```
   ✅ Correct - retention rate should update immediately

### Why These Are Different

The **Calculator** section (deal value calculation) needs preview-then-commit because:
- Complex multi-step calculations
- Users want to see results before committing
- Changes affect fundamental business model

The **Payment Terms** section syncs immediately because:
- Simple percentage splits
- Users expect real-time updates
- Changes are incremental, not fundamental

## Testing

### Test Case 1: Template Load → Apply
1. Open dashboard
2. Go to Tab 5: Configuration
3. Select "Insurance (Long-term)" template
4. Click "📋 Load Template"
5. Verify: Calculator inputs populated (2000, 2.7%, 25 years)
6. Verify: Preview shows $16,200 commission
7. Click "✅ Apply Calculator Values"
8. Verify: Success message appears
9. Go to Tab 1: GTM
10. Verify: Deal value is $16,200 (not reset)
11. **Expected:** ✅ Values persist

### Test Case 2: Manual Calculator Changes
1. With template loaded
2. Change monthly premium to 3000
3. Verify: Preview updates to $24,300
4. DO NOT click Apply yet
5. Switch to Tab 1
6. Switch back to Tab 5
7. Verify: Preview still shows $24,300 (not reset)
8. Click Apply
9. Verify: Committed value is $24,300
10. **Expected:** ✅ Preview persists until Apply

### Test Case 3: Change Calculator Method
1. With Insurance calculator loaded
2. Change dropdown to "💰 Direct Value"
3. Verify: Calculator inputs change to Direct Value fields
4. DO NOT click Apply
5. Verify: Committed values in other tabs unchanged
6. Change back to "🏥 Insurance (Premium-Based)"
7. Verify: Insurance inputs reappear with previous values
8. **Expected:** ✅ Method change doesn't trigger auto-commit

### Test Case 4: JSON Import
1. Export current config
2. Modify JSON: Change `calc_monthly_premium` to 5000
3. Import JSON
4. Verify: Calculator input shows 5000
5. Verify: Preview updates
6. Click Apply
7. Verify: New values committed
8. **Expected:** ✅ Import works without widget collision

## Files Modified

- **[dashboard_fast.py](dashboards/production/dashboard_fast.py)** - 2 locations
  - Line 2444-2445: Removed auto-sync from calculator method dropdown
  - Line 2629: Added method sync to Apply button

## Impact

**Before Fix:**
- ❌ Values reset randomly
- ❌ Apply button appeared broken
- ❌ User confusion about what was committed
- ❌ Compensation calculations used wrong values

**After Fix:**
- ✅ Values persist until Apply clicked
- ✅ Apply button commits all values atomically
- ✅ Clear separation: preview vs committed
- ✅ No circular references
- ✅ No random resets

## Related Issues

This fix completes the calculator refactor started in [BUG_FIXES_2025-11-11.md](BUG_FIXES_2025-11-11.md):

- **Bug #5:** Template widget collision → Fixed with `calc_` prefix
- **Bug #6:** Calculator state mutations → Fixed with Apply button pattern
- **Bug #8:** Multiple sources of truth → Fixed with single source architecture
- **THIS BUG:** Circular reference from dropdown auto-sync → Fixed by removing auto-sync

All four bugs were related to the same root issue: **improper separation between widget state and committed state**.

## Prevention

To prevent similar issues in the future:

### Rule 1: Calculator Preview Values
Any widget in the "Calculator Inputs" section must:
- Use `calc_` prefixed key
- Show preview only (metrics, captions)
- NOT auto-sync to actual session state
- Only commit on Apply button click

### Rule 2: Immediate Update Values
Any widget that should update immediately must:
- Still use `calc_` prefixed key (to allow JSON import)
- Auto-sync to actual session state after widget creation
- Be in "Payment Terms" or "Team Structure" sections (not Calculator)

### Rule 3: The Litmus Test
Ask: "If the user changes this widget, should it immediately affect calculations in other tabs?"
- **YES** → Auto-sync after widget creation
- **NO** → Preview only, sync on Apply

---

**Fixed by:** Claude (Durov mode)
**Total time:** 15 minutes
**Risk level:** Low (2-line change, preserves all existing functionality)
**Status:** ✅ Ready for testing
