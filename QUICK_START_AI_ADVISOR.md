# Quick Start: AI Strategic Advisor

**Version:** Dashboard v3.5.1
**Status:** ✅ READY TO USE

---

## 🚀 Getting Started (5 Minutes)

### Step 1: Get Your Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Click **API Keys** in the left sidebar
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-...`)

**Cost:** Each conversation costs $0.01-0.02 (very affordable!)

### Step 2: Launch Dashboard

```bash
cd /Users/castillo/CascadeProjects/comp-structure
streamlit run dashboards/production/dashboard_fast.py
```

### Step 3: Configure API Key

1. Navigate to **Tab 7: 🧠 AI Strategic Advisor**
2. Paste your API key in the input field
3. Click **"💾 Save API Key"**
4. Dashboard will refresh automatically

**Privacy Note:** API key stored in session state only (not saved to disk)

---

## 🎯 Three Ways to Use the AI Advisor

### 1. 🚀 One-Click Business Analysis

**What it does:**
- Analyzes ALL your dashboard metrics
- Provides A-F health grade
- Identifies top 3 growth constraints
- Suggests quick wins (next 30 days)
- Strategic recommendations (6-12 months)
- Flags concerning metrics

**How to use:**
1. Make sure your GTM metrics are set (Tab 1)
2. Go to Tab 7
3. Click **"🧠 Analyze My Business"**
4. Wait 10-20 seconds
5. Read comprehensive analysis

**Example Output:**
```markdown
## Health Check: B+ Grade

Your business shows strong unit economics (LTV:CAC 11.3x) but is
constrained by closer capacity at 68% utilization...

### Top 3 Constraints:

1. **Marketing Budget** (Impact: $340K/mo potential)
   - Current: $30K generating 182 meetings
   - Fix: Increase by $10K → add 100 meetings → unlock $340K

2. **Close Rate Below Optimal** (Impact: $150K/mo)
   - Current: 30% (optimal: 35-40% for insurance)
   - Fix: Implement sales coaching → improve 5% → add $150K

3. **Setter Capacity** (Impact: $200K/mo)
   - Current: 2 setters @ 100% utilization
   - Fix: Add 1 setter → increase meeting volume by 40%
```

---

### 2. 💬 Conversational Chat (NEW!)

**What's new in v3.5.1:**
- Full conversation history
- Follow-up questions
- Context awareness
- ChatGPT-like interface

**How to use:**
1. Type question in chat input at bottom of screen
2. Press Enter (no button needed!)
3. AI responds with analysis
4. Ask follow-up questions naturally
5. Click **"🗑️ Clear Chat History"** to reset

**Example Conversation:**

```
You: What's my biggest constraint right now?

AI: Based on your metrics, your biggest constraint is closer capacity.
    You have 8 closers at 68% utilization, which means they can handle
    25% more meetings. However, your marketing spend of $30K is only
    generating 182 meetings/month...

You: How much would it cost to fix that?

AI: To fix the closer capacity constraint:
    1. Increase marketing by $10K/month → +100 meetings
    2. After 2 months, hire 2 more closers at $5,670 OTE each

    Total investment:
    - Month 1-2: $10K/mo marketing (test phase)
    - Month 3+: $10K marketing + $11,340 team costs

    Expected return:
    - +30 deals/mo at $11,340 = $340K/mo revenue
    - ROI: 30x in first year

You: What if I improve close rate instead of increasing marketing?

AI: Improving close rate from 30% to 35% would:
    - Same 182 meetings
    - Generate 63.7 deals (up from 54.6)
    - Revenue: $722K (up from $619K)
    - Net increase: $103K/month

    This is lower than the marketing approach ($103K vs $340K) but
    requires zero investment. Recommendation: Do BOTH for maximum impact.
```

**Key Features:**
- Remembers previous questions
- Builds on earlier answers
- Compares options naturally
- Provides context-aware recommendations

---

### 3. 🔮 Scenario Analysis

**What it does:**
- Models specific changes
- Calculates expected impact
- Provides recommendations
- Identifies risks
- Suggests alternatives

**How to use:**
1. Type scenario in the input field
2. OR select example from dropdown
3. Click **"🔬 Analyze Scenario"**
4. Review impact analysis

**Example Scenarios:**

#### Scenario 1: "What if I double my marketing spend?"

**AI Response:**
```markdown
**Expected Impact:**
- Current: $30K → 54.6 deals
- Doubled: $60K → 109.2 deals
- Revenue: $619K → $1.24M (+$621K/mo)
- But... team capacity is only 72 deals/mo

**Recommendations:**
DON'T do this immediately. You'll hit capacity constraints.

Better approach:
1. Increase to $40K (+$10K) first
2. Hire 2 closers when utilization hits 85%
3. Once stable, increase to $60K
4. Hire 2 more closers again

**Risks:**
- Lead quality may drop at higher spend
- CPM may increase (diminishing returns)
- Team morale if utilization hits 100%
```

#### Scenario 2: "What if I switch to $3K base + 7% commission?"

**AI Response:**
```markdown
**Current Model:**
- $0 base + 10% commission
- OTE: $5,670/mo at 5 deals

**Proposed Model:**
- $3K base + 7% commission
- OTE: $6,967/mo at 5 deals (22% higher)

**Analysis:**
- **Retention:** Higher base = better retention
- **Cost:** +$1,297/closer/mo (+23%)
- **Margin Impact:** Gross margin drops 2.5%
- **Recruiting:** Easier to attract talent

