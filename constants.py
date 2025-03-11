from datetime import datetime

# Current year
CURRENT_YEAR = datetime.now().year

# Current contribution limits (2025 values)
CURRENT_401K_LIMIT = 23500  # 2025 limit
CURRENT_HSA_LIMIT = 3300  # 2025 limit
CURRENT_IRA_LIMIT = 7000  # 2025 limit

# Economic constants
INFLATION_RATE = 0.02  # 2% annual inflation

# Tax brackets for 2023 (simplified)
# Format: (threshold, rate)
TAX_BRACKETS_FEDERAL = {
    "single": [
        (0, 0.10),
        (11000, 0.12),
        (44725, 0.22),
        (95375, 0.24),
        (182100, 0.32),
        (231250, 0.35),
        (578125, 0.37)
    ],
    "married": [
        (0, 0.10),
        (22000, 0.12),
        (89450, 0.22),
        (190750, 0.24),
        (364200, 0.32),
        (462500, 0.35),
        (693750, 0.37)
    ]
}

# NY State tax brackets (simplified)
TAX_BRACKETS_NY = {
    "single": [
        (0, 0.04),
        (13900, 0.045),
        (21400, 0.0525),
        (80650, 0.0585),
        (215400, 0.0625),
        (1077550, 0.0685),
        (5000000, 0.103),
        (25000000, 0.109)
    ],
    "married": [
        (0, 0.04),
        (27900, 0.045),
        (42800, 0.0525),
        (161550, 0.0585),
        (323200, 0.0625),
        (2155350, 0.0685),
        (5000000, 0.103),
        (25000000, 0.109)
    ]
}

# Colors
COLORS = {
    "primary": "#006D75",  # teal
    "secondary": "#2E5E82",  # navy
    "accent": "#FFB74D",  # gold
    "background": "#F5F7FA",  # light grey
    "text": "#333333",  # dark grey
    "success": "#4CAF50"  # green
}
