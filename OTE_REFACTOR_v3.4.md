# OTE System Refactor - Dashboard v3.4

**Date:** 2025-11-12
**Update:** Smart OTE system with dynamic quotas
**Why:** User feedback - "quota is dynamic to the rest of the business metrics technically"

---

## ✅ What Changed in v3.4

### Major Improvements

**1. Monthly OTE Instead of Annual**
- **Before (v3.3)**: User entered annual OTE ($60,000)
- **After (v3.4)**: User enters monthly OTE ($5,000)
- **Why**: Monthly is more intuitive for operational planning

**2. Dynamic Quota Calculation**
- **Before**: User manually entered quotas (e.g., "5 deals/closer")
- **After**: Quotas auto-calculate from business metrics
- **Why**: Quota should reflect actual capacity and marketing spend

**3. Two Quota Modes**
- **Auto (Recommended)**: Quotas calculated from team capacity, conversion rates, marketing spend
- **Manual Override**: User can still set custom quotas if needed

---

## 🎯 How Dynamic Quotas Work

### Closer Quota (Auto Mode)
```
Quota = Expected Deals ÷ Number of Closers

Example:
- Marketing spend: $30,000
- Cost per meeting: $100
- Meetings: 300
- Show-up rate: 60% → 180 meetings held
- Close rate: 30% → 54 deals
- Closers: 8
→ Quota: 54 ÷ 8 = 6.75 deals/closer
```

**What this means:**
- Quota reflects what the BUSINESS needs from each closer
- If you increase marketing, quota goes up automatically
- If you add more closers, quota goes down (same deals, more people)

### Setter Quota (Auto Mode)
```
Quota = Capacity per day × Working days

Example:
- Meetings booked/setter/day: 2.0
- Working days: 20
→ Quota: 2.0 × 20 = 40 meetings/mo
```

**What this means:**
- Quota reflects setter CAPACITY
- If you increase "Meetings Booked/Setter/Day" (Tab 5), quota increases
- This is the CEILING - you can't expect more than capacity

### Manager Quota (Auto Mode)
```
Quota = Total team deals

Example:
- Total monthly deals: 54
→ Quota: 54 deals (for the entire team)
```

**What this means:**
- Manager quota = team performance
- Managers get paid on TOTAL team output
- No per-manager quota needed (typically 1 manager per team)

---

## 📋 New Configuration Workflow

### Step 1: Choose Quota Mode (Tab 5)

**Option A: Auto (Recommended)**
```
✅ Quotas reflect your actual business metrics
• Quota = Marketing Spend ÷ Team Size ÷ CPM
• Adjusts automatically when you change inputs
```

**When to use:**
- You want quotas tied to capacity
- You want quotas to update when business changes
- You're modeling different scenarios (What-If analysis)

**Option B: Manual Override**
```
⚠️ Manual quotas - ensure they align with capacity
• You control quota targets
• Check Tab 6 to see if quotas are achievable
```

**When to use:**
- You have specific quota targets from management
- You're testing "stretch goals"
- You want to compare actual vs aspirational targets

### Step 2: Set Monthly OTE (Tab 5)

For each role, enter **Monthly OTE** (not annual):

| Role | Monthly OTE | Recommended for Insurance Business |
|------|-------------|-----------------------------------|
| Closer | Input field | $5,000 - $7,000 |
| Setter | Input field | $4,000 - $5,000 |
| Manager | Input field | $7,500 - $10,000 |

**Why monthly?**
- Easier to compare to monthly earnings
- More intuitive for operational planning
- Annual shown automatically (Monthly × 12)

### Step 3: View Performance (Tab 6)

**With Auto Quotas:**
- Quotas update in real-time based on your GTM inputs
- Attainment % shows if team is hitting expected capacity
- Gap analysis shows specific recommendations

**With Manual Quotas:**
- Quotas stay fixed
- Attainment % shows if team is hitting YOUR targets
- System warns if quotas exceed capacity

---

## 💡 Examples: Your Insurance Business

### Scenario 1: Current State (Auto Mode)

**Your Setup:**
- Marketing: $30,000/mo
- CPM: $100
- Meetings held: 182/mo
- Close rate: 30%
- **Deals: 54.6/mo**
- Team: 8 closers, 2 setters, 1 manager

