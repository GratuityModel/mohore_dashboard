import pandas as pd
import numpy as np


def generate_merged_industry_data(
    industry_desc_path,
    industry_rates_path,
    save_output=False,
    output_path=None
):
    """
    Merges industry description with industry rates,
    cleans percentage columns, recalculates key metrics,
    and optionally saves output.

    Returns:
        merged_df (DataFrame)
    """

    # --------------------------------------
    # 1. Load Files
    # --------------------------------------
    industry_desc = pd.read_excel(industry_desc_path)
    industry_rates = pd.read_excel(industry_rates_path)

    industry_desc.columns = industry_desc.columns.str.strip()
    industry_rates.columns = industry_rates.columns.str.strip()

    # --------------------------------------
    # 2. Merge (Left Join on Industry)
    # --------------------------------------
    merged_df = industry_desc.merge(
        industry_rates,
        on="Industry",
        how="left"
    )

    # --------------------------------------
    # 3. Keep Required Columns
    # --------------------------------------
    merged_df = merged_df[[
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
    ]]

    # --------------------------------------
    # 4. Clean Percentage Columns
    # --------------------------------------
    pct_columns = [
        "Retirement Rate",
        "Death Rate",
        "Emp Growth %",
        "Attrition %",
        "Replacement Hiring %",
        "Expansion Hiring %",
        "Total Hiring %",
        "Net Churn %",
        "Salary Growth %"
    ]

    pct_columns = [col for col in pct_columns if col in merged_df.columns]

    merged_df[pct_columns] = merged_df[pct_columns].apply(
        pd.to_numeric, errors="coerce"
    )

    merged_df[pct_columns] = merged_df[pct_columns].applymap(
        lambda x: x / 100 if pd.notnull(x) and x > 1 else x
    )

    # --------------------------------------
    # 5. Recalculate Metrics
    # --------------------------------------
    merged_df['Total Hiring %'] = (
        merged_df['Replacement Hiring %'] +
        merged_df['Expansion Hiring %']
    )

    merged_df['Total Exit (q)'] = (
        merged_df['Retirement Rate'] +
        merged_df['Death Rate'] +
        merged_df['Attrition %']
    )

    merged_df['Total Exit (q)'] = np.where(
        merged_df['Total Exit (q)'] > 1,
        1,
        merged_df['Total Exit (q)']
    )

    merged_df['Net Churn %'] = (
        merged_df['Total Hiring %'] -
        merged_df['Total Exit (q)']
    )

    # --------------------------------------
    # 6. Reorder Columns
    # --------------------------------------
    final_column_order = [
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

    final_column_order = [
        col for col in final_column_order if col in merged_df.columns
    ]

    merged_df = merged_df[final_column_order]

    # --------------------------------------
    # 7. Optional Save
    # --------------------------------------
    if save_output and output_path is not None:
        merged_df.to_excel(output_path, index=False)

    return merged_df
import pandas as pd
import numpy as np


def generate_employee_salary_forecast(
    employee_salary_path,
    merged_industry_df,
    start_year=2025,
    end_year=2040,
    save_output=False,
    employee_output_path=None,
    salary_output_path=None
):
    """
    Generates:
        1. SideBySide Employee Forecast
        2. SideBySide Weighted Salary Forecast

    Parameters
    ----------
    employee_salary_path : str
        Path to Employee_Salary_Data_2025.xlsx
    merged_industry_df : DataFrame
        Output from Script 1 function (Data_Merge)
    start_year : int
    end_year : int
    save_output : bool
    employee_output_path : str
    salary_output_path : str

    Returns
    -------
    employee_agg : DataFrame
    salary_agg : DataFrame
    """

    # ==========================================================
    # 1. LOAD BASE EMPLOYEE DATA
    # ==========================================================
    df1 = pd.read_excel(employee_salary_path)
    df2 = merged_industry_df.copy()

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Standardize column names
    df1 = df1.rename(columns={
        "Age_Brackets": "Age_Brackets",
        "Average Basic Salary": "Average_Base_Salary"
    })

    df2 = df2.rename(columns={
        "Industry": "Industry",
        "Age_Bracket": "Age_Brackets"
    })

    # ==========================================================
    # 2. MERGE EXIT + HIRING + SALARY GROWTH
    # ==========================================================
    df = df1.merge(
        df2[[
            "Industry",
            "Age_Brackets",
            "Total Exit (q)",
            "Total Hiring %",
            "Salary Growth %"
        ]],
        on=["Industry", "Age_Brackets"],
        how="left"
    )

    df[["Total Exit (q)", "Total Hiring %", "Salary Growth %"]] = df[
        ["Total Exit (q)", "Total Hiring %", "Salary Growth %"]
    ].fillna(0)

    # ==========================================================
    # 3. BASE YEAR
    # ==========================================================
    df[f"Emp_{start_year}"] = df["Employees"]
    df[f"Salary_{start_year}"] = df["Average_Base_Salary"]

    # ==========================================================
    # 4. ROLLING FORECAST
    # ==========================================================
    for year in range(start_year + 1, end_year + 1):

        prev_year = year - 1

        hire_emp = df[f"Emp_{prev_year}"] * df["Total Hiring %"]

        df[f"Emp_{year}"] = (
            df[f"Emp_{prev_year}"] +
            hire_emp
        )

        df[f"Salary_{year}"] = (
            df[f"Salary_{prev_year}"] *
            (1 + df["Salary Growth %"])
        )

    # ==========================================================
    # 5. AGGREGATE EMPLOYEES
    # ==========================================================
    emp_cols = [col for col in df.columns if col.startswith("Emp_")]

    employee_agg = (
        df.groupby(["Industry", "Age_Brackets", "Tenure"], as_index=False)[emp_cols]
        .sum()
    )

    # ==========================================================
    # 6. WEIGHTED SALARY
    # ==========================================================
    for year in range(start_year, end_year + 1):
        df[f"SalaryEmp_{year}"] = (
            df[f"Salary_{year}"] *
            df[f"Emp_{year}"]
        )

    salaryemp_cols = [col for col in df.columns if col.startswith("SalaryEmp_")]

    salaryemp_agg = (
        df.groupby(["Industry", "Age_Brackets", "Tenure"], as_index=False)[salaryemp_cols]
        .sum()
    )

    salary_agg = employee_agg.copy()

    for year in range(start_year, end_year + 1):
        salary_agg[f"Salary_{year}"] = np.where(
            salary_agg[f"Emp_{year}"] == 0,
            0,
            salaryemp_agg[f"SalaryEmp_{year}"] /
            salary_agg[f"Emp_{year}"]
        )

    salary_agg = salary_agg[
        ["Industry", "Age_Brackets", "Tenure"] +
        [f"Salary_{y}" for y in range(start_year, end_year + 1)]
    ]

    # ==========================================================
    # 7. NEW HIRING LOGIC (Only tenure 0 or 0.5 allowed)
    # ==========================================================
    emp_cols_excl_base = [
        col for col in employee_agg.columns
        if col.startswith("Emp_") and col != f"Emp_{start_year}"
    ]

    mask = ~employee_agg["Tenure"].isin([0, 0.5])
    employee_agg.loc[mask, emp_cols_excl_base] = 0

    # ==========================================================
    # 8. OPTIONAL SAVE
    # ==========================================================
    if save_output:
        if employee_output_path:
            employee_agg.to_excel(employee_output_path, index=False)

        if salary_output_path:
            salary_agg.to_excel(salary_output_path, index=False)

    return employee_agg, salary_agg

def generate_old_employee_survival_template(
    meta_info_path,
    start_year=2025,
    end_year=2040
):
    """
    Generates old employee survival template grid (vectorized).
    """

    # --------------------------------
    # 1️⃣ Load Meta Info
    # --------------------------------
    df_raw = pd.read_csv(meta_info_path)

    industries = df_raw["Industry"].dropna().unique()
    age_buckets = df_raw["Age_Bracket"].dropna().unique()

    old_tenure_values = df_raw["Old_Tenure"].dropna().astype(int)

    min_tenure = old_tenure_values.min()
    max_tenure = old_tenure_values.max()

    old_tenures = range(min_tenure, max_tenure + 1)
    projection_years = range(start_year, end_year + 1)

    # --------------------------------
    # 2️⃣ Cartesian Product (FAST)
    # --------------------------------
    index = pd.MultiIndex.from_product(
        [industries, age_buckets, old_tenures, projection_years],
        names=[
            "industry",
            "age_bucket",
            "old_tenure_2025",
            "year"
        ]
    )

    df_old_progression = index.to_frame(index=False)

    # --------------------------------
    # 3️⃣ Compute Progressed Tenure
    # --------------------------------
    df_old_progression["tenure"] = (
        df_old_progression["old_tenure_2025"]
        + (df_old_progression["year"] - start_year)
    )

    return df_old_progression



def generate_new_employee_survival_template(
    meta_info_path
):
    """
    Generates rolling cohort survival template (vectorized).
    """

    # --------------------------------
    # 1️⃣ Load Meta Info
    # --------------------------------
    df_raw = pd.read_csv(meta_info_path)

    industries = df_raw["Industry"].dropna().unique()
    years = df_raw["Year"].dropna().astype(int).unique()
    tenures = sorted(df_raw["Tenure"].dropna().astype(float).unique())
    age_buckets = df_raw["Age_Bracket"].dropna().unique()

    start_year = min(years)
    end_year = max(years)

    # --------------------------------
    # 2️⃣ Cartesian Product
    # --------------------------------
    index = pd.MultiIndex.from_product(
        [industries, age_buckets, years, tenures],
        names=[
            "industry",
            "age_bucket",
            "cohort_start",
            "tenure"
        ]
    )

    df_final = index.to_frame(index=False)

    # --------------------------------
    # 3️⃣ Compute Year
    # --------------------------------
    df_final["year"] = (
        df_final["cohort_start"] +
        df_final["tenure"]
    )

    # --------------------------------
    # 4️⃣ Keep Only Valid Projection Years
    # --------------------------------
    df_final = df_final[
        df_final["year"] <= end_year
    ]

    df_final = df_final.sort_values(
        ["industry", "age_bucket", "cohort_start", "tenure"]
    ).reset_index(drop=True)

    return df_final



def attach_exit_rates(
    merged_industry_df,
    new_survival_df=None,
    old_survival_df=None
):
    """
    Attaches exit and hiring rates to survival templates.

    Parameters
    ----------
    merged_industry_df : DataFrame
        Output of Script 1 (industry merge function)

    new_survival_df : DataFrame (optional)
        Output of Script 3 (new survival template)

    old_survival_df : DataFrame (optional)
        Output of Script 4 (old survival template)

    Returns
    -------
    new_updated : DataFrame or None
    old_updated : DataFrame or None
    """

    # ----------------------------------------
    # 1️⃣ Prepare Exit Data
    # ----------------------------------------
    exit_df = merged_industry_df.copy()

    exit_df = exit_df[[
        "Industry",
        "Age_Bracket",
        "Total Exit (q)",
        "Total Hiring %"
    ]]

    exit_df = exit_df.rename(columns={
        "Industry": "industry",
        "Age_Bracket": "age_bucket",
        "Total Exit (q)": "total exit (q)",
        "Total Hiring %": "total hiring %"
    })
    # Normalize
    exit_df["industry"] = exit_df["industry"].str.strip().str.lower()
    exit_df["age_bucket"] = exit_df["age_bucket"].str.strip().str.lower()

    # ----------------------------------------
    # 2️⃣ Merge into NEW survival template
    # ----------------------------------------
    new_updated = None
    if new_survival_df is not None:

        new_df = new_survival_df.copy()
        new_df["industry"] = new_df["industry"].str.strip().str.lower()
        new_df["age_bucket"] = new_df["age_bucket"].str.strip().str.lower()

        new_updated = new_df.merge(
            exit_df,
            on=["industry", "age_bucket"],
            how="left"
        )

    # ----------------------------------------
    # 3️⃣ Merge into OLD survival template
    # ----------------------------------------
    old_updated = None
    if old_survival_df is not None:

        old_df = old_survival_df.copy()
        old_df["industry"] = old_df["industry"].str.strip().str.lower()
        old_df["age_bucket"] = old_df["age_bucket"].str.strip().str.lower()

        old_updated = old_df.merge(
            exit_df,
            on=["industry", "age_bucket"],
            how="left"
        )

    return new_updated, old_updated

import pandas as pd
import numpy as np

def generate_new_employee_full_calculation(
    new_survival_df,
    employee_forecast_df,
    salary_forecast_df,
    fund_return_rate=0.04
):
    """
    Full financial calculation for NEW employees
    Includes:
    - Workforce survival logic (Exit only, no hiring impact)
    - Gratuity accrual
    - Defined Benefit (No Return)
    - Defined Contribution (With Return)
    """

    # ---------------------------------------------------
    # 1️⃣ Standardize Columns
    # ---------------------------------------------------
    survival_df = new_survival_df.copy()
    employee_df = employee_forecast_df.copy()
    salary_df = salary_forecast_df.copy()

    survival_df.columns = survival_df.columns.str.strip().str.lower()
    employee_df.columns = employee_df.columns.str.strip().str.lower()
    salary_df.columns = salary_df.columns.str.strip().str.lower()

    employee_df = employee_df.rename(columns={"age_brackets": "age_bucket"})
    salary_df = salary_df.rename(columns={"age_brackets": "age_bucket"})

    survival_df = survival_df.rename(columns={
        "total exit (q)": "exit_rate",
        "total hiring %": "total_hiring_pct"
    })

    # Normalize strings
    def normalize(df):
        df["industry"] = df["industry"].str.strip().str.lower()
        df["age_bucket"] = df["age_bucket"].str.strip().str.lower()
        return df

    survival_df = normalize(survival_df)
    employee_df = normalize(employee_df)
    salary_df = normalize(salary_df)

    # Treat tenure 0 as 0.5
    survival_df["tenure"] = survival_df["tenure"].replace(0, 0.5)

    # ---------------------------------------------------
    # 2️⃣ Convert Forecasts to Long Format
    # ---------------------------------------------------
    emp_cols = [c for c in employee_df.columns if c.startswith("emp_")]
    emp_long = employee_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=emp_cols,
        var_name="year",
        value_name="forecast_employee"
    )
    emp_long["year"] = emp_long["year"].str.extract(r"(\d+)").astype(int)

    sal_cols = [c for c in salary_df.columns if c.startswith("salary_")]
    salary_long = salary_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=sal_cols,
        var_name="year",
        value_name="salary"
    )
    salary_long["year"] = salary_long["year"].str.extract(r"(\d+)").astype(int)

    # ---------------------------------------------------
    # 3️⃣ Merge Base Forecast
    # ---------------------------------------------------
    survival_df = survival_df.merge(
        emp_long,
        how="left",
        on=["industry", "age_bucket", "year", "tenure"]
    )

    survival_df = survival_df.sort_values(
        ["industry", "age_bucket", "cohort_start", "year"]
    )

    survival_df["survived_employee"] = np.nan
    survival_df["exit_employee"] = 0.0

    # ---------------------------------------------------
    # 4️⃣ Workforce Flow (Correct Vectorized EXIT ONLY)
    # ---------------------------------------------------

    survival_df = survival_df.sort_values(
        ["industry", "age_bucket", "cohort_start", "year"]
    )

    group_cols = ["industry", "age_bucket", "cohort_start"]

    # Base employees (first year of cohort)
    survival_df["base_employee"] = survival_df.groupby(group_cols)[
        "forecast_employee"
    ].transform("first")

    # Survival factor
    survival_df["survival_factor"] = 1 - survival_df["exit_rate"]

    # SHIFT survival factor so first year has no exit
    survival_df["shifted_factor"] = survival_df.groupby(group_cols)[
        "survival_factor"
    ].shift(1).fillna(1)

    # Cumulative survival
    survival_df["cum_survival"] = survival_df.groupby(group_cols)[
        "shifted_factor"
    ].cumprod()

    # Survived employees
    survival_df["survived_employee"] = (
        survival_df["base_employee"] *
        survival_df["cum_survival"]
    )

    # Exit employees
    survival_df["exit_employee"] = (
        survival_df.groupby(group_cols)["survived_employee"].shift(1)
        - survival_df["survived_employee"]
    ).clip(lower=0).fillna(0)



    # ---------------------------------------------------
    # 5️⃣ Merge Salary
    # ---------------------------------------------------
    survival_df = survival_df.merge(
        salary_long,
        how="left",
        on=["industry", "age_bucket", "tenure", "year"]
    )

    final_df = survival_df.copy()

    # ---------------------------------------------------
    # 6️⃣ Gratuity Calculation
    # ---------------------------------------------------
    def gratuity_rate(tenure):
        if tenure < 1:
            return 0.0
        elif tenure <= 5:
            return tenure * 0.05833
        elif tenure < 25:
            return (5 * 0.05833) + ((tenure - 5) * 0.08333)
        else:
            return (5 * 0.05833) + ((25 - 5) * 0.08333)

    final_df["gratuity_rate"] = final_df["tenure"].apply(gratuity_rate)

    final_df["gratuity_per_employee"] = (
        final_df["salary"] * final_df["gratuity_rate"]
    )

    # ---------------------------------------------------
    # 7️⃣ Incremental Fund Contribution
    # ---------------------------------------------------
    final_df = final_df.sort_values(
        ["industry", "age_bucket", "cohort_start", "year"]
    )

    final_df["prev_gratuity_per_employee"] = final_df.groupby(
        ["industry", "age_bucket", "cohort_start"]
    )["gratuity_per_employee"].shift(1)

    final_df["fund_contribution"] = np.where(
        final_df["prev_gratuity_per_employee"].isna(),
        final_df["gratuity_per_employee"] * final_df["survived_employee"],
        (final_df["gratuity_per_employee"]
         - final_df["prev_gratuity_per_employee"])
        * final_df["survived_employee"]
    )

    final_df["fund_contribution"] = final_df["fund_contribution"].clip(lower=0)

    # =====================================================
    # 8️⃣ & 9️⃣ Vectorized Fund Roll Forward
    # =====================================================

    final_df = final_df.sort_values(
        ["industry", "age_bucket", "cohort_start", "year"]
    )

    group_cols = ["industry", "age_bucket", "cohort_start"]

    # Previous survived employee
    final_df["prev_survived"] = final_df.groupby(group_cols)["survived_employee"].shift(1)

    # Exit ratio
    final_df["exit_ratio"] = (
        (final_df["prev_survived"] - final_df["survived_employee"])
        / final_df["prev_survived"]
    ).clip(lower=0).fillna(0)

    # =========================
    # Defined Benefit (No Return)
    # =========================

    # Cumulative contribution
    final_df["cum_contribution_nr"] = final_df.groupby(group_cols)["fund_contribution"].cumsum()

    # Cumulative exit factor
    final_df["survival_multiplier"] = (
        1 - final_df["exit_ratio"]
    )

    final_df["cum_survival_multiplier"] = final_df.groupby(group_cols)[
        "survival_multiplier"
    ].cumprod()

    # Closing fund without return
    final_df["closing_fund_no_return"] = (
        final_df["cum_contribution_nr"]
        * final_df["cum_survival_multiplier"]
    )

    # Opening fund = previous closing
    final_df["opening_fund_no_return"] = final_df.groupby(group_cols)[
        "closing_fund_no_return"
    ].shift(1).fillna(0)

    # Accumulated before exit payout
    final_df["accumulated_fund_no_return"] = (
        final_df["opening_fund_no_return"]
        + final_df["fund_contribution"]
    )

    final_df["exit_payout_no_return"] = (
        final_df["accumulated_fund_no_return"]
        * final_df["exit_ratio"]
    )

    # =========================
    # Defined Contribution (With Return)
    # =========================

    # Apply rolling compounding using cumulative product
    final_df["return_factor"] = (1 + fund_return_rate)

    # Discounted contribution trick:
    # Convert to present value form then re-accumulate

    final_df["discount_factor"] = final_df.groupby(group_cols).cumcount()
    final_df["discount_multiplier"] = (
        final_df["return_factor"] ** final_df["discount_factor"]
    )

    final_df["discounted_contribution"] = (
        final_df["fund_contribution"]
        * final_df["discount_multiplier"]
    )

    final_df["cum_discounted"] = final_df.groupby(group_cols)[
        "discounted_contribution"
    ].cumsum()

    final_df["closing_fund_with_return"] = (
        final_df["cum_discounted"]
        * final_df["cum_survival_multiplier"]
    )

    final_df["opening_fund_with_return"] = final_df.groupby(group_cols)[
        "closing_fund_with_return"
    ].shift(1).fillna(0)

    final_df["accumulated_fund_with_return"] = (
        final_df["opening_fund_with_return"]
        + final_df["fund_contribution"]
    )

    final_df["fund_return"] = (
        final_df["opening_fund_with_return"]
        * fund_return_rate
    )

    final_df["exit_payout_with_return"] = (
        final_df["accumulated_fund_with_return"]
        * final_df["exit_ratio"]
    )

    return final_df


