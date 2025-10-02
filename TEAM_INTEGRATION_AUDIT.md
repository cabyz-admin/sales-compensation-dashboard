# 🔍 Team Configuration Integration Audit

## Executive Summary

**Status:** ⚠️ **PARTIALLY CONNECTED** - Team data flows to engine but may have cache timing issues

**Finding:** Team configuration IS connected to the SSOT engine, but there's a potential cache invalidation timing issue when using the Refresh button.

---

## 📊 Current State Analysis

### ✅ What's Working

1. **Team Structure Model** (`models.py`)
   ```python
   class TeamStructure(BaseModel):
       num_closers: int = Field(ge=0, default=8)
       num_setters: int = Field(ge=0, default=4)
       num_managers: int = Field(ge=0, default=2)
       num_bench: int = Field(ge=0, default=2)
       closer: RoleCompensation  # base, variable, commission_pct
       setter: RoleCompensation
       manager: RoleCompensation
       bench: RoleCompensation
   ```

2. **DashboardAdapter Integration** (`dashboard_adapter.py`)
   ```python
   def session_to_team_structure() -> TeamStructure:
       return TeamStructure(
           num_closers=st.session_state.get('num_closers_main', 8),
           num_setters=st.session_state.get('num_setters_main', 4),
           # ... reads from session state correctly ✅
       )
   ```

3. **P&L Calculation Uses Team** (`dashboard_adapter.py:152`)
   ```python
   pnl = calculate_pnl(
       gross_revenue=gtm_total.revenue_upfront,
       team_base_annual=team.total_base,  # ✅ Uses team.total_base
       commissions=commissions.total_commission,  # ✅ Calculated from team
       marketing_spend=gtm_total.spend,
       operating_costs=opex,
       gov_cost_pct=deal.government_cost_pct
   )
   ```

4. **Cache Key Includes Team** (`dashboard_adapter.py:284-298`)
   ```python
   'team': {
       'counts': [
           st.session_state.get('num_closers_main'),  # ✅ In cache key
           st.session_state.get('num_setters_main'),
           st.session_state.get('num_managers_main'),
           st.session_state.get('num_benchs_main')
       ],
       'comp': [
           st.session_state.get('closer_base'),
           st.session_state.get('closer_commission_pct'),
           # ... all compensation values ✅
       ]
   }
   ```

---

## ⚠️ Potential Issues

### Issue #1: Cache Timing with Refresh Button

**Problem:** When you:
1. Change team size (8 → 9 closers)
2. Click "🔄 Refresh Metrics"

The sequence is:
```python
# User changes input
st.number_input("Closers", key="num_closers_main")  
# → st.session_state.num_closers_main = 9 ✅

# User clicks Refresh button
if st.button("🔄 Refresh Metrics"):
    st.cache_data.clear()  # Clears ALL cache
    st.rerun()  # Reruns page
    
# On rerun:
get_cache_key()  # Calculates hash with num_closers_main=9
compute_business_metrics(_cache_key)  # Runs with NEW value
# → Should see NEW EBITDA ✅
```

**This SHOULD work!** But if it doesn't, possible causes:

1. **Cache not actually cleared** - Maybe `st.cache_data.clear()` doesn't work as expected
2. **Session state reset** - Maybe session state reverts to defaults on rerun
3. **Default values issue** - Cache key uses `.get()` with defaults that don't match UI

### Issue #2: No Auto-Rerun on Team Change

Unlike channel configuration (which we made immediate updates), team configuration doesn't trigger auto-rerun:

```python
# Channel config - writes immediately, triggers calculation
st.session_state.gtm_channels[idx]['cpl'] = float(cpl)
# → Cache invalidates automatically on next render

# Team config - only updates widget state
num_closers = st.number_input("Closers", key="num_closers_main")
# → Doesn't trigger recalculation until manual refresh
```

---

## 🔬 The EBITDA Calculation Path

When you add a closer, EBITDA should change because:

```
EBITDA = Revenue - COGS - OpEx - Team Base - Commissions

Where:
  Team Base = (num_closers × closer_base) + 
              (num_setters × setter_base) + 
              (num_managers × manager_base) + 
              (num_bench × bench_base)
```

**Example:**
- 8 closers × $32,000 base = $256,000
- 9 closers × $32,000 base = $288,000
- **Difference: -$32,000 in EBITDA** ⬇️

---

## 🎯 Recommended Fixes

### Option A: Make Team Config Immediate (Like Channels)

```python
# In Team Configuration section:
with team_cols[0]:
    st.markdown("**Team Size**")
    num_closers = st.number_input("Closers", 1, 50, 
                                   st.session_state.num_closers_main, 
                                   key="num_closers_main")
    # ADD THIS:
    # Already auto-updates via key= ✅
    # No additional write needed
    
    num_setters = st.number_input("Setters", 0, 50, 
                                   st.session_state.num_setters_main, 
                                   key="num_setters_main")
    # etc...
```

