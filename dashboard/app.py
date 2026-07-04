import streamlit as st
import pandas as pd

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
