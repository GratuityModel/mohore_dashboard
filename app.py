import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline import *

# ==========================================================
# CONFIG
# ==========================================================

st.set_page_config(layout="wide")

st.markdown("""
<style>

/* ============================= */
/* GLOBAL BACKGROUND + TEXT      */
/* ============================= */

.stApp {
    background-color: #ffffff !important;
    color: #111111 !important;
}

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}

html, body {
    color: #111111 !important;
}

/* ============================= */
/* SELECTBOX MAIN BOX            */
/* ============================= */

[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* ============================= */
/* DROPDOWN MENU (SAFE TARGET)   */
/* ============================= */

div[data-baseweb="popover"] ul {
    background-color: #ffffff !important;
}

div[data-baseweb="popover"] li {
    background-color: #ffffff !important;
    color: #111111 !important;
}

div[data-baseweb="popover"] li:hover {
    background-color: #f2f2f2 !important;
}

/* ============================= */
/* NUMBER INPUT FIX              */
/* ============================= */

[data-testid="stNumberInput"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px !important;
}

[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #111111 !important;
    border: none !important;
}

[data-testid="stNumberInput"] button {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* ============================= */
/* METRICS                       */
/* ============================= */

[data-testid="stMetricLabel"] {
    color: #555555 !important;
}

[data-testid="stMetricValue"] {
    color: #111111 !important;
}

            
/* ============================= */
/* FIX TABS VISIBILITY           */
/* ============================= */

/* Inactive tabs */
button[data-baseweb="tab"] {
    color: #444444 !important;
    font-weight: 600 !important;
}

/* Active tab */
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1f3c66 !important;
    border-bottom: 3px solid #1f3c66 !important;
}

/* Remove weird dark background */
div[data-baseweb="tab-list"] {
    background-color: #ffffff !important;
}

            

* ============================= */
/* FIX LABEL VISIBILITY          */
/* ============================= */

/* All input labels */
label {
    color: #222222 !important;
    font-weight: 600 !important;
}

/* Sidebar labels specifically */
[data-testid="stSidebar"] label {
    color: #222222 !important;
    font-weight: 600 !important;
}

/* Section headers in sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #111111 !important;
}

/* Make small helper text darker */
small {
    color: #444444 !important;
}            

</style>
""", unsafe_allow_html=True)



BASE_YEAR = 2025
BASE_RETURN = 0.04
BASE_LEAKAGE = 0.28

# ==========================================================
# CLEAN WHITE THEME
# ==========================================================

