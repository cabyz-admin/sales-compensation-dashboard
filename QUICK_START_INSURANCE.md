# Quick Start Guide - Insurance RevOps Model

## 🎯 Your Business (Based on Our Conversation)

**Business Model:** Insurance agency/broker (RevOps consulting)
- **Product:** Long-term insurance policies (25-year contracts)
- **Customer Premium:** $2,000 MXN/month minimum
- **Your Commission:** 2.7% of total premium value (one-time payment)
- **Payment Terms:** 70% upfront, 30% after 18 months
- **Currency:** MXN (dashboard is currency-agnostic)

**Team Structure (Commission-Only):**
- 8 Closers @ 10% commission (on upfront cash only)
- 2 Part-time Setters @ 5% commission
- 1 Manager (Luis) @ 3% commission

**GTM Strategy:**
- Month 3 Target: $30,000 MXN/month marketing budget
- Cost per meeting: $100 MXN (optimizing down to $80)
- Target close rate: 12% → 15% → 20% (3mo → 6mo → 12mo)
- Goal: 100 sales/month by month 12

---

## 🚀 How to Use the Dashboard (NEW Fixed Version)

### **Step 1: Load Your Insurance Template**

1. Open dashboard: `streamlit run dashboards/production/dashboard_fast.py`
2. Navigate to **Tab 5: Configuration**
3. In "Quick Start Templates" section:
   - Select: **"Insurance (Long-term)"**
   - Click: **"📋 Load Template"**
   - Template pre-fills: $2,000 MXN premium, 2.7% commission, 25 years

### **Step 2: Customize Your Numbers**

The calculator section now shows your insurance inputs:

**Calculator Inputs:**
- **Monthly Premium:** `2000` (MXN)
- **Commission Rate:** `2.7` (%)
- **Contract Term:** `25` (years)

**📊 Calculated Values (Preview):**
- Total Premium: $600,000 MXN
- Your Commission: **$16,200 MXN** ← This is your deal value
- Contract Length: 300 months

**IMPORTANT:** These are just PREVIEWS until you click Apply!

### **Step 3: Apply Calculator Values**

Click the big blue button: **"✅ Apply Calculator Values"**

This commits:
- `avg_deal_value = $16,200 MXN`
- `contract_length_months = 300`

You'll see: ✅ Deal value set to $16,200!

### **Step 4: Set Payment Terms**

**Payment Terms section:**
- **Upfront Payment %:** Slide to `70%`
  - Upfront: $11,340 MXN (70%)
  - Deferred: $4,860 MXN (30%)
- **Deferred Payment Month:** `18` (after 18 months)

**Commission Policy:**
- Select: **"Upfront Cash Only"**
  - Commission Base: $11,340 MXN
  - This is what your team gets paid on