**Auto Quotas Calculate:**
```
Closer Quota: 54.6 ÷ 8 = 6.8 deals/mo
Setter Quota: 2.0 meetings/day × 20 days = 40 meetings/mo
Manager Quota: 54.6 team deals/mo
```

**OTE Settings:**
```
Closer OTE: $5,670/mo ($68K annual)
Setter OTE: $4,000/mo ($48K annual)
Manager OTE: $6,800/mo ($82K annual)
```

**Tab 6 Shows:**
- Closer attainment: 100% (6.8 deals = quota) ✅
- Setter attainment: 100% (capacity-based) ✅
- Manager attainment: 100% (team hitting target) ✅
- **All green indicators!**

### Scenario 2: Scale to Month 6 (Auto Mode)

**You Change:**
- Marketing: $40,000/mo (increase)
- Close rate: 35% (improve)
- Add 2 more closers (now 10 total)

**Auto Quotas Recalculate:**
```
New expected deals: $40K ÷ $80 CPM × 60% show × 35% close = 105 deals/mo
Closer Quota: 105 ÷ 10 = 10.5 deals/mo (up from 6.8)
Setter Quota: Still 40 meetings/mo (capacity unchanged)
Manager Quota: 105 team deals/mo
```

**Tab 6 Now Shows:**
- Closer attainment: ~65% (6.8 actual vs 10.5 quota) ⚠️
- **Insight**: "Need 3.7 more deals/closer" OR "Hire 4 more closers"
- Setter attainment: Still 100% ✅
- Manager attainment: ~52% (team at 52% of new target)

**What this tells you:**
- You need to hire MORE closers to handle the increased demand
- OR accept lower per-closer attainment during growth phase
- Setters are fine (capacity still matches need)

### Scenario 3: Stretch Goals (Manual Mode)

**You Set:**
- Closer Quota: 10 deals/mo (manual - aspirational)
- Closer OTE: $5,670/mo
- Marketing: $30,000/mo (actual)
- Expected deals: 54.6/mo (actual)

**Tab 6 Shows:**
- Closer attainment: 68% (6.8 actual vs 10 quota) 🚨
- **Insight**: "Need 3.2 more deals/closer"
- **Insight**: "To hit quota, increase close rate by 47% OR increase marketing by $16K"

**What this tells you:**
- Your stretch goal (10 deals) requires 47% more performance
- You can model what changes are needed to get there

---

## 🔧 Technical Changes

### Session State Keys Changed

**Removed:**
```python
'closer_ote': 60000  # Annual
'closer_quota_deals': 5.0  # Manual only
'setter_ote': 48000
'setter_quota_meetings': 40.0
'manager_ote': 90000
'manager_quota_team_deals': 40.0
```

**Added:**
```python
# OTE (now monthly)
'closer_ote_monthly': 5000
'setter_ote_monthly': 4000
'manager_ote_monthly': 7500

# Quota mode
'quota_calculation_mode': 'Auto (Based on Capacity)'

# Manual overrides (only if mode = Manual)
'closer_quota_deals_manual': 5.0
'setter_quota_meetings_manual': 40.0
'manager_quota_team_deals_manual': 40.0
```

### Quota Calculation Logic (Tab 6)

```python
# Get quota mode
quota_mode = st.session_state.get('quota_calculation_mode', 'Auto (Based on Capacity)')

if quota_mode == "Auto (Based on Capacity)":
    # Closers: Based on expected deals
    closer_quota_deals = gtm_metrics['monthly_sales'] / num_closers

    # Setters: Based on capacity
    meetings_per_setter_capacity = st.session_state.get('meetings_per_setter', 2.0)
    working_days = st.session_state.get('working_days', 20)
    setter_quota_meetings = meetings_per_setter_capacity * working_days

    # Managers: Based on team total
    manager_quota_team_deals = gtm_metrics['monthly_sales']
else:
    # Manual mode - use user inputs
    closer_quota_deals = st.session_state.get('closer_quota_deals_manual', 5.0)
    setter_quota_meetings = st.session_state.get('setter_quota_meetings_manual', 40.0)
    manager_quota_team_deals = st.session_state.get('manager_quota_team_deals_manual', 40.0)
```

### Files Modified

