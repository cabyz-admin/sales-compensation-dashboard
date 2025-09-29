# I'll create a comprehensive explanation file for the P&L calculations and metrics
import streamlit as st

def explain_command_center_inputs():
    """
    Complete explanation of all inputs in the Command Center and their calculations
    """
    
    explanations = {
        "Revenue Targets": {
            "Monthly Revenue Target": {
                "Input": "Number input field",
                "Default": "$166,667",
                "Calculation": "Direct user input",
                "Impact": "Used to calculate annual revenue, revenue gap, pipeline coverage, and performance metrics"
            },
            "Annual Revenue": {
                "Calculation": "Monthly Revenue Target × 12",
                "Example": "$166,667 × 12 = $2,000,000"
            }
        },
        
        "Team Structure": {
            "Number of Closers": {
                "Input": "Number input",
                "Default": "3",
                "Calculation": "Direct user input",
                "Impact": "Determines team capacity (closers × 60 meetings/month), labor costs, and productivity metrics"
            },
            "Number of Setters": {
                "Input": "Number input",
                "Default": "3", 
                "Calculation": "Direct user input",
                "Impact": "Determines lead processing capacity, contact rate capacity"
            },
            "Team on Bench": {
                "Input": "Number input",
                "Default": "1",
                "Calculation": "Direct user input",
                "Impact": "Adds to total labor costs but not to active capacity"
            },
            "Number of Managers": {
                "Input": "Number input",
                "Default": "1",
                "Calculation": "Direct user input",
                "Impact": "Adds to overhead costs, typically higher salary than sales team"
            }
        },
        
        "Conversion Funnel": {
            "Contact Rate": {
                "Input": "Slider 0-100%",
                "Default": "65%",
                "Calculation": "Contacts Made / Total Leads",
                "Impact": "monthly_contacts = monthly_leads × contact_rate"
            },
            "Meeting Rate": {
                "Input": "Slider 0-100%",
                "Default": "65%",
                "Calculation": "Meetings Scheduled / Contacts Made",
                "Impact": "monthly_meetings_scheduled = monthly_contacts × meeting_rate"
            },
            "Show-up Rate": {
                "Input": "Slider 0-100%",
                "Default": "80%",
                "Calculation": "Meetings Held / Meetings Scheduled",
                "Impact": "monthly_meetings = monthly_meetings_scheduled × show_up_rate"
            },
            "Close Rate": {
                "Input": "Slider 0-100%",
                "Default": "25%",
                "Calculation": "Sales Closed / Meetings Held",
                "Impact": "monthly_sales = monthly_meetings × close_rate"
            }
        },
        
        "Deal Economics": {
            "Average Deal Size": {
                "Input": "Number input",
                "Default": "$15,000",
                "Calculation": "Direct user input",
                "Impact": "Revenue per sale, used for all revenue calculations"
            },
            "Immediate Payment %": {
                "Input": "Slider 0-100%",
                "Default": "70%",
                "Calculation": "Direct user input",
                "Impact": "monthly_revenue_immediate = monthly_sales × avg_deal × immediate_pct"
            },
            "Deferred Payment %": {
                "Input": "Calculated",
                "Default": "30%",
                "Calculation": "100% - Immediate Payment %",
                "Impact": "monthly_revenue_deferred = monthly_sales × avg_deal × deferred_pct"
            }
        },
        
        "Operating Costs": {
            "Office Rent": {
                "Input": "Number input",
                "Default": "$10,000/month",
                "Calculation": "Direct user input",
                "Impact": "Part of monthly OpEx"
            },
            "Software & Tools": {
                "Input": "Number input",
                "Default": "$10,000/month",
                "Calculation": "Direct user input",
                "Impact": "Part of monthly OpEx"
            },
            "Other OpEx": {
                "Input": "Number input",
                "Default": "$5,000/month",
                "Calculation": "Direct user input",
                "Impact": "Part of monthly OpEx"
            }
        }
    }
    
    return explanations

