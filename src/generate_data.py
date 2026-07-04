"""
generate_data.py

Generates simulated data inspired by public product analytics and AI
observability themes in AI-powered audit/accounting software.

IMPORTANT: This is 100% synthetic/fake data. No real company, firm, user,
or product data is used anywhere in this project.

Running this script creates 7 CSV files inside data/raw/:
    users.csv
    firms.csv
    product_events.csv
    ai_traces.csv
    feature_adoption.csv
    funnel_steps.csv
    trust_signals.csv

How to run (from the project root folder, with your venv activated):
    python src/generate_data.py
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_FIRMS = 25
NUM_USERS = 250
SIM_START_DATE = datetime(2025, 1, 1)
SIM_END_DATE = datetime(2026, 6, 30)
TOTAL_DAYS = (SIM_END_DATE - SIM_START_DATE).days

FIRM_SIZE_TIERS = ["Small", "Mid-Market", "Large"]
FIRM_SIZE_WEIGHTS = [0.55, 0.30, 0.15]

PLAN_TIERS = ["Starter", "Professional", "Enterprise"]
USER_ROLES = ["Staff Accountant", "Senior Accountant", "Manager", "Partner", "Admin"]

AI_FEATURES = [
    "risk_summary_generator",
    "variance_explanation",
    "document_qa_assistant",
    "workpaper_draft_assistant",
    "anomaly_flagging",
]

NON_AI_EVENT_TYPES = [
    "login",
    "open_engagement",
    "upload_workpaper",
    "review_workpaper",
    "export_report",
    "invite_teammate",
]


def random_date(start, end):
    delta_days = (end - start).days
    random_days = random.randint(0, max(delta_days, 0))
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)


def generate_firms():
    firms = []
    for i in range(1, NUM_FIRMS + 1):
        firm_id = f"F{i:03d}"
        size_tier = np.random.choice(FIRM_SIZE_TIERS, p=FIRM_SIZE_WEIGHTS)
        signup_date = random_date(SIM_START_DATE, SIM_START_DATE + timedelta(days=200))
        firms.append({
            "firm_id": firm_id,
            "firm_name": fake.company() + " & Associates",
            "firm_size_tier": size_tier,
            "plan_tier": np.random.choice(PLAN_TIERS, p=[0.4, 0.4, 0.2]),
            "region": np.random.choice(["Ontario", "Quebec", "Western Canada", "Atlantic Canada"]),
            "signup_date": signup_date.date(),
        })
    return pd.DataFrame(firms)


def generate_users(firms_df):
    users = []
    firm_ids = firms_df["firm_id"].tolist()
    firm_signup_map = dict(zip(firms_df["firm_id"], firms_df["signup_date"]))

    for i in range(1, NUM_USERS + 1):
        user_id = f"U{i:04d}"
        firm_id = random.choice(firm_ids)
        firm_signup = firm_signup_map[firm_id]

        earliest = datetime.combine(firm_signup, datetime.min.time())
        signup_date = random_date(earliest, SIM_END_DATE)

        does_activate = random.random() < 0.85
        if does_activate:
            first_login_gap = np.random.exponential(scale=3)
            first_login_date = signup_date + timedelta(days=min(first_login_gap, 60))
        else:
            first_login_date = None

        users.append({
            "user_id": user_id,
            "firm_id": firm_id,
            "role": np.random.choice(USER_ROLES, p=[0.35, 0.25, 0.20, 0.10, 0.10]),
            "signup_date": signup_date.date(),
            "first_login_date": first_login_date.date() if first_login_date else None,
            "is_activated": does_activate,
        })
    return pd.DataFrame(users)


def generate_product_events(users_df):
    events = []
    event_id_counter = 1
    active_users = users_df[users_df["is_activated"]]

    for _, user in active_users.iterrows():
        first_login = datetime.combine(user["first_login_date"], datetime.min.time())
        engagement_level = np.random.choice(["low", "medium", "high"], p=[0.35, 0.40, 0.25])
        num_active_days = {"low": 5, "medium": 20, "high": 60}[engagement_level]
        churns = random.random() < {"low": 0.7, "medium": 0.35, "high": 0.1}[engagement_level]
        usage_window_days = random.randint(10, 120) if churns else (SIM_END_DATE - first_login).days
        usage_window_days = max(usage_window_days, 1)

        for _ in range(num_active_days):
            day_offset = random.randint(0, usage_window_days)
            event_time = first_login + timedelta(days=day_offset, seconds=random.randint(0, 86399))
            if event_time > SIM_END_DATE:
                continue
            event_type = np.random.choice(NON_AI_EVENT_TYPES)
            events.append({
                "event_id": f"E{event_id_counter:06d}",
                "user_id": user["user_id"],
                "firm_id": user["firm_id"],
                "event_type": event_type,
                "event_timestamp": event_time,
                "session_id": f"S{user['user_id']}_{day_offset}",
            })
            event_id_counter += 1

    return pd.DataFrame(events)


def generate_ai_traces(users_df):
    traces = []
    trace_id_counter = 1
    active_users = users_df[users_df["is_activated"]]

    for _, user in active_users.iterrows():
        first_login = datetime.combine(user["first_login_date"], datetime.min.time())
        tries_ai = random.random() < 0.6
        if not tries_ai:
            continue

        num_ai_uses = np.random.poisson(lam=8) + 1
        trust_tendency = np.random.beta(a=5, b=3)

        for _ in range(num_ai_uses):
            day_offset = random.randint(0, 150)
            event_time = first_login + timedelta(days=day_offset, seconds=random.randint(0, 86399))
            if event_time > SIM_END_DATE:
                continue

            feature = np.random.choice(AI_FEATURES)
            confidence_score = round(np.clip(np.random.normal(0.82, 0.14), 0.05, 0.99), 2)
            latency_ms = int(np.clip(np.random.exponential(scale=900) + 400, 200, 8000))

            accept_prob = np.clip(0.5 * confidence_score + 0.5 * trust_tendency, 0.05, 0.95)
            outcome_roll = random.random()
            if outcome_roll < accept_prob:
                outcome = "accepted"
            elif outcome_roll < accept_prob + 0.3:
                outcome = "edited"
            else:
                outcome = "rejected"

            retried = random.random() < (0.35 if confidence_score < 0.6 else 0.08)
            escalated = (confidence_score < 0.5 or outcome == "rejected") and random.random() < 0.4
            source_link_clicked = random.random() < 0.45

            traces.append({
                "trace_id": f"T{trace_id_counter:06d}",
                "user_id": user["user_id"],
                "firm_id": user["firm_id"],
                "feature": feature,
                "timestamp": event_time,
                "confidence_score": confidence_score,
                "latency_ms": latency_ms,
                "outcome": outcome,
                "retried": retried,
                "escalated_to_human": escalated,
                "source_link_clicked": source_link_clicked,
            })
            trace_id_counter += 1

    return pd.DataFrame(traces)


def generate_feature_adoption(ai_traces_df):
    if ai_traces_df.empty:
        return pd.DataFrame(columns=[
            "user_id", "firm_id", "feature", "first_used_at", "last_used_at", "total_uses"
        ])
    grouped = ai_traces_df.groupby(["user_id", "firm_id", "feature"]).agg(
        first_used_at=("timestamp", "min"),
        last_used_at=("timestamp", "max"),
        total_uses=("trace_id", "count"),
    ).reset_index()
    return grouped


def generate_funnel_steps(users_df, product_events_df, ai_traces_df):
    funnel_rows = []

    for _, user in users_df.iterrows():
        user_id = user["user_id"]
        firm_id = user["firm_id"]

        signup_time = datetime.combine(user["signup_date"], datetime.min.time())
        funnel_rows.append({
            "user_id": user_id, "firm_id": firm_id,
            "step_name": "signup", "step_timestamp": signup_time, "completed": True,
        })

        if pd.isna(user["first_login_date"]) or user["first_login_date"] is None:
            continue

        first_login_time = datetime.combine(user["first_login_date"], datetime.min.time())
        funnel_rows.append({
            "user_id": user_id, "firm_id": firm_id,
            "step_name": "first_login", "step_timestamp": first_login_time, "completed": True,
        })

        user_events = product_events_df[product_events_df["user_id"] == user_id]
        real_usage_events = user_events[user_events["event_type"] != "login"]
        if not real_usage_events.empty:
            first_real_usage = real_usage_events["event_timestamp"].min()
            funnel_rows.append({
                "user_id": user_id, "firm_id": firm_id,
                "step_name": "first_real_usage", "step_timestamp": first_real_usage, "completed": True,
            })

        user_traces = ai_traces_df[ai_traces_df["user_id"] == user_id]
        if not user_traces.empty:
            first_ai_use = user_traces["timestamp"].min()
            funnel_rows.append({
                "user_id": user_id, "firm_id": firm_id,
                "step_name": "first_ai_use", "step_timestamp": first_ai_use, "completed": True,
            })

        export_events = user_events[user_events["event_type"] == "export_report"]
        if not export_events.empty:
            first_export = export_events["event_timestamp"].min()
            funnel_rows.append({
                "user_id": user_id, "firm_id": firm_id,
                "step_name": "first_export", "step_timestamp": first_export, "completed": True,
            })

    return pd.DataFrame(funnel_rows)


def generate_trust_signals(ai_traces_df):
    signal_rows = []
    signal_id_counter = 1

    for _, trace in ai_traces_df.iterrows():
        if trace["escalated_to_human"]:
            signal_rows.append({
                "signal_id": f"TS{signal_id_counter:06d}",
                "user_id": trace["user_id"],
                "firm_id": trace["firm_id"],
                "trace_id": trace["trace_id"],
                "timestamp": trace["timestamp"],
                "signal_type": "escalated_to_human",
            })
            signal_id_counter += 1

        if random.random() < 0.15:
            if trace["outcome"] == "accepted":
                feedback = "positive_feedback"
            elif trace["outcome"] == "rejected":
                feedback = "negative_feedback"
            else:
                feedback = random.choice(["positive_feedback", "negative_feedback"])

            signal_rows.append({
                "signal_id": f"TS{signal_id_counter:06d}",
                "user_id": trace["user_id"],
                "firm_id": trace["firm_id"],
                "trace_id": trace["trace_id"],
                "timestamp": trace["timestamp"],
                "signal_type": feedback,
            })
            signal_id_counter += 1

    return pd.DataFrame(signal_rows)


def main():
    print("Generating firms...")
    firms_df = generate_firms()

    print("Generating users...")
    users_df = generate_users(firms_df)

    print("Generating product events...")
    product_events_df = generate_product_events(users_df)

    print("Generating AI traces...")
    ai_traces_df = generate_ai_traces(users_df)

    print("Generating feature adoption summary...")
    feature_adoption_df = generate_feature_adoption(ai_traces_df)

    print("Generating funnel steps...")
    funnel_steps_df = generate_funnel_steps(users_df, product_events_df, ai_traces_df)

    print("Generating trust signals...")
    trust_signals_df = generate_trust_signals(ai_traces_df)

    firms_df.to_csv(os.path.join(OUTPUT_DIR, "firms.csv"), index=False)
    users_df.to_csv(os.path.join(OUTPUT_DIR, "users.csv"), index=False)
    product_events_df.to_csv(os.path.join(OUTPUT_DIR, "product_events.csv"), index=False)
    ai_traces_df.to_csv(os.path.join(OUTPUT_DIR, "ai_traces.csv"), index=False)
    feature_adoption_df.to_csv(os.path.join(OUTPUT_DIR, "feature_adoption.csv"), index=False)
    funnel_steps_df.to_csv(os.path.join(OUTPUT_DIR, "funnel_steps.csv"), index=False)
    trust_signals_df.to_csv(os.path.join(OUTPUT_DIR, "trust_signals.csv"), index=False)

    print("\nDone! Files created in data/raw/:")
    print(f"  firms.csv            - {len(firms_df)} rows")
    print(f"  users.csv            - {len(users_df)} rows")
    print(f"  product_events.csv   - {len(product_events_df)} rows")
    print(f"  ai_traces.csv        - {len(ai_traces_df)} rows")
    print(f"  feature_adoption.csv - {len(feature_adoption_df)} rows")
    print(f"  funnel_steps.csv     - {len(funnel_steps_df)} rows")
    print(f"  trust_signals.csv    - {len(trust_signals_df)} rows")


if __name__ == "__main__":
    main()
