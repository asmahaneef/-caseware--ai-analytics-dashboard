import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------
# Page setup
# -----------------------------------------------------------------------
st.set_page_config(page_title="Caseware-Inspired AI Analytics Dashboard", layout="wide")

st.title("Caseware-Inspired AI Product Analytics & Trust Dashboard")
st.caption("Simulated data inspired by public product analytics and AI observability themes. Not affiliated with or representing real Caseware data.")

# -----------------------------------------------------------------------
# Load data directly from GitHub (cached so it doesn't reload every click)
# -----------------------------------------------------------------------
BASE_URL = "https://raw.githubusercontent.com/asmahaneef/-caseware--ai-analytics-dashboard/main/data/raw/"

@st.cache_data
def load_data():
    users = pd.read_csv(BASE_URL + "users.csv", parse_dates=["signup_date", "first_login_date"])
    firms = pd.read_csv(BASE_URL + "firms.csv", parse_dates=["signup_date"])
    product_events = pd.read_csv(BASE_URL + "product_events.csv", parse_dates=["event_timestamp"])
    ai_traces = pd.read_csv(BASE_URL + "ai_traces.csv", parse_dates=["timestamp"])
    funnel_steps = pd.read_csv(BASE_URL + "funnel_steps.csv", parse_dates=["step_timestamp"])
    return users, firms, product_events, ai_traces, funnel_steps

users, firms, product_events, ai_traces, funnel_steps = load_data()

# -----------------------------------------------------------------------
# Calculate the key numbers we already looked at
# -----------------------------------------------------------------------
activation_rate = users["is_activated"].sum() / len(users) * 100

activated_count = users["is_activated"].sum()
ai_adoption_rate = ai_traces["user_id"].nunique() / activated_count * 100

outcome_counts = ai_traces["outcome"].value_counts(normalize=True) * 100
acceptance_rate = outcome_counts.get("accepted", 0)

avg_latency = ai_traces["latency_ms"].mean()

# -----------------------------------------------------------------------
# Display as KPI cards across the top
# -----------------------------------------------------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Activation Rate", f"{activation_rate:.1f}%")
col2.metric("AI Adoption Rate", f"{ai_adoption_rate:.1f}%")
col3.metric("AI Acceptance Rate", f"{acceptance_rate:.1f}%")
col4.metric("Avg AI Latency", f"{avg_latency:.0f} ms")

st.divider()
st.write("More charts and the 'So What' recommendations section are coming in the next steps.")

# -----------------------------------------------------------------------
# Chart 1: AI Outcomes (accepted / edited / rejected)
# -----------------------------------------------------------------------
st.subheader("AI Output Outcomes")

outcome_df = ai_traces["outcome"].value_counts().reset_index()
outcome_df.columns = ["outcome", "count"]

fig_outcomes = px.pie(
    outcome_df,
    names="outcome",
    values="count",
    title="How users respond to AI-generated outputs",
    color="outcome",
    color_discrete_map={
        "accepted": "#2ca02c",
        "edited": "#ff7f0e",
        "rejected": "#d62728",
    },
)
st.plotly_chart(fig_outcomes, use_container_width=True)

st.caption(
    "Most AI outputs are accepted as-is, but roughly 1 in 5 are edited by the user before use — "
    "suggesting the AI works well as a first draft rather than a final answer."
)

# -----------------------------------------------------------------------
# Chart 2: AI Feature Popularity
# -----------------------------------------------------------------------
st.subheader("AI Feature Usage")

feature_counts = ai_traces["feature"].value_counts().reset_index()
feature_counts.columns = ["feature", "uses"]

fig_features = px.bar(
    feature_counts.sort_values("uses"),
    x="uses",
    y="feature",
    orientation="h",
    title="Number of times each AI feature was used",
    color="uses",
    color_continuous_scale="Blues",
)
st.plotly_chart(fig_features, use_container_width=True)

st.caption(
    "Usage is fairly evenly spread across features, with no single AI capability dramatically "
    "outperforming the others — worth investigating whether any one feature deserves deeper investment."
)

# -----------------------------------------------------------------------
# Chart 3: Usage by Firm Size Tier
# -----------------------------------------------------------------------
st.subheader("Usage by Firm Size")

events_with_firm = product_events.merge(firms[["firm_id", "firm_size_tier"]], on="firm_id")
traces_with_firm = ai_traces.merge(firms[["firm_id", "firm_size_tier"]], on="firm_id")

product_usage_by_size = events_with_firm.groupby("firm_size_tier")["event_id"].count().reset_index()
product_usage_by_size.columns = ["firm_size_tier", "product_events"]