import pandas as pd
import numpy as np

def generate_old_employee_full_calculation(
    old_survival_df,
    employee_forecast_df,
    salary_forecast_df,
    fund_return_rate=0.04
):

    # ---------------------------------------------------
    # 1️⃣ Standardize Columns
    # ---------------------------------------------------
    survival_df = old_survival_df.copy()
    employee_df = employee_forecast_df.copy()
    salary_df = salary_forecast_df.copy()

    survival_df.columns = survival_df.columns.str.strip().str.lower()
    employee_df.columns = employee_df.columns.str.strip().str.lower()
    salary_df.columns = salary_df.columns.str.strip().str.lower()

    employee_df = employee_df.rename(columns={"age_brackets": "age_bucket"})
    salary_df = salary_df.rename(columns={"age_brackets": "age_bucket"})

    survival_df = survival_df.rename(columns={
        "total exit (q)": "exit_rate",
        "total hiring %": "total_hiring_pct"
    })

    def normalize(df):
        df["industry"] = df["industry"].str.strip().str.lower()
        df["age_bucket"] = df["age_bucket"].str.strip().str.lower()
        return df

    survival_df = normalize(survival_df)
    employee_df = normalize(employee_df)
    salary_df = normalize(salary_df)

    survival_df["tenure"] = survival_df["tenure"].replace(0, 0.5)

    # ---------------------------------------------------
    # 2️⃣ Convert Forecasts to Long
    # ---------------------------------------------------
    emp_cols = [c for c in employee_df.columns if c.startswith("emp_")]
    emp_long = employee_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=emp_cols,
        var_name="year",
        value_name="forecast_employee"
    )
    emp_long["year"] = emp_long["year"].str.extract(r"(\d+)").astype(int)

    sal_cols = [c for c in salary_df.columns if c.startswith("salary_")]
    salary_long = salary_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=sal_cols,
        var_name="year",
        value_name="salary"
    )
    salary_long["year"] = salary_long["year"].str.extract(r"(\d+)").astype(int)


    # ===============================
    # FIX DTYPE BEFORE MERGE
    # ===============================

    # Ensure consistent types
    survival_df["year"] = survival_df["year"].astype(int)
    survival_df["tenure"] = survival_df["tenure"].astype(float)

    emp_long["year"] = emp_long["year"].astype(int)
    emp_long["tenure"] = emp_long["tenure"].astype(float)

    salary_long["year"] = salary_long["year"].astype(int)
    salary_long["tenure"] = salary_long["tenure"].astype(float)



    # ---------------------------------------------------
    # 3️⃣ Merge Base Employees
    # ---------------------------------------------------
    survival_df = survival_df.merge(
        emp_long,
        how="left",
        on=["industry", "age_bucket", "year", "tenure"]
    )

    survival_df = survival_df.sort_values(
        ["industry", "age_bucket", "old_tenure_2025", "year"]
    )

    survival_df["survived_employee"] = np.nan

    # ---------------------------------------------------
    # 4️⃣ Workforce Flow (Correct Vectorized EXIT ONLY)
    # ---------------------------------------------------

    survival_df = survival_df.sort_values(
        ["industry", "age_bucket", "old_tenure_2025", "year"]
    )

    group_cols = ["industry", "age_bucket", "old_tenure_2025"]

    # Base employees
    survival_df["base_employee"] = survival_df.groupby(group_cols)[
        "forecast_employee"
    ].transform("first")

    # Survival factor
    survival_df["survival_factor"] = 1 - survival_df["exit_rate"]

    # Shift so first year has no exit
    survival_df["shifted_factor"] = survival_df.groupby(group_cols)[
        "survival_factor"
    ].shift(1).fillna(1)

    # Cumulative survival
    survival_df["cum_survival"] = survival_df.groupby(group_cols)[
        "shifted_factor"
    ].cumprod()

    # Survived employees
    survival_df["survived_employee"] = (
        survival_df["base_employee"] *
        survival_df["cum_survival"]
    )

    # Exit employees
    survival_df["exit_employee"] = (
        survival_df.groupby(group_cols)["survived_employee"].shift(1)
        - survival_df["survived_employee"]
    ).clip(lower=0).fillna(0)

    # =====================================
    # Drop near-zero survival rows
    # =====================================
    survival_df = survival_df[
        survival_df["survived_employee"] > 0.5
    ]

    # ---------------------------------------------------
    # 5️⃣ Merge Salary
    # ---------------------------------------------------
    survival_df = survival_df.merge(
        salary_long,
        how="left",
        on=["industry", "age_bucket", "tenure", "year"]
    )

    final_df = survival_df.copy()

    # ---------------------------------------------------
    # 6️⃣ Gratuity Calculation
    # ---------------------------------------------------
    def gratuity_rate(tenure):
        if tenure < 1:
            return 0.0
        elif tenure <= 5:
            return tenure * 0.05833
        elif tenure < 25:
            return (5 * 0.05833) + ((tenure - 5) * 0.08333)
        else:
            return (5 * 0.05833) + ((25 - 5) * 0.08333)

    final_df["gratuity_rate"] = final_df["tenure"].apply(gratuity_rate)
    final_df["gratuity_per_employee"] = (
        final_df["salary"] * final_df["gratuity_rate"]
    )

    # ---------------------------------------------------
    # 7️⃣ Incremental Fund Contribution
    # ---------------------------------------------------
    final_df = final_df.sort_values(
        ["industry", "age_bucket", "old_tenure_2025", "year"]
    )

    final_df["prev_gratuity_per_employee"] = final_df.groupby(
        ["industry", "age_bucket", "old_tenure_2025"]
    )["gratuity_per_employee"].shift(1)

    final_df["fund_contribution"] = np.where(
        final_df["prev_gratuity_per_employee"].isna(),
        final_df["gratuity_per_employee"] * final_df["survived_employee"],
        (final_df["gratuity_per_employee"]
         - final_df["prev_gratuity_per_employee"])
        * final_df["survived_employee"]
    )

    final_df["fund_contribution"] = final_df["fund_contribution"].clip(lower=0)

    # =====================================================
    # 8️⃣ FUND ROLL FORWARD (DB + DC)
    # =====================================================
    final_df["opening_fund_no_return"] = 0.0
    final_df["opening_fund_with_return"] = 0.0
    final_df["fund_return"] = 0.0
    final_df["accumulated_fund_no_return"] = 0.0
    final_df["accumulated_fund_with_return"] = 0.0
    final_df["exit_employee"] = 0.0
    final_df["exit_payout_no_return"] = 0.0
    final_df["exit_payout_with_return"] = 0.0
    final_df["closing_fund_no_return"] = 0.0
    final_df["closing_fund_with_return"] = 0.0

    for (ind, age, old_ten), group in final_df.groupby(
        ["industry", "age_bucket", "old_tenure_2025"]
    ):

        group = group.sort_values("year")
        fund_nr = 0.0
        fund_wr = 0.0
        prev_emp = None

        for idx, row in group.iterrows():

            current_emp = row["survived_employee"]

            opening_nr = fund_nr
            opening_wr = fund_wr

            # Apply return
            fund_return = fund_wr * fund_return_rate
            fund_wr += fund_return

            # Add contribution
            fund_nr += row["fund_contribution"]
            fund_wr += row["fund_contribution"]

            accumulated_nr = fund_nr
            accumulated_wr = fund_wr

            if prev_emp is None or prev_emp == 0:
                exit_emp = 0.0
                exit_ratio = 0.0
            else:
                exit_emp = max(prev_emp - current_emp, 0)
                exit_ratio = exit_emp / prev_emp

            exit_payout_nr = accumulated_nr * exit_ratio
            exit_payout_wr = accumulated_wr * exit_ratio

            fund_nr -= exit_payout_nr
            fund_wr -= exit_payout_wr

            fund_nr = max(fund_nr, 0)
            fund_wr = max(fund_wr, 0)

            final_df.loc[idx, "opening_fund_no_return"] = opening_nr
            final_df.loc[idx, "opening_fund_with_return"] = opening_wr
            final_df.loc[idx, "fund_return"] = fund_return
            final_df.loc[idx, "accumulated_fund_no_return"] = accumulated_nr
            final_df.loc[idx, "accumulated_fund_with_return"] = accumulated_wr
            final_df.loc[idx, "exit_employee"] = exit_emp
            final_df.loc[idx, "exit_payout_no_return"] = exit_payout_nr
            final_df.loc[idx, "exit_payout_with_return"] = exit_payout_wr
            final_df.loc[idx, "closing_fund_no_return"] = fund_nr
            final_df.loc[idx, "closing_fund_with_return"] = fund_wr

            prev_emp = current_emp

    return final_df


