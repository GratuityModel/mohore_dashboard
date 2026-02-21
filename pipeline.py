import pandas as pd
import numpy as np


def generate_merged_industry_data(
    industry_desc,
    industry_rates,
    save_output=False,
    output_path=None
):
    # Assumes industry_desc and industry_rates are already DataFrames
    industry_desc = industry_desc.copy()
    industry_rates = industry_rates.copy()
    industry_desc.columns = industry_desc.columns.str.strip()
    industry_rates.columns = industry_rates.columns.str.strip()
    if "Industry" not in industry_desc.columns:
        raise ValueError("Industry column missing in industry description DataFrame.")

    # -----------------------------
    # 2. Merge
    # -----------------------------
    merged_df = industry_desc.merge(
        industry_rates,
        on="Industry",
        how="left"
    )

    # -----------------------------
    # 3. Keep Required Columns (safe filtering)
    # -----------------------------
    required_columns = [
        'Industry',
        'Age_Bracket',
        'Retirement Rate',
        'Death Rate',
        'Emp Growth %',
        'Attrition %',
        'Replacement Hiring %',
        'Expansion Hiring %',
        'Total Hiring %',
        'Net Churn %',
        'Salary Growth %'
    ]

    merged_df = merged_df[
        [c for c in required_columns if c in merged_df.columns]
    ]

    # -----------------------------
    # 4. Clean Percentage Columns
    # -----------------------------
    pct_columns = [
        c for c in required_columns
        if c in merged_df.columns and (
            "%" in c or "Rate" in c
        )
    ]

    # Remove % symbol if exists
    for col in pct_columns:
        merged_df[col] = (
            merged_df[col]
            .astype(str)
            .str.replace("%", "", regex=False)
        )

    merged_df[pct_columns] = merged_df[pct_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    print("i am here")
    # Convert >1 values to decimal
    for col in pct_columns:
        if merged_df[col].max() > 1:
            merged_df[col] = merged_df[col] / 100
            print(merged_df[col])

    # -----------------------------
    # 5. Recalculate Metrics
    # -----------------------------
    merged_df['Total Hiring %'] = (
        merged_df['Replacement Hiring %'] +
        merged_df['Expansion Hiring %']
    )

    # merged_df['Attrition %'] = (
    #     merged_df['Attrition %'] + 0.005
    # )

    merged_df['Attrition %'] = (
        merged_df['Attrition %']
    )

    merged_df['Total Exit (q)'] = (
        merged_df['Retirement Rate'] +
        merged_df['Death Rate'] +
        merged_df['Attrition %']
    ).clip(upper=1)

    merged_df['Net Churn %'] = (
        merged_df['Total Hiring %'] -
        merged_df['Total Exit (q)']
    )

    # -----------------------------
    # 6. Reorder
    # -----------------------------
    final_order = [
        "Industry",
        "Age_Bracket",
        "Expansion Hiring %",
        "Replacement Hiring %",
        "Total Hiring %",
        "Attrition %",
        "Retirement Rate",
        "Death Rate",
        "Total Exit (q)",
        "Salary Growth %",
        "Net Churn %"
    ]

    merged_df = merged_df[
        [c for c in final_order if c in merged_df.columns]
    ]

    # -----------------------------
    # 7. Optional Save
    # -----------------------------
    if save_output and output_path:
        merged_df.to_excel(output_path, index=False)

    return merged_df


def generate_employee_salary_forecast(
    df_emp,
    merged_industry_df,
    start_year=2025,
    end_year=2040,
    save_output=False,
    employee_output_path=None,
    salary_output_path=None
):
    # Assumes df_emp and merged_industry_df are already DataFrames
    df_emp = df_emp.copy()
    df_rates = merged_industry_df.copy()
    df_emp.columns = df_emp.columns.str.strip()
    df_rates.columns = df_rates.columns.str.strip()
    # Standardize names
    df_emp = df_emp.rename(columns={
        "Average Basic Salary": "Average_Base_Salary"
    })
    df_rates = df_rates.rename(columns={
        "Age_Bracket": "Age_Brackets"
    })

    # ==========================================================
    # 2. MERGE RATES
    # ==========================================================
    merge_cols = [
        "Industry",
        "Age_Brackets",
        "Total Exit (q)",
        "Total Hiring %",
        "Salary Growth %",
        "Expansion Hiring %"
    ]

    df = df_emp.merge(
        df_rates[merge_cols],
        on=["Industry", "Age_Brackets"],
        how="left"
    )

    df[["Total Exit (q)", "Total Hiring %", "Salary Growth %"]] = (
        df[["Total Exit (q)", "Total Hiring %", "Salary Growth %"]]
        .fillna(0)
    )

    # ==========================================================
    # 3. BASE YEAR
    # ==========================================================
    df[f"Emp_{start_year}"] = df["Employees"]
    df[f"Salary_{start_year}"] = df["Average_Base_Salary"]

    # ==========================================================
    # 4. BUILD FULL CUMULATIVE SERIES
    # ==========================================================
    tenure0_mask = df["Tenure"] == 0
    non_tenure0_mask = ~tenure0_mask

    # Keep base year cumulative copy
    df[f"Emp_{start_year}_cum"] = df[f"Emp_{start_year}"]

    for year in range(start_year + 1, end_year + 1):

        prev = year - 1

        # CUMULATIVE expansion growth (tenure 0 only)
        df.loc[tenure0_mask, f"Emp_{year}_cum"] = (
            df.loc[tenure0_mask, f"Emp_{prev}_cum"]
            * (1 + df.loc[tenure0_mask, "Expansion Hiring %"])
        )

        # Other tenures remain zero cumulative
        df.loc[non_tenure0_mask, f"Emp_{year}_cum"] = 0

        # Salary grows normally (unchanged)
        df[f"Salary_{year}"] = (
            df[f"Salary_{prev}"] *
            (1 + df["Salary Growth %"])
        )
    

    # ==========================================================
    # 5. CONVERT TO INCREMENTAL (2026 onward)
    # ==========================================================

    df[f"Emp_{start_year}"] = df[f"Emp_{start_year}_cum"]

    for year in range(start_year + 1, end_year + 1):

        prev = year - 1

        df[f"Emp_{year}"] = (
            df[f"Emp_{year}_cum"] -
            df[f"Emp_{prev}_cum"]
        )

    # Keep only tenure 0 incremental
    emp_cols = [f"Emp_{y}" for y in range(start_year, end_year + 1)]
    df.loc[non_tenure0_mask, emp_cols[1:]] = 0
    cum_cols = [c for c in df.columns if c.endswith("_cum")]
    df.drop(columns=cum_cols, inplace=True)

    # ==========================================================
    # 6. AGGREGATE EMPLOYEES
    # ==========================================================
    emp_cols = [c for c in df.columns if c.startswith("Emp_")]

    employee_agg = (
        df.groupby(
            ["Industry", "Age_Brackets", "Tenure"],
            as_index=False
        )[emp_cols]
        .sum()
    )

    salary_cols = [f"Salary_{y}" for y in range(start_year, end_year + 1)]

    salary_agg = (
        df.groupby(
            ["Industry", "Age_Brackets", "Tenure"],
            as_index=False
        )[salary_cols]
        .first()
    )
    salary_agg = salary_agg[
        ["Industry", "Age_Brackets", "Tenure"] +
        [f"Salary_{y}" for y in range(start_year, end_year + 1)]
    ]

    # ==========================================================
    # 8. NEW HIRING LOGIC
    # ==========================================================
    emp_cols_excl_base = [
        c for c in employee_agg.columns
        if c.startswith("Emp_") and c != f"Emp_{start_year}"
    ]

    mask_invalid = ~employee_agg["Tenure"].isin([0, 0.5])
    employee_agg.loc[mask_invalid, emp_cols_excl_base] = 0

    # ==========================================================
    # 9. OPTIONAL SAVE
    # ==========================================================
    if save_output:
        if employee_output_path:
            employee_agg.to_excel(employee_output_path, index=False)
        if salary_output_path:
            salary_agg.to_excel(salary_output_path, index=False)

    return employee_agg, salary_agg


def generate_survival_template_cohort_style(
    meta_info_df,
    start_year=2025,
    end_year=2040
):
    """
    Creates survival template in cohort format + extra fixed 2025 cohort block.
    Structure 1:
        Normal yearly cohorts (2025_0, 2026_0, ...)
    Structure 2:
        Fixed 2025 starting cohort
        Tenure starts from 1 and increases every year
    """
    # Assumes meta_info_df is already a DataFrame
    df_raw = meta_info_df.copy()
    df_raw.columns = df_raw.columns.str.strip()
    industries = df_raw["Industry"].dropna().unique()
    age_bracket = df_raw["Age_Bracket"].dropna().unique()
    projection_years = range(start_year, end_year + 1)
    records = []

    # ----------------------------------------------------------
    # 2. ORIGINAL COHORT STRUCTURE (UNCHANGED)
    # ----------------------------------------------------------
    for ind in industries:
        for age in age_bracket:

            for cohort_start in projection_years:

                cohort_name = f"{cohort_start}_0"

                for year in projection_years:

                    if year >= cohort_start:

                        tenure = year - cohort_start

                        records.append([
                            ind,
                            age,
                            cohort_name,
                            year,
                            tenure
                        ])

    max_initial_tenure = df_raw["Tenure"].max()

    for ind in industries:
        for age in age_bracket:

            for initial_tenure in range(1, int(max_initial_tenure) + 1):

                cohort_name = f"{start_year}_{initial_tenure}"

                for year in projection_years:

                    tenure = initial_tenure + (year - start_year)

                    records.append([
                        ind,
                        age,
                        cohort_name,
                        year,
                        tenure
                    ])

    survival_template = pd.DataFrame(
        records,
        columns=[
            "Industry",
            "Age_Bracket",
            "cohort",
            "Year",
            "Tenure"
        ]
    )

    survival_template = survival_template.sort_values(
        ["Industry", "Age_Bracket", "cohort", "Year"]
    ).reset_index(drop=True)

    return survival_template


def attach_salary_to_survival(
    survival_template_df,
    salary_forecast_df
):
    # Assumes DataFrames are already provided
    surv = survival_template_df.copy()
    sal = salary_forecast_df.copy()

    # ----------------------------
    # 1. Standardize column names
    # ----------------------------
    surv.columns = surv.columns.str.strip()
    sal.columns = sal.columns.str.strip()

    sal = sal.rename(columns={
        "Age_Brackets": "Age_Bracket"
    })

    # ----------------------------
    # 2. Melt salary wide → long
    # ----------------------------
    salary_cols = [c for c in sal.columns if c.startswith("Salary_")]

    sal_long = sal.melt(
        id_vars=["Industry", "Age_Bracket", "Tenure"],
        value_vars=salary_cols,
        var_name="Year",
        value_name="Salary"
    )

    sal_long["Year"] = sal_long["Year"].str.extract(r"(\d+)").astype(int)

    # ----------------------------
    # 3. Merge with survival
    # ----------------------------
    merged = surv.merge(
        sal_long,
        on=["Industry", "Age_Bracket", "Tenure", "Year"],
        how="left"
    )

    return merged
def attach_employees_to_survival(
    survival_template_df,
    employee_forecast_df
):
    # Assumes DataFrames are already provided
    surv = survival_template_df.copy()
    emp = employee_forecast_df.copy()

    # ----------------------------
    # 1. Standardize columns
    # ----------------------------
    surv.columns = surv.columns.str.strip()
    emp.columns = emp.columns.str.strip()

    emp = emp.rename(columns={
        "Age_Brackets": "Age_Bracket"
    })

    # ----------------------------
    # 2. Melt employee wide → long
    # ----------------------------
    emp_cols = [c for c in emp.columns if c.startswith("Emp_")]

    emp_long = emp.melt(
        id_vars=["Industry", "Age_Bracket", "Tenure"],
        value_vars=emp_cols,
        var_name="Year",
        value_name="Employees"
    )

    emp_long["Year"] = emp_long["Year"].str.extract(r"(\d+)").astype(int)

    # ----------------------------
    # 3. Keep only non-zero employees
    # ----------------------------
    emp_long = emp_long[emp_long["Employees"] > 0]

    # ----------------------------
    # 4. Merge into survival template
    # ----------------------------
    merged = surv.merge(
        emp_long,
        on=["Industry", "Age_Bracket", "Tenure", "Year"],
        how="left"
    )

    # Replace missing with 0
    merged["Employees"] = merged["Employees"].fillna(0)

    return merged


def attach_exit_and_replacement(
    survival_with_employees_df,
    merged_industry_df
):
    # Assumes DataFrames are already provided
    surv = survival_with_employees_df.copy()
    rates = merged_industry_df.copy()

    # --------------------------------
    # 1. Standardize column names
    # --------------------------------
    surv.columns = surv.columns.str.strip()
    rates.columns = rates.columns.str.strip()

    # Align naming
    rates = rates.rename(columns={
        "Industry": "industry",
        "Age_Bracket": "age_bracket",
        "Total Exit (q)": "exit_rate",
        "Replacement Hiring %": "replacement_rate"
    })

    surv.columns = surv.columns.str.strip().str.lower()

    # Lowercase for safe matching
    surv["industry"] = surv["industry"].astype(str).str.strip().str.lower()
    surv["age_bracket"] = surv["age_bracket"].astype(str).str.strip().str.lower()

    rates["industry"] = rates["industry"].astype(str).str.strip().str.lower()
    rates["age_bracket"] = rates["age_bracket"].astype(str).str.strip().str.lower()

    # --------------------------------
    # 2. Merge Rates
    # --------------------------------
    updated = surv.merge(
        rates[["industry", "age_bracket", "exit_rate", "replacement_rate"]],
        on=["industry", "age_bracket"],
        how="left"
    )

    # --------------------------------
    # 3. Override Replacement Logic
    # --------------------------------
    override_groups = ["<55", "55-59","60-64","65-69","70+"]

    updated.loc[
        updated["age_bracket"].isin(override_groups),
        "replacement_rate"
    ] = updated["exit_rate"]

    # --------------------------------
    # 4. Add Exit Mapping Columns
    # --------------------------------
    updated["exit_year"] = np.where(updated["year"] < 2040, updated["year"] + 1, np.nan)
    updated["exit_tenure"] = 0

    return updated


def run_full_survival_eosg_model(
    df,
    fund_return_rate=0.04,
    start_year=2025
):

    df = df.copy()
    df.columns = df.columns.str.lower().str.strip()

    df = df.sort_values(
        ["industry", "age_bracket", "cohort", "year"]
    ).reset_index(drop=True)

    final_blocks = []

    # -----------------------------------------------------
    # Loop Industry × Age_Bracket
    # -----------------------------------------------------
    for (ind, age), block in df.groupby(
        ["industry", "age_bracket"],
        sort=False
    ):

        block = block.sort_values(
            ["cohort", "year"]
        )

        exit_pool = {}

        cohort_groups = {
            c: g.copy()
            for c, g in block.groupby("cohort")
        }

        # Phase split
        phase1 = []
        phase2 = []

        for c, g in cohort_groups.items():
            first = g.iloc[0]
            if first["year"] == start_year and first["tenure"] > 0:
                phase1.append(c)
            else:
                phase2.append(c)

        # ==================================================
        # PROCESS ALL COHORTS
        # ==================================================
        for cohort_list in [phase1, phase2]:

            for c in cohort_list:

                g = cohort_groups[c].copy()
                g = g.sort_values("year")

                g["survived_employee"] = 0.0
                g["exit_employee"] = 0.0

                # -------------------------------------------
                # SURVIVAL ENGINE
                # -------------------------------------------
                for i in range(len(g)):

                    row = g.iloc[i]

                    if i == 0:

                        base = row["employees"]
                        exit_rate = row["exit_rate"]
                        repl_rate = row["replacement_rate"]

                        # Apply exit immediately (even in 2025 tenure > 0)
                        survived = round(base * (1 - exit_rate), 0)
                        exit_emp = round(base * exit_rate, 0)

                        if age in ["<55", "55-59","60-64","65-69","70+"]:
                            replacement = exit_emp
                        else:
                            replacement = round(exit_emp * repl_rate, 0)

                        g.iloc[i, g.columns.get_loc("survived_employee")] = survived
                        g.iloc[i, g.columns.get_loc("exit_employee")] = exit_emp

                        # Push replacements to next year tenure 0
                        key = (row["exit_year"], row["exit_tenure"])
                        exit_pool[key] = exit_pool.get(key, 0) + replacement

                        continue

                    prev_surv = g.iloc[i-1]["survived_employee"]
                    exit_rate = g.iloc[i-1]["exit_rate"]
                    repl_rate = g.iloc[i-1]["replacement_rate"]

                    survived = round(prev_surv * (1 - exit_rate),0)
                    exit_emp = round(prev_surv * exit_rate,0)

                    if age in ["<55", "55-59","60-64","65-69","70+"]:
                        replacement = exit_emp
                    else:
                        replacement = round(exit_emp * repl_rate,0)

                    g.iloc[i, g.columns.get_loc(
                        "survived_employee")] = survived
                    g.iloc[i, g.columns.get_loc(
                        "exit_employee")] = exit_emp

                    key = (
                        g.iloc[i-1]["exit_year"],
                        g.iloc[i-1]["exit_tenure"]
                    )

                    exit_pool[key] = exit_pool.get(
                        key, 0
                    ) + replacement

                # ==================================================
                # EOSG CALCULATION
                # ==================================================

                def gratuity_rate(tenure):
                    if tenure < 1:
                        return 0.0
                    elif tenure <= 5:
                        return tenure * 0.05833
                    elif tenure < 25:
                        return (5 * 0.05833) + (
                            (tenure - 5) * 0.08333
                        )
                    else:
                        return (5 * 0.05833) + (
                            (25 - 5) * 0.08333
                        )

                g["gratuity_rate"] = g["tenure"].apply(
                    gratuity_rate
                )

                g["gratuity_per_employee"] = (
                    g["salary"] * g["gratuity_rate"]
                )

                g["prev_gratuity_per_employee"] = (
                    g["gratuity_per_employee"].shift(1)
                )

                g["fund_contribution"] = np.where(
                    g["prev_gratuity_per_employee"].isna(),
                    g["gratuity_per_employee"] *
                    g["survived_employee"],
                    (g["gratuity_per_employee"]
                     - g["prev_gratuity_per_employee"])
                     * g["survived_employee"]
                )
                g["fund_contribution"] = np.maximum(g["fund_contribution"], 0)

                # ==================================================
                # FUND ROLL FORWARD
                # ==================================================

                # Initialize columns
                g["opening_fund_no_return"] = 0.0
                g["closing_fund_no_return"] = 0.0
                g["exit_payout_no_return"] = 0.0

                g["opening_fund_with_return"] = 0.0
                g["fund_return"] = 0.0
                g["closing_fund_with_return"] = 0.0
                g["exit_payout_with_return"] = 0.0

                fund_nr = 0.0
                fund_wr = 0.0

                for idx in g.index:

                    # -------------------
                    # WITHOUT RETURN
                    # -------------------
                    opening_nr = fund_nr

                    contribution = g.loc[idx,
                                         "fund_contribution"]

                    fund_nr += contribution

                    survived = g.loc[idx,
                                     "survived_employee"]
                    exited = g.loc[idx,
                                   "exit_employee"]

                    exit_ratio = (
                        exited / survived
                        if survived > 0 else 0
                    )

                    payout_nr = fund_nr * exit_ratio
                    fund_nr -= payout_nr

                    # -------------------
                    # WITH RETURN
                    # -------------------
                    opening_wr = fund_wr

                    fund_return = fund_wr * fund_return_rate
                    fund_wr += fund_return
                    fund_wr += contribution

                    payout_wr = fund_wr * exit_ratio
                    fund_wr -= payout_wr

                    # -------------------
                    # STORE
                    # -------------------
                    g.loc[idx, [
                        "opening_fund_no_return",
                        "exit_payout_no_return",
                        "closing_fund_no_return",
                        "opening_fund_with_return",
                        "fund_return",
                        "exit_payout_with_return",
                        "closing_fund_with_return"
                    ]] = [
                        opening_nr,
                        payout_nr,
                        fund_nr,
                        opening_wr,
                        fund_return,
                        payout_wr,
                        fund_wr
                    ]

                final_blocks.append(g)

    final_df = pd.concat(
        final_blocks
    ).reset_index(drop=True)

    return final_df

def aggregate_industry_year_combined(df):
    """
    Aggregates Industry × Year metrics
    for full survival + EOSG output.
    """

    df = df.copy()

    # ==========================================================
    # 1. PRE-CALCULATIONS
    # ==========================================================
    df["salary_x_emp"] = (
        df["salary"] * df["survived_employee"]
    )

    df["gratuity_x_emp"] = (
        df["gratuity_per_employee"] *
        df["survived_employee"]
    )

    df["annual_salary_total"] = (
        df["salary_x_emp"] * 12
    )

    df["annual_gratuity_total"] = (
        df["gratuity_x_emp"] * 12
    )

    # ==========================================================
    # 2. GROUP & SUM
    # ==========================================================
    grouped = df.groupby(
        ["industry", "year"],
        as_index=False
    ).agg(
        total_employees=("survived_employee", "sum"),
        salary_weighted_sum=("salary_x_emp", "sum"),
        annual_total_salary=("annual_salary_total", "sum"),
        gratuity_weighted_sum=("gratuity_x_emp", "sum"),
        annual_total_gratuity_accrual=("annual_gratuity_total", "sum"),
        annual_fund_contribution=("fund_contribution", "sum"),
        closing_fund_no_return=("closing_fund_no_return", "sum"),
        closing_fund_with_return=("closing_fund_with_return", "sum"),
        exit_employee_total=("exit_employee", "sum")
    )

    # ==========================================================
    # 3. WEIGHTED AVERAGES
    # ==========================================================
    grouped["weighted_monthly_salary"] = np.where(
        grouped["total_employees"] > 0,
        grouped["salary_weighted_sum"] /
        grouped["total_employees"],
        0
    )

    grouped["weighted_monthly_gratuity_per_employee"] = np.where(
        grouped["total_employees"] > 0,
        grouped["gratuity_weighted_sum"] /
        grouped["total_employees"],
        0
    )

    # ==========================================================
    # 4. OPTIONAL FUND GAP METRICS (Helpful for analysis)
    # ==========================================================
    grouped["fund_gap_no_return"] = (
        grouped["annual_total_gratuity_accrual"] -
        grouped["closing_fund_no_return"]
    )

    grouped["fund_gap_with_return"] = (
        grouped["annual_total_gratuity_accrual"] -
        grouped["closing_fund_with_return"]
    )

    # ==========================================================
    # 5. FINAL COLUMN ORDER
    # ==========================================================
    grouped = grouped[[
        "industry",
        "year",
        "total_employees",
        "exit_employee_total",
        "weighted_monthly_salary",
        "annual_total_salary",
        "weighted_monthly_gratuity_per_employee",
        "annual_total_gratuity_accrual",
        "annual_fund_contribution",
        "closing_fund_no_return",
        "closing_fund_with_return",
        "fund_gap_no_return",
        "fund_gap_with_return"
    ]]

    return grouped

def apply_economic_impact_combined(
    industry_year_df,
    economic_df,
    leakage_rate=0.28
):
    """
    Applies economic multipliers to
    Industry × Year aggregated survival output.
    """

    df = industry_year_df.copy()
    econ = economic_df.copy()

    # ==========================================================
    # 1. STANDARDIZE KEYS
    # ==========================================================
    df["industry"] = (
        df["industry"].astype(str)
        .str.strip()
        .str.lower()
    )

    econ["industry"] = (
        econ["Industry"].astype(str)
        .str.strip()
        .str.lower()
    )

    # ==========================================================
    # 2. MERGE ECONOMIC PARAMETERS
    # ==========================================================
    df = df.merge(
        econ,
        on="industry",
        how="left"
    )

    # ==========================================================
    # 3. YEAR TOTALS (VECTORIZE ONCE)
    # ==========================================================
    yearly_totals = df.groupby(
        "year",
        as_index=False
    ).agg(
        yearly_total_payroll=("annual_total_salary", "sum"),
        yearly_total_contribution=("annual_fund_contribution", "sum")
    )

    df = df.merge(
        yearly_totals,
        on="year",
        how="left"
    )

    # ==========================================================
    # 4. CONTRIBUTION ALLOCATION
    # ==========================================================
    df["contribution_allocated"] = np.where(
        df["yearly_total_payroll"] > 0,
        df["yearly_total_contribution"]
        * df["annual_total_salary"]
        / df["yearly_total_payroll"],
        0
    )

    # ==========================================================
    # 5. ECONOMIC IMPACT CALCULATIONS
    # ==========================================================

    # Net new savings entering system
    df["net_new_saving"] = df["contribution_allocated"]

    # Leakage assumption
    df["leakage_assumption"] = leakage_rate

    # Domestic investable portion
    df["domestic_investable"] = (
        df["net_new_saving"] * (1 - leakage_rate)
    )

    # Output impact
    df["output_impact"] = (
        df["Output_Multiplier_Type_I"]
        * df["domestic_investable"]
    )

    # GVA impact
    df["gva_impact"] = (
        df["GVA_to_Output_Ratio"]
        * df["domestic_investable"]
    )

    # Jobs impact
    df["jobs_impact"] = (
        df["Employment_Multiplier (jobs per AED 1M output)"]
        * (df["domestic_investable"] / 1_000_000)
    )

    # ==========================================================
    # 6. FINAL OUTPUT ORDER
    # ==========================================================
    df = df[[
        "industry",
        "year",
        "total_employees",
        "annual_total_salary",
        "annual_fund_contribution",
        "closing_fund_with_return",
        "net_new_saving",
        "domestic_investable",
        "output_impact",
        "gva_impact",
        "jobs_impact"
    ]]

    return df

def generate_cohort_fund_scenarios(combined_df):
    """
    Cohort-wise fund simulation at:
        0%, 4%, 6%, 8%

    Includes:
        - Fund accumulation
        - Exit-adjusted remaining balance

    Returns:
        fund_0, fund_4, fund_6, fund_8
        fund_0_exit_adj, fund_4_exit_adj,
        fund_6_exit_adj, fund_8_exit_adj
    """

    df = combined_df.copy()

    df = df.sort_values(
        ["industry", "age_bracket", "cohort", "year"]
    )

    result_blocks = []

    return_rates = {
        "0": 0.0,
        "4": 0.04,
        "6": 0.06,
        "8": 0.08
    }

    for (ind, age, cohort), g in df.groupby(
        ["industry", "age_bracket", "cohort"],
        sort=False
    ):

        g = g.sort_values("year").copy()

        for label, r in return_rates.items():

            fund = 0
            balances = []
            balances_exit_adj = []

            for _, row in g.iterrows():

                contribution = row["fund_contribution"]
                survivors = row["survived_employee"]
                exits = row["exit_employee"]

                # ---------------------------------------------
                # Roll forward with return
                # ---------------------------------------------
                fund = fund * (1 + r)
                fund += contribution

                balances.append(fund)

                # ---------------------------------------------
                # Exit payout logic
                # ---------------------------------------------
                total_before_exit = survivors + exits

                if total_before_exit > 0:
                    exit_ratio = exits / total_before_exit
                else:
                    exit_ratio = 0.0

                payout = fund * exit_ratio
                fund_after_exit = fund - payout

                balances_exit_adj.append(fund_after_exit)

                # Next year starts from remaining balance
                fund = fund_after_exit

            g[f"fund_{label}"] = balances
            g[f"fund_{label}_exit_adj"] = balances_exit_adj

        result_blocks.append(
            g[[
                "industry",
                "age_bracket",
                "cohort",
                "year",
                "tenure",
                "survived_employee",
                "exit_employee",
                "fund_contribution",
                "fund_0",
                "fund_4",
                "fund_6",
                "fund_8",
                "fund_0_exit_adj",
                "fund_4_exit_adj",
                "fund_6_exit_adj",
                "fund_8_exit_adj"
            ]]
        )

    final_df = pd.concat(result_blocks).reset_index(drop=True)

    return final_df


