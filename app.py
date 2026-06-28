import io
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


# ------------------------------------------------------------
# Origins Amazon Ads Optimization Copilot
# Prototype only. Uses CSV uploads / sample data. No live API calls.
# ------------------------------------------------------------

st.set_page_config(
    page_title="Origins Amazon Ads Copilot",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# Origins-inspired UI styling
# --------------------------
st.markdown(
    """
    <style>
    /* Better tab visibility */
button[data-baseweb="tab"] {
    color: #214336 !important;
    background: rgba(255,255,255,.62) !important;
    border-radius: 999px !important;
    padding: 8px 14px !important;
    margin-right: 6px !important;
    border: 1px solid rgba(33,67,54,.12) !important;
}

button[data-baseweb="tab"] p {
    color: #214336 !important;
    font-weight: 650 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: #214336 !important;
    border: 1px solid #214336 !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #F7F1E7 !important;
}

div[data-testid="stFileUploader"] label p {
    color: #214336 !important;
    font-weight: 650 !important;
}

div[data-testid="stExpander"] p {
    color: #25322E;
}
        :root {
            --forest: #214336;
            --sage: #8FAF8A;
            --cream: #F7F1E7;
            --clay: #C96F4A;
            --moss: #5E7F4D;
            --ink: #25322E;
            --muted: #6C746F;
        }
        .stApp {
            background: linear-gradient(180deg, #fbf7ef 0%, #f7f1e7 55%, #eef3ea 100%);
            color: var(--ink);
        }
        [data-testid="stSidebar"] {
            background: #214336;
        }
        [data-testid="stSidebar"] * {
            color: #F7F1E7 !important;
        }
        .hero {
            background: linear-gradient(135deg, #214336 0%, #5E7F4D 62%, #8FAF8A 100%);
            padding: 28px 34px;
            border-radius: 24px;
            color: #fff;
            box-shadow: 0 14px 30px rgba(33,67,54,.18);
            margin-bottom: 22px;
        }
        .hero h1 {
            font-size: 42px;
            line-height: 1.05;
            margin: 0 0 8px 0;
            font-weight: 760;
            letter-spacing: -0.03em;
        }
        .hero p {
            font-size: 17px;
            margin: 0;
            opacity: 0.96;
        }
        .pill {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,.18);
            margin-right: 8px;
            margin-top: 14px;
            font-size: 13px;
        }
        .metric-card {
            padding: 18px 18px;
            background: rgba(255,255,255,.78);
            border: 1px solid rgba(33,67,54,.10);
            border-radius: 18px;
            box-shadow: 0 8px 18px rgba(33,67,54,.07);
        }
        .metric-label {
            color: #5f6a64;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: .06em;
            margin-bottom: 6px;
        }
        .metric-value {
            color: #214336;
            font-size: 32px;
            font-weight: 720;
            line-height: 1.1;
        }
        .metric-note {
            color: #6c746f;
            font-size: 13px;
            margin-top: 6px;
        }
        .section-title {
            color: #214336;
            font-size: 24px;
            font-weight: 740;
            margin: 28px 0 10px 0;
        }
        .callout {
            padding: 16px 18px;
            border-left: 5px solid #C96F4A;
            background: rgba(255,255,255,.72);
            border-radius: 14px;
            margin: 10px 0 20px 0;
        }
        div[data-testid="stMetricValue"] {
            color: #214336;
        }
        .small-muted {
            color: #6c746f;
            font-size: 13px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------
# Helpers
# --------------------------
def money(x):
    if pd.isna(x) or np.isinf(x):
        return "$0"
    return "${:,.0f}".format(float(x))


def pct(x):
    if pd.isna(x) or np.isinf(x):
        return "0.0%"
    return "{:.1%}".format(float(x))


def num(x):
    if pd.isna(x) or np.isinf(x):
        return "0"
    return "{:,.0f}".format(float(x))


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes common Amazon Ads export names into one standard schema.
    This is the prototype equivalent of cleaning a messy Excel workbook.
    """
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("%", "pct", regex=False)
    )

    aliases = {
        "campaign_name": "campaign",
        "campaign": "campaign",
        "ad_group_name": "ad_group",
        "ad_group": "ad_group",
        "advertised_asin": "asin",
        "asin": "asin",
        "search_term": "search_term",
        "customer_search_term": "search_term",
        "keyword_text": "keyword",
        "keyword": "keyword",
        "match_type": "match_type",
        "impressions": "impressions",
        "clicks": "clicks",
        "spend": "spend",
        "cost": "spend",
        "sales": "sales",
        "7_day_total_sales": "sales",
        "orders": "orders",
        "7_day_total_orders": "orders",
        "conversions": "orders",
        "bid": "current_bid",
        "current_bid": "current_bid",
        "budget": "budget",
        "daily_budget": "budget",
        "product": "product",
        "product_name": "product",
    }

    rename = {}
    for c in df.columns:
        if c in aliases:
            rename[c] = aliases[c]
    df = df.rename(columns=rename)

    for col in ["impressions", "clicks", "spend", "sales", "orders", "current_bid", "budget"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    needed = ["impressions", "clicks", "spend", "sales", "orders"]
    for col in needed:
        if col not in df.columns:
            df[col] = 0

    df["ctr"] = np.where(df["impressions"] > 0, df["clicks"] / df["impressions"], 0)
    df["cpc"] = np.where(df["clicks"] > 0, df["spend"] / df["clicks"], 0)
    df["cvr"] = np.where(df["clicks"] > 0, df["orders"] / df["clicks"], 0)
    df["acos"] = np.where(df["sales"] > 0, df["spend"] / df["sales"], np.nan)
    df["roas"] = np.where(df["spend"] > 0, df["sales"] / df["spend"], 0)
    return df


def load_csv(uploaded_file, fallback_path):
    if uploaded_file:
        return normalize_columns(pd.read_csv(uploaded_file))
    return normalize_columns(pd.read_csv(fallback_path))


def build_campaign_summary(df):
    # PivotTable equivalent:
    # Excel: Insert Pivot Table; Rows = Campaign; Values = SUM(Impressions, Clicks, Spend, Sales, Orders)
    summary = (
        df.groupby("campaign", dropna=False)[["impressions", "clicks", "spend", "sales", "orders"]]
        .sum()
        .reset_index()
    )
    return add_kpis(summary)


def build_asin_summary(df):
    if "asin" not in df.columns:
        return pd.DataFrame()
    group_cols = ["asin"]
    if "product" in df.columns:
        group_cols.append("product")
    summary = (
        df.groupby(group_cols, dropna=False)[["impressions", "clicks", "spend", "sales", "orders"]]
        .sum()
        .reset_index()
    )
    return add_kpis(summary)


def generate_recommendations(search_df, campaign_df, target_acos, target_roas, min_spend, min_clicks, max_bid_change):
    recs = []

    if search_df is not None and len(search_df) > 0:
        df = add_kpis(search_df)
        for _, r in df.iterrows():
            search_term = r.get("search_term", r.get("keyword", "Unknown"))
            campaign = r.get("campaign", "Unknown")
            keyword = r.get("keyword", search_term)
            current_bid = float(r.get("current_bid", 0) or 0)

            if r["spend"] >= min_spend and r["orders"] == 0:
                recs.append({
                    "priority": "High",
                    "action_type": "Add Negative Exact",
                    "campaign": campaign,
                    "keyword_or_search_term": search_term,
                    "reason": f"Spent {money(r['spend'])} with zero orders.",
                    "metric_signal": f"Clicks {num(r['clicks'])}, Sales {money(r['sales'])}",
                    "recommended_change": "Add as negative exact or reduce match exposure.",
                    "current_bid": current_bid,
                    "suggested_bid": current_bid,
                    "status": "Dry Run"
                })

            if r["clicks"] >= min_clicks and pd.notna(r["acos"]) and r["acos"] > target_acos:
                suggested = current_bid
                if current_bid > 0:
                    suggested = max(current_bid * (1 - max_bid_change), 0.10)
                recs.append({
                    "priority": "Medium",
                    "action_type": "Bid Down",
                    "campaign": campaign,
                    "keyword_or_search_term": keyword,
                    "reason": f"ACOS {pct(r['acos'])} is above target {pct(target_acos)}.",
                    "metric_signal": f"ROAS {r['roas']:.2f}, CPC {money(r['cpc'])}, CVR {pct(r['cvr'])}",
                    "recommended_change": f"Lower bid by up to {int(max_bid_change*100)}%.",
                    "current_bid": current_bid,
                    "suggested_bid": round(suggested, 2),
                    "status": "Dry Run"
                })

            if r["clicks"] >= min_clicks and r["roas"] >= target_roas and r["cvr"] >= df["cvr"].median():
                suggested = current_bid
                if current_bid > 0:
                    suggested = current_bid * (1 + max_bid_change)
                recs.append({
                    "priority": "Growth",
                    "action_type": "Bid Up / Scale",
                    "campaign": campaign,
                    "keyword_or_search_term": keyword,
                    "reason": f"ROAS {r['roas']:.2f} is above target {target_roas:.2f} with healthy conversion.",
                    "metric_signal": f"CTR {pct(r['ctr'])}, CVR {pct(r['cvr'])}, Sales {money(r['sales'])}",
                    "recommended_change": f"Increase bid or budget by up to {int(max_bid_change*100)}%.",
                    "current_bid": current_bid,
                    "suggested_bid": round(suggested, 2),
                    "status": "Dry Run"
                })

            if r["ctr"] >= 0.007 and r["cvr"] < 0.03 and r["clicks"] >= min_clicks:
                recs.append({
                    "priority": "Content",
                    "action_type": "PDP Review",
                    "campaign": campaign,
                    "keyword_or_search_term": search_term,
                    "reason": "CTR is healthy but CVR is low; traffic may be interested but not converting.",
                    "metric_signal": f"CTR {pct(r['ctr'])}, CVR {pct(r['cvr'])}",
                    "recommended_change": "Review ASIN detail page, price, claims, hero image, reviews, and offer.",
                    "current_bid": current_bid,
                    "suggested_bid": current_bid,
                    "status": "Dry Run"
                })

    if campaign_df is not None and len(campaign_df) > 0:
        cdf = build_campaign_summary(campaign_df)
        for _, r in cdf.iterrows():
            if r["spend"] >= min_spend and pd.notna(r["acos"]) and r["acos"] > target_acos:
                recs.append({
                    "priority": "High",
                    "action_type": "Budget Reallocation",
                    "campaign": r["campaign"],
                    "keyword_or_search_term": "Campaign-level",
                    "reason": f"Campaign ACOS {pct(r['acos'])} exceeds target.",
                    "metric_signal": f"Spend {money(r['spend'])}, Sales {money(r['sales'])}, ROAS {r['roas']:.2f}",
                    "recommended_change": "Shift budget toward higher-ROAS campaigns; review keyword mix.",
                    "current_bid": 0,
                    "suggested_bid": 0,
                    "status": "Dry Run"
                })

            if r["roas"] >= target_roas and r["sales"] > 0:
                recs.append({
                    "priority": "Growth",
                    "action_type": "Protect / Scale",
                    "campaign": r["campaign"],
                    "keyword_or_search_term": "Campaign-level",
                    "reason": "Campaign is above target ROAS.",
                    "metric_signal": f"ROAS {r['roas']:.2f}, CVR {pct(r['cvr'])}",
                    "recommended_change": "Protect budget; evaluate impression share and expansion terms.",
                    "current_bid": 0,
                    "suggested_bid": 0,
                    "status": "Dry Run"
                })

    rec_df = pd.DataFrame(recs).drop_duplicates()
    if len(rec_df) == 0:
        rec_df = pd.DataFrame(columns=[
            "priority", "action_type", "campaign", "keyword_or_search_term",
            "reason", "metric_signal", "recommended_change",
            "current_bid", "suggested_bid", "status"
        ])
    return rec_df


def executive_summary(campaign_summary, rec_df, target_acos):
    spend = campaign_summary["spend"].sum()
    sales = campaign_summary["sales"].sum()
    roas = sales / spend if spend > 0 else 0
    acos = spend / sales if sales > 0 else np.nan
    orders = campaign_summary["orders"].sum()
    clicks = campaign_summary["clicks"].sum()
    impressions = campaign_summary["impressions"].sum()
    ctr = clicks / impressions if impressions > 0 else 0
    cvr = orders / clicks if clicks > 0 else 0

    top_campaign = "N/A"
    if len(campaign_summary) > 0:
        top_campaign = campaign_summary.sort_values("sales", ascending=False).iloc[0]["campaign"]

    high_count = int((rec_df["priority"] == "High").sum()) if len(rec_df) else 0
    growth_count = int((rec_df["priority"] == "Growth").sum()) if len(rec_df) else 0

    if pd.notna(acos) and acos > target_acos:
        diagnosis = "Overall ACOS is above target, so the first priority is spend quality: reduce waste, tighten match types, and move budget into proven terms."
    else:
        diagnosis = "Overall efficiency is within or near target, so the next priority is controlled scaling: protect strong campaigns and expand into high-intent search terms."

    return f"""
**Executive readout:** The account generated **{money(sales)} in attributed sales** from **{money(spend)} in spend**, producing **ROAS of {roas:.2f}** and **ACOS of {pct(acos) if pd.notna(acos) else 'N/A'}**. 
CTR is **{pct(ctr)}** and CVR is **{pct(cvr)}**, which helps separate traffic quality from detail-page conversion.

**Top sales driver:** {top_campaign}

**Optimization queue:** {high_count} high-priority efficiency actions and {growth_count} growth/protection opportunities are currently flagged.

**Recommendation:** {diagnosis}
"""


def to_excel_bytes(dataframes):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in dataframes.items():
            clean_name = name[:31]
            df.to_excel(writer, sheet_name=clean_name, index=False)
    output.seek(0)
    return output


# --------------------------
# Sidebar
# --------------------------
st.sidebar.markdown("## 🌿 Origins Ads Copilot")
st.sidebar.caption("Prototype: CSV → KPIs → Recommendations → Export")
st.sidebar.markdown("---")

use_sample = st.sidebar.toggle("Use sample Origins-style data", value=True)

target_acos = st.sidebar.slider("Target ACOS", min_value=0.05, max_value=0.80, value=0.35, step=0.01)
target_roas = st.sidebar.slider("Target ROAS", min_value=1.0, max_value=10.0, value=3.0, step=0.25)
min_spend = st.sidebar.number_input("Waste threshold: minimum spend", min_value=0.0, value=50.0, step=10.0)
min_clicks = st.sidebar.number_input("Minimum clicks for decisioning", min_value=1, value=20, step=1)
max_bid_change = st.sidebar.slider("Safety cap: max bid change", min_value=0.05, max_value=0.30, value=0.15, step=0.01)

st.sidebar.markdown("---")
st.sidebar.markdown("### What these controls affect")
st.sidebar.caption(
    "These controls do not change sales/spend totals. They change the recommendation logic: "
    "what gets flagged as waste, what qualifies for bid-up, bid-down, negative keyword, or PDP review."
)
st.sidebar.caption("Safety mode is always ON: recommendations are dry-run only.")

# --------------------------
# Hero
# --------------------------
st.markdown(
    """
    <div class="hero">
      <h1>Origins Amazon Ads Optimization Copilot</h1>
      <p>A prototype that turns Amazon Ads CSV exports into ASIN, keyword, pacing, and bid recommendations — with Excel logic built into the workflow.</p>
      <span class="pill">Retail Readiness</span>
      <span class="pill">ASIN-Level Growth</span>
      <span class="pill">Budget Pacing</span>
      <span class="pill">Dry-Run Safety</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Uploads
# --------------------------
with st.expander("Step 1 — Upload Amazon Ads reports or use sample data", expanded=not use_sample):
    c1, c2, c3 = st.columns(3)
    with c1:
        campaign_upload = st.file_uploader("Campaign report CSV", type=["csv"], key="campaign")
    with c2:
        search_upload = st.file_uploader("Search term report CSV", type=["csv"], key="search")
    with c3:
        asin_upload = st.file_uploader("Advertised product / ASIN report CSV", type=["csv"], key="asin")

campaign_path = "sample_data/campaign_report.csv"
search_path = "sample_data/search_term_report.csv"
asin_path = "sample_data/asin_report.csv"

try:
    if use_sample:
        campaign_df = load_csv(None, campaign_path)
        search_df = load_csv(None, search_path)
        asin_df = load_csv(None, asin_path)
    else:
        if not campaign_upload or not search_upload:
            st.info("Upload at least a Campaign report and Search Term report, or turn on sample data.")
            st.stop()
        campaign_df = load_csv(campaign_upload, campaign_path)
        search_df = load_csv(search_upload, search_path)
        asin_df = load_csv(asin_upload, asin_path) if asin_upload else pd.DataFrame()
except Exception as e:
    st.error(f"Could not read the uploaded files. Please check CSV format. Error: {e}")
    st.stop()

campaign_df = add_kpis(campaign_df)
search_df = add_kpis(search_df)
asin_df = add_kpis(asin_df) if len(asin_df) else pd.DataFrame()

campaign_summary = build_campaign_summary(campaign_df)
asin_summary = build_asin_summary(asin_df if len(asin_df) else campaign_df)

rec_df = generate_recommendations(
    search_df=search_df,
    campaign_df=campaign_df,
    target_acos=target_acos,
    target_roas=target_roas,
    min_spend=min_spend,
    min_clicks=min_clicks,
    max_bid_change=max_bid_change
)
high_actions = int((rec_df["priority"] == "High").sum()) if len(rec_df) else 0
growth_actions = int((rec_df["priority"] == "Growth").sum()) if len(rec_df) else 0
content_actions = int((rec_df["priority"] == "Content").sum()) if len(rec_df) else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### Recommendation impact")
st.sidebar.metric("High-priority actions", high_actions)
st.sidebar.metric("Growth opportunities", growth_actions)
st.sidebar.metric("PDP/content reviews", content_actions)
# --------------------------
# Top KPIs
# --------------------------
total_spend = campaign_summary["spend"].sum()
total_sales = campaign_summary["sales"].sum()
total_orders = campaign_summary["orders"].sum()
total_clicks = campaign_summary["clicks"].sum()
total_impr = campaign_summary["impressions"].sum()
overall_roas = total_sales / total_spend if total_spend else 0
overall_acos = total_spend / total_sales if total_sales else np.nan
overall_ctr = total_clicks / total_impr if total_impr else 0
overall_cvr = total_orders / total_clicks if total_clicks else 0

k1, k2, k3, k4, k5 = st.columns(5)
for col, label, value, note in [
    (k1, "Attributed Sales", money(total_sales), "Sales from uploaded report"),
    (k2, "Spend", money(total_spend), "Media investment"),
    (k3, "ROAS", f"{overall_roas:.2f}", f"Target {target_roas:.2f}"),
    (k4, "ACOS", pct(overall_acos) if pd.notna(overall_acos) else "N/A", f"Target {pct(target_acos)}"),
    (k5, "CVR", pct(overall_cvr), "Orders / Clicks"),
]:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
st.markdown(
    """
    <div class="callout">
      <strong>How to use this:</strong> The KPI cards show actual uploaded/sample performance.
      The sidebar controls adjust the decision rules used to generate recommendations.
      For example, lowering the target ACOS will flag more campaigns for bid-down or budget review.
    </div>
    """,
    unsafe_allow_html=True
)
# --------------------------
# Tabs
# --------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Summary",
    "Campaign Health",
    "ASIN View",
    "Keyword & Search Terms",
    "Excel Logic + Export"
])

with tab1:
    st.markdown('<div class="section-title">AI-style executive readout</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="callout">This section is rule-based for the prototype. In a production version, this can be replaced with Claude/OpenAI API using a secure backend.</div>',
        unsafe_allow_html=True
    )
    st.markdown(executive_summary(campaign_summary, rec_df, target_acos))

    st.markdown('<div class="section-title">Optimization queue</div>', unsafe_allow_html=True)
    st.dataframe(rec_df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown('<div class="section-title">Campaign health dashboard</div>', unsafe_allow_html=True)

    cc1, cc2 = st.columns([1.1, 1])
    with cc1:
        display_cols = ["campaign", "impressions", "clicks", "spend", "sales", "orders", "ctr", "cpc", "cvr", "acos", "roas"]
        st.dataframe(
            campaign_summary[display_cols].sort_values("sales", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "spend": st.column_config.NumberColumn("Spend", format="$%.2f"),
                "sales": st.column_config.NumberColumn("Sales", format="$%.2f"),
                "ctr": st.column_config.ProgressColumn("CTR", min_value=0, max_value=max(campaign_summary["ctr"].max(), .01), format="%.2f"),
                "cvr": st.column_config.ProgressColumn("CVR", min_value=0, max_value=max(campaign_summary["cvr"].max(), .01), format="%.2f"),
                "acos": st.column_config.NumberColumn("ACOS", format="%.2f"),
                "roas": st.column_config.NumberColumn("ROAS", format="%.2f"),
            }
        )
    with cc2:
        chart = px.bar(
            campaign_summary.sort_values("sales", ascending=False),
            x="sales",
            y="campaign",
            orientation="h",
            title="Attributed Sales by Campaign",
            color="roas",
            color_continuous_scale=["#C96F4A", "#8FAF8A", "#214336"]
        )
        chart.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=480)
        st.plotly_chart(chart, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        chart = px.scatter(
            campaign_summary,
            x="ctr",
            y="cvr",
            size="spend",
            color="roas",
            hover_name="campaign",
            title="CTR vs CVR: traffic quality vs conversion",
            color_continuous_scale=["#C96F4A", "#8FAF8A", "#214336"]
        )
        chart.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(chart, use_container_width=True)
    with c4:
        chart = px.bar(
            campaign_summary.sort_values("acos", ascending=False),
            x="campaign",
            y="acos",
            title="ACOS by Campaign",
            color="acos",
            color_continuous_scale=["#8FAF8A", "#C96F4A"]
        )
        chart.add_hline(y=target_acos, line_dash="dash", annotation_text="Target ACOS")
        chart.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-35)
        st.plotly_chart(chart, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">ASIN-level growth view</div>', unsafe_allow_html=True)
    if len(asin_summary) == 0:
        st.warning("No ASIN-level file detected. Upload an advertised product report or use sample data.")
    else:
        asin_display = asin_summary.sort_values("sales", ascending=False)
        st.dataframe(asin_display, use_container_width=True, hide_index=True)

        chart = px.scatter(
            asin_display,
            x="roas",
            y="cvr",
            size="sales",
            color="acos",
            hover_data=[c for c in ["asin", "product"] if c in asin_display.columns],
            title="ASIN Readiness Matrix: ROAS vs CVR",
            color_continuous_scale=["#8FAF8A", "#C96F4A"]
        )
        chart.add_vline(x=target_roas, line_dash="dash", annotation_text="Target ROAS")
        chart.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=520)
        st.plotly_chart(chart, use_container_width=True)

        st.markdown(
            """
            **How to read this for Origins:**  
            High ROAS + strong CVR = candidates to scale.  
            High CTR + low CVR = PDP/retail-readiness review.  
            Low traffic + strong CVR = keyword expansion or budget opportunity.
            """
        )

with tab4:
    st.markdown('<div class="section-title">Search term diagnostics</div>', unsafe_allow_html=True)

    cols = [c for c in ["campaign", "search_term", "keyword", "match_type", "impressions", "clicks", "spend", "sales", "orders", "ctr", "cpc", "cvr", "acos", "roas", "current_bid"] if c in search_df.columns]
    st.dataframe(search_df[cols].sort_values("spend", ascending=False), use_container_width=True, hide_index=True)

    q1, q2 = st.columns(2)
    with q1:
        waste = search_df[(search_df["spend"] >= min_spend) & (search_df["orders"] == 0)].copy()
        st.markdown("#### Potential wasted spend / negative candidates")
        st.dataframe(waste[cols].sort_values("spend", ascending=False), use_container_width=True, hide_index=True)
    with q2:
        winners = search_df[(search_df["roas"] >= target_roas) & (search_df["orders"] > 0)].copy()
        st.markdown("#### Potential scale candidates")
        st.dataframe(winners[cols].sort_values("roas", ascending=False), use_container_width=True, hide_index=True)

with tab5:
    st.markdown('<div class="section-title">Excel logic translated into a repeatable workflow</div>', unsafe_allow_html=True)
    st.markdown(
        """
        This prototype deliberately uses the same logic hiring managers ask about in Excel interviews, but makes it repeatable:

        - **Pivot Tables →** `pandas.groupby()` / `pivot_table()` for campaign and ASIN summaries  
        - **VLOOKUP / XLOOKUP →** `merge()` to join ASIN metadata, product names, campaign files, and search terms  
        - **SUMIFS →** filtered aggregations for spend, sales, orders, CTR, CVR, ROAS, and ACOS  
        - **IF / IFS logic →** optimization rules for bid down, bid up, negative keyword, and PDP review  
        - **Conditional formatting →** priority labels: High, Medium, Growth, Content  
        - **Export to Excel →** recommendation workbook for manager approval or bulk-upload preparation
        """
    )

    export_bytes = to_excel_bytes({
        "campaign_summary": campaign_summary,
        "asin_summary": asin_summary,
        "search_terms": search_df,
        "recommendations": rec_df
    })

    st.download_button(
        "Download Excel recommendation workbook",
        data=export_bytes,
        file_name=f"origins_ads_copilot_recommendations_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        "Download recommendations CSV",
        data=rec_df.to_csv(index=False).encode("utf-8"),
        file_name="dry_run_recommendations.csv",
        mime="text/csv"
    )

    st.markdown("#### Raw files preview")
    with st.expander("Campaign report"):
        st.dataframe(campaign_df, use_container_width=True)
    with st.expander("Search term report"):
        st.dataframe(search_df, use_container_width=True)
    with st.expander("ASIN report"):
        st.dataframe(asin_df, use_container_width=True)