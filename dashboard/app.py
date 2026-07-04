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
Looking at this data, three things stood out enough that I'd want to act on them if this were a real product.

**1. Almost half of active users never touch the AI features, and real industry data backs up why that's normal, not alarming.**
84% of users log in, but only 58% of those ever try an AI feature. My first instinct was that this must be a trust problem. But looking at actual research on AI adoption in accounting and audit, the bigger issue across the industry usually isn't trust. It's that people don't know what the AI can actually do for their daily work, and most firms still haven't trained staff on it at all. One widely cited 2025 industry report found that 85% of accounting professionals were excited about AI, but only 37% of firms had invested in any AI training. That gap between curiosity and actual habitual use shows up everywhere in the real data, not just in this simulation. So instead of assuming people don't trust the AI, I'd want to find out if they even know what it's for.

**2. Small firms showing more usage in my data is a plausible story, but I checked, and the real research is actually split on this, which is a useful lesson on its own.**
In my simulated data, small firms generate close to 3x the usage of large firms. My first read was that small firms move faster because they have less bureaucracy. That's a real pattern some industry sources describe. But other 2026 industry data shows the opposite: large firms actually adopting AI faster overall, precisely because they have more budget and staff time to invest in training. So the honest answer is that firm size alone doesn't predict AI usage in a clean, one directional way. If I saw this pattern in a real product, I wouldn't act on the firm size story alone. I'd want to talk to actual small firm and large firm users directly before drawing conclusions, since the research shows this could go either way depending on how well each firm invests in onboarding and training.

**3. People trust the AI, but not fully, and that's not a flaw, it's expected behavior in this industry.**
73% of AI outputs get accepted as is, but 22% get edited before use. That tracks with something real practitioners say directly: accountants worry that leaning too much on AI risks losing the professional judgment their clients are actually paying for. So a 22% edit rate isn't a red flag on its own. It might mean the AI is doing its job as a first draft, while people still apply their own judgment on top, which is exactly the behavior the profession says it wants. What I'd actually track over time is whether that edit rate trends down as the AI improves, or whether it stays flat. That tells you something real about whether the tool is earning more trust or just being tolerated.

**What I'd prioritize first, based on both my data and the research:** training and clear, concrete use case examples, not just more AI features. Across nearly every real industry report I looked at, the single most consistent lever for higher AI usage wasn't a better model. It was whether firms actually showed people how and when to use it, with small, low stakes examples they could try safely. That's a cheaper and more addressable fix than trying to make the AI itself more "trustworthy" in the abstract.

**One honest caveat on the funnel chart above:** the stages aren't a strict cumulative funnel. A user can export a report without ever touching an AI feature, since these are tracked as separate milestones rather than forced steps. I kept it that way because it's closer to how people actually use a flexible product, but it does mean you shouldn't read the funnel percentages as "percent of the previous stage," the way you would in a classic checkout funnel.
""")

st.subheader("Grounded in Real Industry Research")
st.markdown("""
The patterns above aren't just guesses. They're consistent with real, recent research on AI adoption in accounting and audit:

* Only about 25% of internal auditors report actively using AI day to day, even though a much larger share are curious or piloting it, showing a real gap between interest and habitual use, not just in this simulation. ([Audit Beacon, 2025](https://www.richardchambers.com/five-barriers-slowing-ai-adoption-in-internal-audit/))
* The most commonly cited barriers are lack of in house expertise and limited understanding of what AI can actually do day to day, not necessarily distrust of the technology itself. ([Audit Beacon, 2025](https://www.richardchambers.com/five-barriers-slowing-ai-adoption-in-internal-audit/))
* Firms that invest in AI training see meaningfully higher confidence and lower skepticism among staff, yet training investment still lags behind interest industry wide. ([Accountancy Age, 2025](https://accountancyage.com/2025/02/19/the-real-ai-divide-in-accounting-is-between-the-fearful-and-the-fearless/))
* Firm size effects on adoption speed are genuinely mixed across sources. Some report large firms adopting faster due to training budgets, others report small firms moving faster due to less internal bureaucracy. ([Forbes Technology Council, 2026](https://www.forbes.com/councils/forbestechcouncil/2026/04/09/why-small-accounting-firms-face-more-ai-risk-than-large-ones/), [Thomson Reuters, 2026](https://tax.thomsonreuters.com/blog/small-accounting-firm-tech-adoption-the-secret-superpower-that-large-practices-cant-match/))

I'm including these sources so the recommendations above are grounded in real industry context, not just this simulated dataset in isolation.
""")

st.caption("All data on this page is simulated and generated for this personal portfolio project. It is not real Caseware data and does not reflect any actual Caseware product, users, or metrics.")
