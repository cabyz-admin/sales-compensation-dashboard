# Quick Start Guide - Updated Dashboard
## Using the Fixed Sales Compensation Dashboard

---

## 🚀 What's New

The dashboard has been **fixed** to properly use your Deal Economics and Payment Terms configuration. No more hardcoded values!

### Key Improvements:
✅ Commission Flow now uses YOUR deal economics  
✅ Total Compensation Summary reflects YOUR payment terms  
✅ New Commission Policy selector (upfront vs full deal)  
✅ All calculations update in real-time  

---

## 📋 How to Use

### Step 1: Configure Deal Economics

1. **Expand the "Deal Economics & Payment Terms" section**
2. **Choose your business type** (or Custom):
   - Insurance: Auto-calculates from premium × years × carrier rate
   - SaaS: Uses MRR × contract length
   - Consulting: Project value
   - Custom: Manual entry

3. **Set your payment terms**:
   - **Upfront Payment %**: What you receive immediately (default: 70%)
   - **Deferred Payment %**: What you receive later (auto-calculated)
   - **Deferred Timing**: When deferred payment comes (e.g., 18 months)

4. **Choose Commission Policy**:
   - **Upfront Cash Only**: Pay commissions on upfront portion only
     - Example: $100K deal with 70% upfront → commissions on $70K
   - **Full Deal Value**: Pay commissions on entire deal value
     - Example: $100K deal → commissions on $100K

---

### Step 2: View Commission Flow

**Location**: Compensation Structure tab → Commission Flow Visualization

**What you'll see**:
- **Per Deal view**: How commissions split for ONE deal
- **Monthly Total view**: Total commissions for the month

**Key metrics**:
- Deal Value (what you configured)
- Commission Base (based on your policy)
- Commission pools per role (Closer, Setter, Manager)
- Per-person amounts

**Toggle between views** to see both unit economics and monthly totals.

---

### Step 3: Check Period Earnings

**Location**: Compensation Structure tab → Period-Based Earnings Preview

**What you'll see**:
- Daily, Weekly, Monthly, Annual earnings per role
- Base salary + commission combined
- vs OTE % (how close to hitting targets)

**This updates automatically** when you change:
- Deal value
- Payment terms
- Commission policy
- Team size

---

## 🎯 Common Scenarios

### Scenario 1: Insurance Business (Like Allianz)

```
Business Type: Insurance
Monthly Premium: $3,000 MXN
Contract Years: 18
Carrier Rate: 2.7%
```

**Result**:
- Auto-calculates deal value: $3,000 × 18 × 12 × 2.7% = ~$17,500
- Default split: 70% upfront, 30% deferred at 18 months
- Commission policy: Upfront Cash Only recommended

**Commission Flow shows**:
- Upfront: $12,250 (70% of $17,500)
- Commission base: $12,250
- Closer gets: $2,450 (20% of $12,250)

---

### Scenario 2: SaaS Subscription

```
Business Type: SaaS/Subscription
Monthly MRR: $5,000
Contract Length: 12 months
```

**Result**:
- Auto-calculates ACV: $5,000 × 12 = $60,000
- Default split: 60% upfront, 40% monthly residuals
- Commission policy: Upfront Cash Only recommended

**Commission Flow shows**:
- Upfront: $36,000 (60% of $60,000)
- Commission base: $36,000
- Closer gets: $7,200 (20% of $36,000)

---

### Scenario 3: Consulting Services

```
Business Type: Consulting/Services
Project Value: $100,000
Project Duration: 3 months
```

**Result**:
- Deal value: $100,000
- Default split: 50% deposit, 50% on completion
- Commission policy: Full Deal Value (you choose)

**With Full Deal Value**:
- Commission base: $100,000
- Closer gets: $20,000 (20% of $100,000)

**With Upfront Only**:
- Commission base: $50,000
- Closer gets: $10,000 (20% of $50,000)

---

## 🔍 Verify It's Working

### Test 1: Change Deal Value
1. Go to Deal Economics
2. Change deal value from $50K to $100K
3. **Look at Commission Flow** → Should show 2x higher amounts ✅
4. **Look at Period Earnings** → Monthly should be 2x higher ✅

### Test 2: Change Payment Terms
1. Change upfront % from 70% to 50%
2. Keep Commission Policy on "Upfront Cash Only"
3. **Look at Commission Flow** → Should show lower commissions ✅
4. Revenue box should show $25K instead of $35K ✅

### Test 3: Commission Policy
1. Set deal at $100K, upfront 60%, commission 20%
2. Policy = "Upfront Only" → Shows $12K commission ✅
3. Change to "Full Deal" → Shows $20K commission ✅

---

## 🎨 Visual Guide

