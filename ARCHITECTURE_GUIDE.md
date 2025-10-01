# 🏗️ New Architecture Guide

## Overview

The dashboard has been refactored into a **clean architecture** with:
- **Single source of truth**: All math in pure Python modules
- **Type safety**: Pydantic models for all business entities
- **Testability**: 20+ pytest tests locking down the math
- **Traceability**: See exactly how inputs flow to outputs
- **Performance**: Smart caching with proper invalidation

---

## 📁 File Structure

```
modules/
├── models.py              # Pydantic models (Channel, DealEconomics, etc.)
├── engine.py              # GTM funnel calculations (SINGLE SOURCE OF TRUTH)
├── engine_pnl.py          # Unit economics, commissions, P&L
├── scenario.py            # Sensitivity analysis, what-if modeling
├── state.py               # Cache key generation
├── ui_components.py       # Reusable UI widgets
├── dashboard_adapter.py   # Bridge to existing dashboard
└── tests/
    └── test_engine.py     # 20+ tests locking math

dashboards/production/
└── dashboard_fast.py      # Main UI (now thin layer over engine)
```

---

## 🎯 How to Use the New Architecture

### Option 1: Drop-in Replacement (Easiest)

Replace your existing calculations with the adapter:

```python
# OLD WAY (ad-hoc calculations scattered everywhere)
marketing_spend = sum(ch.get('monthly_leads', 0) * ch.get('cpl', 50) 
                     for ch in st.session_state.gtm_channels)
sales = leads * contact_rate * meeting_rate * show_up_rate * close_rate
# ... scattered math everywhere

# NEW WAY (single source of truth)
from modules.dashboard_adapter import DashboardAdapter

metrics = DashboardAdapter.get_metrics()

# All metrics available:
revenue = metrics['monthly_revenue_immediate']
spend = metrics['total_marketing_spend']  # ✅ Respects cost method!
ltv_cac = metrics['unit_economics']['ltv_cac']
ebitda = metrics['pnl']['ebitda']
```

**Benefits**:
- ✅ All tabs use the SAME calculations
- ✅ No more duplicate/inconsistent math
- ✅ Smart caching (only recalculates when inputs change)
- ✅ Traceability built-in

### Option 2: Use Engine Directly (More Control)

```python
from modules.models import Channel, DealEconomics
from modules.engine import compute_gtm_aggregate
from modules.engine_pnl import calculate_unit_economics

# Convert session state to typed models
deal = DealEconomics(
    avg_deal_value=st.session_state.avg_deal_value,
    upfront_pct=st.session_state.upfront_payment_pct,
    grr=st.session_state.grr_rate,
    commission_policy='upfront'
)

channels = [
    Channel(
        id=ch['id'],
        name=ch['name'],
        monthly_leads=ch['monthly_leads'],
        contact_rate=ch['contact_rate'],
        # ... all fields
        cost_method=ch['cost_method'],
        cpl=ch.get('cpl')
    )
    for ch in st.session_state.gtm_channels
]

# Compute metrics (pure functions, no side effects)
per_channel, gtm_total = compute_gtm_aggregate(channels, deal)
unit_econ = calculate_unit_economics(deal, gtm_total.cost_per_sale)

# Use results
st.metric("Revenue", f"${gtm_total.revenue_upfront:,.0f}")
st.metric("ROAS", f"{gtm_total.roas:.1f}x")
```

---

## 🔍 Dependency Inspector (Traceability)

Show users exactly how numbers flow:

```python
from modules.ui_components import render_dependency_inspector

render_dependency_inspector(
    inputs={
        'monthly_leads': 1000,
        'contact_rate': 0.65,
        'meeting_rate': 0.30,
        'close_rate': 0.30,
        'cost_per_meeting': 200
    },
    intermediates={
        'contacts': 650,
        'meetings_held': 136.5,
        'sales': 40.95,
        'spend': 27300
    },
    outputs={
        'revenue': 1433250,
        'roas': 52.5,
        'ebitda': 650000
    }
)
```

This creates an expandable panel showing:
```
INPUTS → CALCULATIONS → OUTPUTS
Leads     Contacts       Revenue
CPM       Meetings       ROAS
Rates     Sales          EBITDA
```

