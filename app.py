import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pipeline2 import *
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
    logo = Image.open("data/Synarchy_Primary_Logo - Blue Synarchy.png")
    st.image(logo, width=180)

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




with main_col:
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
    # Optimize types for faster groupby/merge
    if "Industry" in merged_df.columns:
        merged_df["Industry"] = merged_df["Industry"].astype("category")
    if "Age_Bracket" in merged_df.columns:
        merged_df["Age_Bracket"] = merged_df["Age_Bracket"].astype("category")


    if "industry_assumptions" not in st.session_state:
        st.session_state.industry_assumptions = merged_df.copy()

    # ==========================================================
    # LOAD SURVIVAL TEMPLATES
    # ==========================================================

    @st.cache_data
    def load_template():
        return generate_survival_template_cohort_style(META_INFO)

    survival_template = load_template()


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

    @st.cache_data(show_spinner=False)
    def run_full_engine(industry_assumptions,
                        fund_return,
                        leakage_rate):

        # ==========================================================
        # 1️⃣ Employee + Salary Forecast
        # ==========================================================

        emp_forecast, sal_forecast = generate_employee_salary_forecast(
            EMPLOYEE_SALARY,
            industry_assumptions,
            start_year=BASE_YEAR
        )

        # ==========================================================
        # 2️⃣ Survival Template
        # ==========================================================

        survival_template = generate_survival_template_cohort_style(
            META_INFO,
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
            pd.read_excel(ECONOMIC_FILE),
            leakage_rate
        )

        impact_df = impact_df.rename(columns={
            "output_impact": "Output_Impact",
            "gva_impact": "GVA_Impact",
            "jobs_impact": "Jobs_Impact"
        })

        economic_df = pd.read_excel(ECONOMIC_FILE)

        economic_df["Industry"] = economic_df["Industry"].str.lower().str.strip()

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

        st.markdown("### Input Parameters")

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


    st.markdown("## Full Economy Structure")

    if baseline_year == "2026-2040":

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
        marker_color="#053048"
    ))

    # ----------------------------------
    # GVA Bars
    # ----------------------------------
    fig.add_trace(go.Bar(
        x=eco_grouped["SectorMap"],
        y=eco_grouped["GVA_Bn"],
        name="GVA Impact (Bn)",
        marker_color="#8BAAAD"
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
        marker=dict(color="#F5B718", size=8),
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



    # ==========================================================
    # DYNAMIC SCENARIO (FULL ENGINE RUN ONCE, CACHED)
    # ==========================================================
    # Create a unique key based on current parameters
    import hashlib
    import pickle
    def get_engine_key(assumptions, fund_return, leakage):
        # Use a hash of the assumptions DataFrame and parameters
        assumptions_bytes = pickle.dumps(assumptions)
        key_str = assumptions_bytes + str(fund_return).encode() + str(leakage).encode()
        return hashlib.md5(key_str).hexdigest()

    engine_key = get_engine_key(st.session_state.industry_assumptions, fund_return, leakage)

    if 'dynamic_engine_cache' not in st.session_state:
        st.session_state.dynamic_engine_cache = {}

    if engine_key not in st.session_state.dynamic_engine_cache:
        st.session_state.dynamic_engine_cache[engine_key] = run_full_engine(
            st.session_state.industry_assumptions,
            fund_return,
            leakage
        )

    combined_full, industry_full, impact_full = st.session_state.dynamic_engine_cache[engine_key]


    # Filtered data for selected industry + age
    selected_industry_lower = selected_industry.lower()
    selected_age_lower = selected_age.lower()

    if selected_age != "All":

        combined_dyn = combined_full[
            (combined_full["industry"] == selected_industry_lower) &
            (combined_full["age_bracket"] == selected_age_lower)
        ]

    else:
        combined_dyn = combined_full[
            combined_full["industry"] == selected_industry_lower
        ]


    selected_industry_lower = selected_industry.lower()
    selected_age_lower = selected_age.lower()

    if selected_age != "All":

        industry_dyn = industry_full[
            (industry_full["industry"] == selected_industry_lower) &
            (industry_full["age_bracket"] == selected_age_lower)
        ].copy()

        impact_dyn = impact_full[
            (impact_full["industry"] == selected_industry_lower) &
            (impact_full["age_bracket"] == selected_age_lower)
        ].copy()

    else:

        industry_dyn = industry_full[
            industry_full["industry"] == selected_industry_lower
        ].copy()

        impact_dyn = impact_full[
            impact_full["industry"] == selected_industry_lower
        ].copy()

    # Full economy for economic tab
    impact_economy = impact_full


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
    # JOBS IMPACT (ASSUMPTION LINKED)
    # ==========================================================

    with tabs[0]:

        jobs_df = impact_dyn.groupby("year")["Jobs_Impact"].sum().reset_index()
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
            yaxis_title="Jobs Impact (Thousand)"
        )

        st.plotly_chart(fig, use_container_width=True)



    # Fund Risk
    with tabs[1]:

        st.markdown("### Fund Growth Under Different Return Assumptions")

        # -------------------------------------------------------
        # Base contributions from selected scenario
        # -------------------------------------------------------

        base_df = industry_full.copy()

        # Aggregate yearly contributions
        contrib_year = base_df.groupby("year")[
            "annual_fund_contribution"
        ].sum().reset_index()

        years = contrib_year["year"].tolist()

        # -------------------------------------------------------
        # Function to simulate fund roll-forward
        # -------------------------------------------------------

        def simulate_fund(contrib_df, return_rate):
            fund = 0
            balances = []

            for _, row in contrib_df.iterrows():
                fund = fund * (1 + return_rate)
                fund += row["annual_fund_contribution"]
                balances.append(fund)

            return balances

        # -------------------------------------------------------
        # Fixed return comparisons
        # -------------------------------------------------------

        fixed_returns = [0.04, 0.06, 0.08]

        fig = go.Figure()

        for r, color in zip(
            fixed_returns,
            ["#053048", "#8BAAAD", "#F5B718"]
        ):

            balances = simulate_fund(contrib_year, r)

            fig.add_trace(go.Scatter(
                x=years,
                y=[b/1e9 for b in balances],
                name=f"{int(r*100)}%",
                line=dict(width=3, color=color)
            ))

    # -------------------------------------------------------
    # User-selected return (from global slider)
    # -------------------------------------------------------

    user_balances = simulate_fund(contrib_year, fund_return)

    fig.add_trace(go.Scatter(
        x=years,
        y=[b/1e9 for b in user_balances],
        name=f"Selected ({int(fund_return*100)}%)",
        line=dict(width=4, dash="dash", color="#93838E")
    ))

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Fund Balance (Bn)",
        legend=dict(orientation="h", y=1.1),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)



    # ==========================================================
    # Economic
    # ==========================================================

    # ==========================================================
    # Economic
    # ==========================================================

    with tabs[2]:

        st.markdown("### Economic Impact (Scenario Driven) - All Industry Groups Included")


        year_options = sorted(impact_full["year"].dropna().astype(int).unique())
        economic_year = st.selectbox(
            "Select Year",
            year_options,
            key="economic_tab_year"
        )

        eco = impact_full[
            impact_full["year"] == economic_year
        ].copy()

        # Unit Conversions
        eco["Output_Mn"] = eco["Output_Impact"] / 1_000_000
        eco["GVA_Mn"] = eco["GVA_Impact"] / 1_000_000
        eco["Jobs_K"] = eco["Jobs_Impact"] / 1_000

        # Brand Color Sequence
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
            title="Output Impact by Sector (Million)"
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
            legend=dict(font=dict(color="#053048"))
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
            legend=dict(font=dict(color="#053048"))
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
            title="Employment Impact by Sector (Thousand Jobs)"
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
            legend=dict(font=dict(color="#053048"))
        )

        c3.plotly_chart(fig_jobs, use_container_width=True)


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
            marker_color="#BDD4E7",  # light blue
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
            line=dict(color="#EFD59B", width=4),  # green
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

st.markdown(
    """
    <div style="
        text-align:center;
        font-size:20px;
        color:#77878C;
        margin-top:8px;">
        * All currency values are expressed in AED (United Arab Emirates Dirham).
    </div>
    """,
    unsafe_allow_html=True
)
