# 🔍 QA Protocol & Architecture Recommendations
## Making Live Calculations Bulletproof & Developer-Friendly

---

## 🚨 Current Pain Points Identified

### 1. **Session State Chaos**
**Problem**: 176 direct `st.session_state` calls in dashboard_fast.py
```python
# Scattered everywhere:
st.session_state['avg_deal_value']
st.session_state.get('upfront_payment_pct', 70.0)
st.session_state.num_closers_main
```

**Impact**: 
- Hard to track what state exists
- Easy to misspell keys
- No validation of values
- Difficult to debug

---

### 2. **Calculation Duplication**
**Problem**: Same calculations repeated in multiple places
```python
# In GTM tab:
team_base = (closer_base * num_closers + setter_base * num_setters...)

# In Compensation tab:
team_base = (closer_base * num_closers + setter_base * num_setters...)

# In What-If tab:
team_base = (closer_base * num_closers + setter_base * num_setters...)
```

**Impact**:
- Bug in one place, not in others
- Hard to maintain consistency
- Performance waste (no caching)

---

### 3. **No Input Validation**
**Problem**: Can enter nonsensical values
```python
# Nothing stops this:
avg_deal_value = -50000  # Negative deal?
commission_pct = 500.0   # 500% commission?
num_closers = 0          # Divide by zero waiting to happen
```

**Impact**:
- Silent failures
- Incorrect calculations
- Hard to debug user errors

---

### 4. **No QA Framework**
**Problem**: Manual testing of every scenario
- No test data sets
- No automated checks
- No calculation verification
- No regression testing

**Impact**:
- Time-consuming QA
- Bugs slip through
- Can't verify fixes work

---

## ✅ Recommended Solutions

### **SOLUTION 1: State Manager Class**
**Create**: `dashboard_state_manager.py`

```python
class DashboardState:
    """Centralized state management with validation"""
    
    # Define schema with validation
    SCHEMA = {
        'avg_deal_value': {
            'type': float,
            'min': 0,
            'max': 10_000_000,
            'default': 50000,
            'description': 'Average deal value in dollars'
        },
        'num_closers_main': {
            'type': int,
            'min': 1,
            'max': 50,
            'default': 8,
            'description': 'Number of closers on the team'
        },
        'commission_pct': {
            'type': float,
            'min': 0.0,
            'max': 100.0,
            'default': 20.0,
            'description': 'Commission percentage'
        }
    }
    
    @classmethod
    def get(cls, key, default=None):
        """Get value with automatic validation"""
        if key not in cls.SCHEMA:
            raise KeyError(f"Unknown state key: {key}")
        
        schema = cls.SCHEMA[key]
        value = st.session_state.get(key, default or schema['default'])
        
        # Validate
        if not isinstance(value, schema['type']):
            value = schema['type'](value)
        
        if value < schema['min'] or value > schema['max']:
            st.warning(f"⚠️ {key} out of range. Using default.")
            value = schema['default']
        
        return value
    
    @classmethod
    def set(cls, key, value):
        """Set value with validation"""
        if key not in cls.SCHEMA:
            raise KeyError(f"Unknown state key: {key}")
        
        schema = cls.SCHEMA[key]
        
        # Validate before setting
        if value < schema['min']:
            raise ValueError(f"{key} cannot be less than {schema['min']}")
        if value > schema['max']:
            raise ValueError(f"{key} cannot be greater than {schema['max']}")
        
        st.session_state[key] = value
    
    @classmethod
    def get_all(cls):
        """Get complete state snapshot"""
        return {key: cls.get(key) for key in cls.SCHEMA}
    
    @classmethod
    def validate_all(cls):
        """Validate entire state and return errors"""
        errors = []
        for key, schema in cls.SCHEMA.items():
            try:
                value = cls.get(key)
            except Exception as e:
                errors.append(f"{key}: {str(e)}")
        return errors

# Usage:
# Instead of: st.session_state['avg_deal_value']
# Use: DashboardState.get('avg_deal_value')
```

**Benefits**:
- ✅ Type safety
- ✅ Range validation
- ✅ Documentation in code
- ✅ Easy to debug
- ✅ Autocomplete support

---

### **SOLUTION 2: Calculation Engine**
**Create**: `calculation_engine.py`

