# OTE System - Dashboard v3.3

**Date:** 2025-11-12
**Feature:** On-Target Earnings (OTE) tracking and Team Performance analysis

---

## ✅ What's New in v3.3

### New Features
1. **OTE Configuration** (Tab 5: Configuration)
   - Define On-Target Earnings for each role
   - Set monthly quotas (deals, meetings, team performance)
   - See real-time calculations of what quotas require

2. **Team Performance Tab** (NEW Tab 6)
   - OTE vs Actual earnings comparison
   - Quota attainment tracking
   - Gap analysis with specific recommendations
   - Strategic insights for optimization
   - Performance comparison table

3. **Export/Import Support**
   - OTE and quota settings now included in config JSON
   - Version bumped to 1.1

---

## 🎯 OTE System Overview

### What is OTE?
**On-Target Earnings (OTE)** = Total compensation when a rep hits 100% of quota

For commission-only roles:
- **OTE = Base Salary + Commission at Quota**
- Example: $0 base + $5,000/mo commission at 5 deals = **$60,000 annual OTE**

For mixed roles:
- **OTE = Base + Variable + Commission at Quota**

### Why Track OTE?
1. **Investor Reporting**: Show predictable team costs
2. **Hiring Planning**: Know what comp levels to offer
3. **Performance Management**: Identify underperforming roles
4. **Budget Forecasting**: Model team costs at different growth stages
5. **Comp Plan Optimization**: Ensure OTE is achievable and aligned with revenue

---

## 📋 How to Use

### Step 1: Configure OTE & Quotas (Tab 5)

Navigate to **Tab 5: Configuration** → Expand **"🎯 OTE & Quota Configuration"**

#### Closer Configuration
- **Annual OTE**: Total target comp per year (e.g., $60,000)
- **Monthly Quota**: Deals expected per month (e.g., 5.0 deals)
- **Live Calculations**:
  - Monthly OTE: $5,000
  - Required commission/deal: $1,000 (if commission-only)

#### Setter Configuration
- **Annual OTE**: Total target comp (e.g., $48,000)
- **Monthly Quota**: Meetings booked per month (e.g., 40 meetings)
- **Live Calculations**:
  - Monthly OTE: $4,000
  - Required commission/meeting: $100

#### Manager Configuration
- **Annual OTE**: Total target comp (e.g., $90,000)
- **Monthly Quota**: Team deals expected (e.g., 40 deals)
- **Live Calculations**:
  - Monthly OTE: $7,500
  - Required override/deal: $187.50

### Step 2: View Team Performance (Tab 6)

Navigate to **Tab 6: Team Performance**

#### Performance Summary (Top Row)
- **Team Avg Attainment**: Average OTE attainment across all roles
- **Total OTE (Monthly)**: Total team OTE target
- **Total Actual**: Actual team earnings
- **OTE Gap**: Difference between actual and target
- **Revenue per $1 OTE**: Efficiency metric (higher = better)

#### Role-by-Role Breakdown
Each role shows:

**Performance Metrics:**
- Actual production vs quota
- Quota attainment %
- Visual progress bar
- Status indicator (✅ exceeding, ⚠️ at target, 🚨 below)

**OTE Tracking:**
- Monthly OTE target
- Actual monthly earnings
- OTE attainment %

**Team Total:**
- Headcount
- Team OTE (monthly)
- Team actual earnings (monthly)

**Gap Analysis:**
- Gap per person ($)
- Team gap ($)
- Specific recommendations

#### Strategic Insights
**Performance Gaps:**
- Sorted by role (worst to best)
- Specific recommendations for each gap:
  - Closers: "Need X more deals" OR "Increase close rate by Y%"
  - Setters: "Need X more meetings" OR "Increase marketing by $Z"
  - Managers: "Focus on improving team performance"

**OTE Efficiency Analysis:**
- OTE as % of revenue (target: <20%)
- Health check (🚨 high, ⚠️ moderate, ✅ efficient)
- Break-even analysis:
  - How many deals needed to hit OTE?
  - Is OTE aligned with quota?
  - Red flags if OTE requires more than quota

**Comparison Table:**
- All roles side-by-side
- Headcount, OTE, Actual, Attainment %
- Quota vs Actual performance

---

## 📊 Example: Your Insurance Business