def combine_new_old_results(new_df, old_df):
    """
    Combines new and old employee outputs.

    Parameters
    ----------
    new_df : DataFrame
        Output of new_employee_full_calculation

    old_df : DataFrame
        Output of old_employee_full_calculation

    Returns
    -------
    combined_df : DataFrame
    summary_df : DataFrame
    """

    new_df = new_df.copy()
    old_df = old_df.copy()

    new_df["employee_type"] = "New"
    old_df["employee_type"] = "Old"

    # Align column names
    if "cohort_start" in new_df.columns:
        new_df = new_df.rename(columns={"cohort_start": "entry_marker"})

    if "old_tenure_2025" in old_df.columns:
        old_df = old_df.rename(columns={"old_tenure_2025": "entry_marker"})

    common_cols = list(set(new_df.columns).intersection(set(old_df.columns)))

    combined_df = pd.concat(
        [new_df[common_cols], old_df[common_cols]],
        ignore_index=True
    )

    summary_df = combined_df.groupby(
        ["industry", "year"],
        as_index=False
    ).agg({
        "survived_employee": "sum",
        "salary": "mean",
        "gratuity_per_employee": "mean",
        "fund_contribution": "sum",
        "closing_fund_with_return": "sum"
    }).rename(columns={
        "survived_employee": "total_employees",
        "salary": "avg_salary",
        "gratuity_per_employee": "avg_gratuity_per_employee",
        "fund_contribution": "total_fund_contribution",
        "closing_fund_with_return": "total_fund_balance"
    })

    return combined_df, summary_df

