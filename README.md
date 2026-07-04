# Caseware-Inspired AI Product Analytics & Trust Dashboard
Simulated AI product analytics dashboard, inspired by public AI/audit product themes
**Live dashboard:** https://analytics-ai-dashboard.streamlit.app/

This is a personal portfolio project. It is **not affiliated with Caseware** and uses **no real Caseware data**. Everything here, including users, firms, product events, and AI interactions, is simulated data inspired by public product analytics and AI observability themes in AI-powered audit and accounting software.

---

## Why I Built This

I'm pivoting from a business and financial services background (TD Bank, MBA from Ivey) into AI product and data analytics roles. I wanted a project that proved I can do the actual work of a Product Analyst on an AI/data platform team, not just talk about it. That means going beyond a single chart or metric and showing the full loop: generating realistic data, calculating the metrics that actually matter for an AI feature, building something interactive and turning the numbers into a real recommendation, the way I'd do it on the job.

I chose to theme this project around Caseware's public direction (AI powered audit and accounting workflows) because reasoning through this specific problem space, rather than a generic dataset, is what makes the analysis feel real instead of academic.

## The Business Problem

When a product adds AI features, the usual metrics (logins, clicks, page views) stop being enough. You also need to know things like:

* Are people actually trying the AI features, or ignoring them?
* When the AI gives an answer, do people accept it, edit it, or reject it outright?
* Where does the AI struggle (low confidence responses, training or lack of knowledge for use cases, retries, escalations to a human reviewer)?
* Does usage differ across different types of customers (in this case, firms of different sizes)?
* Is the AI actually saving people time and building trust over time, or creating more work?

This project simulates a fictional audit and accounting SaaS product with AI features, and builds the kind of dashboard a Product Analyst would use to answer exactly these questions.

## The Simulated Dataset

All data is synthetic, generated with a fixed random seed for reproducibility, using Python (pandas, numpy, faker). No real company, firm, or individual is represented. Seven datasets are generated:

| Dataset | What it represents |
|---|---|
| `firms.csv` | Fictional accounting firms using the product (size tier, plan, region, signup date) |
| `users.csv` | Individual users at each firm (role, signup date, activation status) |
| `product_events.csv` | General product usage events (logins, opening files, exporting reports, etc.) |
| `ai_traces.csv` | Every AI assistant interaction, including confidence score, latency, outcome (accepted, edited, rejected), retries, and escalation to a human reviewer |
| `feature_adoption.csv` | Per user, per AI feature summary of first use, last use, and total uses |
| `funnel_steps.csv` | Key milestones in the user journey (signup, first login, first real usage, first AI use, first export) |
| `trust_signals.csv` | Explicit trust related events, like human escalations and positive or negative feedback on AI outputs |

The data generation script is at `src/generate_data.py`, fully commented, and reproducible: running it with the same random seed produces the same dataset every time.

## Key Metrics

The dashboard and underlying analysis cover:

* **Activation:** percentage of signed up users who ever log in
* **AI adoption:** percentage of active users who try at least one AI feature, and which features are most and least used
* **Engagement:** average product events per active user
* **Retention:** early churn estimate based on how long users stay active
* **Firm level usage:** how usage differs across small, mid market, and large firms
* **AI trust metrics:** acceptance, edit, and rejection rates, retry rate, human escalation rate, low confidence response rate, and average latency
* **Funnel drop off:** where in the user journey the biggest gaps appear

## How to Run This Project

**Option 1: Just view the live dashboard**
No setup needed. Visit https://analytics-ai-dashboard.streamlit.app/

**Option 2: Regenerate the data yourself**
1. Open a new notebook in [Google Colab](https://colab.research.google.com/)
2. Install the one extra dependency Colab doesn't already have: `!pip install faker`
3. Copy the contents of `src/generate_data.py` into a cell and run it
4. This regenerates all 7 CSVs with the same fixed random seed, so results are reproducible

**Option 3: Run the dashboard locally**
1. Clone or download this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run dashboard/app.py`

## Limitations

* All data is synthetic and does not reflect any real company's actual metrics, users, or product behavior.
* The funnel is tracked as independent milestones rather than a strict cumulative funnel. For example, a user can export a report without ever using an AI feature, so funnel percentages should not be read the same way as a classic sequential conversion funnel.
* The firm size versus usage pattern in this simulated data is a plausible story, but real industry research on this topic is genuinely mixed. Some studies show large firms adopting AI faster due to greater training budgets, while others show small firms moving faster due to less internal bureaucracy. I call this out directly in the dashboard's So What section rather than treating my simulated finding as a universal truth.
* Retry, escalation, and confidence thresholds are simulated using reasonable assumptions, not derived from any real system's actual AI behavior.

## Future Improvements

* Add a time series view to track how AI trust metrics (acceptance rate, edit rate, escalation rate) change over time, rather than only showing point in time totals
* Add filtering controls so a viewer can slice the dashboard by firm size, region, or plan tier
* Add a cohort based retention view (for example, week 1 versus week 4 versus week 8 retention by signup cohort)