---

## 📊 Sensitivity Analysis

See which inputs drive which outputs:

```python
from modules.scenario import calculate_sensitivity

def calculate_ebitda(inputs):
    # Your EBITDA formula using inputs
    return ebitda_value

sensitivities = calculate_sensitivity(
    baseline_fn=calculate_ebitda,
    inputs={
        'close_rate': 0.30,
        'cost_per_meeting': 200,
        'upfront_pct': 70.0,
        'avg_deal_value': 50000
    },
    bump_pct=0.01  # 1% bump
)

# Results show: "1% increase in close_rate increases EBITDA by 2.3%"
# Render chart
from modules.ui_components import render_sensitivity_chart
render_sensitivity_chart(sensitivities, "EBITDA")
```

---

## 🧪 Tests (Regression Prevention)

Run tests before deploying:

```bash
cd /Users/castillo/CascadeProjects/comp-structure
pytest modules/tests/test_engine.py -v
```

**Test Coverage**:
- ✅ CPL/CPM/CPA/Budget spend calculations
- ✅ Pipeline monotonicity (leads ≥ contacts ≥ meetings ≥ sales)
- ✅ GTM aggregation matches sum of channels
- ✅ Commission policy (upfront vs full)
- ✅ Unit economics formulas (LTV, CAC, payback)
- ✅ P&L calculations (margins, EBITDA)
- ✅ Reverse engineering (leads needed for target)

---

## 🎨 UI Components

Reusable components for consistency:

### KPI Row
```python
from modules.ui_components import render_kpi_row

render_kpi_row({
    'Revenue': {'value': 200000, 'format': '$,.0f', 'help': 'Monthly revenue'},
    'ROAS': {'value': 15.2, 'format': '.1f', 'delta': '+2.3x'},
    'EBITDA': {'value': 65000, 'format': '$,.0f', 'delta_color': 'normal'}
}, columns=3)
```

### Funnel Chart
```python
from modules.ui_components import render_funnel_chart

render_funnel_chart(
    leads=1000,
    contacts=650,
    meetings_sched=195,
    meetings_held=136,
    sales=41,
    title="Channel 1 Funnel"
)
```

### Health Score
```python
from modules.ui_components import render_health_score

render_health_score(
    ltv_cac=4.2,
    payback_months=8.5,
    ebitda_margin=22.3,
    gross_margin=68.5
)
```

---

## 🔄 Migration Path

### Phase 1: Add Adapter (Current State)
- ✅ Install new modules alongside existing code
- ✅ Use `DashboardAdapter.get_metrics()` for new calculations
- ✅ Keep old code as fallback
- ✅ Test side-by-side

### Phase 2: Replace Top KPIs
```python
# In dashboard_fast.py, replace lines 477-520 with:
metrics = DashboardAdapter.get_metrics()

st.metric("Revenue", f"${metrics['monthly_revenue_immediate']:,.0f}")
st.metric("Sales", f"{metrics['monthly_sales']:.1f}")
st.metric("Marketing", f"${metrics['total_marketing_spend']:,.0f}")
st.metric("EBITDA", f"${metrics['pnl']['ebitda']:,.0f}")
st.metric("LTV:CAC", f"{metrics['unit_economics']['ltv_cac']:.1f}:1")
```

### Phase 3: Update Each Tab
- Tab 1 (GTM): Use `metrics['channels_breakdown']`
- Tab 2 (Compensation): Use `metrics['commissions']`
- Tab 3 (Performance): Use `metrics['pnl']`
- Tab 4 (What-If): Use `scenario.py` functions

### Phase 4: Remove Old Code
- Delete duplicate calculation functions
- Remove `calculate_gtm_metrics_cached` (replaced by engine)
- Remove `calculate_pnl_cached` (replaced by engine_pnl)

---

## 🚀 Advanced Features

