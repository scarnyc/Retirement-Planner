import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from calculations import (
    calculate_retirement_projections,
    calculate_years_to_retirement,
    calculate_total_current_savings
)
from visualizations import (
    create_retirement_projection_chart,
    create_allocation_pie_chart,
    create_savings_milestone_chart
)
from constants import (
    CURRENT_YEAR,
    CURRENT_401K_LIMIT,
    CURRENT_IRA_LIMIT,
    CURRENT_HSA_LIMIT,
    INFLATION_RATE
)
from styles import apply_custom_styles

# Set page config
st.set_page_config(
    page_title="Retirement Savings Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
apply_custom_styles()

# Page header
st.title("Retirement Savings Calculator")
st.markdown("""
This calculator helps you project your retirement savings based on your current financial status,
considering multiple income sources, investment returns, and economic factors.
""")

# Create sidebar for inputs
st.sidebar.header("Your Financial Information")

# Personal information
with st.sidebar.expander("Personal Information", expanded=True):
    current_age = st.number_input("Current Age", min_value=18, max_value=80, value=35)
    retirement_age = st.number_input("Retirement Age", min_value=current_age+1, max_value=100, value=65)
    years_to_retirement = calculate_years_to_retirement(current_age, retirement_age)
    st.info(f"Years until retirement: {years_to_retirement}")

# Current balances
with st.sidebar.expander("Current Balances", expanded=True):
    current_savings = st.number_input("Current High-Yield Savings", min_value=0.0, value=243543.0, format="%.2f")
    current_roth_ira = st.number_input("Current Roth IRA", min_value=0.0, value=63181.0, format="%.2f")
    current_trad_ira = st.number_input("Current Traditional IRA", min_value=0.0, value=93974.0, format="%.2f")
    current_hsa = st.number_input("Current HSA", min_value=0.0, value=9869.0, format="%.2f")
    current_roth_401k = st.number_input("Current Roth 401k", min_value=0.0, value=81988.0, format="%.2f")
    current_trad_401k = st.number_input("Current Traditional 401k", min_value=0.0, value=40140.0, format="%.2f")
    monthly_expenses = st.number_input("Current Monthly Expenses", min_value=0.0, value=6100.0, format="%.2f")

# Income and growth assumptions
with st.sidebar.expander("Income & Growth", expanded=True):
    annual_salary = st.number_input("Annual Salary", min_value=0.0, value=182753.0, format="%.2f")
    annual_bonus = st.number_input("Annual Bonus", min_value=0.0, value=36551.0, format="%.2f")
    annual_rsu = st.number_input("Annual RSU Grant", min_value=0.0, value=10000.0, format="%.2f")
    annual_merit_increase = st.number_input("Annual Merit Increase (%)", min_value=0.0, max_value=25.0, value=3.25, format="%.2f")
    investment_return = st.number_input("Annual Investment Return (%)", min_value=0.0, max_value=30.0, value=6.0, format="%.2f")
    savings_apy = st.number_input("Current APY on Savings (%)", min_value=0.0, max_value=20.0, value=3.8, format="%.2f")

# Contribution settings
with st.sidebar.expander("Contributions", expanded=True):
    st.markdown(f"**401k Annual Limit: ${CURRENT_401K_LIMIT:,.0f}**")
    roth_401k_percent = st.number_input("401k Roth Contribution (% per paycheck)", min_value=0.0, max_value=100.0, value=6.0, format="%.2f")
    trad_401k_percent = st.number_input("401k Traditional Contribution (% per paycheck)", min_value=0.0, max_value=100.0, value=8.0, format="%.2f")
    employer_401k_match = st.number_input("Employer 401k Match (%)", min_value=0.0, max_value=100.0, value=6.0, format="%.2f")
    
    st.markdown(f"**HSA Annual Limit: ${CURRENT_HSA_LIMIT:,.0f}**")
    employer_hsa_contribution = st.number_input("Employer HSA Contribution", min_value=0.0, value=1000.0, format="%.2f")
    
    st.markdown(f"**IRA Annual Limit: ${CURRENT_IRA_LIMIT:,.0f}**")
    annual_ira_contribution = st.number_input("Annual IRA Contribution", min_value=0.0, max_value=float(CURRENT_IRA_LIMIT), value=0.0, format="%.2f")

# Main dashboard content
total_current_savings = calculate_total_current_savings(
    current_savings, current_roth_ira, current_trad_ira, 
    current_hsa, current_roth_401k, current_trad_401k
)

# Current financial snapshot
st.header("Current Financial Snapshot")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Current Savings", f"${total_current_savings:,.2f}")
with col2:
    annual_expenses = monthly_expenses * 12
    st.metric("Annual Expenses", f"${annual_expenses:,.2f}")
with col3:
    annual_total_income = annual_salary + annual_bonus + annual_rsu
    st.metric("Annual Income", f"${annual_total_income:,.2f}")

# Retirement projections
st.header("Retirement Projections")

# Calculate projections
projection_data = calculate_retirement_projections(
    current_age=current_age,
    retirement_age=retirement_age,
    current_savings=current_savings,
    current_roth_ira=current_roth_ira,
    current_trad_ira=current_trad_ira,
    current_hsa=current_hsa,
    current_roth_401k=current_roth_401k,
    current_trad_401k=current_trad_401k,
    annual_salary=annual_salary,
    annual_bonus=annual_bonus,
    annual_rsu=annual_rsu,
    annual_merit_increase=annual_merit_increase/100,
    investment_return=investment_return/100,
    savings_apy=savings_apy/100,
    roth_401k_percent=roth_401k_percent/100,
    trad_401k_percent=trad_401k_percent/100,
    employer_401k_match=employer_401k_match/100,
    employer_hsa_contribution=employer_hsa_contribution,
    annual_ira_contribution=annual_ira_contribution
)

# Display projection chart
st.plotly_chart(create_retirement_projection_chart(projection_data), use_container_width=True)

# Allocation and milestones
col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Retirement Allocation")
    current_allocation = {
        "High-Yield Savings": current_savings,
        "Roth IRA": current_roth_ira,
        "Traditional IRA": current_trad_ira,
        "HSA": current_hsa,
        "Roth 401k": current_roth_401k,
        "Traditional 401k": current_trad_401k
    }
    st.plotly_chart(create_allocation_pie_chart(current_allocation), use_container_width=True)

with col2:
    st.subheader("Savings Milestones")
    retirement_target = annual_expenses * 25  # 4% safe withdrawal rate assumption
    milestones = {
        "Current": total_current_savings,
        "25%": retirement_target * 0.25,
        "50%": retirement_target * 0.5,
        "75%": retirement_target * 0.75,
        "Target": retirement_target
    }
    st.plotly_chart(create_savings_milestone_chart(milestones, total_current_savings), use_container_width=True)

# Detailed projections table
st.header("Detailed Projection Table")
st.dataframe(projection_data)

# Insights and recommendations
st.header("Insights & Recommendations")

# Calculate some basic insights
current_year = datetime.now().year
retirement_year = current_year + years_to_retirement
final_balance = projection_data.iloc[-1]['Total Balance']
monthly_retirement_income = final_balance * 0.04 / 12  # 4% withdrawal rate

insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.subheader("Retirement Summary")
    st.markdown(f"* **Retirement Year:** {retirement_year}")
    st.markdown(f"* **Projected Final Balance:** ${final_balance:,.2f}")
    st.markdown(f"* **Estimated Monthly Income:** ${monthly_retirement_income:,.2f}")
    
    # Compare to current expenses
    income_ratio = monthly_retirement_income / monthly_expenses
    if income_ratio >= 1:
        st.success(f"Projected monthly income covers {income_ratio:.1f}x your current expenses")
    else:
        st.warning(f"Projected monthly income covers only {income_ratio:.1f}x your current expenses")

with insights_col2:
    st.subheader("Optimization Opportunities")
    
    # Contribution gap analysis
    total_401k_percent = roth_401k_percent + trad_401k_percent
    if total_401k_percent < employer_401k_match:
        st.warning(f"You're not maximizing your employer match. Consider increasing your 401k contribution by at least {(employer_401k_match - total_401k_percent):.1f}%")
    
    # IRA recommendation
    if annual_ira_contribution < CURRENT_IRA_LIMIT:
        st.info(f"You can contribute up to ${CURRENT_IRA_LIMIT - annual_ira_contribution:,.0f} more to your IRA this year")
    
    # Savings rate analysis
    annual_savings = (annual_salary * (roth_401k_percent + trad_401k_percent) / 100) + annual_ira_contribution
    savings_rate = annual_savings / annual_salary * 100
    if savings_rate < 15:
        st.warning(f"Your current savings rate is {savings_rate:.1f}%. Financial experts often recommend saving at least 15% of income for retirement.")
    else:
        st.success(f"Your current savings rate is {savings_rate:.1f}%, which meets or exceeds expert recommendations.")

# Footer
st.markdown("---")
st.markdown("""
**Note:** This calculator provides estimates based on the information you provide and general assumptions.
Actual results may vary due to market fluctuations, tax law changes, and other factors.
Consider consulting a financial advisor for personalized advice.
""")
