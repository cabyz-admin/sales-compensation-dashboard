# 💎 Sales Compensation Dashboard

Unified repository for the production compensation model, cloud build, supporting modules, and historical dashboards.

## 📁 Repository Structure

- `dashboards/production/`
  - `dashboard_improved_final.py` — **Primary Streamlit app** (full feature set)
- `dashboards/cloud/`
  - `dashboard_cloud.py` — **Lightweight Streamlit Cloud deployment**
- `dashboards/legacy/`
  - Archived dashboards (`app.py`, `sales_compensation_dashboard.py`, etc.)
- `modules/` — Shared business logic, GTM models, revenue retention
- `components/`, `app/` — Next.js UI assets (currently unused by Streamlit app)
- `docs/` — Deployment notes, feature summaries, research memos

## 🚀 Run Locally (Production App)

```bash
pip install -r requirements.txt
streamlit run dashboards/production/dashboard_improved_final.py
```

## ☁️ Streamlit Cloud

Set the entry point to `dashboards/cloud/dashboard_cloud.py`.

## 🗂 Documentation

Key references live in `docs/`:

- `DEPLOYMENT_GUIDE.md`
- `FINAL_IMPROVEMENTS_SUMMARY.md`
- `ENHANCED_FEATURES.md`

## 📦 Support Scripts & Tools

- `run_dashboard.sh` — Legacy launcher (points to archived app)
- `analyze_excel_files.py`, `optimaxx_plus_model.py` — Supplemental analysis utilities

Maintained by Sales Ops Engineering.
