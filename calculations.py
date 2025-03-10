import pandas as pd
import numpy as np
from constants import (
    CURRENT_YEAR,
    CURRENT_401K_LIMIT,
    CURRENT_HSA_LIMIT,
    CURRENT_IRA_LIMIT,
    INFLATION_RATE,
    TAX_BRACKETS_FEDERAL,
    TAX_BRACKETS_NY
)

def calculate_years_to_retirement(current_age, retirement_age):
    """Calculate years until retirement"""
    return retirement_age - current_age

def calculate_total_current_savings(
    current_savings, current_roth_ira, current_trad_ira, 
    current_hsa, current_roth_401k, current_trad_401k
):
    """Calculate total current retirement savings"""
    return (
        current_savings + current_roth_ira + current_trad_ira + 
        current_hsa + current_roth_401k + current_trad_401k
    )

def calculate_retirement_projections(
    current_age,
    retirement_age,
    current_savings,
    current_roth_ira,
    current_trad_ira,
    current_hsa,
    current_roth_401k,
    current_trad_401k,
    annual_salary,
    annual_bonus,
    annual_rsu,
    annual_merit_increase,
    investment_return,
    savings_apy,
    roth_401k_percent,
    trad_401k_percent,
    employer_401k_match,
    employer_hsa_contribution,
    annual_ira_contribution
):
    """
    Calculate retirement savings projections considering multiple income sources,
    investment vehicles, and economic factors
    """
    years_to_retirement = retirement_age - current_age
    
    # Initialize projections dataframe
    projections = pd.DataFrame(index=range(years_to_retirement + 1))
    
    # Initialize starting values
    projections.loc[0, 'Age'] = current_age
    projections.loc[0, 'Year'] = CURRENT_YEAR
    projections.loc[0, 'Salary'] = annual_salary
    projections.loc[0, 'Bonus'] = annual_bonus
    projections.loc[0, 'RSU'] = annual_rsu
    projections.loc[0, 'High-Yield Savings'] = current_savings
    projections.loc[0, 'Roth IRA'] = current_roth_ira
    projections.loc[0, 'Traditional IRA'] = current_trad_ira
    projections.loc[0, 'HSA'] = current_hsa
    projections.loc[0, 'Roth 401k'] = current_roth_401k
    projections.loc[0, 'Traditional 401k'] = current_trad_401k
    projections.loc[0, 'Total Balance'] = calculate_total_current_savings(
        current_savings, current_roth_ira, current_trad_ira, 
        current_hsa, current_roth_401k, current_trad_401k
    )
    
    # Set up contribution limits with annual increases
    contribution_limits = {
        '401k': CURRENT_401K_LIMIT,
        'HSA': CURRENT_HSA_LIMIT,
        'IRA': CURRENT_IRA_LIMIT
    }
    
    # Number of paychecks per year
    paychecks_per_year = 26
    
    # Project for each year until retirement
    for year in range(1, years_to_retirement + 1):
        # Update age and year
        projections.loc[year, 'Age'] = current_age + year
        projections.loc[year, 'Year'] = CURRENT_YEAR + year
        
        # Adjust contribution limits for inflation (approximately 2% per year)
        for account_type in contribution_limits:
            contribution_limits[account_type] *= (1 + INFLATION_RATE)
        
        # Calculate new salary with merit increase
        projections.loc[year, 'Salary'] = projections.loc[year-1, 'Salary'] * (1 + annual_merit_increase)
        
        # Adjust bonus and RSU with merit increase too
        projections.loc[year, 'Bonus'] = projections.loc[year-1, 'Bonus'] * (1 + annual_merit_increase)
        projections.loc[year, 'RSU'] = projections.loc[year-1, 'RSU'] * (1 + annual_merit_increase)
        
        # Current year salary
        salary = projections.loc[year, 'Salary']
        
        # Calculate 401k contributions
        paycheck_amount = salary / paychecks_per_year
        roth_401k_contribution_per_paycheck = paycheck_amount * roth_401k_percent
        trad_401k_contribution_per_paycheck = paycheck_amount * trad_401k_percent
        
        # Calculate total annual 401k employee contributions
        annual_401k_contribution = (roth_401k_contribution_per_paycheck + trad_401k_contribution_per_paycheck) * paychecks_per_year
        
        # Adjust if exceeding annual limit
        if annual_401k_contribution > contribution_limits['401k']:
            adjustment_factor = contribution_limits['401k'] / annual_401k_contribution
            roth_401k_contribution_per_paycheck *= adjustment_factor
            trad_401k_contribution_per_paycheck *= adjustment_factor
            annual_401k_contribution = contribution_limits['401k']
        
        # Calculate annual Roth and Traditional 401k contributions
        annual_roth_401k_contribution = roth_401k_contribution_per_paycheck * paychecks_per_year
        annual_trad_401k_contribution = trad_401k_contribution_per_paycheck * paychecks_per_year
        
        # Calculate employer match
        match_eligible_contribution = min(
            paycheck_amount * employer_401k_match * paychecks_per_year,
            (roth_401k_contribution_per_paycheck + trad_401k_contribution_per_paycheck) * paychecks_per_year
        )
        employer_contribution = min(match_eligible_contribution, contribution_limits['401k'] - annual_401k_contribution)
        
        # Add employer contribution to Traditional 401k
        annual_trad_401k_contribution += employer_contribution
        
        # Calculate HSA contribution (assuming employee maxes out minus employer contribution)
        employee_hsa_contribution = max(0, contribution_limits['HSA'] - employer_hsa_contribution)
        total_hsa_contribution = employee_hsa_contribution + employer_hsa_contribution
        
        # Update account balances with new contributions and returns
        # High-Yield Savings (assuming interest compounds annually)
        projections.loc[year, 'High-Yield Savings'] = projections.loc[year-1, 'High-Yield Savings'] * (1 + savings_apy)
        
        # Retirement accounts with market returns
        projections.loc[year, 'Roth IRA'] = (
            projections.loc[year-1, 'Roth IRA'] * (1 + investment_return) + 
            min(annual_ira_contribution, contribution_limits['IRA'])
        )
        
        projections.loc[year, 'Traditional IRA'] = (
            projections.loc[year-1, 'Traditional IRA'] * (1 + investment_return)
        )
        
        projections.loc[year, 'HSA'] = (
            projections.loc[year-1, 'HSA'] * (1 + investment_return) + 
            total_hsa_contribution
        )
        
        projections.loc[year, 'Roth 401k'] = (
            projections.loc[year-1, 'Roth 401k'] * (1 + investment_return) + 
            annual_roth_401k_contribution
        )
        
        projections.loc[year, 'Traditional 401k'] = (
            projections.loc[year-1, 'Traditional 401k'] * (1 + investment_return) + 
            annual_trad_401k_contribution
        )
        
        # Calculate total balance
        projections.loc[year, 'Total Balance'] = (
            projections.loc[year, 'High-Yield Savings'] +
            projections.loc[year, 'Roth IRA'] +
            projections.loc[year, 'Traditional IRA'] +
            projections.loc[year, 'HSA'] +
            projections.loc[year, 'Roth 401k'] +
            projections.loc[year, 'Traditional 401k']
        )
        
        # Add annual contributions for reference
        projections.loc[year, '401k Contribution'] = annual_401k_contribution
        projections.loc[year, 'Employer 401k Match'] = employer_contribution
        projections.loc[year, 'HSA Contribution'] = total_hsa_contribution
        projections.loc[year, 'IRA Contribution'] = min(annual_ira_contribution, contribution_limits['IRA'])
    
    # Format currency columns
    for col in [
        'Salary', 'Bonus', 'RSU', 'High-Yield Savings', 'Roth IRA', 
        'Traditional IRA', 'HSA', 'Roth 401k', 'Traditional 401k', 
        'Total Balance', '401k Contribution', 'Employer 401k Match',
        'HSA Contribution', 'IRA Contribution'
    ]:
        if col in projections.columns:
            projections[col] = projections[col].round(2)
    
    return projections

def estimate_tax_impact(income, filing_status="single"):
    """
    Estimate federal and NY state taxes based on income
    This is a simplified calculation
    """
    # Federal tax calculation
    federal_tax = calculate_federal_tax(income, filing_status)
    
    # NY state tax calculation
    ny_tax = calculate_ny_tax(income, filing_status)
    
    return federal_tax + ny_tax

def calculate_federal_tax(income, filing_status):
    """Calculate federal income tax based on income and filing status"""
    brackets = TAX_BRACKETS_FEDERAL[filing_status]
    return calculate_tax_from_brackets(income, brackets)

def calculate_ny_tax(income, filing_status):
    """Calculate NY state income tax based on income and filing status"""
    brackets = TAX_BRACKETS_NY[filing_status]
    return calculate_tax_from_brackets(income, brackets)

def calculate_tax_from_brackets(income, brackets):
    """Calculate tax given income and tax brackets"""
    tax = 0
    prev_threshold = 0
    
    for threshold, rate in brackets:
        if income > prev_threshold:
            taxable_amount = min(income, threshold) - prev_threshold
            tax += taxable_amount * rate
        
        if income <= threshold:
            break
            
        prev_threshold = threshold
    
    return tax