**Government Costs:**
- Set to: `0%` (you don't have government fees)

**Revenue Retention (GRR):**
- Set to: `95%` (5% churn on deferred payments)

### **Step 5: Configure Your Team**

Scroll to **"👥 Team Structure"** section:

**Headcount:**
- Closers: `8`
- Setters: `2`
- Managers: `1`
- Bench: `0`

**Closer Compensation:**
- Base Salary: `0` (commission-only)
- Variable/OTE: `0`
- Commission %: `10`
  - Per deal: $11,340 × 10% = **$1,134 MXN**

**Setter Compensation:**
- Base Salary: `0`
- Variable/OTE: `0`
- Commission %: `5`
  - Per deal: $11,340 × 5% = **$567 MXN**

**Manager Compensation:**
- Base Salary: `0`
- Variable/OTE: `0`
- Commission %: `3`
  - Per deal: $11,340 × 3% = **$340 MXN**

**Total payout per deal:** $1,134 + $567 + $340 = **$2,041 MXN** (18% of upfront cash)

### **Step 6: Set Operating Costs**

**💰 Operating Costs (Monthly):**
- Office Rent: `15000` MXN
- Software: `12000` MXN
- Other OpEx: `8000` MXN
- **Total:** `35000` MXN/month

### **Step 7: Configure GTM Channel**

Go to **Tab 1: GTM & Funnel** (or stay in Tab 5 GTM section)

**Channel Configuration:**
- **Cost Method:** Select **"Cost per Meeting"**
- **Monthly Budget:** `30000` MXN (Month 3 target)
- **Cost per Meeting:** `100` MXN
- **Meetings scheduled:** 300 (auto-calculated: $30K ÷ $100)

**Conversion Rates:**
- **Contact Rate:** `1.0` (100% - you're buying meetings, not leads)
- **Meeting Rate:** `1.0` (100%)
- **Show-up Rate:** `0.6` (60%)
- **Close Rate:** `0.12` (12% for Month 3)

**Expected Results (Month 3):**
- 300 meetings scheduled
- 180 meetings held (60% show-up)
- **~22 deals closed** (12% close rate)

---

## 📊 What You Should See Across Tabs

### **Tab 1: GTM Metrics**
- Monthly meetings held: **180**
- Monthly sales: **22 deals**
- Marketing spend: **$30,000 MXN**
- Cost per sale (CPA): **~$1,364 MXN**
- Blended close rate: **12%**

### **Tab 2: Compensation**
- **Closer pool:** $24,948 MXN/month (22 deals × $1,134)
- **Setter pool:** $12,474 MXN/month (22 deals × $567)
- **Manager pool:** $7,480 MXN/month (22 deals × $340)
- **Total commissions:** $44,902 MXN/month (18% of upfront revenue)

**Per-Person Earnings:**
- Average Closer: ~$3,118 MXN/month (24,948 ÷ 8)
- Average Setter: ~$6,237 MXN/month (12,474 ÷ 2)
- Manager (Luis): ~$7,480 MXN/month

### **Tab 3: P&L & Unit Economics**

**Monthly P&L:**
- Gross Revenue: **$249,480 MXN** (22 deals × $11,340 upfront)
- COGS (Commissions): **$44,902 MXN** (18%)
- Gross Profit: **$204,578 MXN** (82% margin)
- Marketing: **$30,000 MXN**
- OpEx: **$35,000 MXN**
- **EBITDA: ~$139,578 MXN/month** (56% margin) 🔥

**Unit Economics:**
- **LTV:** $15,390 MXN
  - Upfront: $11,340
  - Deferred: $4,860 × 95% retention = $4,617
- **CAC:** $1,364 MXN
- **LTV:CAC Ratio:** **11.3x** 🚀 (Excellent! >3x is good)
- **Payback Period:** **0.5 months** (immediate since 70% upfront)
- **Magic Number:** TBD (needs 12-month data)

### **Tab 4: What-If Analysis**

Test scenarios:
- "What if I increase marketing to $50K/month?"
- "What if close rate improves to 15%?"
- "What if deal value increases to $18K?"

Sliders now work without crashing! ✅

### **Tab 5: Configuration**

Your current setup is saved here. You can:
- **Export Config:** Download JSON backup
- **Import Config:** Load saved configurations
- **Switch Calculators:** Try Subscription or Commission models

---

## 🎯 Month 3 → Month 6 → Month 12 Targets

### **Month 3 (Conservative Start)** ← YOU ARE HERE
- Budget: $30K MXN
- CPM: $100
- Meetings: 180 held
- Close rate: 12%
- **Deals: 22/month**
- **Revenue: $249K MXN/month**
- **EBITDA: $140K MXN/month**

### **Month 6 (Improving)**
To model this, go to Tab 1 and adjust:
- Increase budget to: $40K MXN
- Lower CPM to: $80 (optimized)
- Meetings: 350 held
- Close rate: 15%
- **Deals: 53/month**
- **Revenue: $601K MXN/month**
- **EBITDA: $420K MXN/month**

### **Month 12 (Target - 100 deals/month)**
To model this:
- Budget: $60K MXN
- CPM: $70 (economies of scale)
- Meetings: 600 held
- Close rate: 20%
- **Deals: 120/month** 🎯
- **Revenue: $1.36M MXN/month**
- **EBITDA: $1M MXN/month**

**Note:** To hit 100 deals EXACTLY, adjust close rate or meetings until you see "Monthly Sales: 100.0"

---

## 💡 Pro Tips

### **Tip #1: Currency Consistency**
Dashboard doesn't care about currency. Just stay consistent:
- All MXN values
- OR all USD values (convert at ~18 MXN/USD)
- DON'T mix currencies!

### **Tip #2: Testing Scenarios**
1. **Export your base config** (Tab 5 → Export)
2. Make changes in dashboard
3. Compare results
4. **Import base config** to reset

### **Tip #3: Refresh Button**
If numbers look stale after changing something:
1. Click **"🔄 Refresh Metrics"** (top of page)
2. All caches clear
3. Fresh calculations

### **Tip #4: Commission Policy Gotcha**
- **"Upfront Cash Only"** = Team gets paid on $11,340 (realistic for cash flow)
- **"Full Deal Value"** = Team gets paid on $16,200 (ignore deferred timing)

Most insurance agencies use "Upfront Cash Only" since you can't pay commissions on money you haven't received yet!

### **Tip #5: Adjust for Reality**
Your actual numbers will vary. Use the calculator to:
- Model different premium tiers ($1,500, $2,000, $3,000)
- Test commission rate changes (2.5%, 2.7%, 3.0%)
- Adjust close rates as you improve sales process

---

## 🐛 If Something Breaks

### **"Widget key collision" error:**
- Click **"🔄 Refresh Metrics"** first
- Then try your action again
- All widget keys are now isolated (should be rare)

### **Numbers don't update:**
1. Did you click **"✅ Apply Calculator Values"**?
2. Try **"🔄 Refresh Metrics"**
3. Check Tab 1 → are GTM inputs correct?

### **Template doesn't load:**
1. Make sure you selected a non-"Custom" option
2. Click **"📋 Load Template"** button
3. You should see success message
4. Calculator inputs should populate
5. **Don't forget to click Apply!**

---

## 📧 Questions?

This dashboard models YOUR business as discussed:
- ✅ Insurance commission structure (2.7% of premium)
- ✅ Long-term contracts (25 years)
- ✅ Commission-only team (8 closers, 2 setters, 1 manager)
- ✅ GTM via paid meetings (CPM model)
- ✅ Month 3 target (22 deals) → Month 12 target (100 deals)

**All bugs are now fixed!** The calculator system works properly with Apply buttons and no widget collisions.

Ready to model your RevOps business! 🚀
