import streamlit as st
from constants import COLORS

def apply_custom_styles():
    """Apply custom styles to the Streamlit application"""
    
    # Define CSS styles
    st.markdown("""
        <style>
        /* Main styles */
        .stApp {
            background-color: #F5F7FA;
            color: #333333;
            font-family: 'Roboto', 'Inter', sans-serif;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #006D75;
            font-weight: 600;
        }
        
        /* Metric styles */
        .stMetric label {
            color: #2E5E82;
            font-weight: 500;
        }
        
        .stMetric .metric-value {
            color: #333333;
            font-weight: 700;
        }
        
        /* Sidebar styles */
        .sidebar .sidebar-content {
            background-color: #F5F7FA;
        }
        
        /* Expander styles */
        .streamlit-expanderHeader {
            background-color: #F5F7FA;
            color: #2E5E82;
            font-weight: 600;
        }
        
        /* Button styles */
        .stButton button {
            background-color: #006D75;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stButton button:hover {
            background-color: #2E5E82;
        }
        
        /* Info box styling */
        .stAlert {
            background-color: rgba(0, 109, 117, 0.1);
            border-color: #006D75;
        }
        
        /* Success styles */
        .element-container div[data-testid="stAlert"][aria-label="Success"] {
            background-color: rgba(76, 175, 80, 0.1);
            border-color: #4CAF50;
        }
        
        /* Warning styles */
        .element-container div[data-testid="stAlert"][aria-label="Warning"] {
            background-color: rgba(255, 183, 77, 0.1);
            border-color: #FFB74D;
        }
        
        /* Input field styles */
        .stTextInput input, .stNumberInput input, .stSelectbox, .stMultiselect {
            border-radius: 4px;
            border: 1px solid #E0E0E0;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #006D75;
            box-shadow: 0 0 0 2px rgba(0, 109, 117, 0.2);
        }
        
        /* Table styles */
        .stTable td, .stDataFrame td {
            color: #333333;
        }
        
        .stTable th, .stDataFrame th {
            background-color: #2E5E82;
            color: white;
            font-weight: 600;
        }
        
        /* Slider styles */
        .stSlider div[data-baseweb="slider"] div {
            background-color: #006D75 !important;
        }
        
        /* Progress bar */
        .stProgress div {
            background-color: #006D75;
        }
        
        /* Footer styles */
        footer {
            visibility: hidden;
        }
        
        /* Customize the sidebar width */
        [data-testid="stSidebar"] {
            min-width: 350px;
            max-width: 450px;
        }
        </style>
    """, unsafe_allow_html=True)
