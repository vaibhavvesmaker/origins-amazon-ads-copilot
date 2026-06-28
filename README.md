# Origins Amazon Ads Optimization Copilot

A prototype Streamlit app that turns Amazon Ads CSV exports into a manager-ready optimization dashboard.

This is designed as an interview/demo project for a Performance Marketing / Retail Media role. It does **not** connect to Amazon Ads API yet. It starts with CSV exports so the logic is safe, auditable, and easy to demo.

## What it does

- Upload Amazon Ads campaign, search term, and ASIN/product CSV reports
- Calculates key KPIs: Spend, Sales, CTR, CPC, CVR, ACOS, ROAS
- Builds pivot-style campaign and ASIN summaries
- Flags search terms that may need negative keywords
- Recommends bid-down / bid-up actions using dry-run rules
- Identifies product detail page / retail-readiness issues
- Exports a manager approval workbook in Excel

## Why this is better than manually uploading reports into ChatGPT

Uploading CSVs into a chatbot is good for one-off analysis, but it has several limitations:

1. **No repeatable business logic**  
   Each upload depends on the prompt. This app applies the same KPI formulas and decision rules every time.

2. **No audit trail**  
   This app generates a recommendation table with action type, reason, metric signal, suggested bid, and dry-run status.

3. **Excel logic is preserved but automated**  
   Pivot tables, VLOOKUP/XLOOKUP-style joins, SUMIFS-style aggregations, and IF/IFS decision rules are embedded in the workflow.

4. **Safer for enterprise use**  
   The prototype runs locally and does not require Amazon API credentials or live bid changes.

5. **Manager approval workflow**  
   Recommendations are dry-run only and can be exported before any action is taken.

6. **API-ready architecture**  
   The CSV upload layer can later be replaced with Amazon Ads API reporting and a FastAPI backend.

## Excel concepts represented

- Pivot Tables → pandas `groupby()` summaries
- VLOOKUP / XLOOKUP → pandas `merge()` joins
- SUMIFS → filtered aggregations
- IF / IFS → recommendation rules
- Conditional formatting → priority labels
- Export workbook → approval-ready Excel file

## Quick start

```bash
git clone <your-repo-url>
cd origins-amazon-ads-copilot
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Suggested repo structure

```text
origins-amazon-ads-copilot/
  app.py
  requirements.txt
  README.md
  sample_data/
    campaign_report.csv
    search_term_report.csv
    asin_report.csv
```

## Interview positioning

> I built this as a dry-run Amazon Ads optimization copilot. The goal is not to let AI blindly change bids, but to make reporting and optimization more systematic. It takes campaign and search term reports, calculates the same metrics I would normally analyze in Excel, flags inefficient spend, identifies scalable keywords, and exports recommendations for human approval. The next version could connect to Amazon Ads API, but I would keep safety caps, audit logs, and manager approval before any live changes.

## Future roadmap

- Amazon Ads API integration
- FastAPI middleware
- BigQuery/Postgres storage
- Scheduled daily ingestion
- Brand vs non-brand split
- ASIN retail-readiness scoring
- Slack/email pacing alerts
- Human approval queue
- Bulk upload file generation