**Recommendation:**
Consider a hybrid: $2K base + 8% commission
- OTE: $6,071/mo (+7% vs current)
- Better retention, lower cost increase
- Still attractive for recruiting
```

---

## 📋 Example Questions to Ask

### GTM & Marketing
- "What's the optimal marketing spend for my team size?"
- "How do I improve my CAC efficiency?"
- "Should I focus on volume or quality of leads?"
- "What channels should I invest in next?"

### Team & Hiring
- "How many closers do I need to hit $1M/mo?"
- "Should I hire closers or setters first?"
- "What's the ROI of hiring a sales manager?"
- "When should I add my first VP of Sales?"

### Compensation
- "Is my OTE structure competitive?"
- "Should I increase base or commission %?"
- "What accelerators should I add for >100% quota?"
- "How do I structure comp for a new market?"

### Unit Economics
- "How do I improve my LTV:CAC from 11x to 15x?"
- "Should I focus on ACV or retention?"
- "What's a healthy EBITDA margin target?"
- "How do I increase gross margin?"

### Strategy
- "What's my biggest growth bottleneck?"
- "How do I prioritize: hiring, marketing, or product?"
- "What should my 6-month roadmap be?"
- "How do I prepare for Series A?"

---

## 💡 Pro Tips

### 1. Start with One-Click Analysis
Run the full business analysis first, then use chat for follow-ups. This gives the AI maximum context.

### 2. Be Specific
Instead of: "Should I hire?"
Ask: "I have $50K budget and 70% utilization. Should I hire 2 closers now or wait 2 months?"

### 3. Use Chat for Comparisons
Ask about Option A, then immediately ask "What about Option B?" The AI will compare them naturally.

### 4. Reference Your Numbers
The AI sees all your dashboard metrics. Ask questions like:
- "With my current close rate..."
- "Given my marketing spend..."
- "Based on my OTE structure..."

### 5. Test Scenarios Before Implementing
Before making major changes, model them in the Scenario Analysis section.

---

## 🔧 Troubleshooting

### Issue: "Invalid API Key"
- Check key starts with `sk-ant-`
- No extra spaces when pasting
- Verify key is active in Anthropic Console
- Try regenerating the key

### Issue: "Rate Limit Exceeded"
- You're making too many requests (rare)
- Wait 60 seconds and try again
- Consider upgrading Anthropic plan if you use it heavily

### Issue: "Generic responses"
- Your metrics may be at default values
- Update inputs in Tab 1 (GTM Command Center)
- Set team data in Tab 5 (Configuration)
- Then re-run analysis

### Issue: Chat history not persisting
- This is expected - history clears when you close the browser
- Chat persists during active session only
- Use "Export" feature (coming in v3.6) to save conversations

---

## 📊 Cost Management

### Typical Usage Costs

**Per Request:**
- One-Click Analysis: ~$0.03
- Chat question: ~$0.017
- Scenario analysis: ~$0.02

**Monthly Budget Examples:**

**Light Usage:**
- 5 analyses/month: $0.15
- 10 questions/month: $0.17
- **Total: ~$0.32/month**

**Medium Usage:**
- 10 analyses/month: $0.30
- 50 questions/month: $0.85
- 10 scenarios/month: $0.20
- **Total: ~$1.35/month**

**Heavy Usage:**
- 20 analyses/month: $0.60
- 100 questions/month: $1.70
- 20 scenarios/month: $0.40
- **Total: ~$2.70/month**

**Even heavy usage is <$3/month!**

### Monitor Usage

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Click **Usage** in left sidebar
3. View token consumption by day
4. Set billing alerts if desired

---

## 🎓 Learning the System

### Day 1: Get Oriented
1. Run One-Click Analysis
2. Read the output carefully
3. Ask 2-3 clarifying questions in chat

### Week 1: Explore
1. Test different scenarios
2. Ask questions about each tab's metrics
3. Compare different strategies

### Month 1: Master It
1. Use for monthly business reviews
2. Model hiring decisions
3. Optimize comp structures
4. Prepare investor updates

---

## 🚀 Next Steps

1. **Right Now:** Get your API key and run your first analysis
2. **This Week:** Ask 10+ strategic questions to understand your constraints
3. **This Month:** Use scenario analysis to model your growth plan
4. **Ongoing:** Monthly business reviews with AI insights

---

## 📚 Additional Resources

- **Full Documentation:** [AI_ADVISOR_v3.5.md](AI_ADVISOR_v3.5.md)
- **Fix Log:** [AI_ADVISOR_FIX_2025-11-12.md](AI_ADVISOR_FIX_2025-11-12.md)
- **OTE System:** [OTE_REFACTOR_v3.4.md](OTE_REFACTOR_v3.4.md)
- **Anthropic Docs:** [docs.anthropic.com](https://docs.anthropic.com)
- **Streamlit Chat:** [Chat App Tutorial](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)

---

## Summary

The AI Strategic Advisor gives you a **180 IQ strategic partner** that:
- ✅ Analyzes your entire business in seconds
- ✅ Answers complex strategic questions
- ✅ Models scenarios before you commit
- ✅ Provides specific, actionable recommendations
- ✅ Costs less than $3/month even with heavy use

**Get started now:** Open Tab 7 and paste your API key!

---

**Version:** Dashboard v3.5.1
**Last Updated:** 2025-11-12
**Status:** ✅ Production Ready