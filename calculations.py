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
    annual_ira_contribution,
    monthly_expenses=0.0,
    filing_status="single"
):
    """
    Calculate retirement savings projections considering multiple income sources,
    investment vehicles, economic factors, taxes, and expenses
    """
    years_to_retirement = retirement_age - current_age
    
    # Initialize projections dataframe
    projections = pd.DataFrame(index=range(years_to_retirement + 40))  # +40 years for post-retirement projections
    
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
    projections.loc[0, 'Monthly Expenses'] = monthly_expenses
    projections.loc[0, 'Annual Expenses'] = monthly_expenses * 12
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
    
    # Cap on annual merit increases (salary growth slows over time)
    max_merit_years = 15
    reduced_merit_rate = annual_merit_increase * 0.5  # After max years, merit rate is halved
    
    # Adjust return rates based on portfolio age (more conservative as retirement approaches)
    def get_adjusted_return(year, base_return):
        years_left = max(0, retirement_age - (current_age + year))
        if years_left > 20:
            return base_return
        elif years_left > 10:
            return base_return * 0.9  # 10% reduction for moderate risk
        elif years_left > 5:
            return base_return * 0.8  # 20% reduction for lower risk
        else:
            return base_return * 0.7  # 30% reduction for conservative approach
    
    # Project for each year
    for year in range(1, len(projections)):
        # Update age and year
        projections.loc[year, 'Age'] = current_age + year
        projections.loc[year, 'Year'] = CURRENT_YEAR + year
        
        # Get adjusted investment return based on years to retirement
        adjusted_return = get_adjusted_return(year, investment_return)
        
        # Update expenses with inflation
        projections.loc[year, 'Monthly Expenses'] = projections.loc[year-1, 'Monthly Expenses'] * (1 + INFLATION_RATE)
        projections.loc[year, 'Annual Expenses'] = projections.loc[year, 'Monthly Expenses'] * 12
        
        # Determine if in retirement phase
        is_retirement = projections.loc[year, 'Age'] >= retirement_age
        
        # If in retirement, set income to 0
        if is_retirement:
            projections.loc[year, 'Salary'] = 0
            projections.loc[year, 'Bonus'] = 0
            projections.loc[year, 'RSU'] = 0
        else:
            # Adjust contribution limits for inflation
            for account_type in contribution_limits:
                contribution_limits[account_type] *= (1 + INFLATION_RATE)
            
            # Calculate new salary with merit increase (capped over time to be more realistic)
            current_merit_rate = annual_merit_increase
            if year > max_merit_years:
                current_merit_rate = reduced_merit_rate
            
            projections.loc[year, 'Salary'] = projections.loc[year-1, 'Salary'] * (1 + current_merit_rate)
            
            # Adjust bonus and RSU with merit increase too
            projections.loc[year, 'Bonus'] = projections.loc[year-1, 'Bonus'] * (1 + current_merit_rate)
            projections.loc[year, 'RSU'] = projections.loc[year-1, 'RSU'] * (1 + current_merit_rate)
        
        # Current year values
        salary = projections.loc[year, 'Salary']
        annual_expenses = projections.loc[year, 'Annual Expenses']
        total_income = salary + projections.loc[year, 'Bonus'] + projections.loc[year, 'RSU']
        
        # PRE-RETIREMENT CALCULATIONS
        if not is_retirement:
            # Tax calculations for pre-tax contributions
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
            
            # Calculate pre-tax income for tax purposes
            pre_tax_income = total_income - annual_trad_401k_contribution
            
            # Calculate taxes
            tax_amount = estimate_tax_impact(pre_tax_income, filing_status)
            projections.loc[year, 'Taxes Paid'] = tax_amount
            
            # Calculate after-tax income
            after_tax_income = pre_tax_income - tax_amount
            projections.loc[year, 'After-Tax Income'] = after_tax_income
            
            # Calculate disposable income (after tax and expenses)
            disposable_income = after_tax_income - annual_expenses - annual_roth_401k_contribution
            projections.loc[year, 'Disposable Income'] = disposable_income
            
            # Calculate employer match
            match_eligible_contribution = min(
                paycheck_amount * employer_401k_match * paychecks_per_year,
                (roth_401k_contribution_per_paycheck + trad_401k_contribution_per_paycheck) * paychecks_per_year
            )
            employer_contribution = match_eligible_contribution
            
            # Add employer contribution to Traditional 401k
            annual_trad_401k_contribution += employer_contribution
            
            # Calculate HSA contribution
            employee_hsa_contribution = max(0, min(contribution_limits['HSA'] - employer_hsa_contribution, 
                                              contribution_limits['HSA'] * 0.8))  # Realistic employee contribution
            total_hsa_contribution = employee_hsa_contribution + employer_hsa_contribution
            
            # Limit IRA contribution based on IRS income limits (simplified)
            effective_ira_contribution = annual_ira_contribution
            if pre_tax_income > 150000:  # Simplified phaseout threshold
                reduction_factor = min(1.0, (pre_tax_income - 150000) / 30000)
                effective_ira_contribution = annual_ira_contribution * (1 - reduction_factor)
            
            # Update account balances with new contributions and returns
            # High-Yield Savings (assuming extra disposable income goes here)
            extra_savings = max(0, disposable_income)  # Any extra money after expenses goes to savings
            
            # Cap the extra savings to make it more realistic (people don't save everything)
            realistic_savings_rate = min(0.7, extra_savings / after_tax_income)  # Cap at 70% of after-tax income
            realistic_extra_savings = extra_savings * realistic_savings_rate
            
            projections.loc[year, 'High-Yield Savings'] = (
                projections.loc[year-1, 'High-Yield Savings'] * (1 + savings_apy) + 
                realistic_extra_savings
            )
            
            # Retirement accounts with market returns
            projections.loc[year, 'Roth IRA'] = (
                projections.loc[year-1, 'Roth IRA'] * (1 + adjusted_return) + 
                min(effective_ira_contribution, contribution_limits['IRA'])
            )
            
            projections.loc[year, 'Traditional IRA'] = (
                projections.loc[year-1, 'Traditional IRA'] * (1 + adjusted_return)
            )
            
            projections.loc[year, 'HSA'] = (
                projections.loc[year-1, 'HSA'] * (1 + adjusted_return) + 
                total_hsa_contribution
            )
            
            projections.loc[year, 'Roth 401k'] = (
                projections.loc[year-1, 'Roth 401k'] * (1 + adjusted_return) + 
                annual_roth_401k_contribution
            )
            
            projections.loc[year, 'Traditional 401k'] = (
                projections.loc[year-1, 'Traditional 401k'] * (1 + adjusted_return) + 
                annual_trad_401k_contribution
            )
            
            # Add annual contributions for reference
            projections.loc[year, '401k Contribution'] = annual_401k_contribution
            projections.loc[year, 'Employer 401k Match'] = employer_contribution
            projections.loc[year, 'HSA Contribution'] = total_hsa_contribution
            projections.loc[year, 'IRA Contribution'] = min(effective_ira_contribution, contribution_limits['IRA'])
            
        # RETIREMENT PHASE CALCULATIONS
        else:
            # Set contributions to 0 in retirement
            projections.loc[year, '401k Contribution'] = 0
            projections.loc[year, 'Employer 401k Match'] = 0
            projections.loc[year, 'HSA Contribution'] = 0
            projections.loc[year, 'IRA Contribution'] = 0
            
            # Use a more conservative return rate in retirement
            retirement_return = adjusted_return * 0.8  # More conservative in retirement
            
            # Calculate required withdrawals for expenses
            withdrawal_needed = annual_expenses
            
            # Apply growth to accounts first (with more conservative returns)
            high_yield_savings_growth = projections.loc[year-1, 'High-Yield Savings'] * savings_apy
            roth_ira_growth = projections.loc[year-1, 'Roth IRA'] * retirement_return
            trad_ira_growth = projections.loc[year-1, 'Traditional IRA'] * retirement_return
            hsa_growth = projections.loc[year-1, 'HSA'] * retirement_return
            roth_401k_growth = projections.loc[year-1, 'Roth 401k'] * retirement_return
            trad_401k_growth = projections.loc[year-1, 'Traditional 401k'] * retirement_return
            
            # Apply growth to accounts
            projections.loc[year, 'High-Yield Savings'] = projections.loc[year-1, 'High-Yield Savings'] + high_yield_savings_growth
            projections.loc[year, 'Roth IRA'] = projections.loc[year-1, 'Roth IRA'] + roth_ira_growth
            projections.loc[year, 'Traditional IRA'] = projections.loc[year-1, 'Traditional IRA'] + trad_ira_growth
            projections.loc[year, 'HSA'] = projections.loc[year-1, 'HSA'] + hsa_growth
            projections.loc[year, 'Roth 401k'] = projections.loc[year-1, 'Roth 401k'] + roth_401k_growth
            projections.loc[year, 'Traditional 401k'] = projections.loc[year-1, 'Traditional 401k'] + trad_401k_growth
            
            # Withdrawal strategy in order:
            # 1. Taxable accounts (High-Yield Savings)
            # 2. Traditional accounts (taxed on withdrawal)
            # 3. Roth accounts (tax-free)
            # 4. HSA (for qualified medical expenses)
            
            # First withdraw from High-Yield Savings
            high_yield_withdrawal = min(withdrawal_needed, projections.loc[year, 'High-Yield Savings'])
            projections.loc[year, 'High-Yield Savings'] -= high_yield_withdrawal
            withdrawal_needed -= high_yield_withdrawal
            
            # If more needed, withdraw from Traditional accounts
            if withdrawal_needed > 0:
                # Calculate tax on traditional withdrawals
                trad_withdrawal_pretax = min(
                    withdrawal_needed * 1.25,  # Inflate the needed amount to account for taxes
                    projections.loc[year, 'Traditional 401k'] + projections.loc[year, 'Traditional IRA']
                )
                tax_on_withdrawal = estimate_tax_impact(trad_withdrawal_pretax, filing_status)
                trad_withdrawal_actual = trad_withdrawal_pretax - tax_on_withdrawal
                
                # Track taxes
                projections.loc[year, 'Taxes Paid'] = tax_on_withdrawal
                
                # Apportion the withdrawal between Traditional 401k and IRA
                total_trad = projections.loc[year, 'Traditional 401k'] + projections.loc[year, 'Traditional IRA']
                if total_trad > 0:
                    trad_401k_ratio = projections.loc[year, 'Traditional 401k'] / total_trad
                    trad_ira_ratio = projections.loc[year, 'Traditional IRA'] / total_trad
                    
                    trad_401k_withdrawal = trad_withdrawal_pretax * trad_401k_ratio
                    trad_ira_withdrawal = trad_withdrawal_pretax * trad_ira_ratio
                    
                    projections.loc[year, 'Traditional 401k'] -= trad_401k_withdrawal
                    projections.loc[year, 'Traditional IRA'] -= trad_ira_withdrawal
                    
                    withdrawal_needed -= trad_withdrawal_actual
            else:
                projections.loc[year, 'Taxes Paid'] = 0
            
            # If more needed, withdraw from Roth accounts
            if withdrawal_needed > 0:
                # Apportion between Roth 401k and IRA
                total_roth = projections.loc[year, 'Roth 401k'] + projections.loc[year, 'Roth IRA']
                if total_roth > 0:
                    roth_401k_ratio = projections.loc[year, 'Roth 401k'] / total_roth
                    roth_ira_ratio = projections.loc[year, 'Roth IRA'] / total_roth
                    
                    roth_401k_withdrawal = min(withdrawal_needed * roth_401k_ratio, projections.loc[year, 'Roth 401k'])
                    roth_ira_withdrawal = min(withdrawal_needed * roth_ira_ratio, projections.loc[year, 'Roth IRA'])
                    
                    projections.loc[year, 'Roth 401k'] -= roth_401k_withdrawal
                    projections.loc[year, 'Roth IRA'] -= roth_ira_withdrawal
                    
                    withdrawal_needed -= (roth_401k_withdrawal + roth_ira_withdrawal)
            
            # If more needed, withdraw from HSA (assuming qualified medical expenses)
            if withdrawal_needed > 0:
                hsa_withdrawal = min(withdrawal_needed, projections.loc[year, 'HSA'])
                projections.loc[year, 'HSA'] -= hsa_withdrawal
                withdrawal_needed -= hsa_withdrawal
            
            # If still needed more than available, mark as shortfall
            if withdrawal_needed > 0:
                projections.loc[year, 'Retirement Shortfall'] = withdrawal_needed
            else:
                projections.loc[year, 'Retirement Shortfall'] = 0
        
        # Calculate total balance
        projections.loc[year, 'Total Balance'] = (
            projections.loc[year, 'High-Yield Savings'] +
            projections.loc[year, 'Roth IRA'] +
            projections.loc[year, 'Traditional IRA'] +
            projections.loc[year, 'HSA'] +
            projections.loc[year, 'Roth 401k'] +
            projections.loc[year, 'Traditional 401k']
        )
    
    # Format currency columns
    for col in [
        'Salary', 'Bonus', 'RSU', 'High-Yield Savings', 'Roth IRA', 
        'Traditional IRA', 'HSA', 'Roth 401k', 'Traditional 401k', 
        'Total Balance', '401k Contribution', 'Employer 401k Match',
        'HSA Contribution', 'IRA Contribution', 'Monthly Expenses',
        'Annual Expenses', 'Taxes Paid', 'After-Tax Income', 
        'Disposable Income', 'Retirement Shortfall'
    ]:
        if col in projections.columns:
            projections[col] = projections[col].round(2)
    
    # Truncate to focus on relevant years (pre-retirement + 30 years after)
    projections = projections.iloc[:years_to_retirement + 30]
    
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