st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #000000; }
.block-container { padding-top: 1.5rem; }
[data-testid="stSidebar"] { background-color: #ffffff; }
html, body, [class*="css"] { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 UAE -  Mandatory Gratuity  Savings - Funding & Economic Impact analysis \n for Private Expatriate employees")

# ==========================================================
# FILES
# ==========================================================

INDUSTRY_DESC = "data/Industry Desc.xlsx"
INDUSTRY_RATES = "data/P2 Industry rates.xlsx"
EMPLOYEE_SALARY = "data/Employee_Salary_Data_2025.xlsx"
META_INFO = "data/Meta_info.csv"
ECONOMIC_FILE = "data/Economic Parameters.xlsx"

# ==========================================================
# LOAD BASE DATA
# ==========================================================

@st.cache_data
def load_base():
    return generate_merged_industry_data(
        INDUSTRY_DESC,
        INDUSTRY_RATES
    )

merged_df = load_base()

if "industry_assumptions" not in st.session_state:
    st.session_state.industry_assumptions = merged_df.copy()

# ==========================================================
# LOAD SURVIVAL TEMPLATES
# ==========================================================

@st.cache_data
def load_templates():
    return (
        generate_new_employee_survival_template(META_INFO),
        generate_old_employee_survival_template(META_INFO)
    )

new_template, old_template = load_templates()


# ==========================================================
# ECONOMIC LAYER (SectorMap Based)
# ==========================================================

@st.cache_data
def run_economic_layer(industry_year_df, economic_file, leakage_rate):

    economic_df = pd.read_excel(economic_file)

    df = industry_year_df.copy()

    # Normalize
    df["industry"] = df["industry"].str.lower().str.strip()
    economic_df["Industry"] = economic_df["Industry"].str.lower().str.strip()

    # Map industry → SectorMap
    df = df.merge(
        economic_df[["Industry", "SectorMap"]],
        left_on="industry",
        right_on="Industry",
        how="left"
    )

    # Sector multipliers
    sector_mult = economic_df[[
        "SectorMap",
        "Output_Multiplier_Type_I",
        "GVA_to_Output_Ratio",
        "Employment_Multiplier (jobs per AED 1M output)"
    ]].drop_duplicates()

    df = df.merge(sector_mult, on="SectorMap", how="left")

    # Allocate contribution proportionally
    df["yearly_total_payroll"] = (
        df.groupby("year")["annual_total_salary"].transform("sum")
    )

    df["yearly_total_contribution"] = (
        df.groupby("year")["annual_fund_contribution"].transform("sum")
    )

    df["Contrib_Allocated"] = (
        df["yearly_total_contribution"]
        * df["annual_total_salary"]
        / df["yearly_total_payroll"]
    ).fillna(0)

    df["Domestic_Investable"] = (
        df["Contrib_Allocated"] * (1 - leakage_rate)
    )

    # Economic Impacts
    df["Output_Impact"] = (
        df["Output_Multiplier_Type_I"] * df["Domestic_Investable"]
    )

    df["GVA_Impact"] = (
        df["GVA_to_Output_Ratio"] * df["Domestic_Investable"]
    )

    df["Jobs_Impact"] = (
        df["Employment_Multiplier (jobs per AED 1M output)"]
        * (df["Domestic_Investable"]/ 1_000_000)
    )

    return df



# ==========================================================
# ENGINE FUNCTIONS
# ==========================================================

@st.cache_data
def run_full_engine(industry_assumptions,
                    fund_return,
                    leakage_rate):

    # Employee forecast
    emp_forecast, sal_forecast = generate_employee_salary_forecast(
        EMPLOYEE_SALARY,
        industry_assumptions
    )

    # Survival templates
    new_surv, old_surv = attach_exit_rates(
        industry_assumptions,
        new_template,
        old_template
    )

    # Fund layer
    new_final = generate_new_employee_full_calculation(
        new_surv,
        emp_forecast,
        sal_forecast,
        fund_return
    )

    old_final = generate_old_employee_full_calculation(
        old_surv,
        emp_forecast,
        sal_forecast,
        fund_return
    )

    combined_df, _ = combine_new_old_results(
        new_final,
        old_final
    )

    industry_year = aggregate_industry_year(combined_df)

    # Economic layer (SectorMap)
    impact_df = run_economic_layer(
        industry_year,
        ECONOMIC_FILE,
        leakage_rate
    )

    # Drop base year
    combined_df = combined_df[
        combined_df["year"] > BASE_YEAR
    ]

    industry_year = industry_year[
        industry_year["year"] > BASE_YEAR
    ]

    impact_df = impact_df[
        impact_df["year"] > BASE_YEAR
    ]

    return combined_df, industry_year, impact_df


# ==========================================================
# SIDEBAR – FULL ASSUMPTION PANEL
# ==========================================================

with st.sidebar:

    st.header("⚙ Industry Assumptions")

    selected_industry = st.selectbox(
        "Industry",
        sorted(st.session_state.industry_assumptions["Industry"].unique())
    )

    industry_df = st.session_state.industry_assumptions[
        st.session_state.industry_assumptions["Industry"] == selected_industry
    ]

    age_options = ["All"] + sorted(industry_df["Age_Bracket"].unique())

    selected_age = st.selectbox(
        "Age Bracket",
        age_options
    )

    if selected_age != "All":
        row_idx = industry_df[
            industry_df["Age_Bracket"] == selected_age
        ].index[0]
        row = st.session_state.industry_assumptions.loc[row_idx]
    else:
        row = industry_df.mean(numeric_only=True)

    st.markdown("### Editable Rates")

    exp = st.number_input("Expansion Hiring %",
                          0.0, 1.0,
                          float(row["Expansion Hiring %"]), step=0.01)

    rep = st.number_input("Replacement Hiring %",
                          0.0, 1.0,
                          float(row["Replacement Hiring %"]), step=0.01)

    attr = st.number_input("Attrition %",
                           0.0, 1.0,
                           float(row["Attrition %"]), step=0.01)

    ret = st.number_input("Retirement Rate",
                          0.0, 1.0,
                          float(row["Retirement Rate"]), step=0.01)

    death = st.number_input("Death Rate",
                            0.0, 1.0,
                            float(row["Death Rate"]), step=0.01)

    sal_g = st.number_input("Salary Growth %",
                            0.0, 0.20,
                            float(row["Salary Growth %"]), step=0.005)

    if st.button("Update Assumptions"):

        df = st.session_state.industry_assumptions

        if selected_age != "All":

            df.loc[row_idx, [
                "Expansion Hiring %",
                "Replacement Hiring %",
                "Attrition %",
                "Retirement Rate",
                "Death Rate",
                "Salary Growth %"
            ]] = [exp, rep, attr, ret, death, sal_g]

        else:
            df.loc[
                df["Industry"] == selected_industry,
                [
                    "Expansion Hiring %",
                    "Replacement Hiring %",
                    "Attrition %",
                    "Retirement Rate",
                    "Death Rate",
                    "Salary Growth %"
                ]
            ] = [exp, rep, attr, ret, death, sal_g]


        df["Total Hiring %"] = (
            df["Expansion Hiring %"] +
            df["Replacement Hiring %"]
        )

        df["Total Exit (q)"] = (
            df["Attrition %"] +
            df["Retirement Rate"] +
            df["Death Rate"]
        )

        df["Net Churn %"] = (
            df["Total Hiring %"] -
            df["Total Exit (q)"]
        )

        st.success("Assumptions Updated ✔")

    st.markdown("---")
    st.header("🌍 Global Controls")

    fund_return = st.slider(
        "Fund Return %",
        0.0, 12.0, 4.0
    ) / 100

    leakage = st.slider(
        "Leakage %",
        0.0, 50.0, 28.0
    ) / 100


# ==========================================================
# STATIC BASELINE (DOES NOT CHANGE)
# ==========================================================

combined_static, industry_static, impact_static = run_full_engine(
    merged_df,
    BASE_RETURN,
    BASE_LEAKAGE
)

# ==========================================================
# GLOBAL BASELINE SUMMARY
# ==========================================================

st.markdown("## 🌍 Global Baseline Overview (Policy Scenario)")

# -----------------------------------------
# Year Filter (Baseline Only)
# -----------------------------------------

year_options = ["All"] + sorted(industry_static["year"].unique())

baseline_year = st.selectbox(
    "Select Year (Baseline Scenario)",
    year_options,
    key="baseline_year_filter"
)

# Filter static data for selected year
if baseline_year == "All":

    industry_static_year = industry_static.copy()
    impact_static_year = impact_static.copy()

else:

    industry_static_year = industry_static[
        industry_static["year"] == baseline_year
    ]

    impact_static_year = impact_static[
        impact_static["year"] == baseline_year
    ]

# -----------------------------------------
# KPI GRID (YEAR-SPECIFIC)
# -----------------------------------------

c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

c1.metric("Payroll (Bn)",
          f"{industry_static_year['annual_total_salary'].sum()/1e9:.2f}")

c2.metric("EOSG Contribution (Bn)",
          f"{industry_static_year['annual_fund_contribution'].sum()/1e9:.2f}")

c3.metric("Fund Balance (Bn)",
          f"{industry_static_year['closing_fund_with_return'].sum()/1e9:.2f}")

c4.metric("GDP Impact (Bn)",
          f"{impact_static_year['GVA_Impact'].sum()/1e9:.2f}")

c5.metric("Jobs Impact",
          f"{int(impact_static_year['Jobs_Impact'].sum()):,}")

c6.metric("Output Impact (Bn)",
          f"{impact_static_year['Output_Impact'].sum()/1e9:.2f}")


st.markdown("## 🌍 Full Economy Structure")

if baseline_year == "All":

    eco_baseline = impact_static.copy()

    # Aggregate across all years by Sector
    eco_baseline = eco_baseline.groupby("SectorMap").agg({
        "Output_Impact": "sum",
        "GVA_Impact": "sum",
        "Jobs_Impact": "sum"
    }).reset_index()

else:

    eco_baseline = impact_static[
        impact_static["year"] == baseline_year
    ].copy()

# Convert units
eco_baseline["Output_Bn"] = eco_baseline["Output_Impact"] / 1_000_000_000
eco_baseline["GVA_Bn"] = eco_baseline["GVA_Impact"] / 1_000_000_000
eco_baseline["Jobs_K"] = eco_baseline["Jobs_Impact"] / 1_000


# Aggregate by Sector
eco_grouped = eco_baseline.groupby("SectorMap").agg({
    "Output_Bn": "sum",
    "GVA_Bn": "sum",
    "Jobs_K": "sum"
}).reset_index()

fig = go.Figure()

# ----------------------------------
# Output Bars
# ----------------------------------
fig.add_trace(go.Bar(
    x=eco_grouped["SectorMap"],
    y=eco_grouped["Output_Bn"],
    name="Output Impact (Bn)",
    marker_color="#1f77b4"
))

# ----------------------------------
# GVA Bars
# ----------------------------------
fig.add_trace(go.Bar(
    x=eco_grouped["SectorMap"],
    y=eco_grouped["GVA_Bn"],
    name="GVA Impact (Bn)",
    marker_color="#2ca02c"
))

# ----------------------------------
# Jobs Line (Secondary Axis)
# ----------------------------------
fig.add_trace(go.Scatter(
    x=eco_grouped["SectorMap"],
    y=eco_grouped["Jobs_K"],
    name="Jobs Impact (Thousand)",
    mode="lines+markers",
    yaxis="y2",
    marker=dict(color="#ff7f0e", size=8),
    line=dict(width=3)
))

fig.update_layout(
    barmode="group",
    template="plotly_white",
    height=600,
    xaxis=dict(title="Sector"),
    yaxis=dict(title="Impact (Bn)"),
    yaxis2=dict(
        title="Jobs Impact (Thousand)",
        overlaying="y",
        side="right",
        showgrid=False
    ),
    legend=dict(
        orientation="h",
        y=1.1
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📈 Evolution Over Years (Selected Sectors)")

# ---------------------------------------------
# Sector Filter (same categories as bar chart)
# ---------------------------------------------

sector_options = sorted(impact_static["SectorMap"].unique())

selected_sectors = st.multiselect(
    "Select Sectors",
    sector_options,
    default=sector_options
)

evo_df = impact_static[
    impact_static["SectorMap"].isin(selected_sectors)
].copy()

# Convert units
evo_df["Output_Bn"] = evo_df["Output_Impact"] / 1_000_000_000
evo_df["GVA_Bn"] = evo_df["GVA_Impact"] / 1_000_000_000
evo_df["Jobs_K"] = evo_df["Jobs_Impact"] / 1_000

# Aggregate by Year
evo_year = evo_df.groupby("year").agg({
    "Output_Bn": "sum",
    "GVA_Bn": "sum",
    "Jobs_K": "sum"
}).reset_index()

# ---------------------------------------------
# Line Chart
# ---------------------------------------------

fig_evo = go.Figure()

# Output
fig_evo.add_trace(go.Scatter(
    x=evo_year["year"],
    y=evo_year["Output_Bn"],
    name="Output (Bn)",
    mode="lines+markers",
    line=dict(color="#1f77b4", width=3)
))

# GVA
fig_evo.add_trace(go.Scatter(
    x=evo_year["year"],
    y=evo_year["GVA_Bn"],
    name="GVA (Bn)",
    mode="lines+markers",
    line=dict(color="#2ca02c", width=3)
))

# Jobs – Bar on secondary axis
fig_evo.add_trace(go.Bar(
    x=evo_year["year"],
    y=evo_year["Jobs_K"],
    name="Jobs (K)",
    marker_color="#ff7f0e",
    yaxis="y2",
    opacity=0.4
))

fig_evo.update_layout(
    template=None,   # 🔥 disable plotly theme
    paper_bgcolor="white",
    plot_bgcolor="white",

    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor="black",
        mirror=True
    ),

    yaxis=dict(
        title="Impact (Bn)",
        showgrid=False,
        showline=True,
        linecolor="black",
        mirror=True
    ),

    yaxis2=dict(
        title="Jobs (Thousand)",
        overlaying="y",
        side="right",
        showgrid=False,
        showline=True,
        linecolor="black"
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),

    height=500
)

st.plotly_chart(fig_evo, use_container_width=True)


# ==========================================================
# DYNAMIC SCENARIO (FULL ENGINE RUN ONCE)
# ==========================================================

combined_full, industry_full, impact_full = run_full_engine(
    st.session_state.industry_assumptions,
    fund_return,
    leakage
)


# Filtered data for selected industry + age
selected_industry_lower = selected_industry.lower()
selected_age_lower = selected_age.lower()

if selected_age != "All":

    combined_dyn = combined_full[
        (combined_full["industry"] == selected_industry_lower) &
        (combined_full["age_bucket"] == selected_age_lower)
    ]

else:
    combined_dyn = combined_full[
        combined_full["industry"] == selected_industry_lower
    ]


industry_dyn = aggregate_industry_year(combined_dyn)

impact_dyn = run_economic_layer(
    industry_dyn,
    ECONOMIC_FILE,
    leakage
)

# Full economy for economic tab
impact_economy = impact_full


# ==========================================================
# SCENARIO TABS
# ==========================================================

st.markdown("## ⚙ Scenario Analysis")

tabs = st.tabs([
    "Jobs Impact",
    "Fund Risk",
    "Economic",
    "EOSG & Payroll",
    "Individual Benefit"
])

# ==========================================================
# JOBS IMPACT (ASSUMPTION LINKED)
# ==========================================================

with tabs[0]:

    jobs_df = impact_dyn.groupby("year")["Jobs_Impact"].sum().reset_index()
    jobs_df["Jobs_K"] = jobs_df["Jobs_Impact"] / 1_000

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=jobs_df["year"],
        y=jobs_df["Jobs_K"],
        marker_color="#0b3d91",
        text=[f"{v:.2f}K" for v in jobs_df["Jobs_K"]],
        textposition="outside"
    ))

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Jobs Impact (Thousand)"
    )

    st.plotly_chart(fig, use_container_width=True)



