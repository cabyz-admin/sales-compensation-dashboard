"""
Visualizations module - All chart and visualization components
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import streamlit as st

class TimelineVisualizer:
    """Creates timeline and projection visualizations"""
    
    @staticmethod
    def create_revenue_timeline(df: pd.DataFrame, 
                               show_components: bool = True,
                               title: str = "Revenue Timeline") -> go.Figure:
        """Create month-by-month revenue visualization"""
        fig = go.Figure()
        
        # Add immediate revenue
        fig.add_trace(go.Bar(
            x=df['month'],
            y=df['immediate_revenue'],
            name='Immediate (70%)',
            marker_color='#2E86AB',
            text=df['immediate_revenue'].apply(lambda x: f'${x:,.0f}'),
            textposition='inside',
            hovertemplate='Month %{x}<br>Immediate: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add deferred revenue
        if 'deferred_revenue' in df.columns:
            fig.add_trace(go.Bar(
                x=df['month'],
                y=df['deferred_revenue'],
                name='Deferred (30%)',
                marker_color='#A23B72',
                text=df['deferred_revenue'].apply(lambda x: f'${x:,.0f}' if x > 0 else ''),
                textposition='inside',
                hovertemplate='Month %{x}<br>Deferred: $%{y:,.0f}<extra></extra>'
            ))
        
        # Add cumulative line
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['cumulative_revenue'],
            name='Cumulative',
            mode='lines+markers',
            line=dict(color='#F18F01', width=3),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate='Month %{x}<br>Cumulative: $%{y:,.0f}<extra></extra>'
        ))
        
        # Add vertical line at month 18
        fig.add_vline(x=18, line_dash="dash", line_color="red", opacity=0.5,
                     annotation_text="Deferred payments start")
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Month",
            yaxis_title="Monthly Revenue ($)",
            yaxis2=dict(
                title="Cumulative Revenue ($)",
                overlaying='y',
                side='right'
            ),
            barmode='stack',
            height=400,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add quarterly markers
        for q in range(1, int(df['month'].max() / 3) + 1):
            month = q * 3
            if month <= df['month'].max():
                fig.add_vline(x=month, line_dash="dot", line_color="gray", opacity=0.3)
                fig.add_annotation(x=month, y=0, text=f"Q{q}", showarrow=False, yshift=-20)
        
        return fig
    
    @staticmethod
    def create_daily_weekly_monthly_view(monthly_value: float, 
                                        working_days: int = 20) -> Dict[str, go.Figure]:
        """Create daily, weekly, and monthly target visualizations"""
        daily_value = monthly_value / working_days
        weekly_value = monthly_value / 4
        
        # Daily view
        daily_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = daily_value,
            title = {'text': "Daily Target"},
            delta = {'reference': daily_value * 0.9},
            gauge = {'axis': {'range': [0, daily_value * 1.5]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, daily_value * 0.8], 'color': "lightgray"},
                        {'range': [daily_value * 0.8, daily_value * 1.2], 'color': "gray"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': daily_value}}
        ))
        
        # Weekly view
        weekly_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = weekly_value,
            title = {'text': "Weekly Target"},
            delta = {'reference': weekly_value * 0.9},
            gauge = {'axis': {'range': [0, weekly_value * 1.5]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, weekly_value * 0.8], 'color': "lightgray"},
                        {'range': [weekly_value * 0.8, weekly_value * 1.2], 'color': "gray"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': weekly_value}}
        ))
        
        # Monthly view
        monthly_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = monthly_value,
            title = {'text': "Monthly Target"},
            delta = {'reference': monthly_value * 0.9},
            gauge = {'axis': {'range': [0, monthly_value * 1.5]},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, monthly_value * 0.8], 'color': "lightgray"},
                        {'range': [monthly_value * 0.8, monthly_value * 1.2], 'color': "gray"}],
                    'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': monthly_value}}
        ))
        
        for fig in [daily_fig, weekly_fig, monthly_fig]:
            fig.update_layout(height=250)
        
        return {
            'daily': daily_fig,
            'weekly': weekly_fig,
            'monthly': monthly_fig
        }


class FunnelVisualizer:
    """Creates funnel and pipeline visualizations"""
    
    @staticmethod
    def create_funnel_chart(metrics: Dict[str, float]) -> go.Figure:
        """Create funnel visualization"""
        stages = ['Leads', 'Contacts', 'Meetings', 'Sales', 'Onboarded']
        values = [
            metrics.get('leads', 0),
            metrics.get('contacts', 0),
            metrics.get('meetings', 0),
            metrics.get('sales', 0),
            metrics.get('onboarded', 0)
        ]
        
        fig = go.Figure(go.Funnel(
            y = stages,
            x = values,
            textposition = "inside",
            textinfo = "value+percent initial",
            opacity = 0.8,
            marker = {
                "color": ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"],
                "line": {"width": 2, "color": "white"}
            },
            connector = {"line": {"color": "royalblue", "dash": "dot", "width": 3}}
        ))
        
        fig.update_layout(
            title="Sales Funnel",
            height=400,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_pipeline_coverage_chart(pipeline_data: Dict[str, float]) -> go.Figure:
        """Create pipeline coverage visualization"""
        categories = ['Required', 'Current Pipeline', 'Gap']
        
        required = pipeline_data.get('pipeline_value_needed', 0)
        current = pipeline_data.get('current_pipeline', required * 0.8)  # Example
        gap = max(0, required - current)
        
        fig = go.Figure(data=[
            go.Bar(name='Required', x=categories[:1], y=[required], marker_color='lightgray'),
            go.Bar(name='Current', x=categories[1:2], y=[current], 
                  marker_color='green' if current >= required else 'orange'),
            go.Bar(name='Gap', x=categories[2:], y=[gap], 
                  marker_color='red' if gap > 0 else 'green')
        ])
        
        # Add coverage ratio line
        coverage_ratio = current / required if required > 0 else 0
        fig.add_hline(y=required, line_dash="dash", line_color="blue", 
                     annotation_text=f"Coverage: {coverage_ratio:.1f}x")
        
        fig.update_layout(
            title="Pipeline Coverage Analysis",
            yaxis_title="Pipeline Value ($)",
            showlegend=True,
            height=350
        )
        
        return fig


class TeamVisualizer:
    """Creates team and capacity visualizations"""
    
    @staticmethod
    def create_capacity_utilization(capacity_data: Dict[str, float], 
                                   actual_data: Dict[str, float]) -> go.Figure:
        """Create capacity utilization chart"""
        categories = ['Meetings', 'Contacts']
        capacity = [
            capacity_data.get('closer_capacity_meetings', 0),
            capacity_data.get('setter_capacity_contacts', 0)
        ]
        actual = [
            actual_data.get('actual_meetings', 0),
            actual_data.get('actual_contacts', 0)
        ]
        
        utilization = [a/c * 100 if c > 0 else 0 for a, c in zip(actual, capacity)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Capacity',
            x=categories,
            y=capacity,
            marker_color='lightgray',
            text=[f'{c:,.0f}' for c in capacity],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            name='Actual',
            x=categories,
            y=actual,
            marker_color=['green' if u >= 80 else 'orange' if u >= 60 else 'red' 
                         for u in utilization],
            text=[f'{a:,.0f}<br>({u:.0f}%)' for a, u in zip(actual, utilization)],
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Team Capacity Utilization",
            yaxis_title="Volume",
            barmode='overlay',
            height=350,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_ramp_visualization(ramp_df: pd.DataFrame) -> go.Figure:
        """Visualize ramping schedule"""
        fig = go.Figure()
        
        # Add productivity curve
        fig.add_trace(go.Scatter(
            x=ramp_df['month'],
            y=ramp_df['productivity'] * 100,
            name='Productivity %',
            mode='lines+markers',
            line=dict(color='blue', width=3),
            marker=dict(size=10),
            text=[f'{p:.0%}' for p in ramp_df['productivity']],
            textposition='top center'
        ))
        
        # Add effective capacity
        fig.add_trace(go.Bar(
            x=ramp_df['month'],
            y=ramp_df['effective_capacity'],
            name='Effective Capacity',
            marker_color='lightblue',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Ramp-up Schedule",
            xaxis_title="Month",
            yaxis_title="Productivity %",
            yaxis2=dict(
                title="Effective Capacity",
                overlaying='y',
                side='right'
            ),
            height=350,
            hovermode='x'
        )
        
        return fig


class MetricsVisualizer:
    """Creates metrics and KPI visualizations"""
    
    @staticmethod
    def create_health_scorecard(metrics: Dict[str, any]) -> go.Figure:
        """Create health scorecard visualization"""
        categories = ['LTV:CAC', 'EBITDA Margin', 'Pipeline Coverage', 'Team Utilization', 'OTE Health']
        
        # Example scores (0-100)
        scores = [
            min(100, metrics.get('ltv_cac_ratio', 3) / 5 * 100),  # Target 5:1
            min(100, metrics.get('ebitda_margin', 0.25) / 0.30 * 100),  # Target 30%
            min(100, metrics.get('pipeline_coverage', 3) / 4 * 100),  # Target 4x
            metrics.get('team_utilization', 75),  # Target 75%
            metrics.get('ote_health_score', 80)  # Target 80%
        ]
        
        colors = ['green' if s >= 80 else 'orange' if s >= 60 else 'red' for s in scores]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            marker_color=colors[0]  # Use first color as primary
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            title="Business Health Scorecard",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_attainment_distribution(attainment_data: List[float]) -> go.Figure:
        """Create attainment distribution chart"""
        fig = go.Figure()
        
        # Create histogram
        fig.add_trace(go.Histogram(
            x=attainment_data,
            nbinsx=20,
            name='Rep Distribution',
            marker_color='blue',
            opacity=0.7
        ))
        
        # Add tier boundaries
        for tier in ['tier_1', 'tier_2', 'tier_3', 'tier_4', 'tier_5']:
            from modules.config import config
            tier_data = config.ATTAINMENT_TIERS[tier]
            if tier_data['max'] < 10:  # Don't show unrealistic max
                fig.add_vline(
                    x=tier_data['max'] * 100,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=tier_data['name']
                )
        
        fig.update_layout(
            title="Attainment Distribution",
            xaxis_title="Attainment %",
            yaxis_title="Number of Reps",
            height=350,
            showlegend=True
        )
        
        return fig


class ComparisonVisualizer:
    """Creates comparison and scenario visualizations"""
    
    @staticmethod
    def create_scenario_comparison(scenarios: Dict[str, Dict]) -> go.Figure:
        """Compare multiple scenarios side by side"""
        metrics = ['Revenue', 'EBITDA', 'LTV:CAC', 'Headcount']
        
        fig = go.Figure()
        
        for scenario_name, scenario_data in scenarios.items():
            values = [
                scenario_data.get('revenue', 0),
                scenario_data.get('ebitda', 0),
                scenario_data.get('ltv_cac', 0),
                scenario_data.get('headcount', 0)
            ]
            
            fig.add_trace(go.Bar(
                name=scenario_name,
                x=metrics,
                y=values,
                text=[f'{v:,.0f}' if i < 2 else f'{v:.1f}' if i == 2 else f'{v:.0f}' 
                     for i, v in enumerate(values)],
                textposition='outside'
            ))
        
        fig.update_layout(
            title="Scenario Comparison",
            barmode='group',
            height=400,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_sensitivity_analysis(base_value: float, 
                                   variable_name: str,
                                   impact_data: Dict[float, float]) -> go.Figure:
        """Create sensitivity analysis chart"""
        changes = list(impact_data.keys())
        impacts = list(impact_data.values())
        
        colors = ['green' if i > base_value else 'red' if i < base_value else 'gray' 
                 for i in impacts]
        
        fig = go.Figure(go.Waterfall(
            name = "Sensitivity",
            orientation = "v",
            x = [f"{variable_name} {c:+.0%}" for c in changes],
            y = [i - base_value for i in impacts],
            text = [f"${i:,.0f}" for i in impacts],
            textposition = "outside",
            connector = {"line": {"color": "rgb(63, 63, 63)"}},
            increasing = {"marker": {"color": "green"}},
            decreasing = {"marker": {"color": "red"}},
            totals = {"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title=f"Sensitivity Analysis: {variable_name}",
            yaxis_title="Impact on EBITDA",
            height=400,
            showlegend=False
        )
        
        return fig