### Commission Flow Diagram

```
┌─────────────────┐
│  Deal Value     │  ← Your input from Deal Economics
│    $100,000     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Commission Base │  ← Based on your policy choice
│    $70,000      │     (Upfront 70% in this case)
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌────────┐ ┌───────┐ ┌─────────┐
│Closer  │ │Setter │ │Manager  │  ← Commission % from role config
│$14,000 │ │$2,100 │ │$3,500   │     (20%, 3%, 5% in this case)
└───┬────┘ └───┬───┘ └────┬────┘
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌───────┐ ┌─────────┐
│Per     │ │Per    │ │Per      │  ← Divided by team count
│Closer  │ │Setter │ │Manager  │
│$1,750  │ │$525   │ │$1,750   │     (8, 4, 2 in this case)
└────────┘ └───────┘ └─────────┘
```

---

## 💡 Pro Tips

### Tip 1: Use Business Type Templates
Instead of manually entering everything, select a template:
- **Insurance**: Auto-calculates from premium/years/rate
- **SaaS**: Auto-calculates from MRR/contract
- **Consulting**: Just enter project value

Templates set sensible defaults for payment terms!

### Tip 2: Commission Policy Matters
Choose based on your cash flow:
- **Upfront Only**: Conservative, matches cash received
- **Full Deal**: Aggressive, incentivizes larger deals

Example: $100K deal, 60% upfront
- Upfront Only: Pay $12K commission (20% of $60K)
- Full Deal: Pay $20K commission (20% of $100K)

**You pay more with Full Deal but incentivize bigger contracts!**

### Tip 3: Watch the vs OTE Column
In Period Earnings table:
- **100% vs OTE** = Team is hitting targets ✅
- **<80% vs OTE** = Team underperforming ⚠️
- **>120% vs OTE** = Team crushing it 🚀

This updates as you change commission policy!

---

## 🚨 Troubleshooting

### Issue: "Commission Flow shows wrong numbers"

**Solution**: 
1. Check that you've configured Deal Economics section
2. Verify your commission policy selection
3. Ensure team configuration has commission % set per role

### Issue: "Numbers don't update when I change deal value"

**Solution**:
1. Make sure you're using the inputs in Deal Economics section (not legacy sidebar)
2. Give Streamlit a second to recalculate
3. Try toggling between "Per Deal" and "Monthly Total" views

### Issue: "Not sure which commission policy to use"

**Decision Guide**:
- **Cash flow tight?** → Use "Upfront Cash Only"
- **Want to incentivize big deals?** → Use "Full Deal Value"
- **Deferred payment certain?** → Use "Full Deal Value"
- **Deferred payment uncertain?** → Use "Upfront Cash Only"

---

## 📚 Understanding the Math

### Revenue Calculation
```python
# Example: $100K deal, 70% upfront
Upfront Revenue = $100,000 × 70% = $70,000
Deferred Revenue = $100,000 × 30% = $30,000

# Month 1
Total Revenue = $70,000 (upfront only)

# Month 18 (when deferred comes)
Total Revenue = $70,000 (new upfront) + $30,000 (old deferred)
```

### Commission Calculation
```python
# Commission Policy: Upfront Only
Commission Base = Upfront Revenue = $70,000
Closer Commission = $70,000 × 20% = $14,000

# Commission Policy: Full Deal
Commission Base = Full Deal Value = $100,000
Closer Commission = $100,000 × 20% = $20,000
```

### Period Earnings
```python
# Example: Closer with $4,000 base, $14,000 monthly commission

Monthly = $4,000 (base) + $14,000 (comm) = $18,000
Weekly = $18,000 ÷ 4.33 = $4,157
Daily = $18,000 ÷ 20 working days = $900
Annual = $18,000 × 12 = $216,000

vs OTE = $18,000 / $6,667 OTE = 270% 🚀
```

---

## ✅ Checklist

Before running scenarios, ensure:
- [ ] Deal Economics configured with your business model
- [ ] Payment terms set (upfront % and timing)
- [ ] Commission policy selected
- [ ] Team configuration has commission % per role
- [ ] Role counts are accurate

Then verify:
- [ ] Commission Flow shows correct amounts
- [ ] Period Earnings reflect your inputs
- [ ] vs OTE percentages make sense
- [ ] Changing inputs updates all sections

---

## 🎯 Next Steps

Once you've verified everything works:

1. **Save your configuration** using the Export Config button
2. **Test different scenarios** (growth, profit focus, etc.)
3. **Share with stakeholders** - all math is now correct!
4. **Use for planning** - accurate compensation forecasting

---

*For detailed technical information, see `DASHBOARD_10X_IMPROVEMENT_PLAN.md` and `FIXES_APPLIED.md`*