```python
class CalculationEngine:
    """Centralized calculation logic with caching and validation"""
    
    def __init__(self, state_manager):
        self.state = state_manager
        self._cache = {}
    
    @functools.lru_cache(maxsize=128)
    def calculate_team_costs(self, num_closers, num_setters, num_managers, num_bench,
                            closer_base, setter_base, manager_base, bench_base):
        """Calculate total team base salaries"""
        return (
            num_closers * closer_base +
            num_setters * setter_base +
            num_managers * manager_base +
            num_bench * bench_base
        )
    
    @functools.lru_cache(maxsize=128)
    def calculate_revenue_metrics(self, sales, deal_value, upfront_pct):
        """Calculate all revenue-related metrics"""
        upfront_cash = deal_value * (upfront_pct / 100)
        total_revenue = sales * upfront_cash
        
        return {
            'upfront_cash': upfront_cash,
            'total_revenue': total_revenue,
            'revenue_per_sale': upfront_cash,
            'annual_revenue': total_revenue * 12
        }
    
    def calculate_all_metrics(self):
        """Calculate complete dashboard metrics in correct order"""
        
        # Get base state
        state = self.state.get_all()
        
        # Calculate in dependency order
        results = {}
        
        # 1. Deal Economics
        results['deal_economics'] = self.calculate_deal_economics(state)
        
        # 2. GTM Metrics (depends on deal economics)
        results['gtm_metrics'] = self.calculate_gtm_metrics(
            state, results['deal_economics']
        )
        
        # 3. Team Costs
        results['team_costs'] = self.calculate_team_costs(
            state['num_closers_main'],
            state['num_setters_main'],
            state['num_managers_main'],
            state['num_benchs_main'],
            state['closer_base'],
            state['setter_base'],
            state['manager_base'],
            state['bench_base']
        )
        
        # 4. Commissions (depends on GTM + deal economics)
        results['commissions'] = self.calculate_commissions(
            results['gtm_metrics'], results['deal_economics'], state
        )
        
        # 5. P&L (depends on all above)
        results['pnl'] = self.calculate_pnl(
            results['gtm_metrics'],
            results['team_costs'],
            results['commissions'],
            state
        )
        
        # 6. Unit Economics (depends on GTM + P&L)
        results['unit_economics'] = self.calculate_unit_economics(
            results['gtm_metrics'], results['pnl'], results['deal_economics']
        )
        
        return results
    
    def verify_calculations(self, results):
        """Verify calculation consistency"""
        checks = []
        
        # Check 1: Revenue consistency
        if results['gtm_metrics']['monthly_revenue_immediate'] != \
           results['pnl']['gross_revenue']:
            checks.append({
                'status': 'FAIL',
                'check': 'Revenue Consistency',
                'message': 'GTM revenue != P&L revenue'
            })
        else:
            checks.append({
                'status': 'PASS',
                'check': 'Revenue Consistency'
            })
        
        # Check 2: Team costs = sum of individual costs
        expected_team_cost = results['team_costs']
        actual_team_cost = results['pnl']['team_base']
        if abs(expected_team_cost - actual_team_cost) > 0.01:
            checks.append({
                'status': 'FAIL',
                'check': 'Team Cost Consistency',
                'message': f'Expected {expected_team_cost}, got {actual_team_cost}'
            })
        else:
            checks.append({
                'status': 'PASS',
                'check': 'Team Cost Consistency'
            })
        
        # Check 3: EBITDA calculation
        expected_ebitda = (
            results['pnl']['gross_revenue'] -
            results['pnl']['cogs'] -
            results['pnl']['total_opex']
        )
        if abs(expected_ebitda - results['pnl']['ebitda']) > 0.01:
            checks.append({
                'status': 'FAIL',
                'check': 'EBITDA Calculation',
                'message': 'EBITDA formula incorrect'
            })
        else:
            checks.append({
                'status': 'PASS',
                'check': 'EBITDA Calculation'
            })
        
        return checks

# Usage:
engine = CalculationEngine(DashboardState)
results = engine.calculate_all_metrics()
verification = engine.verify_calculations(results)
```

**Benefits**:
- ✅ Single source of truth for calculations
- ✅ Automatic caching
- ✅ Dependency tracking
- ✅ Self-verification
- ✅ Easy to test

---

### **SOLUTION 3: Test Scenario Manager**
**Create**: `test_scenarios.py`