# Fund Risk
with tabs[1]:

    fig = go.Figure()

    comparison_rates = [0.04, 0.08, 0.11]

    for r, color in zip(comparison_rates,
                        ["#1f77b4","#2ca02c","#ff7f0e"]):

        _, ind_tmp, _ = run_full_engine(
            st.session_state.industry_assumptions,
            r,
            leakage
        )

        ind_tmp = ind_tmp.groupby("year")[
            "closing_fund_with_return"
        ].sum().reset_index()

        fig.add_trace(go.Scatter(
            x=ind_tmp["year"],
            y=ind_tmp["closing_fund_with_return"]/1e9,
            name=f"{int(r*100)}%",
            line=dict(color=color, width=2)
        ))

    # 🔥 Recalculate selected scenario fresh (NOT using cached industry_dyn)
    _, selected_industry, _ = run_full_engine(
        st.session_state.industry_assumptions,
        fund_return,
        leakage
    )

    selected_industry = selected_industry.groupby("year")[
        "closing_fund_with_return"
    ].sum().reset_index()

    fig.add_trace(go.Scatter(
        x=selected_industry["year"],
        y=selected_industry["closing_fund_with_return"]/1e9,
        name="Selected Scenario",
        line=dict(color="#d62728", width=4)
    ))

    fig.update_layout(
        yaxis_title="Fund Balance (Bn)",
        legend=dict(orientation="h")
    )

    st.plotly_chart(fig, use_container_width=True)