### Current Setup (from previous sessions)
**Team:**
- 8 Closers
- 2 Setters
- 1 Manager
- Commission-only model

**Deal Economics:**
- $11,340 upfront commission per deal (70% of $16,200)
- 10% closer commission = $1,134/deal
- 5% setter commission = $567/deal
- 3% manager override = $340/deal

### Recommended OTE Configuration

#### Closers
- **Annual OTE**: $68,040 (60 deals/year × $1,134)
- **Monthly OTE**: $5,670
- **Monthly Quota**: 5 deals
- **At quota**: Earns exactly OTE ✅

#### Setters
- **Annual OTE**: $68,040 (120 deals/year × $567)
- **Monthly OTE**: $5,670
- **Monthly Quota**: 40 meetings
  - Assumes 25% close rate (40 mtgs → 10 meetings held → 2.5 deals)
  - 2.5 deals × 4 setters × $567 = $5,670 ✅

#### Manager
- **Annual OTE**: $81,600 (240 team deals/year × $340)
- **Monthly OTE**: $6,800
- **Monthly Quota**: 40 team deals (across all closers)
- **At quota**: Earns exactly OTE ✅

### What You'll See in Tab 6

#### If hitting quota (100% attainment):
- **Team Avg Attainment**: 100%
- **Total OTE**: $47,180/month
- **Total Actual**: $47,180/month
- **OTE Gap**: $0
- **Revenue per $1 OTE**: $13.12 (based on your $619K revenue)
- **All roles**: ✅ Green indicators

#### If at 80% of quota (typical ramp):
- **Team Avg Attainment**: 80%
- **Closer Gap**: $1,134/person (need 1 more deal/closer)
- **Setter Gap**: $1,134/person (need 8 more meetings/setter)
- **Recommendations**: "Increase marketing by $1,600 to add 16 meetings"

#### If exceeding quota (120%):
- **Team Avg Attainment**: 120%
- **OTE Gap**: +$9,436/month
- **Recommendations**: "Consider increasing OTE targets" OR "Scale team to match demand"

---

## 💡 Best Practices

### Setting OTE Targets
1. **Start with market rates** for your geography/industry
2. **Back into quota** from OTE and commission structure
3. **Validate quota is achievable** with current conversion rates
4. **Align OTE with revenue** (target: OTE = 10-20% of revenue)

### Using OTE for Decision Making

**Scenario 1: Team consistently below OTE**
- **Problem**: Team earning less than expected
- **Causes**: Low conversion rates, insufficient marketing spend, quota too aggressive
- **Actions**:
  - Check Tab 6 → Strategic Insights → Performance Gaps
  - Increase marketing budget to feed more leads
  - Lower OTE targets if quota is unrealistic
  - Provide more training/coaching

**Scenario 2: Team consistently above OTE**
- **Problem**: Paying more than planned (but good for morale!)
- **Causes**: Quota too easy, strong market conditions, excellent team
- **Actions**:
  - Increase OTE targets to retain talent
  - Add more headcount to capture demand
  - Consider ramping quota gradually

**Scenario 3: Wide variance across roles**
- **Problem**: Closers at 120%, Setters at 60%
- **Causes**: Bottleneck in setter capacity
- **Actions**:
  - Hire more setters
  - Increase setter OTE to attract better talent
  - Adjust setter quota to be more realistic

### For Investors/Board
Export these metrics monthly:
1. **OTE Attainment %** (trend over time)
2. **OTE as % of Revenue** (should decrease as you scale)
3. **Revenue per $1 OTE** (should increase as you optimize)
4. **Headcount vs Quota Capacity** (are we fully utilized?)

---

## 🔧 Technical Details

### Files Modified
- **[dashboard_fast.py](dashboards/production/dashboard_fast.py)**
  - Lines 211-217: Added OTE defaults to session_state
  - Lines 796-802: Added Tab 6 to tab list
  - Lines 3377-3470: Added OTE configuration section
  - Lines 3533-3540: Added OTE to export config
  - Lines 3329-3336: Added OTE to import handler
  - Lines 3603-3930: New Tab 6 implementation (330 lines)
  - Version updated to 3.3

