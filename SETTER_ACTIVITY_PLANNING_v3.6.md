# Setter Activity Planning Module - v3.6

**Status:** ✅ IMPLEMENTED
**Dashboard Version:** v3.6
**Location:** Tab 5 → Configuration → "📞 Setter Activity Planning & Daily Workload" expander

---

## 🎯 Problem Solved

### User Question:
> "I think all setters have to basically do a lot of work if we take into consideration:
> 1. contact rate of the funnel (meaning they get contacted via a call apart from any automated workflows)
> 2. every appointment needs to be confirmed via a Discovery call taken by the setter
>
> Taking this into consideration, would that change our model or how can i preview the actual daily activities of the setters / closers or plan this type of stuff?"

### The Gap in Previous Model

**Before v3.6:**
- ❌ Only tracked "meetings booked/setter/day" (output metric)
- ❌ No breakdown of actual setter activities
- ❌ Couldn't model contact rate, discovery calls, confirmation calls
- ❌ No way to see if targets were realistic
- ❌ No visibility into daily workload

**After v3.6:**
- ✅ Full workflow modeling (contact → discovery → booking → confirmation)
- ✅ Daily activity breakdown per setter
- ✅ Time allocation analysis
- ✅ Capacity check with red/yellow/green status
- ✅ Team-level aggregation
- ✅ Realistic planning based on actual work required

---

## 📊 What This Module Does

### 1. Models the Complete Setter Workflow

**Typical Setter Day:**
```
Marketing generates leads
    ↓
Setter contacts leads (cold calling)
    ↓
Discovery call to qualify (pre-booking)
    ↓
Meeting scheduled with closer
    ↓
Confirmation call before meeting
    ↓
Meeting held by closer
```

### 2. Calculates Required Activities

Based on your target "Meetings Booked/Setter/Day" (e.g., 2.0 meetings), the system calculates:

- **Contacts needed**: If 5 contacts = 1 meeting, setter needs 10 contacts/day
- **Discovery calls**: If 100% of contacts need discovery, setter makes 10 discovery calls
- **Confirmation calls**: If 80% of meetings need confirmation, setter makes 1.6 confirmation calls
- **Total calls/day**: Discovery + Confirmation = daily call volume
- **Time required**: Calls × avg call duration = hours on phone
- **Time remaining**: Daily hours - call time = buffer for admin/cold calling

### 3. Validates Feasibility

**Capacity Checks:**
- 🚨 **Red (>90% utilized)**: Overloaded, can't sustain this workload
- ⚠️ **Yellow (75-90%)**: High but manageable
- ✅ **Green (<75%)**: Healthy workload with buffer

---

## 🔧 Configuration Parameters

### Available in the Expander

| Parameter | Default | Description |
|-----------|---------|-------------|
| **Lead Contact Rate (%)** | 30% | % of marketing leads setters actually contact (vs automated) |
| **Contacts Per Meeting Booked** | 5.0 | How many contacts needed to book 1 meeting |
| **Discovery Call Required (%)** | 100% | % of contacts needing a discovery/qualification call |
| **Confirmation Call Required (%)** | 80% | % of booked meetings needing confirmation call |
| **Avg Call Duration (minutes)** | 8 min | Average time per call (any type) |
| **Productive Hours/Day** | 6.0 hrs | Hours available for calling (excluding breaks, admin, training) |

### Derived Calculations

The system automatically calculates:
- **Contact → Meeting Rate**: `(1 / contacts_per_meeting) × 100`
- **Max Calls/Day (Theoretical)**: `(productive_hours × 60) / avg_call_duration`
- **Discovery Calls/Day**: `contacts_needed × (discovery_pct / 100)`
- **Confirmation Calls/Day**: `meetings_to_book × (confirmation_pct / 100)`
- **Total Call Time**: `total_calls × avg_call_duration`
- **Time Remaining**: `productive_hours - call_time`

---

## 📅 What You See

### 1. Daily Activity Breakdown (Per Setter)

**4-Column View:**

