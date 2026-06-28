# Origins Amazon Ads Optimization Copilot

A prototype Streamlit app that turns Amazon Ads CSV exports into a manager-ready optimization dashboard and dry-run recommendation engine.

This project was built as an interview/demo prototype for a Performance Marketing / Retail Media role. It does not connect to the Amazon Ads API yet. Instead, it starts with exported CSV reports so the workflow is safe, auditable, easy to demo, and easy to explain.

## Project Purpose

Amazon Ads reports already provide raw metrics such as impressions, clicks, spend, sales, orders, CTR, CPC, ACOS, and ROAS. The goal of this prototype is not to replace Amazon reporting.

The goal is to build the layer after reporting:

> Upload the report → calculate KPIs → apply business rules → flag issues/opportunities → export a dry-run recommendation workbook for manager review.

In a real Amazon retail media workflow, this helps reduce repetitive Excel analysis and creates a consistent decision process for campaign, keyword, and ASIN-level optimization.

## What It Does

The app allows users to upload three Amazon Ads-style CSV reports:

* Campaign report
* Search term / keyword report
* Advertised product / ASIN report

It then:

* Calculates key KPIs: Spend, Sales, CTR, CPC, CVR, ACOS, ROAS
* Builds pivot-style campaign and ASIN summaries
* Identifies high-spend search terms with weak or zero conversion
* Flags search terms that may need negative keyword review
* Recommends dry-run bid-down or bid-up actions based on performance rules
* Identifies possible product detail page / retail-readiness issues
* Shows campaign-level and ASIN-level performance views
* Allows managers to simulate different Target ACOS, spend threshold, click threshold, and bid-change rules
* Exports an Excel recommendation workbook for review before any action is taken

## Why This Is Useful

A manager could manually download Amazon Ads reports and analyze them in Excel. This prototype is designed to make that process more repeatable, faster, and easier to review.

The difference is not that the app has data Amazon does not provide. The difference is that the app applies consistent business logic to the data and turns the report into an action queue.

Instead of only showing:

> Campaign A has 48% ACOS.

The app can flag:

> Campaign A is above the Target ACOS threshold and should be reviewed for bid-down, keyword tightening, or budget reallocation.

Instead of only showing:

> Search term X spent $80 and generated 0 orders.

The app can flag:

> Search term X is a negative keyword candidate because it crossed the waste threshold with no conversion.

## Dry-Run Recommendation Engine

The app uses a dry-run model. It does not make live changes to Amazon campaigns, bids, or budgets.

This is intentional.

The workflow is:

1. Upload Amazon Ads reports
2. Review campaign, keyword, and ASIN performance
3. Adjust business rules in the sidebar
4. Generate recommendation queue
5. Export Excel workbook
6. Manager reviews and approves actions
7. Future version could push approved changes through Amazon Ads API

Dry run makes the tool safer for enterprise use because recommendations can be reviewed before any live media changes happen.

## Sidebar Business Rules

The sidebar controls do not change historical campaign performance. They change the recommendation logic.

### Target ACOS

Defines the efficiency threshold.

If Target ACOS is lowered, more campaigns and keywords may be flagged as inefficient.

### Minimum Spend Threshold

Defines when wasted spend is meaningful enough to review.

If the threshold is lowered, more search terms may be flagged. If it is raised, only higher-impact waste gets flagged.

### Minimum Clicks for Decisioning

Controls confidence.

Higher click thresholds reduce low-confidence recommendations.

### Max Bid Change Safety Cap

Controls how aggressive suggested bid changes can be.

For example, if a keyword has a $1.00 bid:

* 10% cap may suggest $0.90
* 20% cap may suggest $0.80

The app keeps this in dry-run mode and does not apply changes directly.

## Where Recommendations Appear

The recommendation logic appears in three main places:

### Executive Summary

Shows the high-level performance readout and optimization queue.

### Keyword & Search Terms

Shows search-term-level issues and opportunities, including possible negative keyword candidates and scale candidates.

### Excel Logic + Export

Exports a workbook with:

* Campaign summary
* ASIN summary
* Search term data
* Recommendation queue

The recommendations sheet is the main output for manager review.

## Excel Concepts Represented

This prototype translates common Excel workflows into a repeatable Python workflow:

| Excel Concept          | Python / App Equivalent                                               |
| ---------------------- | --------------------------------------------------------------------- |
| Pivot Tables           | `pandas groupby()` campaign and ASIN summaries                        |
| VLOOKUP / XLOOKUP      | Data joins and lookup-style mapping                                   |
| SUMIFS                 | Filtered aggregations for spend, sales, orders, and KPIs              |
| IF / IFS               | Business rules for bid-down, bid-up, negative keyword, and PDP review |
| Conditional Formatting | Priority labels such as High, Medium, Growth, and Content             |
| Workbook Export        | Manager-ready Excel recommendation file                               |

## Why This Is Better Than Uploading CSVs Into ChatGPT

Uploading a CSV into ChatGPT, Claude, or Gemini can be useful for one-off analysis. But it has limitations:

### 1. No Repeatable Business Logic

A chatbot response depends heavily on the prompt. This app applies the same formulas and decision rules every time.

### 2. No Audit Trail

The app produces a recommendation table with action type, reason, metric signal, current bid, suggested bid, and dry-run status.

### 3. Better Manager Review

The output can be exported into an Excel workbook for approval before any action is taken.

### 4. Safer Workflow

No API credentials are required for the prototype. No live bids or budgets are changed.

### 5. API-Ready Architecture

The CSV upload layer can later be replaced with Amazon Ads API reporting, scheduled ingestion, and a FastAPI backend.

## Example Use Case

A manager wants to understand how stricter efficiency goals would affect the account.

They lower Target ACOS from 35% to 25%.

The app does not change historical sales or spend. Instead, it updates the recommendation logic and flags additional campaigns, keywords, or ASINs that no longer meet the stricter target.

This allows the manager to simulate:

> “If we need to become more efficient, what would we need to change?”

## Current Features

* Streamlit UI
* Origins-inspired visual design
* Campaign performance dashboard
* ASIN-level performance view
* Keyword and search term diagnostics
* Dry-run recommendation queue
* Target ACOS scenario logic
* Bid-up / bid-down recommendation logic
* Negative keyword candidate detection
* Product detail page review signals
* Excel workbook export

## Quick Start

```bash
git clone <your-repo-url>
cd origins-amazon-ads-copilot

python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Suggested Repo Structure

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

## Interview Positioning

I built this as a dry-run Amazon Ads optimization copilot. The goal is not to let AI blindly change bids or budgets. The goal is to make reporting and optimization more systematic.

The app takes Amazon Ads-style campaign, search term, and ASIN reports, calculates the same performance metrics I would normally analyze in Excel, and then applies business rules to flag inefficient spend, scalable keywords, possible negative keywords, and ASIN-level conversion issues.

What makes it useful is the recommendation layer. A manager can adjust Target ACOS, spend threshold, click threshold, or bid-change limits, and the app updates the optimization queue based on those business rules.

The next version could connect to the Amazon Ads API, but I would still keep human approval, safety caps, and audit logs before making any live changes.

## Future Roadmap

* Amazon Ads API integration
* FastAPI middleware
* BigQuery or Postgres storage
* Scheduled daily ingestion
* Brand vs non-brand campaign split
* ASIN retail-readiness scoring
* Slack or email pacing alerts
* Human approval queue
* Bulk upload file generation
* Audit log for recommended and approved actions
* API-based bid and budget updates after manager approval