### New Session State Keys
```python
'closer_ote': 60000  # Annual OTE
'closer_quota_deals': 5.0  # Monthly quota
'setter_ote': 48000
'setter_quota_meetings': 40.0
'manager_ote': 90000
'manager_quota_team_deals': 40.0
```

### Calculations

**OTE Attainment:**
```python
actual_closer_monthly = (closer_pool / num_closers) + (closer_base / 12)
closer_ote_monthly = closer_ote / 12
closer_attainment = (actual_closer_monthly / closer_ote_monthly) * 100
```

**Quota Attainment:**
```python
deals_per_closer = monthly_sales / num_closers
closer_quota_attainment = (deals_per_closer / closer_quota_deals) * 100
```

**Break-Even Analysis:**
```python
commission_per_deal = avg_deal_value × upfront_pct × closer_commission_pct
deals_for_ote = (closer_ote_monthly - closer_base_monthly) / commission_per_deal
```

---

## 🧪 Testing

### Test Case 1: Basic OTE Configuration
1. Go to Tab 5 → Expand "🎯 OTE & Quota Configuration"
2. Set Closer OTE: $60,000, Quota: 5 deals
3. Verify monthly OTE shows $5,000
4. Verify required commission/deal calculation
5. Go to Tab 6
6. Verify Summary metrics populate
7. **Expected**: All metrics visible, no errors

### Test Case 2: OTE Above/Below Performance
1. Configure team with 8 closers, $60K OTE, 5 deals quota
2. Set GTM to generate 30 deals/month (3.75 deals/closer)
3. Go to Tab 6
4. **Expected**:
   - Closer attainment: ~75%
   - Gap: -$1,260/closer
   - Recommendation: "Need 1.25 more deals/closer"

### Test Case 3: Export/Import with OTE
1. Configure OTE values in Tab 5
2. Export config
3. Change OTE values
4. Import saved config
5. **Expected**: OTE values restore to exported state

### Test Case 4: Strategic Insights
1. Set team to 60% of quota
2. Go to Tab 6 → Strategic Insights
3. **Expected**:
   - Performance Gaps shows all 3 roles
   - Specific recommendations for each
   - OTE Efficiency shows 🚨 or ⚠️ warning

---

## 🚀 Future Enhancements (Not Yet Implemented)

### Phase 2: Advanced OTE Features
1. **Historical Tracking**: Chart OTE attainment over time
2. **Cohort Analysis**: Performance by hire date, channel, etc.
3. **Comp Plan Optimizer**: AI suggests optimal OTE/quota combinations
4. **Ramp Plans**: Different OTE/quotas for new hires (Month 1: 50%, Month 3: 100%)
5. **Accelerators**: Model bonus structures for exceeding quota
6. **Team Leaderboards**: Rank individuals by attainment %

### Phase 3: AI Integration
- **Strategic Advisor**: Claude analyzes OTE data and suggests optimizations
- **Scenario Planning**: "What if I increase OTE by 20%?"
- **Hiring Recommendations**: "Hire 2 more closers to hit $1M ARR"

---

## 📖 Related Documentation

- [FINAL_FIX_VALUE_RESETS.md](FINAL_FIX_VALUE_RESETS.md) - Widget value persistence fixes
- [BUG_FIXES_2025-11-11.md](BUG_FIXES_2025-11-11.md) - Previous bug fixes
- [QUICK_START_INSURANCE.md](QUICK_START_INSURANCE.md) - Insurance business setup guide

---

## Summary

**New in v3.3:**
- ✅ OTE configuration in Tab 5
- ✅ New Tab 6: Team Performance
- ✅ OTE vs Actual tracking
- ✅ Quota attainment monitoring
- ✅ Gap analysis with recommendations
- ✅ Strategic insights
- ✅ Export/Import support
- ✅ Break-even analysis
- ✅ Performance comparison table

**Total additions:**
- 6 new session state keys
- 1 new tab (330 lines)
- 1 new configuration section (95 lines)
- Export/Import integration (15 lines)
- **Total: ~440 new lines of code**

**Status:** ✅ COMPLETE - Ready for testing
**Risk Level:** Low (isolated new feature, no changes to existing logic)
**Next Step:** User testing to validate OTE targets and recommendations

---

**Built by:** Claude (Durov mode)
**Time:** 2 hours
**Version:** Dashboard v3.3