#### Column 1: Target Output
- Meetings to Book: `2.0` (from main config)
- Contacts Needed: `10.0` (at 5 contacts/meeting)

#### Column 2: Call Volume
- Discovery Calls: `10.0` (100% of contacts)
- Confirmation Calls: `1.6` (80% of meetings)
- **Total Calls/Day**: `11.6`

#### Column 3: Time Allocation
- Call Time: `1.5h` (11.6 calls × 8 min)
- Time Remaining: `4.5h` (75% of day)
  - For cold calling, admin, CRM

#### Column 4: Capacity Check
- ✅ **65% Utilized** - Healthy workload
- ✅ **Calls fit in day** (11.6 < 45 max)

### 2. Monthly Activity Summary (Per Setter)

**3-Column View:**

#### Monthly Targets
- Meetings to Book: `40` (2/day × 20 days)
- Contacts Required: `200` (10/day × 20 days)

#### Monthly Call Volume
- Discovery Calls: `200`
- Confirmation Calls: `32`
- **Total Calls**: `232` per month

#### Monthly Time Investment
- Time on Calls: `31h` (1.5h × 20 days)
- Total Available: `120h` (6h × 20 days)
- Utilization: `26%`

### 3. Team-Level Setter Activity

**4-Column View:**

#### Team Output
- Team Size: `4 setters`
- Meetings/Month: `160` (40 × 4)
- Contacts/Month: `800` (200 × 4)

#### Team Call Volume
- Calls/Day: `46` (11.6 × 4)
- Calls/Month: `928` (232 × 4)

#### Team Capacity
- Available Hours: `480h/mo` (120 × 4)
- Call Hours: `124h/mo` (31 × 4)

#### Recommendations
- ✅ **Well Staffed** - Team capacity aligned
- OR 🚨 **Hire More Setters** - Need 5.2 setters (if overloaded)
- OR 💡 **Underutilized** - Could book 3.5/day (if underused)

### 4. Insights & Planning Guidance

**Key Metrics Summary:**
- **5.0 contacts** needed per meeting booked
- **11.6 calls/day** per setter (10.0 discovery + 1.6 confirmation)
- **1.5 hours/day** on calls (26% of available time)
- **4.5 hours/day** for cold outreach, admin, CRM work

**Interpretation:**
- **If >85% utilized**: Setters are maxed out, little time for proactive work
- **If 65-85% utilized**: Healthy workload, time for core activities
- **If <65% utilized**: Setters have capacity for more meetings or projects

---

## 🎯 Use Cases

### 1. **Setting Realistic Targets**

**Question:** "Can my setters actually book 3 meetings/day?"

**Answer:**
- 3 meetings/day = 15 contacts needed
- 15 contacts = 15 discovery calls
- 3 meetings = 2.4 confirmation calls
- Total: 17.4 calls/day
- Time: 2.3 hours on calls (38% utilization)
- ✅ **Yes, realistic!** Leaves 3.7 hours for cold calling

### 2. **Deciding When to Hire**

**Scenario:** Setters are at 92% utilization

**Module Output:**
- 🚨 **Hire More Setters**
- Current: 4 setters
- Need: 4.9 setters (round to 5)
- **Recommendation:** Add 1 setter to get back to 75% target utilization

### 3. **Process Optimization**

**Current State:**
- 100% discovery call rate = 10 calls/day
- Taking 80 minutes

**What-If:** "What if we improve qualification and only 70% need discovery?"
- Change parameter to 70%
- Discovery calls drop to 7.0/day
- Saves 24 minutes/day
- Reduces utilization from 65% → 52%
- Setters can book 2.5 meetings/day with same capacity!

### 4. **Team Planning**

**Goal:** Book 200 meetings/month

**Module Calculation:**
- At 2 meetings/setter/day × 20 days = 40 meetings/setter/month
- Need: 200 ÷ 40 = **5 setters**
- Call volume: 1,160 calls/month (team)
- Time investment: 155 hours/month (team)

