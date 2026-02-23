import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline import *
from PIL import Image

def download_csv_button(df, filename, label="Download CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )

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
    background-color: #EFD59B !important;
}

/* ============================= */
/* NUMBER INPUT FIX              */
/* ============================= */

[data-testid="stNumberInput"] > div {
    background-color: #ffffff !important;
    border: 1px solid #77878C !important;
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
/* ===== EOSG Calculator Styling ===== */

h2, h3 {
    color: #000000 !important;
    font-weight: 700 !important;
}

label {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

[data-testid="stMetricLabel"] {
    color: #000000 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #000000 !important;
    font-size: 28px !important;
    font-weight: 700 !important;
}

[data-testid="stNumberInput"] input {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #000000 !important;
}

div[data-testid="stDownloadButton"] button {
    background-color: #ffffff !important;
    color: #053048 !important;
    border: 1px solid #053048 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background-color: #F5B718 !important;
    color: #000000 !important;
    border: 1px solid #F5B718 !important;
}
</style>
""", unsafe_allow_html=True)



BASE_YEAR = 2025
BASE_RETURN = 0.08
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

header_col1, header_col2 = st.columns([6, 1])

with header_col2:
    st.markdown(
        """
        <div style="margin-top:20px;">
        """,
        unsafe_allow_html=True
    )

    logo = Image.open("data/Synarchy_Primary_Logo - Blue Synarchy.png")
    st.image(logo, width=180)

    st.markdown("</div>", unsafe_allow_html=True)

with header_col1:
    st.title("UAE - Mandatory Gratuity Savings - Funding & Economic Impact Analysis")

    st.markdown(
        """
        <div style="
            font-size:28px;
            font-weight:700;
            color:#053048;
            margin-top:-10px;">
            For Private Expatriate Employees
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div style="
        text-align:left;
        font-size:12px;
        color:#000000;
        margin-top:8px;">
        * All currency values are expressed in AED (United Arab Emirates Dirham).
    </div>
    """,
    unsafe_allow_html=True
)


INDUSTRY_DESC = "data/Industry Desc.csv"
INDUSTRY_RATES = "data/P2 Industry rates.csv"
EMPLOYEE_SALARY = "data/Employee_Salary_Data_2025.csv"
META_INFO = "data/Meta_info.csv"
ECONOMIC_FILE = "data/Economic Parameters.csv"
@st.cache_data
def load_employee():
    return pd.read_csv(EMPLOYEE_SALARY)

@st.cache_data
def load_meta():
    return pd.read_csv(META_INFO)

@st.cache_data
def load_economic():
    df = pd.read_csv(ECONOMIC_FILE)
    df["Industry"] = df["Industry"].str.lower().str.strip()
    return df

employee_master = load_employee()
meta_master = load_meta()
economic_master = load_economic()

# ==========================================================
# LOAD BASE DATA
# ==========================================================

@st.cache_data
def load_base():
    industry_desc_df = pd.read_csv(INDUSTRY_DESC)
    industry_rates_df = pd.read_csv(INDUSTRY_RATES)

    return generate_merged_industry_data(
        industry_desc_df,
        industry_rates_df
    )


merged_df = load_base()
# Optimize types for faster groupby/merge
if "Industry" in merged_df.columns:
    merged_df["Industry"] = merged_df["Industry"].astype("category")
if "Age_Bracket" in merged_df.columns:
    merged_df["Age_Bracket"] = merged_df["Age_Bracket"].astype("category")


if "industry_assumptions" not in st.session_state:
    st.session_state.industry_assumptions = merged_df.copy()

# ==========================================================
# ENGINE FUNCTIONS
# ==========================================================

@st.cache_data(show_spinner=False)
def run_full_engine(industry_assumptions,
                    fund_return,
                    leakage_rate,
                    output_delta,
                    gva_delta,
                    employment_delta):

    # ==========================================================
    # 1️⃣ Employee + Salary Forecast
    # ==========================================================

    emp_forecast, sal_forecast = generate_employee_salary_forecast(
        employee_master,
        industry_assumptions,
        start_year=BASE_YEAR
    )

    # ==========================================================
    # 2️⃣ Survival Template
    # ==========================================================

    survival_template = generate_survival_template_cohort_style(
        meta_master,
        start_year=BASE_YEAR
    )

    # ==========================================================
    # 3️⃣ Attach Salary
    # ==========================================================

    survival_with_salary = attach_salary_to_survival(
        survival_template,
        sal_forecast
    )

    # ==========================================================
    # 4️⃣ Attach Employees
    # ==========================================================

    survival_with_emp = attach_employees_to_survival(
        survival_with_salary,
        emp_forecast
    )

    # ==========================================================
    # 5️⃣ Attach Exit & Replacement Rates
    # ==========================================================

    survival_ready = attach_exit_and_replacement(
        survival_with_emp,
        industry_assumptions
    )

    # ==========================================================
    # 6️⃣ Run Full Survival + EOSG + Fund Engine
    # ==========================================================

    combined_df = run_full_survival_eosg_model(
        survival_ready,
        fund_return_rate=fund_return,
        start_year=BASE_YEAR
    )

    # ==========================================================
    # 7️⃣ Aggregate Industry × Year
    # ==========================================================

    industry_year = aggregate_industry_year_combined(
        combined_df
    )

    # ==========================================================
    # 8️⃣ Apply Economic Layer
    # ==========================================================

    economic_adj = economic_master.copy()

    economic_adj["Output_Multiplier_Type_I"] = (
        economic_adj["Output_Multiplier_Type_I"] + output_delta
    ).clip(lower=0)

    economic_adj["GVA_to_Output_Ratio"] = (
        economic_adj["GVA_to_Output_Ratio"] + gva_delta
    ).clip(lower=0)

    economic_adj["Employment_Multiplier (jobs per AED 1M output)"] = (
        economic_adj["Employment_Multiplier (jobs per AED 1M output)"] + employment_delta
    ).clip(lower=0)
    
    impact_df = apply_economic_impact_combined(
        industry_year,
        economic_adj,
        leakage_rate
    )

    impact_df = impact_df.rename(columns={
        "output_impact": "Output_Impact",
        "gva_impact": "GVA_Impact",
        "jobs_impact": "Jobs_Impact"
    })

    economic_df = economic_master.copy()

    impact_df = impact_df.merge(
        economic_df[["Industry", "SectorMap"]],
        left_on="industry",
        right_on="Industry",
        how="left"
    )

    impact_df.drop(columns=["Industry"], inplace=True)
    # ==========================================================
    # 9️⃣ Drop Base Year
    # ==========================================================

    combined_df = combined_df[combined_df["year"] > BASE_YEAR]
    industry_year = industry_year[industry_year["year"] > BASE_YEAR]
    impact_df = impact_df[impact_df["year"] > BASE_YEAR]

    return combined_df, industry_year, impact_df


with st.sidebar:

    st.header("⚙ Industry Assumptions")
    
    # ------------------------------------------------------
    # Industry Selection
    # ------------------------------------------------------

    industry_list = sorted(
        st.session_state.industry_assumptions["Industry"].unique()
    )

    selected_industry = st.selectbox(
        "Industry",
        ["All Industries"] + industry_list
    )

    if selected_industry == "All Industries":
        industry_df = st.session_state.industry_assumptions.copy()
    else:
        industry_df = st.session_state.industry_assumptions[
            st.session_state.industry_assumptions["Industry"] == selected_industry
        ]

    # ======================================================
    # GLOBAL CONTROLS
    # ======================================================

    st.markdown("---")
    st.header("Global Controls")

    
    st.subheader("Global Workforce & Salary Override")
    st.markdown(
        """
        <div style="font-size:12px; color:#444444; margin-top:-5px; margin-bottom:10px;">
        Applies a uniform adjustment to all industries. 
        Example: if workforce growth is 3% and override = +1%, 
        the effective growth becomes 4% across all sectors.
        </div>
        """,
        unsafe_allow_html=True
    )

    workforce_override = st.slider(
        "Workforce Growth Override (%)",
        -10.0, 10.0, 0.0, step=0.1
    ) / 100

    salary_override = st.slider(
        "Salary Growth Override (%)",
        -10.0, 10.0, 0.0, step=0.1
    ) / 100

    
    st.subheader("Fund return and leakage")
    fund_return = st.slider(
        "Fund Return %",
        0.0, 12.0, 8.0
    ) / 100

    leakage = st.slider(
        "Leakage %",
        0.0, 50.0, 28.0
    ) / 100

    
    st.subheader("Economic Multiplier Absolute Adjustment")
    st.markdown(
        """
        <div style="font-size:12px; color:#444444; margin-top:-5px; margin-bottom:10px;">
        Adds an absolute delta to macro multipliers. 
        Example: if Output Multiplier = 1.8 and Δ = +0.2, 
        the new multiplier becomes 2.0. 
        Positive values strengthen economic transmission; 
        negative values reduce it.
        </div>
        """,
        unsafe_allow_html=True
    )

    output_delta = st.number_input(
        "Output Multiplier Δ",
        value=0.0,
        step=0.1
    )

    gva_delta = st.number_input(
        "GVA Ratio Δ",
        value=0.0,
        step=0.05
    )

    employment_delta = st.number_input(
        "Employment Multiplier Δ",
        value=0.0,
        step=0.5
    )



# ==========================================================
# STATIC BASELINE (DOES NOT CHANGE)
# ==========================================================

if "baseline_cache" not in st.session_state:
    st.session_state.baseline_cache = run_full_engine(
        merged_df,
        BASE_RETURN,
        BASE_LEAKAGE,
        0.0,
        0.0,
        0.0
    )

combined_static, industry_static, impact_static = st.session_state.baseline_cache



assumptions_adj = st.session_state.industry_assumptions.copy()

# Apply workforce override
assumptions_adj["Expansion Hiring %"] = (
    assumptions_adj["Expansion Hiring %"] + workforce_override
).clip(lower=0)

# Apply salary override
assumptions_adj["Salary Growth %"] = (
    assumptions_adj["Salary Growth %"] + salary_override
).clip(lower=0)

# Recalculate derived
assumptions_adj["Total Hiring %"] = (
    assumptions_adj["Expansion Hiring %"] +
    assumptions_adj["Replacement Hiring %"]
)

combined_full, industry_full, impact_full = run_full_engine(
    assumptions_adj,
    fund_return,
    leakage,
    output_delta,
    gva_delta,
    employment_delta
)

@st.cache_data(show_spinner=False)
def run_fund_scenarios(df):
    return generate_cohort_fund_scenarios(df)

fund_scenarios_full = run_fund_scenarios(combined_full)

if selected_industry == "All Industries":

    combined_dyn = combined_full.copy()
    industry_dyn = industry_full.copy()
    impact_dyn = impact_full.copy()

else:

    selected_industry_lower = selected_industry.lower()

    combined_dyn = combined_full[
        combined_full["industry"] == selected_industry_lower
    ].copy()

    industry_dyn = industry_full[
        industry_full["industry"] == selected_industry_lower
    ].copy()

    impact_dyn = impact_full[
        impact_full["industry"] == selected_industry_lower
    ].copy()

    # ==========================================================
    # DASHBOARD TABS
    # ==========================================================

tabs = st.tabs([
    "Workforce & EOSB",
    "Fund Impact",
    "Economic Impact",
    "Employee Calculator"
])
# ==========================================================
# TAB 1 — WORKFORCE & EOSB
# ==========================================================

with tabs[0]:

    st.markdown("## Workforce & EOSB Overview")

    df = industry_dyn.copy()

    # -----------------------------
    # Year Selection (No Age Filter)
    # -----------------------------
    year_options = sorted(df["year"].dropna().astype(int).unique())

    selected_year = st.selectbox(
        "Select Year",
        year_options,
        key="tab1_year"
    )

    df_year = df[df["year"] == selected_year]
    download_csv_button(
        df_year,
        f"workforce_year_{selected_year}.csv",
        "Download Selected Year Data"
    )

    # -----------------------------
    # KPI METRICS
    # -----------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Annual Basic Payroll (Bn)",
        f"{df_year['annual_total_salary'].sum()/1e9:,.2f}"
    )

    col2.metric(
        "Employees (Year End)",
        f"{int(df_year['total_employees'].sum()):,}"
    )

    col3.metric(
        "Average Monthly Salary",
        f"{df_year['weighted_monthly_salary'].mean():,.0f}"
    )

    col4.metric(
        "EOSG Accrual (Bn)",
        f"{df_year['annual_total_gratuity_accrual'].sum()/1e9:,.2f}"
    )

    col5.metric(
        "EOSG Contribution (Bn)",
        f"{df_year['annual_fund_contribution'].sum()/1e9:,.2f}"
    )

    st.markdown("---")

    # ======================================================
    # SUB-TABS FOR CHARTS
    # ======================================================

    chart_tabs = st.tabs([
        "Workforce Trend",
        "Payroll & Contributions",
        "Salary vs Workforce",
        "Payroll vs EOSG Accrual"
    ])

    # Prepare grouped data
    df_grouped = (
        df.groupby("year", as_index=False)
        .agg(
            workforce=("total_employees", "sum"),
            payroll=("annual_total_salary", "sum"),
            contribution=("annual_fund_contribution", "sum"),
            avg_salary=("weighted_monthly_salary", "mean"),
            accrual=("annual_total_gratuity_accrual", "sum")
        )
    )

    df_grouped["payroll_bn"] = df_grouped["payroll"] / 1e9
    df_grouped["contribution_bn"] = df_grouped["contribution"] / 1e9
    df_grouped["accrual_bn"] = df_grouped["accrual"] / 1e9

    # Custom color palette (Synarchy style)
    primary_blue = "#053048"
    gold = "#F5B718"
    light_blue = "#BDD4E7"
    dark_blue = "#1f3c66"

    # ======================================================
    # 1️⃣ Workforce Trend (Bar)
    # ======================================================

    with chart_tabs[0]:
        
        download_csv_button(
            df_grouped[["year", "workforce"]],
            "workforce_trend.csv"
        )

        fig1 = px.bar(
            df_grouped,
            x="year",
            y="workforce",
            title="Total Workforce Size"
        )

        fig1.update_traces(marker_color=primary_blue)

        fig1.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with chart_tabs[1]:
        download_csv_button(
            df_grouped[["year", "payroll_bn", "contribution_bn"]],
            "payroll_contributions.csv"
        )

        fig2 = go.Figure()

        # Bar → Payroll (Left Axis)
        fig2.add_trace(go.Bar(
            x=df_grouped["year"],
            y=df_grouped["payroll_bn"],
            name="Annual Basic Payroll (Bn)",
            marker_color="#BDD4E7",
            yaxis="y1"
        ))

        # Line → Contribution (Right Axis)
        fig2.add_trace(go.Scatter(
            x=df_grouped["year"],
            y=df_grouped["contribution_bn"],
            name="Annual Fund Contribution (Bn)",
            mode="lines+markers",
            line=dict(color="#F5B718", width=3),
            yaxis="y2"
        ))

        fig2.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Payroll & Annual Fund Contribution",
            yaxis=dict(
                title="Payroll (Bn)",
                showgrid=True
            ),
            yaxis2=dict(
                title="Fund Contribution (Bn)",
                overlaying="y",
                side="right",
                showgrid=False
            )
        )

        st.plotly_chart(fig2, use_container_width=True)



    # ======================================================
    # 3️⃣ Salary vs Workforce (Bar + Line Dual Axis)
    # ======================================================

    with chart_tabs[2]:
        download_csv_button(
            df_grouped[["year", "workforce", "avg_salary"]],
            "salary_vs_workforce.csv"
        )

        fig3 = go.Figure()

        fig3.add_trace(go.Bar(
            x=df_grouped["year"],
            y=df_grouped["workforce"],
            name="Workforce",
            marker_color=light_blue,
            yaxis="y2"
        ))

        fig3.add_trace(go.Scatter(
            x=df_grouped["year"],
            y=df_grouped["avg_salary"],
            name="Average Monthly Salary",
            mode="lines+markers",
            line=dict(color=primary_blue, width=3),
            yaxis="y1"
        ))

        fig3.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Average Salary vs Workforce",
            yaxis=dict(title="Avg Salary"),
            yaxis2=dict(
                title="Workforce",
                overlaying="y",
                side="right"
            )
        )

        st.plotly_chart(fig3, use_container_width=True)

    # ======================================================
    # 4️⃣ Payroll vs EOSG Accrual (Line Comparison)
    # ======================================================

    with chart_tabs[3]:
        download_csv_button(
            df_grouped[["year", "payroll_bn", "accrual_bn"]],
            "payroll_vs_accrual.csv"
        )

        fig4 = go.Figure()

        fig4.add_trace(go.Scatter(
            x=df_grouped["year"],
            y=df_grouped["payroll_bn"],
            name="Annual Payroll (Bn)",
            mode="lines",
            line=dict(color=primary_blue, width=3)
        ))

        fig4.add_trace(go.Scatter(
            x=df_grouped["year"],
            y=df_grouped["accrual_bn"],
            name="Annual EOSG Accrual (Bn)",
            mode="lines",
            line=dict(color=gold, width=3)
        ))

        fig4.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Payroll vs EOSG Accrual"
        )

        st.plotly_chart(fig4, use_container_width=True)

# ==========================================================
# TAB 2 — FUND IMPACT
# ==========================================================

with tabs[1]:

    st.markdown("## Fund Impact Overview")

    df_fund = industry_dyn.copy()

    # -----------------------------------------
    # Aggregate Across Years
    # -----------------------------------------

    fund_year = (
        df_fund.groupby("year", as_index=False)
        .agg(
            opening_fund=("opening_fund_with_return", "sum"),
            contribution=("annual_fund_contribution", "sum"),
            return_amt=("fund_return", "sum"),
            payout=("exit_payout_with_return", "sum"),
            closing_fund=("closing_fund_with_return", "sum")
        )
    )

    fund_year["closing_bn"] = fund_year["closing_fund"] / 1e9
    fund_year["contribution_bn"] = fund_year["contribution"] / 1e9
    fund_year["return_bn"] = fund_year["return_amt"] / 1e9
    fund_year["payout_bn"] = fund_year["payout"] / 1e9

    download_csv_button(
        fund_year,
        "fund_overview.csv"
    )
    # -----------------------------------------
    # KPIs (Latest Year)
    # -----------------------------------------

    latest_year = fund_year["year"].max()
    latest = fund_year[fund_year["year"] == latest_year]

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Closing Fund (Bn)",
            f"{latest['closing_bn'].values[0]:,.2f}")

    k2.metric("Annual Contributions (Bn)",
            f"{latest['contribution_bn'].values[0]:,.2f}")

    k3.metric("Annual Fund Return (Bn)",
            f"{latest['return_bn'].values[0]:,.2f}")

    k4.metric("Annual Exit Payout (Bn)",
            f"{latest['payout_bn'].values[0]:,.2f}")

    st.markdown("---")

    # ======================================================
    # SUB-TABS FOR FUND CHARTS
    # ======================================================

    fund_tabs = st.tabs([
        "Fund Growth",
        "Return vs Exit Payout",
        "Fund Growth vs Liability Growth"
    ])

    # ======================================================
    # 1️⃣ FUND GROWTH (Bar + Line Dual Axis)
    # ======================================================

    with fund_tabs[0]:
        download_csv_button(
            fund_year[["year", "closing_bn", "contribution_bn"]],
            "fund_growth.csv"
        )

        fig_fund = go.Figure()

        fig_fund.add_trace(go.Bar(
            x=fund_year["year"],
            y=fund_year["closing_bn"],
            name="Closing Fund (Bn)",
            marker_color="#053048",
            yaxis="y1"
        ))

        fig_fund.add_trace(go.Scatter(
            x=fund_year["year"],
            y=fund_year["contribution_bn"],
            name="Contributions (Bn)",
            mode="lines+markers",
            line=dict(color="#F5B718", width=3),
            yaxis="y2"
        ))

        fig_fund.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Fund Growth Progression",
            yaxis=dict(title="Closing Fund (Bn)"),
            yaxis2=dict(
                title="Contributions (Bn)",
                overlaying="y",
                side="right"
            )
        )

        st.plotly_chart(fig_fund, use_container_width=True)

    # ======================================================
    # 2️⃣ RETURN VS EXIT PAYOUT (Line Comparison)
    # ======================================================

    with fund_tabs[1]:
        download_csv_button(
            fund_year[["year", "return_bn", "payout_bn"]],
            "return_vs_exit.csv"
        )

        fig_flow = go.Figure()

        fig_flow.add_trace(go.Scatter(
            x=fund_year["year"],
            y=fund_year["return_bn"],
            name="Fund Return (Bn)",
            mode="lines",
            line=dict(color="#1f3c66", width=3)
        ))

        fig_flow.add_trace(go.Scatter(
            x=fund_year["year"],
            y=fund_year["payout_bn"],
            name="Exit Payout (Bn)",
            mode="lines",
            line=dict(color="#F5B718", width=3)
        ))

        fig_flow.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Return vs Exit Payout"
        )

        st.plotly_chart(fig_flow, use_container_width=True)
    with fund_tabs[2]:

        
        # -------------------------------------------------------
        # Change in Closing Fund vs Liability (From 2026)
        # -------------------------------------------------------

        change_df = (
            industry_dyn.groupby("year", as_index=False)
            .agg(
                closing_fund=("closing_fund_with_return", "sum"),
                liability=("exit_adjusted_liability", "sum")
            )
        )

        # Remove 2025
        change_df = change_df[change_df["year"] > 2025].copy()

        # Convert to billions
        change_df["closing_bn"] = change_df["closing_fund"] / 1e9
        change_df["liability_bn"] = change_df["liability"] / 1e9

        # YoY Change
        change_df["fund_change_bn"] = change_df["closing_bn"].diff()
        change_df["liability_change_bn"] = change_df["liability_bn"].diff()

        # Remove first row (no previous year for diff)
        change_df = change_df.dropna()

        # -----------------------------
        # CHART
        # -----------------------------
        download_csv_button(
            change_df,
            "fund_vs_liability_change.csv"
        )
        
        fig_change = go.Figure()

        fig_change.add_trace(go.Bar(
            x=change_df["year"],
            y=change_df["fund_change_bn"],
            name="Change in Closing Fund (Bn)",
            marker_color="#053048"
        ))

        fig_change.add_trace(go.Bar(
            x=change_df["year"],
            y=change_df["liability_change_bn"],
            name="Change in Liability (Bn)",
            marker_color="#F5B718"
        ))

        fig_change.update_layout(
            barmode="group",
            title="Change in Closing Fund vs Change in Liability (From 2026)",
            paper_bgcolor="white",
            plot_bgcolor="white",
            yaxis_title="Change (Bn)"
        )

        st.plotly_chart(fig_change, use_container_width=True)


# ==========================================================
# TAB 3 — ECONOMIC IMPACT
# ==========================================================

with tabs[2]:

    st.markdown("## Economic Impact Overview")

    df_eco = impact_dyn.copy()

    # -----------------------------------------
    # Year Filter
    # -----------------------------------------

    year_options = sorted(df_eco["year"].unique())

    year_selection = st.selectbox(
        "Select Year",
        ["All Years"] + year_options,
        key="eco_year_filter"
    )

    if year_selection == "All Years":

        eco_display = (
            df_eco.groupby("industry", as_index=False)
            .agg(
                GDP=("GVA_Impact", "sum"),
                Jobs=("Jobs_Impact", "sum"),
                Output=("Output_Impact", "sum")
            )
        )

        kpi_gdp = eco_display["GDP"].sum()
        kpi_jobs = eco_display["Jobs"].sum()
        kpi_output = eco_display["Output"].sum()

    else:

        eco_display = df_eco[df_eco["year"] == year_selection]

        kpi_gdp = eco_display["GVA_Impact"].sum()
        kpi_jobs = eco_display["Jobs_Impact"].sum()
        kpi_output = eco_display["Output_Impact"].sum()

    # -----------------------------------------
    # KPI DISPLAY
    # -----------------------------------------
    download_csv_button(
        eco_display,
        "economic_impact_filtered.csv"
    )


    k1, k2, k3 = st.columns(3)

    k1.metric("GDP Impact (Bn)",
            f"{kpi_gdp/1e9:,.2f}")

    k2.metric("Jobs Impact",
            f"{int(kpi_jobs):,}")

    k3.metric("Output Impact (Bn)",
            f"{kpi_output/1e9:,.2f}")

    st.markdown("---")

    # ======================================================
    # SUB-TABS FOR ECONOMIC CHARTS
    # ======================================================

    eco_tabs = st.tabs([
        "Economic Progression",
        "Sector Distribution"
    ])

    # ======================================================
    # 1️⃣ ECONOMIC PROGRESSION (Across Years)
    # ======================================================

    with eco_tabs[0]:


        eco_year = (
            df_eco.groupby("year", as_index=False)
            .agg(
                GDP=("GVA_Impact", "sum"),
                Jobs=("Jobs_Impact", "sum"),
                Output=("Output_Impact", "sum")
            )
        )

        eco_year["GDP_bn"] = eco_year["GDP"] / 1e9
        eco_year["Output_bn"] = eco_year["Output"] / 1e9

        download_csv_button(
            eco_year,
            "economic_progression.csv"
        )
        
        fig_progress = go.Figure()

        fig_progress.add_trace(go.Bar(
            x=eco_year["year"],
            y=eco_year["GDP_bn"],
            name="GDP Impact (Bn)",
            marker_color="#053048",
            yaxis="y1"
        ))

        fig_progress.add_trace(go.Scatter(
            x=eco_year["year"],
            y=eco_year["Output_bn"],
            name="Output Impact (Bn)",
            mode="lines+markers",
            line=dict(color="#F5B718", width=3),
            yaxis="y1"
        ))

        fig_progress.add_trace(go.Scatter(
            x=eco_year["year"],
            y=eco_year["Jobs"],
            name="Jobs Impact",
            mode="lines",
            line=dict(color="#1f3c66", width=2),
            yaxis="y2"
        ))

        fig_progress.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            title="Economic Progression Over Time",
            yaxis=dict(title="GDP / Output (Bn)"),
            yaxis2=dict(
                title="Jobs",
                overlaying="y",
                side="right"
            )
        )

        st.plotly_chart(fig_progress, use_container_width=True)

    # ======================================================
    # 2️⃣ SECTOR DISTRIBUTION
    # ======================================================

    with eco_tabs[1]:

        if year_selection == "All Years":

            sector_df = (
                df_eco.groupby("SectorMap", as_index=False)
                .agg(
                    GDP=("GVA_Impact", "sum"),
                    Output=("Output_Impact", "sum"),
                    Jobs=("Jobs_Impact", "sum")
                )
            )

        else:

            sector_df = (
                df_eco[df_eco["year"] == year_selection]
                .groupby("SectorMap", as_index=False)
                .agg(
                    GDP=("GVA_Impact", "sum"),
                    Output=("Output_Impact", "sum"),
                    Jobs=("Jobs_Impact", "sum")
                )
            )

        sector_df["GDP_bn"] = sector_df["GDP"] / 1e9

        download_csv_button(
            sector_df,
            "sector_distribution.csv"
        )

        fig_sector = px.bar(
            sector_df,
            x="SectorMap",
            y="GDP_bn",
            title="GDP Impact by Sector"
        )

        fig_sector.update_traces(marker_color="#BDD4E7")

        fig_sector.update_layout(
            template=None,
            paper_bgcolor="white",
            plot_bgcolor="white",
            xaxis_title="Sector",
            yaxis_title="GDP Impact (Bn)"
        )

        st.plotly_chart(fig_sector, use_container_width=True)
    # ==========================================================
    # TAB 4 — EMPLOYEE BENEFIT CALCULATOR
    # ==========================================================

    with tabs[3]:

        st.markdown("## Employee Benefit Calculator")

        # -----------------------------
        # INPUT SECTION
        # -----------------------------

        colA, colB = st.columns(2)

        with colA:
            prev_salary = st.number_input(
                "Basic Monthly Salary (Previous Year)",
                min_value=0.0,
                value=10000.0,
                step=500.0
            )

            salary_growth_pct = st.number_input(
                "Salary Growth % (YoY)",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.1
            )

        with colB:
            tenure_years = st.number_input(
                "Tenure (Years)",
                min_value=0.0,
                value=5.0,
                step=1.0
            )

            fund_return_pct = st.number_input(
                "Fund Return %",
                min_value=0.0,
                max_value=15.0,
                value=4.0,
                step=0.1
            )

        salary_growth = salary_growth_pct / 100
        fund_return = fund_return_pct / 100

        st.markdown("---")

        # -----------------------------
        # GRATUITY RATE FUNCTION
        # -----------------------------

        def gratuity_rate(tenure):
            if tenure < 1:
                return 0.0
            elif tenure <= 5:
                return tenure * 0.05833
            elif tenure < 25:
                return (5 * 0.05833) + ((tenure - 5) * 0.08333)
            else:
                return (5 * 0.05833) + ((25 - 5) * 0.08333)

        # -----------------------------
        # LIABILITY + FUND ENGINE
        # -----------------------------

        fund_balance = 0
        previous_liability = 0
        yearly_records = []

        for year in range(1, int(tenure_years) + 1):

            # Monthly salary progression
            monthly_salary = prev_salary * ((1 + salary_growth) ** (year - 1))
            annual_salary = monthly_salary * 12

            # Total liability using same function
            rate = gratuity_rate(year)
            total_liability = annual_salary * rate

            # Contribution = change in liability
            contribution = total_liability - previous_liability
            if year == 1:
                contribution = total_liability

            # Fund roll-forward (same as main engine without exit)
            opening_fund = fund_balance
            fund_before_return = opening_fund + contribution
            fund_balance = fund_before_return * (1 + fund_return)

            yearly_records.append({
                "Year": year,
                "Annual Salary (AED)": annual_salary,
                "Total Liability (AED)": total_liability,
                "Contribution (AED)": contribution,
                "Fund Value (AED)": fund_balance
            })

            previous_liability = total_liability

        gratuity_unfunded = previous_liability
        gratuity_funded = fund_balance
        funding_gap = gratuity_funded - gratuity_unfunded

        # -----------------------------
        # EOS SUMMARY
        # -----------------------------

        st.markdown("### EOS Summary")

        k1, k2, k3 = st.columns(3)

        k1.metric("Unfunded EOS",
                f"{gratuity_unfunded:,.0f}")

        k2.metric("Funded EOS",
                f"{gratuity_funded:,.0f}")

        k3.metric("Return Differential",
                f"{funding_gap:,.0f}")

        st.markdown("---")

        # -----------------------------
        # BENEFIT TABLE
        # -----------------------------

        st.markdown("### Individual Benefit Breakdown")

        benefit_df = pd.DataFrame(yearly_records).round(0)

        st.markdown(
            """
            <div style="
                background-color:#FAF6EB;
                padding:10px;
                border-left:5px solid #F5B718;
                font-weight:600;">
                Liability-based contribution method.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.dataframe(
            benefit_df,
            use_container_width=True,
            hide_index=True
        )