### Scenario Comparison
```python
from modules.scenario import ScenarioManager

manager = ScenarioManager()

# Save baseline
manager.add_scenario('baseline', current_inputs, "Current state")

# Save optimistic scenario
optimistic = current_inputs.copy()
optimistic['close_rate'] += 0.05
optimistic['cost_per_meeting'] -= 50
manager.add_scenario('optimistic', optimistic, "Better close rate, lower CAC")

# Compare
comparison = manager.compare('baseline', 'optimistic', calculate_metrics)
# Shows: Revenue +15%, EBITDA +32%, etc.
```

### Multi-Metric Sensitivity
```python
from modules.scenario import multi_metric_sensitivity

def calculate_all_metrics(inputs):
    return {
        'revenue': ...,
        'ebitda': ...,
        'ltv_cac': ...
    }

sensitivities = multi_metric_sensitivity(calculate_all_metrics, inputs)

# See which inputs affect which outputs most
top_revenue_drivers = get_top_drivers(sensitivities, 'revenue', top_n=5)
top_ebitda_drivers = get_top_drivers(sensitivities, 'ebitda', top_n=5)
```

---

## 📝 Key Principles

1. **Engine = Truth**: All math lives in `engine.py` and `engine_pnl.py`
2. **UI = Thin Layer**: Streamlit code only renders, never calculates
3. **Models = Contracts**: Pydantic validates all inputs
4. **Tests = Safety Net**: Can't break math without tests failing
5. **Cache = Speed**: Smart invalidation means fast updates

---

## 🐛 Debugging

### See What Changed
```python
from modules.state import create_business_snapshot, has_state_changed

# Take snapshot
snapshot = create_business_snapshot(st.session_state)

# Later, check what changed
if has_state_changed(st.session_state, snapshot, scope='gtm'):
    st.info("GTM inputs changed - recalculating")
```

### Validate Inputs
```python
from modules.engine import validate_channel

for ch in channels:
    issues = validate_channel(ch)
    if issues:
        st.error(f"Channel {ch.name} has issues: {', '.join(issues)}")
```

### Cache Diagnostics
```python
cache_key = DashboardAdapter.get_cache_key()
st.caption(f"Cache key: {cache_key[:12]}...")
```

---

## 🎯 Next Steps

1. **Run Tests**: `pytest modules/tests/test_engine.py -v`
2. **Try Adapter**: Replace one metric with `DashboardAdapter.get_metrics()`
3. **Add Dependency Inspector**: Show users how numbers flow
4. **Add Sensitivity Analysis**: Let users see top drivers
5. **Migrate Tab-by-Tab**: Replace calculations incrementally

---

## 💡 Examples

### Example 1: Replace Marketing Spend
```python
# ❌ OLD (scattered, inconsistent)
marketing_spend = sum(ch['monthly_leads'] * ch['cpl'] for ch in channels)

# ✅ NEW (single source of truth)
metrics = DashboardAdapter.get_metrics()
marketing_spend = metrics['total_marketing_spend']  # Respects cost method!
```

### Example 2: Add Traceability
```python
# Show users exactly how their slider affects EBITDA
with st.expander("🔍 See Impact"):
    render_dependency_inspector(
        inputs={'close_rate': 0.30, 'cpl': 50},
        intermediates={'sales': 41, 'spend': 50000},
        outputs={'revenue': 1435000, 'ebitda': 620000}
    )
```

### Example 3: Compare Scenarios
```python
# User changes close_rate slider
baseline_ebitda = current_metrics['pnl']['ebitda']

# Recalculate with new value
new_metrics = DashboardAdapter.get_metrics()
new_ebitda = new_metrics['pnl']['ebitda']

delta = new_ebitda - baseline_ebitda
st.metric("EBITDA Impact", f"${delta:+,.0f}", f"{delta/baseline_ebitda:+.1%}")
```

---

## 📚 Reference

- **Models**: `modules/models.py` - All data structures
- **GTM Engine**: `modules/engine.py` - Funnel calculations
- **P&L Engine**: `modules/engine_pnl.py` - Financial calculations
- **Scenarios**: `modules/scenario.py` - What-if analysis
- **Tests**: `modules/tests/test_engine.py` - Math validation
- **Adapter**: `modules/dashboard_adapter.py` - Integration bridge

---

**Questions?** All calculations are now in pure Python modules with full type hints and docstrings. Read the code!