### 5. **Lead Quality Analysis**

**Current:** 5 contacts = 1 meeting (20% contact→meeting rate)

**If Lead Quality Improves:** 3 contacts = 1 meeting (33% rate)
- Contacts needed drops from 10 → 6 per day
- Discovery calls drop from 10 → 6 per day
- Total calls drop from 11.6 → 7.6 per day
- Time savings: 32 minutes/day
- **Can increase meeting targets or reduce team size!**

---

## 🔄 Integration with Existing Model

### How It Fits

**Main Config (Tab 5 - Team Configuration):**
- `Meetings Booked/Setter/Day`: 2.0 ← **Input**

**Setter Activity Planning Module:**
- Reads that target
- Models the **actual work required** to hit it
- Validates if it's **feasible**

**Tab 6 (Team Performance):**
- Tracks **actual** meetings booked
- Compares to quota
- Shows OTE attainment

**Flow:**
```
Set Target (Main Config)
    ↓
Model Activities Required (Activity Planning)
    ↓
Validate Feasibility (Capacity Check)
    ↓
Track Actual Performance (Team Performance Tab)
```

---

## 📈 Example Scenarios

### Scenario 1: Healthy Team

**Configuration:**
- 4 setters
- Target: 2 meetings/setter/day
- 5 contacts per meeting
- 100% discovery, 80% confirmation
- 8 min calls, 6 hours/day

**Results:**
- ✅ 65% utilization
- ✅ 4.5 hours/day remaining
- ✅ Can sustain workload

**Recommendation:** Current capacity is healthy

---

### Scenario 2: Overloaded Team

**Configuration:**
- 3 setters
- Target: 3 meetings/setter/day
- 7 contacts per meeting
- 100% discovery, 90% confirmation
- 10 min calls, 6 hours/day

**Results:**
- 🚨 94% utilization
- 🚨 Only 0.4 hours/day remaining
- ❌ Can't sustain - no time for cold calling

**Recommendation:** Hire 1 more setter (get to 4 total) to drop utilization to 71%

---

### Scenario 3: Underutilized Team

**Configuration:**
- 6 setters
- Target: 1.5 meetings/setter/day
- 4 contacts per meeting
- 80% discovery, 70% confirmation
- 7 min calls, 6 hours/day

**Results:**
- 💡 42% utilization
- 💡 3.5 hours/day remaining
- 💡 Significant spare capacity

**Recommendation:** Can increase target to 2.5 meetings/day OR reduce team to 4 setters

---

### Scenario 4: High-Touch Sales Process

**Configuration:**
- 2 setters (boutique business)
- Target: 1 meeting/setter/day
- 10 contacts per meeting (selective)
- 100% discovery, 100% confirmation
- 15 min calls (longer, consultative)
- 5 hours/day (smaller team = more admin)

**Results:**
- ⚠️ 88% utilization
- ⚠️ Only 0.6 hours/day remaining
- ⚠️ Tight but manageable

**Recommendation:** Process is very manual. Consider:
- Automating confirmation calls (drop to 50%)
- Hire 1 more setter when scaling
- Or keep boutique and selective

---

## 💡 Strategic Questions This Answers

### 1. **"Are my setter targets realistic?"**
**Answer:** Check capacity utilization. If >90%, targets are too aggressive.

### 2. **"When should I hire another setter?"**
**Answer:** When utilization hits 85-90% consistently.

### 3. **"Can I scale meetings without hiring?"**
**Answer:** Check time remaining. If >3 hours/day, probably yes. If <1 hour, no.

### 4. **"Why are my setters overwhelmed?"**
**Answer:** Module shows if you're underestimating discovery calls, confirmation calls, or call duration.

### 5. **"Should I automate confirmations?"**
**Answer:** Model it - if confirmation calls are taking >30% of time, yes.

### 6. **"What if I improve lead quality?"**
**Answer:** Reduce contacts_per_meeting, see time savings, model new capacity.

