# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

Sales Compensation Dashboard - A dual-stack repository containing:
1. **Streamlit Dashboard** (Production) - Python-based interactive sales compensation and GTM modeling tool
2. **Next.js UI** (Unused) - TypeScript/React components (currently not integrated with Streamlit)

The active codebase is **Python/Streamlit**. The Next.js assets exist but are not currently used by the production application.

## Commands

### Running the Dashboard

**Production Dashboard (Full Features)**
```bash
streamlit run dashboards/production/dashboard_improved_final.py
```

**Fast Dashboard (Performance Optimized)**
```bash
streamlit run dashboards/production/dashboard_fast.py --server.port 8501
# OR use the convenience script:
./run_fast_dashboard.sh
```

**Cloud-Optimized Dashboard**
```bash
streamlit run dashboards/cloud/dashboard_cloud.py
```

### Testing

**Run All Tests**
```bash
./run_tests.sh
# OR directly:
pytest modules/tests/test_engine.py -v
```

**Run Specific Test**
```bash
pytest modules/tests/test_engine.py::test_name -v
```

### Next.js (Unused in Production)

```bash
npm run dev      # Development server
npm run build    # Build for production
npm run lint     # Lint TypeScript/React code
```

### Python Environment Setup

```bash
pip install -r requirements.txt
```

## Architecture

### Core Principle: Clean Separation of Concerns

The codebase follows a **clean architecture** pattern where:
- **Engine modules** = Single source of truth for ALL business logic
- **Dashboard files** = Thin UI layer (renders only, never calculates)
- **Pydantic models** = Type-safe contracts between layers

### Key Modules (modules/)

**Business Logic Engines (Pure Python)**
- `engine.py` - GTM funnel calculations (leads → contacts → meetings → sales)
- `engine_pnl.py` - Financial calculations (unit economics, commissions, P&L)
- `scenario.py` - Sensitivity analysis and what-if modeling
- `models.py` - Pydantic data models (Channel, DealEconomics, GTMMetrics, etc.)

**Integration & UI**
- `dashboard_adapter.py` - Bridge pattern connecting session state to engines
- `ui_components.py` - Reusable Streamlit widgets (KPI rows, funnel charts, health scores)
- `state.py` - Cache key generation and state management
- `validation.py` - Input validation logic

**Legacy Modules (Still Used)**
- `calculations_improved.py` - Cost and compensation calculators
- `calculations_enhanced.py` - Revenue and health score logic
- `revenue_retention.py` - Multi-channel GTM and retention modeling

### Dashboard Structure (dashboards/)

```
dashboards/
├── production/
│   ├── dashboard_improved_final.py  # MAIN PRODUCTION FILE (3000+ lines)
│   ├── dashboard_fast.py            # Performance-optimized version
│   ├── compensation_v2.py           # Compensation tab logic
│   ├── business_performance_v2.py   # P&L tab logic
│   └── deal_economics_manager.py    # Deal economics calculations
├── cloud/
│   └── dashboard_cloud.py           # Lightweight Streamlit Cloud version
└── legacy/                          # Archived versions (DO NOT USE)
```

### Cost Model Architecture

The dashboard supports a **convergent cost model** where channels can input costs at different funnel stages:
- **CPL** (Cost per Lead) - Pay per lead generated
- **CPC** (Cost per Contact) - Pay per contacted lead
- **CPM** (Cost per Meeting) - Pay per meeting held
- **CPA** (Cost per Acquisition/Sale) - Pay per closed deal
- **BUDGET** - Fixed monthly budget

**Critical**: Only ONE cost point is paid per channel. If you select CPM, all upstream costs (CPL, CPC) are blocked. The engine in `engine.py` handles this logic.

### Deal Economics System

The dashboard uses a universal deal economics model that works for:
- **Insurance** - Premium × Years × Carrier Rate
- **SaaS** - MRR × Contract Length
- **Consulting** - Project Value
- **Custom** - Manual entry

**Key concepts**:
- `upfront_pct` - Percentage of deal paid immediately (e.g., 70%)
- `deferred_cash` - Remainder paid later (e.g., 30% at month 18)
- `commission_policy` - Pay commissions on "upfront only" or "full deal value"

This is managed by `DealEconomicsManager` in production dashboards.

### Caching Strategy