def aggregate_industry_year(df):
    """
    Aggregates Industry × Year metrics.
    """

    def industry_year_aggregation(group):

        total_emp = group["survived_employee"].sum()

        weighted_salary = (
            (group["salary"] * group["survived_employee"]).sum()
            / total_emp if total_emp > 0 else 0
        )

        annual_total_salary = (
            group["salary"] * group["survived_employee"] * 12
        ).sum()

        weighted_gratuity = (
            (group["gratuity_per_employee"] * group["survived_employee"]).sum()
            / total_emp if total_emp > 0 else 0
        )

        annual_total_gratuity = (
            group["gratuity_per_employee"] * group["survived_employee"] * 12
        ).sum()

        return pd.Series({
            "total_employees": total_emp,
            "weighted_monthly_salary": weighted_salary,
            "annual_total_salary": annual_total_salary,
            "weighted_monthly_gratuity_per_employee": weighted_gratuity,
            "annual_total_gratuity_accrual": annual_total_gratuity,
            "annual_fund_contribution": group["fund_contribution"].sum(),
            "closing_fund_no_return": group["closing_fund_no_return"].sum(),
            "closing_fund_with_return": group["closing_fund_with_return"].sum()
        })

    return (
        df.groupby(["industry", "year"])
          .apply(industry_year_aggregation)
          .reset_index()
    )