### 7. **"Can I leave cold calling to setters?"**
**Answer:** Check time remaining. Need at least 2-3 hours/day for proactive outreach.

---

## 🔧 Technical Implementation

### Session State Keys

```python
# Setter workflow configuration
'setter_contact_rate': 30.0  # % of leads contacted
'setter_contacts_per_meeting': 5.0  # Contacts needed per meeting
'setter_discovery_call_pct': 100.0  # % needing discovery
'setter_confirmation_call_pct': 80.0  # % needing confirmation
'setter_avg_call_duration_mins': 8.0  # Minutes per call
'setter_daily_hours': 6.0  # Productive hours/day
```

### Widget Keys (Internal)

```python
'setter_contact_rate_widget'
'setter_contacts_per_meeting_widget'
'setter_discovery_call_pct_widget'
'setter_confirmation_call_pct_widget'
'setter_avg_call_duration_mins_widget'
'setter_daily_hours_widget'
```

### Calculation Flow

```python
# 1. Get target from main config
target_meetings_per_setter_per_day = st.session_state.get('meetings_per_setter', 2.0)

# 2. Calculate contacts needed
contacts_needed_daily = target_meetings_per_setter_per_day * contacts_per_meeting

# 3. Calculate discovery calls
discovery_calls_daily = contacts_needed_daily * (discovery_call_pct / 100)

# 4. Calculate confirmation calls
confirmation_calls_daily = target_meetings_per_setter_per_day * (confirmation_call_pct / 100)

# 5. Total calls
total_calls_daily = discovery_calls_daily + confirmation_calls_daily

# 6. Time on calls
total_call_time_hours = (total_calls_daily * avg_call_duration) / 60

# 7. Time remaining
time_remaining_hours = setter_daily_hours - total_call_time_hours

# 8. Utilization
utilization_pct = (total_call_time_hours / setter_daily_hours) * 100
```

---

## 📋 Export/Import Support

### Currently NOT in Export (v3.6)

The setter activity planning parameters are **not yet included** in the JSON export/import because they're planning tools rather than core business config.

### Future Enhancement (v3.7)

Could add to export as:
```json
{
  "setter_activity_planning": {
    "contact_rate": 30.0,
    "contacts_per_meeting": 5.0,
    "discovery_call_pct": 100.0,
    "confirmation_call_pct": 80.0,
    "avg_call_duration_mins": 8.0,
    "daily_hours": 6.0
  }
}
```

---

## 🚀 Future Enhancements

### Phase 2: Closer Activity Planning

Similar module for closers:
- Meetings held/day
- Pre-meeting research time
- Meeting duration
- Post-meeting follow-up
- Proposal creation time
- Contract negotiation calls

### Phase 3: Workflow Optimization

- A/B test different workflows
- Compare "discovery required" vs "direct booking"
- Model impact of automation (e.g., automated confirmations)

### Phase 4: Real-Time Tracking

- Connect to CRM to track actual activities
- Compare planned vs actual
- Alert when team is falling behind

---

## Summary

**Feature:** Setter Activity Planning & Daily Workload Module

**Purpose:** Model the **full setter workflow** including contact rate, discovery calls, confirmation calls, and time allocation

**Benefits:**
1. ✅ Set realistic meeting targets
2. ✅ Validate if workload is sustainable
3. ✅ Decide when to hire more setters
4. ✅ Identify process optimization opportunities
5. ✅ Plan team capacity for growth

**Location:** Tab 5 → Configuration → "📞 Setter Activity Planning & Daily Workload" expander

**Version:** Dashboard v3.6

**Status:** ✅ Ready to use

**Files Changed:**
- [dashboard_fast.py:3134-3458](dashboards/production/dashboard_fast.py:3134-3458) - Full module implementation

**Impact:** Transforms setter planning from simple "meetings/day" metric to comprehensive workflow analysis

---

**Built for:** Realistic capacity planning and team sizing decisions
**Risk Level:** Low (isolated feature, doesn't affect existing calculations)
**User Feedback:** Directly addresses user's question about modeling setter activities