```python
class TestScenarios:
    """Pre-configured test scenarios for QA"""
    
    SCENARIOS = {
        'baseline': {
            'name': 'Baseline SaaS Company',
            'description': 'Healthy SaaS metrics for testing',
            'config': {
                'avg_deal_value': 50000,
                'upfront_payment_pct': 100.0,
                'num_closers_main': 8,
                'num_setters_main': 4,
                'closer_commission_pct': 20.0,
                'setter_commission_pct': 3.0,
            },
            'expected_results': {
                'monthly_sales': 70,
                'ltv_cac_min': 3.0,
                'ebitda_margin_min': 20.0
            }
        },
        
        'high_growth': {
            'name': 'High Growth Startup',
            'description': 'Aggressive growth, negative EBITDA',
            'config': {
                'avg_deal_value': 30000,
                'upfront_payment_pct': 100.0,
                'num_closers_main': 15,
                'num_setters_main': 10,
            },
            'expected_results': {
                'ebitda_margin_max': 0.0,  # Should be negative
                'ltv_cac_min': 2.0
            }
        },
        
        'profitable': {
            'name': 'Profitable Enterprise',
            'description': 'Established company with strong margins',
            'config': {
                'avg_deal_value': 100000,
                'upfront_payment_pct': 50.0,
                'num_closers_main': 5,
            },
            'expected_results': {
                'ebitda_margin_min': 30.0,
                'ltv_cac_min': 5.0
            }
        },
        
        'edge_case_low_volume': {
            'name': 'Edge: Low Volume',
            'description': 'Very few sales',
            'config': {
                'num_closers_main': 1,
                'monthly_leads': 50,
            },
            'expected_results': {
                'monthly_sales_max': 5
            }
        }
    }
    
    @classmethod
    def load_scenario(cls, scenario_name):
        """Load a test scenario into session state"""
        if scenario_name not in cls.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = cls.SCENARIOS[scenario_name]
        
        # Apply configuration
        for key, value in scenario['config'].items():
            DashboardState.set(key, value)
        
        return scenario
    
    @classmethod
    def verify_scenario(cls, scenario_name, actual_results):
        """Verify actual results match expected"""
        scenario = cls.SCENARIOS[scenario_name]
        expected = scenario['expected_results']
        
        checks = []
        for key, expected_value in expected.items():
            if key.endswith('_min'):
                actual_key = key.replace('_min', '')
                if actual_results[actual_key] >= expected_value:
                    checks.append({'status': 'PASS', 'check': key})
                else:
                    checks.append({
                        'status': 'FAIL',
                        'check': key,
                        'expected': f'>= {expected_value}',
                        'actual': actual_results[actual_key]
                    })
            elif key.endswith('_max'):
                actual_key = key.replace('_max', '')
                if actual_results[actual_key] <= expected_value:
                    checks.append({'status': 'PASS', 'check': key})
                else:
                    checks.append({
                        'status': 'FAIL',
                        'check': key,
                        'expected': f'<= {expected_value}',
                        'actual': actual_results[actual_key]
                    })
        
        return checks

# Usage in dashboard:
if st.sidebar.checkbox("🧪 Test Mode"):
    scenario = st.sidebar.selectbox("Load Scenario", list(TestScenarios.SCENARIOS.keys()))
    if st.sidebar.button("Load"):
        TestScenarios.load_scenario(scenario)
        st.success(f"Loaded: {TestScenarios.SCENARIOS[scenario]['name']}")
```

**Benefits**:
- ✅ One-click scenario loading
- ✅ Automated verification
- ✅ Regression testing
- ✅ Edge case coverage
- ✅ Reproducible bugs

---

### **SOLUTION 4: Health Check Dashboard**
**Add to Configuration Tab**:

```python
with st.expander("🏥 System Health Checks", expanded=False):
    st.markdown("### Automated Validation")
    
    if st.button("🔍 Run All Checks"):
        # 1. State validation
        st.markdown("**1. State Validation**")
        state_errors = DashboardState.validate_all()
        if state_errors:
            st.error(f"Found {len(state_errors)} state errors")
            for error in state_errors:
                st.write(f"❌ {error}")
        else:
            st.success("✅ All state values valid")
        
        # 2. Calculation verification
        st.markdown("**2. Calculation Verification**")
        engine = CalculationEngine(DashboardState)
        results = engine.calculate_all_metrics()
        checks = engine.verify_calculations(results)
        
        passed = sum(1 for c in checks if c['status'] == 'PASS')
        failed = sum(1 for c in checks if c['status'] == 'FAIL')
        
        if failed > 0:
            st.error(f"❌ {failed} checks failed, {passed} passed")
            for check in checks:
                if check['status'] == 'FAIL':
                    st.write(f"❌ {check['check']}: {check.get('message', '')}")
        else:
            st.success(f"✅ All {passed} calculation checks passed")
        
        # 3. Performance metrics
        st.markdown("**3. Performance Metrics**")
        perf_cols = st.columns(3)
        with perf_cols[0]:
            st.metric("LTV:CAC", f"{results['unit_economics']['ltv_cac']:.1f}:1")
            if results['unit_economics']['ltv_cac'] < 3:
                st.warning("⚠️ Below 3:1 threshold")
        
        with perf_cols[1]:
            st.metric("EBITDA Margin", f"{results['pnl']['ebitda_margin']:.1f}%")
            if results['pnl']['ebitda_margin'] < 20:
                st.warning("⚠️ Below 20% threshold")
        
        with perf_cols[2]:
            st.metric("Payback", f"{results['unit_economics']['payback_months']:.0f}mo")
            if results['unit_economics']['payback_months'] > 12:
                st.warning("⚠️ Over 12 months")
```

