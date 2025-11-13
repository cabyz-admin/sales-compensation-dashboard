"""
AI Strategic Advisor using Claude API
Provides strategic analysis and recommendations based on dashboard metrics
"""

import anthropic
import json
from typing import Dict, Optional


class StrategyAdvisor:
    """
    AI-powered strategic advisor for GTM, unit economics, and team performance.
    Uses Claude Sonnet 4.5 for high-quality strategic analysis.
    """

    def __init__(self, api_key: str):
        """Initialize with Anthropic API key"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def analyze_business_health(self, metrics: Dict) -> str:
        """
        Comprehensive business health analysis.

        Args:
            metrics: Dictionary containing all dashboard metrics

        Returns:
            Markdown-formatted strategic analysis
        """

        prompt = self._build_health_analysis_prompt(metrics)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"❌ **Error analyzing business:** {str(e)}\n\nPlease check your API key configuration."

    def ask_question(self, question: str, metrics: Dict, context: Optional[str] = None) -> str:
        """
        Answer a specific strategic question about the business.

        Args:
            question: User's question
            metrics: Current dashboard metrics
            context: Optional context from previous analysis

        Returns:
            Answer with strategic recommendations
        """

        prompt = self._build_question_prompt(question, metrics, context)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def scenario_analysis(self, scenario: str, metrics: Dict) -> str:
        """
        Analyze a specific scenario (e.g., "What if I double marketing spend?")

        Args:
            scenario: Scenario description
            metrics: Current metrics

        Returns:
            Analysis of scenario impact
        """

        prompt = f"""You are a world-class GTM and unit economics strategist with 180 IQ.

**Current Business Metrics:**
{self._format_metrics_concise(metrics)}

**Scenario to Analyze:**
{scenario}

Provide:
1. **Expected Impact**: What would change?
2. **Recommendations**: Should they do this?
3. **Risks**: What could go wrong?
4. **Alternatives**: Are there better options?