# Economic
with tabs[2]:

    st.markdown("### Economic Impact (Scenario Driven) - All industry Groups Included")

    economic_year = st.selectbox(
        "Select Year",
        sorted(impact_full["year"].unique()),
        key="economic_tab_year"
    )

    # 🔥 Use FULL impact (no industry filter)
    eco = impact_full[
        impact_full["year"] == economic_year
    ].copy()

    eco["Output_Bn"] = eco["Output_Impact"] / 1_000_000
    eco["GVA_Bn"] = eco["GVA_Impact"] / 1_000_000
    eco["Jobs_K"] = eco["Jobs_Impact"] / 1_000

    c1, c2, c3 = st.columns(3)

    c1.plotly_chart(
        px.pie(
            eco,
            names="SectorMap",
            values="Output_Bn",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set2
        ).update_traces(
            texttemplate="%{value:.2f} Mn"
        ).update_layout(template="plotly_white"),
        use_container_width=True
    )

    c2.plotly_chart(
        px.pie(
            eco,
            names="SectorMap",
            values="GVA_Bn",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        ).update_traces(
            texttemplate="%{value:.2f} Mn"
        ).update_layout(template="plotly_white"),
        use_container_width=True
    )

    c3.plotly_chart(
        px.pie(
            eco,
            names="SectorMap",
            values="Jobs_K",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        ).update_traces(
            texttemplate="%{value:.2f} K"
        ).update_layout(template="plotly_white"),
        use_container_width=True
    )