The architecture uses aggressive caching with smart invalidation:
- `@st.cache_data` on pure calculation functions
- Cache keys generated from business state snapshots (see `state.py`)
- Scope-based invalidation (GTM changes don't invalidate P&L cache)

When modifying calculations, ensure cache keys include all relevant inputs.

## Development Patterns

### Adding New Calculations

**DO**: Add logic to `engine.py` or `engine_pnl.py`
```python
def calculate_new_metric(channels: List[Channel], deal: DealEconomics) -> float:
    """Pure function, no side effects"""
    return computed_value
```

**DON'T**: Add calculations directly in dashboard files
```python
# ❌ BAD - scattered business logic in UI
monthly_revenue = sum(ch['leads'] * ch['rate'] * deal_value for ch in channels)
```

### Using the Adapter Pattern

For dashboard code, use `DashboardAdapter` to access all metrics:
```python
from modules.dashboard_adapter import DashboardAdapter

metrics = DashboardAdapter.get_metrics()
revenue = metrics['monthly_revenue_immediate']
ebitda = metrics['pnl']['ebitda']
ltv_cac = metrics['unit_economics']['ltv_cac']
```

This ensures consistency across all tabs and enables proper caching.

### Working with Session State

Session state schema (critical for understanding dashboard flow):
```python
st.session_state.gtm_channels        # List[dict] - Channel configurations
st.session_state.avg_deal_value      # float
st.session_state.upfront_payment_pct # float
st.session_state.commission_policy   # "upfront" | "full"
st.session_state.grr_rate           # float (Gross Revenue Retention)
```

Never mutate session state directly in calculations. Read for inputs, write only in UI event handlers.

### Testing Philosophy

Tests in `modules/tests/test_engine.py` lock down:
- Funnel monotonicity (leads ≥ contacts ≥ meetings ≥ sales)
- Cost method correctness (CPL/CPM/CPA/Budget)
- GTM aggregation (sum of channels = total)
- Commission policies (upfront vs full deal)
- Unit economics formulas (LTV, CAC, payback)

**Before deploying**: Always run `./run_tests.sh` to verify math hasn't broken.

## Common Workflows

### Adding a New Channel Configuration

1. Channels are stored in `st.session_state.gtm_channels` as list of dicts
2. Each channel must have: `id`, `name`, `monthly_leads`, conversion rates, and cost configuration
3. Use `Channel` Pydantic model from `models.py` for validation
4. The engine will automatically include it in aggregations

### Modifying Commission Logic

1. Commission logic lives in `engine_pnl.py` → `calculate_unit_economics()`
2. Two policies: `CommissionPolicy.UPFRONT` (pay on upfront cash) or `CommissionPolicy.FULL` (pay on full deal)
3. Tests cover both policies - update tests if changing formulas
4. UI representation is in compensation tabs (`compensation_v2.py`)

### Adding Sensitivity Analysis

Use `scenario.py`:
```python
from modules.scenario import calculate_sensitivity

def my_metric_fn(inputs):
    # Calculate metric using inputs
    return metric_value

sensitivities = calculate_sensitivity(
    baseline_fn=my_metric_fn,
    inputs={'close_rate': 0.30, 'cpl': 50},
    bump_pct=0.01  # 1% bump
)
```

## File Organization

**Active Production Files**:
- `dashboards/production/dashboard_improved_final.py` - MAIN PRODUCTION (last updated Sep 29, 2025)
- `modules/` - All supporting business logic

**Do Not Modify**:
- `dashboards/legacy/*` - Archived versions for reference only
- Old dashboard files in root (e.g., `unified_dashboard.py`, `app.py`)

**Next.js Assets** (unused):
- `app/`, `components/` - React/TypeScript UI components
- These exist but are NOT integrated with the Streamlit dashboard
- Configuration: `next.config.js`, `tailwind.config.js`, `postcss.config.js`

## Documentation

Comprehensive guides exist in the root directory:
- `ARCHITECTURE_GUIDE.md` - Detailed architecture explanation and migration guide
- `QUICK_START_GUIDE.md` - User-facing guide for using the dashboard
- `docs/DEPLOYMENT_GUIDE.md` - Production deployment procedures
- `docs/ENHANCED_FEATURES.md` - Feature documentation
- `README.md` - Repository overview

When making architectural changes, update `ARCHITECTURE_GUIDE.md`.

## Deployment

### Local Development
```bash
streamlit run dashboards/production/dashboard_improved_final.py
```

### Streamlit Cloud
- Entry point: `dashboards/cloud/dashboard_cloud.py`
- Python version: 3.9+
- Ensure all `modules/` dependencies are present
- Check deployment logs if cloud deployment fails

### Environment Requirements
See `requirements.txt` for Python dependencies. Key dependencies:
- streamlit>=1.35.0
- pandas>=2.1.0
- numpy>=1.26.0
- plotly>=5.18.0
- pydantic>=2.0.0
- pytest>=7.4.0 (for testing)

## Important Constraints

### What NOT to Do
1. **Never** add business logic directly to dashboard files - use `engine.py` or `engine_pnl.py`
2. **Never** create new dashboard files without archiving old ones to `dashboards/legacy/`
3. **Never** bypass the Pydantic models - they provide type safety
4. **Never** mutate channel data in calculations - keep functions pure
5. **Never** deploy without running tests first

### Performance Considerations
- The main production dashboard (`dashboard_improved_final.py`) is 3000+ lines and can be slow
- Use `dashboard_fast.py` for faster iteration during development
- Cache invalidation is scoped - changing GTM inputs won't recalculate P&L unnecessarily
- When adding UI components, consider the 5-10X performance gap between versions

### Language Support
The production dashboard has i18n support (English/Spanish). Strings are in the `TRANSLATIONS` dict at the top of `dashboard_improved_final.py`. Add translations when adding new UI strings.

## Health Checks

Before committing changes:
1. ✅ Run `./run_tests.sh` - All tests pass
2. ✅ Test locally with `streamlit run` - Dashboard loads without errors
3. ✅ Verify calculations match expected values in UI
4. ✅ Check that cache invalidation works (change inputs, see updates)
5. ✅ If modifying engines, update corresponding tests

## Contact & Maintenance

Maintained by: Sales Operations Engineering Team
Last Major Update: September 29, 2025
