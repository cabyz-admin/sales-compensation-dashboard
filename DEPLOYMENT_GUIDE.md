# 📚 Deployment Guide - Sales Compensation Dashboard

## 🎯 CURRENT MAIN FILE
**Production File:** `dashboard_improved_final.py`
- **Size:** ~138KB
- **Lines:** 3000+
- **Status:** Active Production Version
- **Last Updated:** Sep 29, 2025

## 🗂️ FILE ORGANIZATION

### ✅ ACTIVE FILES
- `dashboard_improved_final.py` - **MAIN PRODUCTION FILE**
- `modules/` - Required module dependencies
  - `calculations_improved.py`
  - `calculations_enhanced.py`
  - `revenue_retention.py`

### ⚠️ LEGACY FILES (DO NOT USE)
- `dashboard_enhanced_complete.py` - Old version
- `dashboard_improved_final_v2.py` - Test version
- `unified_dashboard.py` - Experimental
- `app.py` - Original prototype
- `sales_compensation_dashboard.py` - First version
- `enhanced_compensation_dashboard.py` - Early enhancement
- `fixed_compensation_dashboard.py` - Bug fix version

## 🚀 DEPLOYMENT

### Local Development
```bash
cd /Users/castillo/CascadeProjects/comp-structure
source venv/bin/activate
streamlit run dashboard_improved_final.py
```

### Streamlit Cloud
1. **Repository:** https://github.com/cabyz-admin/sales-compensation-dashboard
2. **Main File:** `dashboard_improved_final.py`
3. **Python Version:** 3.9+
4. **App URL:** [Your Streamlit Cloud URL]

## 📦 DEPENDENCIES
All dependencies are in `requirements.txt`:
- streamlit>=1.35.0
- numpy>=1.26.0
- pandas>=2.1.0
- plotly>=5.18.0
- scipy>=1.12.0
- openpyxl>=3.1.2
- xlsxwriter>=3.1.9

## 🐛 TROUBLESHOOTING

### If Streamlit Cloud fails:
1. Check deployment logs in Streamlit Cloud dashboard
2. Verify all modules in `modules/` directory are present
3. Ensure `requirements.txt` is up to date
4. Check Python version compatibility

### If local deployment fails:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 FEATURES
- Multi-Channel GTM Configuration
- Insurance Deal Economics Model
- Smart Input Logic by Cost Point
- Dynamic Revenue Calculations
- Comprehensive P&L Analysis
- What-if Scenarios
- Health Score Metrics

## ⚡ RECENT IMPROVEMENTS (Sep 29, 2025)
1. Multi-channel first approach
2. Insurance deal economics model
3. Smart input logic by cost point
4. Fixed revenue calculations
5. Removed legacy conversion funnel
6. Fixed division by zero errors
7. Deal economics correlation

## 🔒 DO NOT
- Create new dashboard files without archiving old ones
- Edit production file without testing locally first
- Mix legacy modules with current version
- Deploy without checking requirements.txt

---
**Maintained by:** Sales Operations Team
**Last Updated:** Sep 29, 2025