ai_usage_by_size = traces_with_firm.groupby("firm_size_tier")["trace_id"].count().reset_index()
ai_usage_by_size.columns = ["firm_size_tier", "ai_interactions"]

usage_by_size = product_usage_by_size.merge(ai_usage_by_size, on="firm_size_tier")

# Melt into long format so Plotly can group the bars side by side
usage_by_size_long = usage_by_size.melt(
    id_vars="firm_size_tier",
    value_vars=["product_events", "ai_interactions"],
    var_name="metric",
    value_name="count",
)

firm_size_order = ["Small", "Mid-Market", "Large"]

fig_firm_size = px.bar(
    usage_by_size_long,
    x="firm_size_tier",
    y="count",
    color="metric",
    barmode="group",
    category_orders={"firm_size_tier": firm_size_order},
    title="Product events and AI interactions by firm size tier",
    labels={"firm_size_tier": "Firm Size", "count": "Total Count", "metric": "Metric"},
)
st.plotly_chart(fig_firm_size, use_container_width=True)

st.caption(
    "Small firms generate disproportionately more usage - both general product activity and AI "
    "interactions - relative to Mid-Market and Large firms. This is worth investigating: are small "
    "firms finding more value in the product, or are Large firms under-engaged with untapped potential?"
)

# -----------------------------------------------------------------------
# Chart 4: Funnel Stage Reach
# -----------------------------------------------------------------------
st.subheader("User Journey: Funnel Stage Reach")

funnel_order = ["signup", "first_login", "first_real_usage", "first_ai_use", "first_export"]
funnel_counts = funnel_steps["step_name"].value_counts().reindex(funnel_order).fillna(0).astype(int)

funnel_df = funnel_counts.reset_index()
funnel_df.columns = ["stage", "users"]

fig_funnel = px.funnel(
    funnel_df,
    x="users",
    y="stage",
    title="How many users reach each stage of the product journey",
)
st.plotly_chart(fig_funnel, use_container_width=True)

st.caption(
    "Note: these stages are tracked independently rather than as a strict cumulative funnel - "
    "for example, a user can export a report without ever using an AI feature. The steepest drop "
    "is between first login and first AI use, suggesting AI feature discovery/adoption is the "
    "biggest opportunity area in the user journey."
)

# -----------------------------------------------------------------------
# So What? Recommendations
# -----------------------------------------------------------------------
st.divider()
st.header("So What? What I'd Actually Do With This")

st.markdown("""
Looking at this data, three things stood out to me enough that I'd want to act on them if this were a real product.

**1. Almost half of active users never touch the AI features.**
84% of users log in, but only 58% of those ever try an AI feature — and the biggest single drop in the whole user journey is right there, between first login and first AI use. That's a bigger gap than I expected. Before building more AI features, I'd want to know *why*: is it that people don't notice the AI is there, or did they try it once and decide it wasn't worth it? Those are two completely different problems with two completely different fixes, and right now the data can't tell them apart — that's the first thing I'd instrument better.

**2. Small firms are punching way above their weight.**
Small firms make up a bit over half of all firms, but they're generating close to 3x the product usage and nearly 2.5x the AI usage of Large firms. That's not a small gap. My honest first read is that smaller firms probably have simpler workflows and fewer people needing to sign off before someone just tries a new feature, whereas larger firms likely have more process/approval layers slowing adoption down. I'd want to sit down with a few Large-firm admins and just ask them directly what's getting in the way — this feels like a rollout/change-management problem more than a product problem.

**3. People trust the AI, but they don't fully trust it.**
73% of AI outputs get accepted as-is, which is a good sign. But 22% get edited before use — that's a meaningful chunk of people who like the starting point but don't take it at face value. I don't think that's a bad thing on its own; it might just mean the AI is doing its job as a first draft rather than a final answer. What I'd actually track over time is whether that edit rate goes *down* as the AI improves — if it stays flat or climbs, that tells me something in the AI's quality or the way it explains its confidence needs work.

**One honest caveat:** the funnel numbers in the chart above aren't a strict cumulative funnel — a user can technically export a report without ever touching an AI feature, since those are tracked as separate milestones rather than forced steps. I kept it that way because it's more realistic to how people actually use a flexible product, but it does mean you shouldn't read the funnel percentages as "% of the previous stage" the way you would in a classic checkout funnel.
""")

st.caption("All data on this page is simulated and generated for this personal portfolio project. It is not real Caseware data and does not reflect any actual Caseware product, users, or metrics.")