---

### **SOLUTION 5: Debug Mode**
**Add debugging panel**:

```python
if st.sidebar.checkbox("🐛 Debug Mode"):
    with st.sidebar.expander("Debug Info", expanded=True):
        st.markdown("### Calculation Flow")
        
        # Show what's being calculated
        st.code("""
        1. Deal Economics
        2. GTM Metrics (uses #1)
        3. Team Costs
        4. Commissions (uses #1, #2)
        5. P&L (uses #2, #3, #4)
        6. Unit Economics (uses #2, #5)
        """)
        
        # Show current values
        st.markdown("### Current State")
        state_df = pd.DataFrame([
            {'Key': k, 'Value': DashboardState.get(k)} 
            for k in DashboardState.SCHEMA.keys()
        ])
        st.dataframe(state_df, use_container_width=True)
        
        # Show cache status
        st.markdown("### Cache Status")
        st.write(f"Cached calculations: {len(engine._cache)}")
```

---

## 📋 Implementation Plan

### **Phase 1: Foundation** (2-3 hours)
1. Create `dashboard_state_manager.py`
2. Create `calculation_engine.py`
3. Update `dashboard_fast.py` to use new managers
4. Test basic functionality

### **Phase 2: QA Tools** (1-2 hours)
1. Create `test_scenarios.py`
2. Add health check dashboard
3. Add debug mode
4. Test all scenarios

### **Phase 3: Migration** (2-3 hours)
1. Replace all `st.session_state` calls with `DashboardState`
2. Move calculations to `CalculationEngine`
3. Add verification checks
4. Full regression test

### **Total Time**: ~8 hours
### **Payoff**: Save 50+ hours in future development/debugging

---

## 🎯 Immediate Quick Wins (Can do today)

### **1. Add Input Validation** (15 min)
```python
# In number_input calls, add min/max:
st.number_input("Deal Value", min_value=0, max_value=10_000_000)
st.number_input("Commission %", min_value=0.0, max_value=100.0)
```

### **2. Add Calculation Assertions** (30 min)
```python
# After calculations:
assert pnl_data['gross_revenue'] == gtm_metrics['monthly_revenue_immediate'], \
    "Revenue mismatch between GTM and P&L"

assert pnl_data['ebitda'] == pnl_data['gross_profit'] - pnl_data['total_opex'], \
    "EBITDA calculation incorrect"
```

### **3. Add Quick Test Scenarios** (30 min)
```python
# In sidebar:
if st.sidebar.button("Load Baseline Scenario"):
    st.session_state['avg_deal_value'] = 50000
    st.session_state['num_closers_main'] = 8
    st.session_state['commission_pct'] = 20.0
    st.rerun()
```

---

## 📊 Impact Summary

| Improvement | Time to Implement | Time Saved per Session | ROI |
|-------------|------------------|------------------------|-----|
| State Manager | 1 hour | 15 min debugging | 4x |
| Calculation Engine | 2 hours | 30 min | 15x |
| Test Scenarios | 1 hour | 20 min QA | 12x |
| Health Checks | 1 hour | 10 min verification | 6x |
| Debug Mode | 30 min | 5 min troubleshooting | 6x |

**Total Investment**: 5.5 hours  
**Total Time Saved**: ~80 min per development session  
**Break-even**: After 4 development sessions  

---

## 🚀 Recommendation

**Start with**: Quick Wins (1 hour) → State Manager (1 hour) → Test Scenarios (1 hour)

This gives you:
- Immediate validation
- Clean state management
- Easy QA testing

In **3 hours of work**, you'll save **20+ hours** over the next month.

**Want me to implement any of these solutions right now?**