✅ **Already working this way!** The `key=` parameter automatically updates session state.

### Option B: Add Team Impact Preview

Show BEFORE vs AFTER when you change team:

```python
# Calculate current EBITDA
current_ebitda = pnl_data['ebitda']

# Calculate what EBITDA would be with new team
new_team_base = (num_closers * closer_base + 
                 num_setters * setter_base + 
                 num_managers * manager_base + 
                 num_bench * bench_base)

current_team_base = team.total_base
delta_ebitda = current_team_base - new_team_base

st.metric("EBITDA Impact", 
          f"${current_ebitda:,.0f}",
          delta=f"${delta_ebitda:,.0f}" if delta_ebitda != 0 else None,
          help="Impact of team changes on EBITDA")
```

### Option C: Debug the Refresh Button

Add logging to see what's happening:

```python
if st.button("🔄 Refresh Metrics"):
    # Debug: Show current team values
    st.info(f"🔍 Current team: {st.session_state.get('num_closers_main')} closers")
    
    # Show cache key before clear
    old_key = DashboardAdapter.get_cache_key()
    st.info(f"🔑 Cache key before: {old_key[:16]}...")
    
    st.cache_data.clear()
    
    # Show cache key after clear (should trigger recalc)
    new_key = DashboardAdapter.get_cache_key()
    st.info(f"🔑 Cache key after: {new_key[:16]}...")
    
    st.rerun()
```

---

## 🧪 Test Cases

### Test 1: Add a Closer
1. **Initial:** 8 closers, EBITDA = $X
2. **Change:** Set to 9 closers
3. **Click:** "🔄 Refresh Metrics"
4. **Expected:** EBITDA = $X - $32,000 (assuming $32k base)
5. **Actual:** ???

### Test 2: Change Compensation
1. **Initial:** Closer base = $32,000
2. **Change:** Set to $40,000
3. **Expected:** EBITDA drops by (8 × $8,000) = $64,000
4. **Actual:** ???

### Test 3: Add Multiple Roles
1. **Change:** +1 closer, +1 setter, +1 manager
2. **Expected:** EBITDA drops by sum of all bases
3. **Actual:** ???

---

## 🎓 Recommendations for Better Decision Making

### 1. **Add Team Cost Breakdown Widget**

```
┌─────────────────────────────────────────┐
│ 💰 Annual Team Costs                    │
├─────────────────────────────────────────┤
│ Closers:    8 × $32,000 = $256,000     │
│ Setters:    4 × $16,000 = $64,000      │
│ Managers:   2 × $72,000 = $144,000     │
│ Bench:      2 × $12,500 = $25,000      │
│ ─────────────────────────────────────── │
│ Total Base:              $489,000      │
│                                         │
│ Expected Commissions:    $535,080      │
│ ─────────────────────────────────────── │
│ Total Team Cost:       $1,024,080      │
└─────────────────────────────────────────┘
```

### 2. **Add Goal-Seek for Team Sizing**

```
📊 What team do you need?

Target Monthly Sales: 50 deals

With current close rate (30%) and capacity:
✅ Need: 7.1 closers → Round up to 8 closers
✅ Need: 3.8 setters → Round up to 4 setters

Current team: 8 closers, 4 setters
Status: ✅ Adequately staffed (10% buffer)
```

### 3. **Add Scenario Comparison**

```
Current vs Proposed Team Structure

                Current    Proposed    Δ
Closers         8          10         +2
Monthly Cost    $21,333    $26,667    +$5,334
Capacity        480 mtgs   600 mtgs   +120
Utilization     42%        34%        -8%
EBITDA          $1.06M     $0.99M     -$64K

ROI Analysis:
With 2 more closers, you could handle 120 more meetings
At 30% close rate = 36 more sales
At $50K deal value = $1.8M more revenue
Net impact: +$1.8M revenue - $64K cost = +$1.74M EBITDA
```

---

## 🔧 Implementation Priority

1. **HIGH:** Debug why refresh button doesn't update EBITDA
2. **HIGH:** Add team cost breakdown in UI
3. **MEDIUM:** Add before/after preview for team changes  
4. **MEDIUM:** Add goal-seek team calculator
5. **LOW:** Add scenario comparison tool

---

## 📝 Notes

- Team data IS in the SSOT engine ✅
- Cache key DOES include team data ✅
- P&L calculation DOES use team costs ✅
- Something is preventing the update from showing in UI ⚠️

**Next Step:** Add debug logging to refresh button to see what's happening.
