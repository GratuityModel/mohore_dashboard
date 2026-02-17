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

    merged_df['Attrition %'] += 0.005

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
        1. SideBySide Employee Forecast (Incremental from 2026 onward)
        2. SideBySide Weighted Salary Forecast
    """

    # ==========================================================
    # 1. LOAD BASE EMPLOYEE DATA
    # ==========================================================
    df1 = pd.read_excel(employee_salary_path)
    df2 = merged_industry_df.copy()
    print(df1['Tenure'].unique())

    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

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
    # 4. BUILD FULL CUMULATIVE SERIES FIRST
    # ==========================================================

    for year in range(start_year + 1, end_year + 1):

        prev_year = year - 1

        # Only tenure 0 grows cumulatively
        df.loc[df["Tenure"] == 0, f"Emp_{year}"] = (
            df.loc[df["Tenure"] == 0, f"Emp_{prev_year}"]
            * (1 + df.loc[df["Tenure"] == 0, "Total Hiring %"])
        )

        # Other tenures = 0 (survival will populate)
        df.loc[df["Tenure"] != 0, f"Emp_{year}"] = 0

        # Salary growth
        df[f"Salary_{year}"] = (
            df[f"Salary_{prev_year}"] *
            (1 + df["Salary Growth %"])
        )


    # ==========================================================
    # 5. NOW CONVERT TO INCREMENTAL (AFTER FULL BUILD)
    # ==========================================================

    emp_cols = [f"Emp_{y}" for y in range(start_year, end_year + 1)]

    emp_cumulative = df[emp_cols].copy()

    for year in range(start_year + 1, end_year + 1):

        prev_year = year - 1

        df[f"Emp_{year}"] = (
            emp_cumulative[f"Emp_{year}"] -
            emp_cumulative[f"Emp_{prev_year}"]
        )

    # Keep only tenure 0 incremental
    for year in range(start_year + 1, end_year + 1):
        df.loc[df["Tenure"] != 0, f"Emp_{year}"] = 0

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


def generate_combined_employee_survival_template(
    meta_info_path,
    start_year=2025,
    end_year=2040
):
    """
    Generates ONE unified survival template:

    Structure:
        industry × age_bucket × tenure × year

    - Tenure starts at 0
    - Tenure runs up to max tenure found in meta file
    - Covers projection years start_year → end_year
    - No separation of old/new employees
    """

    # --------------------------------
    # 1️⃣ Load Meta Info
    # --------------------------------
    df_raw = pd.read_csv(meta_info_path)

    industries = df_raw["Industry"].dropna().unique()
    age_buckets = df_raw["Age_Bracket"].dropna().unique()

    # Use tenure column if exists, otherwise Old_Tenure
    if "Tenure" in df_raw.columns:
        max_tenure = int(df_raw["Tenure"].dropna().max())
    elif "Old_Tenure" in df_raw.columns:
        max_tenure = int(df_raw["Old_Tenure"].dropna().max())
    else:
        raise ValueError("No Tenure or Old_Tenure column found in meta file.")

    tenures = range(0, max_tenure + 1)
    projection_years = range(start_year, end_year + 1)

    # --------------------------------
    # 2️⃣ Cartesian Product Grid
    # --------------------------------
    index = pd.MultiIndex.from_product(
        [industries, age_buckets, tenures, projection_years],
        names=[
            "industry",
            "age_bucket",
            "tenure",
            "year"
        ]
    )

    survival_template = index.to_frame(index=False)

    survival_template = survival_template.sort_values(
        ["industry", "age_bucket", "year", "tenure"]
    ).reset_index(drop=True)
    print("----------")
    print(survival_template.columns)

    return survival_template


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
        "Total Hiring %",
        "Replacement Hiring %"
    ]]

    exit_df = exit_df.rename(columns={
        "Industry": "industry",
        "Age_Bracket": "age_bucket",
        "Total Exit (q)": "total exit (q)",
        "Total Hiring %": "total hiring %",
        "Replacement Hiring %": "replacement hiring %"
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


def generate_combined_employee_full_calculation(
    survival_template_df,
    employee_forecast_df,
    salary_forecast_df,
    fund_return_rate=0.04
):
    """
    Unified Survival + EOSG + Fund Calculation Engine

    Logic:
    - 2025: actual employees for all tenures
    - Survival forward using exit rate
    - Track exits
    - From 2026 onward:
        * Replacement hiring = exit rate (for <55, 56-64)
        * Prior year exits rehired into tenure 0
        * Add incremental forecast hires
    - EOSG + Fund logic unchanged
    """


    # ==========================================================
    # 1️⃣ Standardize
    # ==========================================================
    df = survival_template_df.copy()
    emp_df = employee_forecast_df.copy()
    sal_df = salary_forecast_df.copy()

    df.columns = df.columns.str.lower().str.strip()
    emp_df.columns = emp_df.columns.str.lower().str.strip()
    sal_df.columns = sal_df.columns.str.lower().str.strip()

    emp_df = emp_df.rename(columns={"age_brackets": "age_bucket"})
    sal_df = sal_df.rename(columns={"age_brackets": "age_bucket"})

    # Normalize strings
    for d in [df, emp_df, sal_df]:
        d["industry"] = d["industry"].str.lower().str.strip()
        d["age_bucket"] = d["age_bucket"].str.lower().str.strip()

    # ==========================================================
    # 2️⃣ Convert Forecasts to Long
    # ==========================================================
    emp_cols = [c for c in emp_df.columns if c.startswith("emp_")]
    emp_long = emp_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=emp_cols,
        var_name="year",
        value_name="forecast_employee"
    )
    emp_long["year"] = emp_long["year"].str.extract(r"(\d+)").astype(int)

    sal_cols = [c for c in sal_df.columns if c.startswith("salary_")]
    sal_long = sal_df.melt(
        id_vars=["industry", "age_bucket", "tenure"],
        value_vars=sal_cols,
        var_name="year",
        value_name="salary"
    )
    sal_long["year"] = sal_long["year"].str.extract(r"(\d+)").astype(int)

    # ==========================================================
    # 3️⃣ Merge Forecast + Salary
    # ==========================================================
    print(emp_long[(emp_long["age_bucket"]=="55-59") &
                (emp_long["tenure"]==0) &
                (emp_long["year"]==2025)]["industry"].unique())

    print(df[(df["age_bucket"]=="55-59") &
            (df["tenure"]==0) &
            (df["year"]==2025)]["industry"].unique())


    for d in [df, emp_long, sal_long]:
        d[["industry", "age_bucket"]] = d[["industry", "age_bucket"]].apply(lambda x: x.str.strip().str.lower())

    
    df = df.merge(
        emp_long,
        how="left",
        on=["industry", "age_bucket", "tenure", "year"]
    )

    df = df.merge(
        sal_long,
        how="left",
        on=["industry", "age_bucket", "tenure", "year"]
    )

    df["forecast_employee"] = df["forecast_employee"].fillna(0)

    # ==========================================================
    # 4️⃣ Attach Exit Rate
    # ==========================================================
    df["exit_rate"] = df["total exit (q)"]

    print(df.columns)
    # Replacement hiring = exit rate for specific age brackets
    df["replacement_rate"] = np.where(
        df["age_bucket"].isin(["<55", "55-59","60-64"]),
        df["exit_rate"],
        df["replacement hiring %"]
    )

    # ==========================================================
    # 5️⃣ SURVIVAL ENGINE
    # ==========================================================

    df = df.sort_values(["industry", "age_bucket", "year", "tenure"])

    df["survived_employee"] = 0.0
    df["exit_employee"] = 0.0

    start_year = df["year"].min()


    for (ind, age), group in df.groupby(["industry", "age_bucket"]):

        group = group.sort_values(["year", "tenure"])
        prev_year_exits = 0.0

        for year in sorted(group["year"].unique()):

            year_mask = (
                (df["industry"] == ind) &
                (df["age_bucket"] == age) &
                (df["year"] == year)
            )

            year_df = df.loc[year_mask].sort_values("tenure")

            if year == start_year:
                # 2025 actual base
                df.loc[year_mask, "survived_employee"] = year_df["forecast_employee"].values
            else:
                # 1️⃣ Rehire prior exits at tenure 0
                tenure0_mask = year_mask & (df["tenure"] == 0)

                incremental_hire = df.loc[tenure0_mask, "forecast_employee"].values

                df.loc[tenure0_mask, "survived_employee"] = (
                    prev_year_exits + incremental_hire
                )

                # 2️⃣ Survival from prior year
                prev_mask = (
                    (df["industry"] == ind) &
                    (df["age_bucket"] == age) &
                    (df["year"] == year - 1)
                )

                prev_year_df = df.loc[prev_mask]

                for t in year_df["tenure"]:
                    if t == 0:
                        continue

                    prev_survivor = prev_year_df.loc[
                        prev_year_df["tenure"] == t - 1,
                        "survived_employee"
                    ]

                    if len(prev_survivor) == 0:
                        continue

                    survived = (
                        prev_survivor.values[0] *
                        (1 - df.loc[
                            (year_mask & (df["tenure"] == t)),
                            "exit_rate"
                        ].values[0])
                    )

                    df.loc[
                        (year_mask & (df["tenure"] == t)),
                        "survived_employee"
                    ] = survived

            # 3️⃣ Calculate exits
            prev_mask = (
                (df["industry"] == ind) &
                (df["age_bucket"] == age) &
                (df["year"] == year - 1)
            )

            if year != start_year:

                prev_df = df.loc[prev_mask]

                total_exit = 0.0

                for t in year_df["tenure"]:
                    if t == 0:
                        continue

                    prev_emp = prev_df.loc[
                        prev_df["tenure"] == t - 1,
                        "survived_employee"
                    ]

                    if len(prev_emp) == 0:
                        continue

                    exit_emp = (
                        prev_emp.values[0] -
                        df.loc[
                            (year_mask & (df["tenure"] == t)),
                            "survived_employee"
                        ].values[0]
                    )

                    exit_emp = max(exit_emp, 0)

                    df.loc[
                        (year_mask & (df["tenure"] == t)),
                        "exit_employee"
                    ] = exit_emp

                    total_exit += exit_emp

                prev_year_exits = total_exit
            else:
                prev_year_exits = 0.0

    final_df = df.copy()

    # ==========================================================
    # 6️⃣ GRATUITY (UNCHANGED)
    # ==========================================================
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

    # ==========================================================
    # 7️⃣ FUND CONTRIBUTION (UNCHANGED)
    # ==========================================================
    final_df = final_df.sort_values(
        ["industry", "age_bucket", "year", "tenure"]
    )

    final_df["prev_gratuity_per_employee"] = final_df.groupby(
        ["industry", "age_bucket", "tenure"]
    )["gratuity_per_employee"].shift(1)

    final_df["fund_contribution"] = np.where(
        final_df["prev_gratuity_per_employee"].isna(),
        final_df["gratuity_per_employee"] * final_df["survived_employee"],
        (final_df["gratuity_per_employee"]
         - final_df["prev_gratuity_per_employee"])
        * final_df["survived_employee"]
    )

    final_df["fund_contribution"] = final_df["fund_contribution"].clip(lower=0)

    # ==========================================================
    # 8️⃣ FUND ROLL FORWARD (IDENTICAL STRUCTURE)
    # ==========================================================

    final_df["opening_fund_no_return"] = 0.0
    final_df["opening_fund_with_return"] = 0.0
    final_df["fund_return"] = 0.0
    final_df["accumulated_fund_no_return"] = 0.0
    final_df["accumulated_fund_with_return"] = 0.0
    final_df["exit_payout_no_return"] = 0.0
    final_df["exit_payout_with_return"] = 0.0
    final_df["closing_fund_no_return"] = 0.0
    final_df["closing_fund_with_return"] = 0.0


    final_df["tenure_start"] = (
        final_df.groupby(["industry", "age_bucket"])["tenure"]
        .transform("min")
    )

    for (ind, age, cohort), group in final_df.groupby(
        ["industry", "age_bucket", "tenure_start"]):

        group = group.sort_values("year")
        fund_nr = 0.0
        fund_wr = 0.0

        for idx, row in group.iterrows():

            opening_nr = fund_nr
            opening_wr = fund_wr

            fund_return = fund_wr * fund_return_rate
            fund_wr += fund_return

            fund_nr += row["fund_contribution"]
            fund_wr += row["fund_contribution"]

            accumulated_nr = fund_nr
            accumulated_wr = fund_wr

            exit_ratio = (
                row["exit_employee"] / row["survived_employee"]
                if row["survived_employee"] > 0 else 0
            )

            exit_payout_nr = accumulated_nr * exit_ratio
            exit_payout_wr = accumulated_wr * exit_ratio

            fund_nr -= exit_payout_nr
            fund_wr -= exit_payout_wr

            final_df.loc[idx, "opening_fund_no_return"] = opening_nr
            final_df.loc[idx, "opening_fund_with_return"] = opening_wr
            final_df.loc[idx, "fund_return"] = fund_return
            final_df.loc[idx, "accumulated_fund_no_return"] = accumulated_nr
            final_df.loc[idx, "accumulated_fund_with_return"] = accumulated_wr
            final_df.loc[idx, "exit_payout_no_return"] = exit_payout_nr
            final_df.loc[idx, "exit_payout_with_return"] = exit_payout_wr
            final_df.loc[idx, "closing_fund_no_return"] = fund_nr
            final_df.loc[idx, "closing_fund_with_return"] = fund_wr

    return final_df


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