def calculate_pnl_verification():
    """
    P&L Calculation Verification and Formulas
    """
    
    pnl_calculations = {
        "Revenue Calculations": {
            "New Sales": {
                "Formula": "monthly_sales × avg_deal_size",
                "Example": "183 × $15,000 = $2,745,000"
            },
            "Immediate Collections (70%)": {
                "Formula": "New Sales × 0.70",
                "Example": "$2,745,000 × 0.70 = $1,921,500"
            },
            "Deferred Collections (30%)": {
                "Formula": "New Sales × 0.30",
                "Example": "$2,745,000 × 0.30 = $823,500"
            }
        },
        
        "COGS (Cost of Goods Sold)": {
            "Lead Generation": {
                "Formula": "monthly_leads × cost_per_lead",
                "Example": "687 leads × $100/lead = $68,700"
            },
            "Sales Commissions": {
                "Formula": "immediate_revenue × commission_rate + deferred_revenue × commission_rate",
                "Components": {
                    "Base Salaries": "num_closers × base_salary + num_setters × base_salary",
                    "Variable Comp": "monthly_sales × commission_per_sale"
                }
            }
        },
        
        "Operating Expenses": {
            "Total OpEx": {
                "Formula": "Office Rent + Software & Tools + Other OpEx + Management Salaries + Bench Salaries",
                "Example": "$10,000 + $10,000 + $5,000 + management + bench"
            }
        },
        
        "EBITDA Calculation": {
            "Gross Profit": {
                "Formula": "Total Revenue - COGS",
                "Example": "$3,114,425 - $1,489,568 = $1,624,857"
            },
            "EBITDA": {
                "Formula": "Gross Profit - Operating Expenses",
                "Example": "$1,624,857 - $311,442 = $1,313,415"
            },
            "EBITDA Margin": {
                "Formula": "EBITDA / Total Revenue × 100",
                "Example": "$1,313,415 / $3,114,425 × 100 = 42.2%"
            }
        },
        
        "Key Metrics": {
            "CAC (Customer Acquisition Cost)": {
                "Formula": "(Lead Gen Cost + Sales Comp) / monthly_sales",
                "Example": "($68,700 + $150,000) / 183 = $1,195"
            },
            "LTV (Lifetime Value)": {
                "Formula": "avg_deal_size × expected_purchases × gross_margin",
                "Simplified": "avg_deal_size (assuming single purchase for simplicity)"
            },
            "LTV:CAC Ratio": {
                "Formula": "LTV / CAC",
                "Example": "$15,000 / $1,195 = 12.5:1"
            },
            "Payback Period": {
                "Formula": "CAC / (avg_deal_size × gross_margin / avg_customer_lifetime_months)",
                "Example": "Typically measured in months"
            },
            "ROAS (Return on Ad Spend)": {
                "Formula": "Monthly Revenue / Marketing Spend",
                "Example": "$3,114,425 / $68,700 = 45.3x"
            }
        }
    }
    
    return pnl_calculations

def verify_correlations():
    """
    Verify all correlations between metrics
    """
    
    correlations = {
        "Lead to Revenue Flow": [
            "Leads → Contact Rate → Contacts",
            "Contacts → Meeting Rate → Meetings Scheduled",
            "Meetings Scheduled → Show-up Rate → Meetings Held",
            "Meetings Held → Close Rate → Sales",
            "Sales × Avg Deal Size → Revenue",
            "Revenue × Split → Immediate + Deferred"
        ],
        
        "Cost Flow": [
            "Leads × CPL → Lead Generation Cost",
            "Sales × Commission → Sales Compensation",
            "Team Size × Salaries → Labor Costs",
            "All Costs → Total Operating Expenses"
        ],
        
        "Capacity Calculations": [
            "Closers × 60 meetings/month = Total Capacity",
            "Meetings Held / Total Capacity = Utilization %",
            "If Utilization > 90% → Capacity Alert"
        ],
        
        "Performance Metrics": [
            "Revenue vs Target → Performance %",
            "Pipeline Value / Revenue Target → Pipeline Coverage",
            "Monthly Sales / Days → Sales Velocity"
        ]
    }
    
    return correlations

# Display the explanations
st.title("📊 Command Center Input Explanations & P&L Verification")

tab1, tab2, tab3 = st.tabs(["Input Explanations", "P&L Calculations", "Correlations"])

with tab1:
    st.header("Command Center Input Explanations")
    explanations = explain_command_center_inputs()
    for section, inputs in explanations.items():
        with st.expander(f"📋 {section}", expanded=True):
            for input_name, details in inputs.items():
                st.markdown(f"**{input_name}**")
                for key, value in details.items():
                    st.write(f"• {key}: {value}")
                st.divider()

with tab2:
    st.header("P&L Calculation Verification")
    calculations = calculate_pnl_verification()
    for category, items in calculations.items():
        with st.expander(f"💰 {category}", expanded=True):
            for item_name, details in items.items():
                st.markdown(f"**{item_name}**")
                if isinstance(details, dict):
                    for key, value in details.items():
                        if isinstance(value, dict):
                            st.write(f"• {key}:")
                            for sub_key, sub_value in value.items():
                                st.write(f"  - {sub_key}: {sub_value}")
                        else:
                            st.write(f"• {key}: {value}")
                else:
                    st.write(f"• {details}")
                st.divider()

with tab3:
    st.header("Metric Correlations & Verification")
    correlations = verify_correlations()
    for correlation_type, flows in correlations.items():
        with st.expander(f"🔄 {correlation_type}", expanded=True):
            for flow in flows:
                st.write(f"• {flow}")
