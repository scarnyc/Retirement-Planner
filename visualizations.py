import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def create_retirement_projection_chart(projection_data):
    """
    Create an interactive line chart showing retirement savings projections over time
    """
    fig = go.Figure()
    
    # Add traces for each account type
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['High-Yield Savings'],
        name='High-Yield Savings',
        stackgroup='one',
        line=dict(width=0.5, color='#FFB74D')
    ))
    
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Roth IRA'],
        name='Roth IRA',
        stackgroup='one',
        line=dict(width=0.5, color='#4CAF50')
    ))
    
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Traditional IRA'],
        name='Traditional IRA',
        stackgroup='one',
        line=dict(width=0.5, color='#2E5E82')
    ))
    
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['HSA'],
        name='HSA',
        stackgroup='one',
        line=dict(width=0.5, color='#006D75')
    ))
    
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Roth 401k'],
        name='Roth 401k',
        stackgroup='one',
        line=dict(width=0.5, color='#7986CB')
    ))
    
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Traditional 401k'],
        name='Traditional 401k',
        stackgroup='one',
        line=dict(width=0.5, color='#9C27B0')
    ))
    
    # Add retirement expenses if available
    if 'Annual Expenses' in projection_data.columns:
        # Find retirement age
        retirement_age = projection_data['Age'].max()
        retirement_year_idx = projection_data[projection_data['Age'] == retirement_age].index[0]
        
        # Create expenses projection (show from retirement onward)
        retirement_years = projection_data.loc[retirement_year_idx:, 'Year']
        retirement_expenses = projection_data.loc[retirement_year_idx:, 'Annual Expenses']
        
        fig.add_trace(go.Scatter(
            x=retirement_years,
            y=retirement_expenses,
            name='Annual Retirement Expenses',
            line=dict(dash='dash', width=2, color='#FF5252'),
            mode='lines'
        ))
    
    # Add a line for total balance
    fig.add_trace(go.Scatter(
        x=projection_data['Year'],
        y=projection_data['Total Balance'],
        name='Total Balance',
        line=dict(width=3, color='#333333'),
        mode='lines'
    ))
    
    # Add retirement line
    if 'Age' in projection_data.columns:
        retirement_ages = projection_data['Age'].unique()
        if len(retirement_ages) > 1:
            retirement_age = retirement_ages[len(retirement_ages) // 2]  # Middle value as approx
            retirement_year_idx = projection_data[projection_data['Age'] == retirement_age].index[0]
            retirement_year = projection_data.loc[retirement_year_idx, 'Year']
            
            fig.add_vline(
                x=retirement_year,
                line_width=2,
                line_dash="dash",
                line_color="#2E5E82",
                annotation_text="Retirement"
            )
    
    # Customize layout
    fig.update_layout(
        title='Retirement Savings Projection',
        xaxis_title='Year',
        yaxis_title='Balance ($)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#F5F7FA',
        yaxis=dict(
            gridcolor='#E0E0E0',
            tickformat='$,.0f'
        ),
        hovermode='x unified',
        height=600
    )
    
    # Add milestone indicators
    milestones = [
        {'year': projection_data['Year'].iloc[5], 'label': '5 Years'},
        {'year': projection_data['Year'].iloc[10], 'label': '10 Years'},
        {'year': projection_data['Year'].iloc[20], 'label': '20 Years'}
    ]
    
    for milestone in milestones:
        if milestone['year'] <= projection_data['Year'].max():
            milestone_value = projection_data.loc[projection_data['Year'] == milestone['year'], 'Total Balance'].values[0]
            
            fig.add_trace(go.Scatter(
                x=[milestone['year']],
                y=[milestone_value],
                mode='markers+text',
                marker=dict(symbol='circle', size=12, color='#006D75'),
                text=[milestone['label']],
                textposition='top center',
                name=milestone['label'],
                showlegend=False
            ))
    
    # Add retirement marker
    retirement_year = projection_data['Year'].max()
    retirement_value = projection_data['Total Balance'].iloc[-1]
    
    fig.add_trace(go.Scatter(
        x=[retirement_year],
        y=[retirement_value],
        mode='markers+text',
        marker=dict(symbol='star', size=16, color='#FFB74D'),
        text=['Retirement'],
        textposition='top center',
        name='Retirement',
        showlegend=False
    ))
    
    return fig

def create_allocation_pie_chart(allocation_data):
    """
    Create a pie chart showing the breakdown of current retirement savings
    """
    labels = list(allocation_data.keys())
    values = list(allocation_data.values())
    
    # Define colors for each category
    colors = {
        'High-Yield Savings': '#FFB74D',
        'Roth IRA': '#4CAF50',
        'Traditional IRA': '#2E5E82',
        'HSA': '#006D75',
        'Roth 401k': '#7986CB',
        'Traditional 401k': '#9C27B0'
    }
    
    color_list = [colors[label] for label in labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=color_list,
        textinfo='percent+label',
        hoverinfo='label+value+percent',
        hovertemplate='%{label}: $%{value:,.2f} (%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        title='Current Retirement Savings Allocation',
        showlegend=False,
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#F5F7FA',
        height=500
    )
    
    # Add center text
    total = sum(values)
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"${total:,.0f}",
        font=dict(size=16, color='#333333'),
        showarrow=False
    )
    
    return fig

def create_savings_milestone_chart(milestones, current_total):
    """
    Create a gauge chart showing progress toward retirement savings milestones
    """
    # Calculate percentage complete to target
    target = milestones['Target']
    percentage = min(100, (current_total / target) * 100)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_total,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Progress to Retirement Target", 'font': {'size': 24}},
        delta={'reference': 0, 'increasing': {'color': "#4CAF50"}},
        gauge={
            'axis': {'range': [0, target], 'tickwidth': 1, 'tickcolor': "#333333", 
                     'tickformat': '$,.0f'},
            'bar': {'color': "#006D75"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#333333",
            'steps': [
                {'range': [0, milestones['25%']], 'color': '#F5F7FA'},
                {'range': [milestones['25%'], milestones['50%']], 'color': '#E0E0E0'},
                {'range': [milestones['50%'], milestones['75%']], 'color': '#BDBDBD'},
                {'range': [milestones['75%'], target], 'color': '#9E9E9E'}
            ],
            'threshold': {
                'line': {'color': "#FFB74D", 'width': 4},
                'thickness': 0.75,
                'value': current_total
            }
        },
        number={'valueformat': '$,.0f', 'font': {'size': 20}}
    ))
    
    fig.update_layout(
        plot_bgcolor='#F5F7FA',
        paper_bgcolor='#F5F7FA',
        height=500
    )
    
    # Add a subtitle with percentage toward goal
    fig.add_annotation(
        x=0.5, y=0.25,
        text=f"{percentage:.1f}% of Target",
        font=dict(size=16, color='#333333'),
        showarrow=False
    )
    
    return fig