# EOSG & Payroll
with tabs[3]:

    compare = industry_dyn.groupby("year").agg({
        "annual_total_salary": "sum",
        "closing_fund_with_return": "sum"
    }).reset_index()

    fig = go.Figure()

    # -------------------------------
    # Payroll Bars (Light Color)
    # -------------------------------
    fig.add_trace(go.Bar(
        x=compare["year"],
        y=compare["annual_total_salary"] / 1e9,
        name="Payroll",
        marker_color="#9ecae1",  # light blue
        yaxis="y2"
    ))

    # -------------------------------
    # Fund Line (Dark & On Top)
    # -------------------------------
    fig.add_trace(go.Scatter(
        x=compare["year"],
        y=compare["closing_fund_with_return"] / 1e9,
        name="Fund",
        mode="lines+markers",
        line=dict(color="#90EE90", width=4),  # green
        marker=dict(size=7)
    ))

    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis=dict(
            title="Fund (Bn)",
            showgrid=True
        ),
        yaxis2=dict(
            title="Payroll (Bn)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(orientation="h", y=1.1)
    )

    st.plotly_chart(fig, use_container_width=True)


# Individual Benefit
with tabs[4]:

    sim_year = st.selectbox(
        "Exit Year",
        sorted(combined_dyn["year"].unique())
    )

    sim_tenure = st.slider("Tenure", 0, 30, 5)

    sim = combined_dyn[
        (combined_dyn["year"] == sim_year) &
        (combined_dyn["tenure"].round() == sim_tenure) &
        (combined_dyn["exit_employee"] > 0)
    ]

    if len(sim) > 0:

        avg_no = (
            sim["exit_payout_no_return"].sum()
            / sim["exit_employee"].sum()
        )

        avg_wr = (
            sim["exit_payout_with_return"].sum()
            / sim["exit_employee"].sum()
        )

        c1, c2 = st.columns(2)
        c1.metric("No Return", f"{avg_no:,.0f}")
        c2.metric("With Return", f"{avg_wr:,.0f}")