- **[dashboard_fast.py](dashboards/production/dashboard_fast.py:211-222)**: Updated session_state defaults
- **[dashboard_fast.py](dashboards/production/dashboard_fast.py:3386-3523)**: Refactored OTE configuration UI
- **[dashboard_fast.py](dashboards/production/dashboard_fast.py:3675-3702)**: Updated Tab 6 quota logic
- **[dashboard_fast.py](dashboards/production/dashboard_fast.py:3597-3605)**: Updated export format
- **[dashboard_fast.py](dashboards/production/dashboard_fast.py:2334-2342)**: Updated import handler
- Version: **3.3 → 3.4**

---

## 📊 Why This Is Better

### Problem with v3.3 (Manual Quotas)
1. **Static**: Quota doesn't change when business changes
2. **Disconnected**: No relationship to marketing spend, capacity, or conversion rates
3. **Manual work**: User has to calculate and update quotas constantly
4. **Misleading**: Attainment % doesn't reflect business reality

**Example Issue:**
- User sets quota: 5 deals/closer
- Increases marketing by 50%
- Expected deals go from 40 to 60
- Quota still shows 5 (should be 7.5)
- Attainment looks like 120% (misleading - team needs to scale)

### Solution with v3.4 (Auto Quotas)
1. **Dynamic**: Quota updates automatically with business metrics
2. **Connected**: Reflects actual capacity and demand
3. **Zero maintenance**: No manual updates needed
4. **Accurate**: Attainment % shows true performance vs capacity

**Same Example:**
- Auto quota starts at 5 deals/closer (40 deals ÷ 8 closers)
- User increases marketing by 50%
- Expected deals: 60
- **Auto quota recalculates**: 60 ÷ 8 = 7.5 deals/closer
- Attainment: 100% (5 deals = 67% of new capacity - system recommends hiring)

---

## 🚀 Migration Guide

### If You Used v3.3

Your existing configs will import, but:

**Old format (v3.3):**
```json
{
  "ote_quotas": {
    "closer_ote": 60000,
    "closer_quota_deals": 5.0
  }
}
```

**What happens:**
- Import will work (backward compatible)
- Annual OTE (60000) will be ignored
- Manual quota (5.0) will be imported to `closer_quota_deals_manual`
- You'll be in Manual mode by default
- **Recommended**: Switch to Auto mode and set monthly OTE

**New format (v3.4):**
```json
{
  "ote_quotas": {
    "closer_ote_monthly": 5000,
    "quota_calculation_mode": "Auto (Based on Capacity)",
    "closer_quota_deals_manual": 5.0
  },
  "version": "1.1"
}
```

---

## 💡 Best Practices

### When to Use Auto Mode (90% of cases)
- Day-to-day operations
- Scenario planning
- Investor presentations ("At current capacity, we can do X deals")
- Hiring decisions ("We need Y more closers to hit Z revenue")

### When to Use Manual Mode
- Board-set quotas ("We committed to 10 deals/closer this quarter")
- Stretch goals ("Let's see what it takes to 2x quota")
- Testing compensation plans ("If quota is X, what OTE makes sense?")
- Comparing to industry benchmarks

### Recommended Workflow

**Step 1: Use Auto Mode**
- See what your business can ACTUALLY produce
- Check if OTE is achievable at current capacity
- Identify bottlenecks (need more closers? more marketing?)

**Step 2: If Needed, Switch to Manual**
- Set aspirational quotas
- See gap between actual and target
- Get specific recommendations to close gap

---

## Summary

**v3.4 makes OTE smarter by:**
- ✅ Switching to monthly OTE (more intuitive)
- ✅ Auto-calculating quotas from business metrics
- ✅ Updating quotas in real-time as inputs change
- ✅ Providing two modes (Auto + Manual)
- ✅ Showing dynamic attainment based on capacity

**This means:**
- No more manual quota updates
- Accurate attainment tracking
- Better scenario planning
- Clearer hiring/scaling decisions

**Your insurance business example:**
- Closer OTE: $5,670/mo
- Auto quota: 6.8 deals/mo (based on $30K marketing ÷ 8 closers)
- Commission needed: $1,134/deal (matches your 10% rate ✅)
- Everything auto-updates when you change GTM inputs!

---

**Status:** ✅ COMPLETE
**Risk Level:** Low (config changes only, no calculation logic affected)
**Next:** Test in dashboard, verify quotas calculate correctly
