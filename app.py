from altair import value
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline import *
from PIL import Image

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


main_col, calc_col = st.columns([3,1])


with calc_col:

    st.markdown("## Employee Benefit Calculator")

    # ---------------------------------
    # Salary Inputs
    # ---------------------------------

    prev_salary = st.number_input(
        "Basic Salary (Previous Year)",
        min_value=0.0,
        value=10000.0,
        step=500.0
    )

    salary_growth = st.number_input(
        "Salary Growth % (YoY)",
        min_value=0.0,
        max_value=20.0,
        value=5.0
    ) / 100

    current_salary = prev_salary * (1 + salary_growth)

    st.metric("Current Year Salary",
              f"{current_salary:,.0f}")

    # ---------------------------------
    # Tenure & Fund Inputs
    # ---------------------------------

    tenure_years = st.number_input(
        "Tenure (Years)",
        min_value=0.0,
        value=5.0,
        step=0.5
    )

    fund_return = st.number_input(
        "Fund Return %",
        min_value=0.0,
        max_value=15.0,
        value=4.0
    ) / 100

    st.markdown("---")

    # ---------------------------------
    # Your Gratuity Function
    # ---------------------------------

    def gratuity_rate(tenure):
        if tenure < 1:
            return 0.0
        elif tenure <= 5:
            return tenure * 0.05833
        elif tenure < 25:
            return (5 * 0.05833) + ((tenure - 5) * 0.08333)
        else:
            return (5 * 0.05833) + ((25 - 5) * 0.08333)

    # ---------------------------------
    # Unfunded Liability
    # ---------------------------------

    rate = gratuity_rate(tenure_years)

    # Final salary based calculation
    gratuity_unfunded = current_salary * rate

    # ---------------------------------
    # Funded Value (Yearly Accrual Model)
    # ---------------------------------

    accrued = 0

    for year in range(int(tenure_years)):

        # salary progression
        salary_year = prev_salary * ((1 + salary_growth) ** year)

        # yearly accrual logic
        if year < 5:
            yearly_accrual = salary_year * 0.05833
        else:
            yearly_accrual = salary_year * 0.08333

        # accumulate with compounding
        accrued = (accrued + yearly_accrual) * (1 + fund_return)

    gratuity_funded = accrued

    funding_gap = gratuity_funded - gratuity_unfunded

    # ---------------------------------
    # Outputs
    # ---------------------------------

    st.markdown("### EOS Summary")

    m1, m2, m3 = st.columns(3)

    card_style = """
        height:150px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        background-color:#ffffff;
        border-radius:12px;
        border:1px solid #BDD4E7;
        padding:10px;
    """

    highlight_style = """
        height:150px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        background-color:#F5B71820;
        border-radius:12px;
        border:1px solid #F5B718;
        padding:10px;
    """

    with m1:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size:14px; color:#77878C;">Unfunded EOS</div>
                <div style="font-size:30px; font-weight:700; color:#053048;">
                    {gratuity_unfunded:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size:14px; color:#77878C;">Funded EOS</div>
                <div style="font-size:30px; font-weight:700; color:#053048;">
                    {gratuity_funded:,.0f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            f"""
            <div style="{highlight_style}">
                <div style="font-size:14px; color:#77878C;">Return Differential</div>
                <div style="font-size:30px; font-weight:700; color:#053048;">
                    {funding_gap:,.0f}
                </div>
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
with main_col:
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
                        leakage_rate):

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

        impact_df = apply_economic_impact_combined(
            industry_year,
            economic_master,
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




    # ==========================================================
    # SIDEBAR – INDUSTRY ASSUMPTIONS (CLEAN VERSION)
    # Editable: Expansion Hiring % + Salary Growth %
    # ==========================================================

    with st.sidebar:

        st.header("⚙ Industry Assumptions")
        st.markdown("""
        <div style="
            background-color:#FAF6EB;
            padding:12px;
            border-radius:8px;
            border-left:6px solid #F5B718;
            font-weight:700;
            color:#053048;
            margin-bottom:15px;
        ">
        ⚙ Scenario Controls <br>
        <span style="font-weight:500; font-size:13px;">
        These inputs affect Scenario Analysis only (below).

        </span>
        </div>
        """, unsafe_allow_html=True)

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

        # ------------------------------------------------------
        # Age Selection (Fixed Logic)
        # ------------------------------------------------------

        if selected_industry == "All Industries":
            industry_df = st.session_state.industry_assumptions.copy()
        else:
            industry_df = st.session_state.industry_assumptions[
                st.session_state.industry_assumptions["Industry"] == selected_industry
            ]

        age_options = ["All"] + sorted(industry_df["Age_Bracket"].unique())

        selected_age = st.selectbox(
            "Age Bracket",
            age_options
        )

        st.markdown("### Editable Parameters")

        # ======================================================
        # IF AGE = ALL → NO EDITING
        # ======================================================
        if selected_age == "All":

            st.info(
                "Assumptions can only be edited at specific Age Bracket level."
            )

        # ======================================================
        # SPECIFIC AGE SELECTED
        # ======================================================
        else:

            # Get selected row
            row_mask = (
                (industry_df["Age_Bracket"] == selected_age)
            )

            row_idx = industry_df[row_mask].index[0]
            row = st.session_state.industry_assumptions.loc[row_idx]

            # --------------------------------------------------
            # ONLY Editable Fields
            # --------------------------------------------------

            exp = st.number_input(
                "Expansion Hiring %",
                min_value=0.0,
                max_value=1.0,
                value=float(row["Expansion Hiring %"]),
                step=0.01
            )

            sal_g = st.number_input(
                "Salary Growth %",
                min_value=0.0,
                max_value=0.20,
                value=float(row["Salary Growth %"]),
                step=0.005
            )

            # --------------------------------------------------
            # Update Button
            # --------------------------------------------------

            if st.button("Update Assumptions"):

                df = st.session_state.industry_assumptions

                # Update ONLY editable fields
                df.loc[row_idx, "Expansion Hiring %"] = exp
                df.loc[row_idx, "Salary Growth %"] = sal_g

                # Recalculate derived fields
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

        # ======================================================
        # GLOBAL CONTROLS
        # ======================================================

        st.markdown("---")
        st.header("Global Controls")

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

    if "baseline_cache" not in st.session_state:
        st.session_state.baseline_cache = run_full_engine(
            merged_df,
            BASE_RETURN,
            BASE_LEAKAGE
        )

    combined_static, industry_static, impact_static = st.session_state.baseline_cache

    
    print(st.session_state.industry_assumptions.equals(merged_df))
    combined_full, industry_full, impact_full = run_full_engine(
        st.session_state.industry_assumptions,
        fund_return,
        leakage
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
    # GLOBAL BASELINE SUMMARY
    # ==========================================================

    st.markdown("## Global Baseline Overview (Policy Scenario)")

    # -----------------------------------------
    # Year Filter (Baseline Only)
    # -----------------------------------------

    year_options = ["2026-2040"] + sorted(industry_static["year"].dropna().astype(int).unique())
    

    baseline_year = st.selectbox(
        "Select Year (Baseline Scenario)",
        year_options,
        key="baseline_year_filter"
    )

    # Filter static data for selected year
    if baseline_year == "2026-2040":

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


    st.markdown("## Workforce & Economic Analytics")

    # 1️⃣ Compute growth first
    growth_df = industry_dyn.copy()
    growth_df["employee_growth_%"] = (
        growth_df.groupby("industry")["total_employees"]
        .pct_change()
        .fillna(0) * 100
    )

    if baseline_year == "2026-2040":

        iy = growth_df.copy()
        eco = impact_dyn.copy()

    else:

        iy = growth_df[growth_df["year"] == int(baseline_year)].copy()
        eco = impact_dyn[impact_dyn["year"] == int(baseline_year)].copy()

    if iy.empty:
        st.warning("No data available.")
        st.stop()

    # 3️⃣ Derived metrics
    iy["avg_monthly_salary"] = (
        iy["annual_total_salary"] / (iy["total_employees"] * 12)
    )

    iy["contribution_ratio_%"] = (
        iy["annual_fund_contribution"] /
        iy["annual_total_salary"] * 100
    )

    iy["fund_coverage_ratio"] = (
        iy["closing_fund_with_return"] /
        iy["annual_total_gratuity_accrual"]
    )

    # ======================================================
    # KPI GRID
    # ======================================================

    c1, c2, c3 = st.columns(3)

    c1.metric("Employees",
            f"{iy['total_employees'].sum():,.0f}")

    c2.metric("Avg Monthly Salary",
            f"{iy['avg_monthly_salary'].mean():,.0f}")


    c3.metric("EOSG Accrual (Bn)",
            f"{iy['annual_total_gratuity_accrual'].sum()/1e9:.2f}")

    c5, c6, c7 = st.columns(3)

    c5.metric("Fund Coverage",
            f"{iy['fund_coverage_ratio'].mean():.2f}x")

    c6.metric("Contribution %",
            f"{iy['contribution_ratio_%'].mean():.2f}%")

    c7.metric("Employee Growth %",
            f"{iy['employee_growth_%'].mean():.2f}%")

    

    st.markdown("## Workforce & Payroll Evolution")

    # ------------------------------------------------------
    # ALWAYS use full dataset (ignore industry & age filters)
    # ------------------------------------------------------
    trend_df = combined_full.copy()

    # ------------------------------------------------------
    # Compute salary totals properly
    # ------------------------------------------------------
    trend_df["salary_x_emp"] = (
        trend_df["salary"] *
        trend_df["survived_employee"]
    )

    trend_df["annual_salary_total"] = (
        trend_df["salary_x_emp"] * 12
    )

    # ------------------------------------------------------
    # YEARLY AGGREGATION (National Level)
    # ------------------------------------------------------
    yearly = trend_df.groupby("year").agg({
        "survived_employee": "sum",
        "annual_salary_total": "sum",
        "fund_contribution": "sum"
    }).reset_index()

    yearly = yearly.rename(columns={
        "survived_employee": "total_employees",
        "annual_salary_total": "annual_total_salary",
        "fund_contribution": "annual_fund_contribution"
    })

    # Derived metrics
    yearly["avg_salary"] = (
        yearly["annual_total_salary"] /
        yearly["total_employees"]
    )

    yearly["payroll_bn"] = yearly["annual_total_salary"] / 1e9
    yearly["fund_contribution_bn"] = yearly["annual_fund_contribution"] / 1e9


    # ==========================================
    # CHART SELECTOR
    # ==========================================

    chart_option = st.selectbox(
        "Select Workforce View",
        [
            "Total Workforce Size",
            "Annual Payroll (Bn)",
            "Annual Fund Contributions (Bn)",
            "Average Salary per Employee",
            "Payroll vs Workforce"
        ]
    )

    def apply_clean_style(fig,paper_bgcolor="#FAF6EB", plot_bgcolor="#FAF6EB"):
        fig.update_layout(
            template=None,
            paper_bgcolor=paper_bgcolor,
            plot_bgcolor=plot_bgcolor,
            font=dict(color="#053048"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            height=520
        )
        return fig

    fig = None   # initialize safely

    if chart_option == "Total Workforce Size":

        # Aggregate by Industry × Year
        industry_yearly = industry_dyn.groupby(
            ["year", "industry"]
        )["total_employees"].sum().reset_index()

        fig = px.bar(
            industry_yearly,
            x="year",
            y="total_employees",
            color="industry",
            title="Workforce Expansion by Industry",
        )

        fig.update_layout(
            barmode="stack",
            xaxis_title="Year",
            yaxis_title="Number of Employees"
        )

        fig = apply_clean_style(fig, paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")

    elif chart_option == "Annual Payroll (Bn)":

        yearly = yearly.sort_values("year")
        yearly["payroll_change"] = yearly["payroll_bn"].diff()
        yearly["payroll_change"].iloc[0] = yearly["payroll_bn"].iloc[0]

        fig = go.Figure()

        fig.add_trace(go.Waterfall(
            x=yearly["year"],
            y=yearly["payroll_change"],
            measure=["absolute"] + ["relative"]*(len(yearly)-1),
            name="Yearly Change",
            increasing=dict(marker=dict(color="#F5B718")),
            decreasing=dict(marker=dict(color="#EFD59B")),
        ))

        fig.add_trace(go.Scatter(
            x=yearly["year"],
            y=yearly["payroll_bn"],
            name="Total Payroll (Bn)",
            mode="lines+markers",
            line=dict(color="#000000", width=4, dash="dot"),
            yaxis="y2"
        ))

        fig.update_layout(
            title="Payroll Evolution & Yearly Change",
            xaxis_title="Year",
            yaxis=dict(title="Annual Change (Billion AED)"),
            yaxis2=dict(
                title="Total Payroll (Billion AED)",
                overlaying="y",
                side="right"
            ),
            template="plotly_white",
            height=550,
            legend=dict(orientation="h", y=1.1)
        )
        fig = apply_clean_style(fig)

    elif chart_option == "Annual Fund Contributions (Bn)":

        
        fig = px.bar(
            yearly,
            x="year",
            y="fund_contribution_bn",
            text="fund_contribution_bn",
            title="Total Annual EOSG Contributions"
        )

        fig.update_traces(
            marker_color="#F5B718",
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Fund Contribution (Billion AED)"
        )

        fig = apply_clean_style(fig, paper_bgcolor="#93838E", plot_bgcolor="#93838E")

    elif chart_option == "Average Salary per Employee":

        fig = px.line(
            yearly,
            x="year",
            y="avg_salary",
            markers=True,
            text="avg_salary",
            title="Average Salary per Employee"
        )

        fig.update_traces(
            line=dict(color="#93838E", width=4),
            marker=dict(size=8, color="#93838E"),
            texttemplate="%{text:,.0f}",
            textposition="top center"
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Average Salary (AED)"
        )


        fig = apply_clean_style(fig,    paper_bgcolor="#F5B718", plot_bgcolor="#F5B718")

    elif chart_option == "Payroll vs Workforce":

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=yearly["year"],
            y=yearly["payroll_bn"],
            name="Payroll (Bn AED)",
            opacity=0.6
        ))

        fig.add_trace(go.Scatter(
            x=yearly["year"],
            y=yearly["total_employees"],
            name="Employees",
            mode="lines+markers",
            yaxis="y2",
            line=dict(width=4)
        ))

        fig.update_layout(
            title="Payroll vs Workforce Size",
            xaxis_title="Year",
            yaxis=dict(title="Payroll (Billion AED)"),
            yaxis2=dict(
                title="Number of Employees",
                overlaying="y",
                side="right"
            ),
            template="plotly_white",
            height=520
        )
        fig = apply_clean_style(fig, paper_bgcolor="#BDD4E7", plot_bgcolor="#BDD4E7")

    # 👇 Only render if figure exists
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Economic Impact Progression")

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
        line=dict(color="#053048", width=3)
    ))

    # GVA
    fig_evo.add_trace(go.Scatter(
        x=evo_year["year"],
        y=evo_year["GVA_Bn"],
        name="GVA (Bn)",
        mode="lines+markers",
        line=dict(color="#8BAAAD", width=3)
    ))

    # Jobs – Bar on secondary axis
    fig_evo.add_trace(go.Bar(
        x=evo_year["year"],
        y=evo_year["Jobs_K"],
        name="Jobs (K)",
        marker_color="#F5B718",
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


    

    # Apply age filter ONLY to employee-level data
    if selected_age != "All":
        combined_dyn = combined_dyn[
            combined_dyn["age_bracket"] == selected_age.lower()
        ]


    # ==========================================================
    # SCENARIO TABS
    # ==========================================================

    st.markdown("## ⚙ Scenario Analysis")

    tabs = st.tabs([
        "Job Impact",
        "Fund Growth",
        "Economic",
        "EOSG & Payroll",
        "Individual Benefit"
   
    ])

    # ==========================================================
    # TAB 0 — JOB IMPACT (Industry Only, Age Ignored)
    # ==========================================================
    with tabs[0]:

        st.markdown("### Jobs Impact (Industry Level)")

        if impact_dyn.empty:
            st.warning("No data available for selected industry.")
            st.stop()

        jobs_df = (
            impact_dyn
            .groupby("year", as_index=False)["Jobs_Impact"]
            .sum()
        )

        jobs_df["Jobs_K"] = jobs_df["Jobs_Impact"] / 1_000

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=jobs_df["year"],
            y=jobs_df["Jobs_K"],
            marker_color="#053048",
            text=[f"{v:.2f}K" for v in jobs_df["Jobs_K"]],
            textposition="outside"
        ))

        fig.update_layout(
            template="plotly_white",
            yaxis_title="Jobs Impact (Thousand)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption("Note: Job impact is calculated at Industry level (age breakdown not applied).")

    # ==========================================================
    # TAB 1 — FUND ACCUMULATION
    # ==========================================================
    with tabs[1]:

        st.markdown("### Fund Growth – Accumulation")

        df = fund_scenarios_full.copy()

        # -----------------------------
        # Industry Filter
        # -----------------------------
        if selected_industry != "All Industries":
            selected_industry_lower = selected_industry.lower()
            df = df[df["industry"] == selected_industry_lower]

        # -----------------------------
        # Age Filter
        # -----------------------------
        if selected_age != "All":
            df = df[df["age_bracket"] == selected_age.lower()]

        if df.empty:
            st.warning("No data available for selected filters.")
            st.stop()

        # -----------------------------
        # Dynamic Return
        # -----------------------------
        if fund_return == 0.04:
            df["fund_dynamic"] = df["fund_4"]

        elif fund_return == 0.06:
            df["fund_dynamic"] = df["fund_6"]

        elif fund_return == 0.08:
            df["fund_dynamic"] = df["fund_8"]

        else:
            dynamic_blocks = []

            for (ind, age, cohort), g in df.groupby(
                ["industry", "age_bracket", "cohort"],
                sort=False
            ):
                g = g.sort_values("year").copy()

                fund = 0
                balances = []

                for _, row in g.iterrows():
                    fund = fund * (1 + fund_return)
                    fund += row["fund_contribution"]
                    balances.append(fund)

                g["fund_dynamic"] = balances
                dynamic_blocks.append(g)

            df = pd.concat(dynamic_blocks)

        # -----------------------------
        # Aggregate
        # -----------------------------
        grouped = df.groupby("year")[[
            "fund_4",
            "fund_6",
            "fund_8",
            "fund_dynamic"
        ]].sum().reset_index()

        # -----------------------------
        # Plot
        # -----------------------------
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=grouped["year"],
            y=grouped["fund_4"] / 1e9,
            name="4%",
            line=dict(width=3)
        ))

        fig.add_trace(go.Scatter(
            x=grouped["year"],
            y=grouped["fund_6"] / 1e9,
            name="6%",
            line=dict(width=3)
        ))

        fig.add_trace(go.Scatter(
            x=grouped["year"],
            y=grouped["fund_8"] / 1e9,
            name="8%",
            line=dict(width=3)
        ))

        fig.add_trace(go.Scatter(
            x=grouped["year"],
            y=grouped["fund_dynamic"] / 1e9,
            name=f"Selected ({int(fund_return*100)}%)",
            line=dict(width=4, dash="dash")
        ))

        fig.update_layout(
            template="plotly_white",
            yaxis_title="Fund Balance (Bn)",
            legend=dict(orientation="h", y=1.1),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# TAB 2 — ECONOMIC (Sector Level, Age Filter Only)
# ==========================================================
    with tabs[2]:

        st.markdown("### Economic Impact")

        df = impact_full.copy()

        if df.empty:
            st.warning("No data available for selected age filter.")
            st.stop()

        # -----------------------------------------------------
        # Year Selector
        # -----------------------------------------------------
        year_options = sorted(df["year"].dropna().astype(int).unique())

        selected_year = st.selectbox(
            "Select Year",
            year_options,
            key="economic_tab_year"
        )

        eco = df[df["year"] == selected_year].copy()

        # -----------------------------------------------------
        # Unit Conversion
        # -----------------------------------------------------
        eco["Output_Mn"] = eco["Output_Impact"] / 1_000_000
        eco["GVA_Mn"] = eco["GVA_Impact"] / 1_000_000
        eco["Jobs_K"] = eco["Jobs_Impact"] / 1_000

        # -----------------------------------------------------
        # Brand Colors
        # -----------------------------------------------------
        brand_colors = [
            "#053048",
            "#F5B718",
            "#BDD4E7",
            "#EFD59B",
            "#8BAAAD",
            "#77878C",
            "#93838E"
        ]

        c1, c2, c3 = st.columns(3)

        # ======================================================
        # OUTPUT IMPACT
        # ======================================================
        fig_output = px.pie(
            eco,
            names="SectorMap",
            values="Output_Mn",
            hole=0.55,
            color_discrete_sequence=brand_colors,
            title="Output Impact (Million)"
        )

        fig_output.update_traces(
            texttemplate="%{value:.2f} Mn",
            textposition="outside",
            textfont=dict(color="#053048", size=13)
        )

        fig_output.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            title_font=dict(size=18, color="#053048"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color="#053048")
            ),
            margin=dict(t=60, b=80)
        )

        c1.plotly_chart(fig_output, use_container_width=True)

        # ======================================================
        # GVA IMPACT
        # ======================================================
        fig_gva = px.pie(
            eco,
            names="SectorMap",
            values="GVA_Mn",
            hole=0.55,
            color_discrete_sequence=brand_colors,
            title="GVA Impact by Sector (Million)"
        )

        fig_gva.update_traces(
            texttemplate="%{value:.2f} Mn",
            textposition="outside",
            textfont=dict(color="#053048", size=13)
        )

        fig_gva.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            title_font=dict(size=18, color="#053048"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color="#053048")
            ),
            margin=dict(t=60, b=80)
        )

        c2.plotly_chart(fig_gva, use_container_width=True)

        # ======================================================
        # EMPLOYMENT IMPACT
        # ======================================================
        fig_jobs = px.pie(
            eco,
            names="SectorMap",
            values="Jobs_K",
            hole=0.55,
            color_discrete_sequence=brand_colors,
            title="Employment Impact (Thousand Jobs)"
        )

        fig_jobs.update_traces(
            texttemplate="%{value:.2f} K",
            textposition="outside",
            textfont=dict(color="#053048", size=13)
        )

        fig_jobs.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            title_font=dict(size=18, color="#053048"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(color="#053048")
            ),
            margin=dict(t=60, b=80)
        )

        c3.plotly_chart(fig_jobs, use_container_width=True)

        st.caption("Note: Economic impact displayed at Sector level. Industry filter not applied. Age filter applied if selected.")
    with tabs[3]:

        st.markdown("### EOSG & Payroll")

        # df = industry_dyn.copy()
        

        # df = df[df["industry"] == selected_industry_lower]
        df = combined_dyn.copy()

        if df.empty:
            st.warning("No data available.")
            st.stop()

        grouped = df.groupby("year").agg({
            "salary": "sum",
            "closing_fund_with_return": "sum"
        }).reset_index()

        grouped = grouped.rename(columns={
            "salary": "annual_total_salary"
        })

        fig = go.Figure()        

        fig.add_trace(go.Scatter(
            x=grouped["year"],
            y=grouped["closing_fund_with_return"] / 1e9,
            name="Fund Balance (Bn)",
            mode="lines+markers",
            line=dict(width=4)
        ))

        fig.add_trace(go.Bar(
            x=grouped["year"],
            y=grouped["annual_total_salary"] / 1e9,
            name="Payroll (Bn)",
            opacity=0.6,
            yaxis="y2"
        ))

        fig.update_layout(
            template="plotly_white",
            yaxis=dict(title="Fund (Bn)"),
            yaxis2=dict(
                title="Payroll (Bn)",
                overlaying="y",
                side="right"
            ),
            legend=dict(orientation="h", y=1.1),
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption("""                
                    **Note:** Payroll and EOSG fund balances are calculated at the  workforce-level. Both industry and Age_bracket changes view
                    """)

    with tabs[4]:

        st.markdown("### Individual Benefit Projection")
        st.caption("Employee assumed to start in 2025 at tenure 0.")
        if selected_age == "All" or selected_industry == "All Industries":

            st.markdown("""
            <div style="
                background-color:#FDECEC;
                border-left:6px solid #C62828;
                padding:15px;
                border-radius:8px;
                font-weight:600;
                color:#7A0000;
                margin-bottom:15px;
            ">
            ⚠ Please select a specific Industry and Age Bracket for Individual Projection.<br>
            One employee cannot belong to multiple industries or age groups.
            </div>
            """, unsafe_allow_html=True)

            st.stop()
        else:

            sim_tenure = st.slider("Years of Service", 1, 15, 5)

            target_year = BASE_YEAR + sim_tenure

            df = fund_scenarios_full.copy()
            # ---------------------------
            # Industry Filter
            # ---------------------------
            #df = df[df["industry"] == selected_industry_lower]

            if selected_industry != "All Industries":
                selected_industry_lower = selected_industry.lower()
                df = df[df["industry"] == selected_industry_lower]


            # ---------------------------
            # Age Filter
            # ---------------------------
            if selected_age != "All":
                df = df[df["age_bracket"] == selected_age.lower()]
            
            # ---------------------------
            # Cohort Filter (2025_0)
            # ---------------------------
            df = df[df["cohort"] == "2025_0"]
    
            
            # ---------------------------
            # Year & Tenure Filter
            # ---------------------------
            df = df[
                (df["year"] == target_year) &
                (df["tenure"] == sim_tenure)
            ]

            if df.empty:
                st.markdown("""
                <div style="
                    background-color:#FDECEC;
                    border-left:6px solid #C62828;
                    padding:16px;
                    border-radius:8px;
                    font-weight:600;
                    color:#7A0000;
                    margin-top:10px;
                    margin-bottom:15px;
                ">
                    ⚠ No surviving employees for selected tenure.<br>
                    All employees have exited before this year.
                </div>
                """, unsafe_allow_html=True)
                st.stop()

            survivors = df["survived_employee"].sum()

            if survivors == 0:
                
                
                st.markdown("""
                                <div style="
                                    background-color:#FDECEC;
                                    border-left:6px solid #C62828;
                                    padding:16px;
                                    border-radius:8px;
                                    font-weight:600;
                                    color:#7A0000;
                                    margin-top:10px;
                                    margin-bottom:15px;
                                ">
                                    ⚠ No surviving employees .<br>
                                    All employees have exited at this age group.
                                </div>
                                """, unsafe_allow_html=True)
                st.stop()
        
            per_0 = df["fund_0_exit_adj"].sum() / survivors
            # 4%, 6%, 8% per person
            per_4 = df["fund_4_exit_adj"].sum() / survivors
            per_6 = df["fund_6_exit_adj"].sum() / survivors
            per_8 = df["fund_8_exit_adj"].sum() / survivors
            
            st.markdown("### Projected Benefit Per Employee (AED)")

            c0, c1, c2, c3, c4 = st.columns(5)

            card_style = """
                height:120px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                background-color:#ffffff;
                border-radius:12px;
                border:1px solid #BDD4E7;
                padding:10px;
            """

            highlight_style = """
                height:120px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                align-items:center;
                background-color:#F5B71820;
                border-radius:12px;
                border:2px solid #F5B718;
                padding:10px;
            """

            def render_card(col, title, tag, value, highlight=False):
                style = highlight_style if highlight else card_style
                col.markdown(
                    f"""
                    <div style="{style}">
                        <div style="font-size:13px; color:#77878C;">{title}</div>
                        <div style="
                            font-size:11px;
                            background:#EFD59B;
                            padding:3px 8px;
                            border-radius:8px;
                            margin:6px 0;
                            font-weight:600;">
                            {tag}
                        </div>
                        <div style="font-size:26px; font-weight:700; color:#053048;">
                            {value:,.0f}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            render_card(c0, "Unfunded", "No Investment", per_0)
            render_card(c1, "4% Return", "Conservative", per_4)
            render_card(c2, "6% Return", "Base Case", per_6)
            render_card(c3, "8% Return", "High Growth", per_8)
            val = per_6 - per_0
            val_pct = (val / per_0 * 100) if per_0 > 0 else 0
            render_card(c4,"6% vs 0%",f"Value Created (+{val_pct:.1f}%)",val_pct,highlight=True)
            st.markdown("---")

        st.caption(
            """
            **Methodology:**  
            Fund value per employee is calculated as:  
            Total Fund Accumulated ÷ Total Surviving Employees  
            Values represent the average benefit per active employee 
            in the selected industry and age group.
            """
        )
    