def aggregate_industry_year_tenure(df):
    """
    Aggregates Industry × Year × Tenure metrics.
    """

    def aggregate_group(group):

        total_emp = group["survived_employee"].sum()

        weighted_salary = (
            (group["salary"] * group["survived_employee"]).sum()
            / total_emp if total_emp > 0 else 0
        )

        annual_total_salary = (
            group["salary"] * group["survived_employee"] * 12
        ).sum()

        weighted_gratuity = (
            (group["gratuity_per_employee"] * group["survived_employee"]).sum()
            / total_emp if total_emp > 0 else 0
        )

        annual_total_gratuity = (
            group["gratuity_per_employee"] * group["survived_employee"] * 12
        ).sum()

        return pd.Series({
            "total_employees": total_emp,
            "weighted_monthly_salary": weighted_salary,
            "annual_total_salary": annual_total_salary,
            "weighted_monthly_gratuity_per_employee": weighted_gratuity,
            "annual_total_gratuity_accrual": annual_total_gratuity,
            "annual_fund_contribution": group["fund_contribution"].sum(),
            "closing_fund_no_return": group["closing_fund_no_return"].sum(),
            "closing_fund_with_return": group["closing_fund_with_return"].sum()
        })

    return (
        df.groupby(["industry", "year", "tenure"])
          .apply(aggregate_group)
          .reset_index()
    )

def apply_economic_impact(
    industry_year_df,
    economic_df,
    leakage_rate=0.28
):
    """
    Applies economic multipliers and impact logic.
    """

    df = industry_year_df.copy()
    economic_df = economic_df.copy()

    economic_df["Industry"] = economic_df["Industry"].str.lower().str.strip()
    df["industry"] = df["industry"].str.lower().str.strip()

    df = df.merge(
        economic_df,
        left_on="industry",
        right_on="Industry",
        how="left"
    )

    # Year totals
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

    # Economic impact
    df["Net_New_Saving"] = df["Contrib_Allocated"]
    df["Leakage_Assumption"] = leakage_rate
    df["Domestic_Investable"] = (
        df["Net_New_Saving"] * (1 - leakage_rate)
    )

    df["Output_Impact"] = (
        df["Output_Multiplier_Type_I"]
        * df["Domestic_Investable"]
    )

    df["GVA_Impact"] = (
        df["GVA_to_Output_Ratio"]
        * df["Domestic_Investable"]
    )

    df["Jobs_Impact"] = (
        df["Employment_Multiplier (jobs per AED 1M output)"]
        * (df["Domestic_Investable"] / 1_000_000)
    )

    return df