Be specific with numbers. Use the metrics provided to calculate expected outcomes.
"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            return f"❌ **Error:** {str(e)}"

    def _build_health_analysis_prompt(self, metrics: Dict) -> str:
        """Build comprehensive health analysis prompt"""

        # Extract key metrics
        ltv_cac = metrics.get('ltv_cac_ratio', 0)
        payback_months = metrics.get('payback_months', 0)
        gross_margin = metrics.get('gross_margin_pct', 0)
        ebitda_margin = metrics.get('ebitda_margin_pct', 0)
        monthly_revenue = metrics.get('monthly_revenue', 0)
        monthly_sales = metrics.get('monthly_sales', 0)
        close_rate = metrics.get('close_rate_pct', 0)
        cac = metrics.get('cac', 0)
        marketing_spend = metrics.get('marketing_spend', 0)

        # Team metrics
        num_closers = metrics.get('num_closers', 0)
        num_setters = metrics.get('num_setters', 0)
        deals_per_closer = metrics.get('deals_per_closer', 0)
        closer_utilization = metrics.get('closer_utilization', 0)

        # OTE metrics
        closer_ote_attainment = metrics.get('closer_ote_attainment', 0)
        setter_ote_attainment = metrics.get('setter_ote_attainment', 0)
        team_avg_attainment = metrics.get('team_avg_attainment', 0)

        prompt = f"""You are a world-class GTM, unit economics, and sales operations strategist with 180 IQ. You have deep expertise in:
- SaaS/Insurance revenue models
- Sales team optimization
- Unit economics and LTV:CAC ratios
- Marketing efficiency
- Compensation structures
- Growth strategy

Analyze this business and provide strategic recommendations.

## Business Metrics

**Unit Economics:**
- LTV:CAC Ratio: {ltv_cac:.1f}x
- CAC: ${cac:,.0f}
- Payback Period: {payback_months:.1f} months
- Gross Margin: {gross_margin:.1f}%
- EBITDA Margin: {ebitda_margin:.1f}%

**Revenue & Sales:**
- Monthly Revenue: ${monthly_revenue:,.0f}
- Monthly Sales: {monthly_sales:.1f} deals
- Close Rate: {close_rate:.1f}%
- Marketing Spend: ${marketing_spend:,.0f}

**Team Performance:**
- Closers: {num_closers} @ {deals_per_closer:.1f} deals each
- Setters: {num_setters}
- Closer Utilization: {closer_utilization:.0f}%

**OTE Tracking:**
- Closer OTE Attainment: {closer_ote_attainment:.0f}%
- Setter OTE Attainment: {setter_ote_attainment:.0f}%
- Team Avg Attainment: {team_avg_attainment:.0f}%

## Analysis Required

Provide a comprehensive strategic analysis with:

### 1. **Health Check** (A-F Grade)
Rate overall business health. Consider:
- Unit economics (LTV:CAC, payback)
- Margins (gross, EBITDA)
- Team efficiency (utilization, OTE attainment)
- Growth potential

### 2. **Top 3 Constraints**
What's limiting growth? Be specific:
- Is it team capacity?
- Marketing budget?
- Conversion rates?
- Comp structure?

For each constraint, explain:
- Why it's a bottleneck
- Impact on revenue ($)
- How to fix it

### 3. **Quick Wins** (Next 30 Days)
3 tactical improvements with:
- What to do (specific action)
- Expected impact ($ or %)
- Effort required (Low/Medium/High)
- Why this will work

### 4. **Strategic Recommendations** (6-12 Months)
Long-term strategy:
- Hiring plan (how many, which roles)
- Marketing scaling ($ spend, expected ROI)
- Comp structure changes
- Process improvements

Be specific with numbers. Use the metrics to calculate expected outcomes.

### 5. **Red Flags** 🚨
Any concerning metrics? What could go wrong?

### 6. **Competitive Positioning**
How does this compare to industry benchmarks?
- LTV:CAC (target: >3x)
- Payback (target: <12 months)
- Close rate (typical: 20-30%)
- Team efficiency

Use markdown formatting. Be direct and actionable. Focus on insights, not just restating the numbers.
"""

        return prompt

    def _build_question_prompt(self, question: str, metrics: Dict, context: Optional[str] = None) -> str:
        """Build prompt for answering specific questions"""

        prompt = f"""You are a world-class GTM and unit economics strategist with 180 IQ.

**Business Context:**
{self._format_metrics_concise(metrics)}

{"**Previous Analysis:**" + context if context else ""}

**Question:**
{question}

Provide a strategic answer with:
1. Direct answer to the question
2. Specific recommendations with numbers
3. Trade-offs to consider
4. Next steps

Be concise but thorough. Use the metrics to support your answer.
"""

        return prompt

    def _format_metrics_concise(self, metrics: Dict) -> str:
        """Format metrics in concise bullet format"""

        return f"""
- Monthly Revenue: ${metrics.get('monthly_revenue', 0):,.0f}
- Monthly Sales: {metrics.get('monthly_sales', 0):.0f} deals
- LTV:CAC: {metrics.get('ltv_cac_ratio', 0):.1f}x
- CAC: ${metrics.get('cac', 0):,.0f}
- Payback: {metrics.get('payback_months', 0):.1f} months
- Close Rate: {metrics.get('close_rate_pct', 0):.1f}%
- Team: {metrics.get('num_closers', 0)} closers, {metrics.get('num_setters', 0)} setters
- Deals/Closer: {metrics.get('deals_per_closer', 0):.1f}
- Utilization: {metrics.get('closer_utilization', 0):.0f}%
- Marketing: ${metrics.get('marketing_spend', 0):,.0f}/mo
"""

    @staticmethod
    def format_for_display(analysis: str) -> str:
        """Format analysis for Streamlit display"""
        # Already in markdown, can enhance if needed
        return analysis
