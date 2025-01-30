import streamlit as st
import pandas as pd

# -------------------
# Helper Functions
# -------------------
def parse_dollar_string(dollar_str: str) -> float:
    """Parse a string like '$25,000,000' or '25,000,000' into a float."""
    # Strip out common symbols/spaces, convert to float
    clean_str = dollar_str.replace("$", "").replace(",", "").strip()
    return float(clean_str)

def format_dollar_value(amount: float) -> str:
    """Format a numeric amount into a string, e.g. 250000000 -> '$250,000,000'."""
    return f"${amount:,.0f}"

# -------------------
# Default Constants
# -------------------
default_safe_raise = 25_000_000
default_capital_raised = 53_000_000
default_pre_money_valuation = 250_000_000
default_capital_gains_tax = 20.0
default_medicare_surtax = 3.8

VALUATION_TIERS = {
    "Very Low (1B)": (1_000_000_000, 1),
    "Low (8-10B)": (9_000_000_000, 3),
    "Mid (36B)": (36_000_000_000, 5),
    "High (80-90B)": (85_000_000_000, 6),
    "Very High (150B)": (150_000_000_000, 7),
}

# Fixed rates
upfront_fee_percent = 0.02       # 2%
preferred_return_rate = 0.08     # 8%
carry_percent = 0.20            # 20%

# -------------------
# Calculation Functions
# -------------------
def calculate_ownership(investment, post_money_valuation):
    return investment / post_money_valuation

def calculate_final_value(ownership, valuation_2028):
    return ownership * valuation_2028

def calculate_preferred_return(investment, time_horizon, pref_rate):
    return investment * ((1 + pref_rate) ** time_horizon)

def calculate_gp_carry(final_value, preferred_return, carry_rate):
    profit = final_value - preferred_return
    return max(0, profit * carry_rate)

def calculate_taxes(investor_value, initial_investment, cap_gains_rate, medicare_rate):
    taxable_gain = investor_value - initial_investment
    return max(0, taxable_gain * (cap_gains_rate + medicare_rate))

def calculate_after_tax_return(investment, valuation, time_horizon, pre_money_valuation, capital_raised):
    post_money_valuation = pre_money_valuation + capital_raised
    ownership = calculate_ownership(investment, post_money_valuation)
    final_value = calculate_final_value(ownership, valuation)
    pref_return = calculate_preferred_return(investment, time_horizon, preferred_return_rate)
    gp_carry = calculate_gp_carry(final_value, pref_return, carry_percent)
    investor_value = final_value - pref_return - gp_carry
    total_taxes = calculate_taxes(investor_value, investment, capital_gains_tax, medicare_surtax)
    return investor_value - total_taxes


# -------------------
# Streamlit App
# -------------------
st.title("Rain AI Investment Return Calculator")

st.sidebar.header("Adjustable Assumptions")

# --- Collect monetary inputs as formatted text, then parse ---
safe_raise_str = st.sidebar.text_input("SAFE Raise ($):", format_dollar_value(default_safe_raise))
safe_raise = parse_dollar_string(safe_raise_str)

capital_raised_str = st.sidebar.text_input("Total Capital Raised to Date ($):", format_dollar_value(default_capital_raised))
capital_raised = parse_dollar_string(capital_raised_str)

pre_money_str = st.sidebar.text_input("Pre-Money Valuation ($):", format_dollar_value(default_pre_money_valuation))
pre_money_valuation = parse_dollar_string(pre_money_str)

# Display some fixed info in the sidebar
st.sidebar.text("Upfront Fee: 2.0%")
st.sidebar.text("Preferred Return/Year: 8.0%")
st.sidebar.text("Carry Rate: 20.0%")

# Let the user adjust capital gains tax & medicare surtax
capital_gains_tax = st.sidebar.slider("Capital Gains Tax (%):", 0.0, 50.0, default_capital_gains_tax) / 100
medicare_surtax = st.sidebar.slider("Medicare Surtax (%):", 0.0, 10.0, default_medicare_surtax) / 100

# --- Add a drop-down for standard valuations plus an optional custom valuation ---
default_tier_index = list(VALUATION_TIERS.keys()).index("Mid (36B)")
selected_tier = st.selectbox("Select the valuation tier:", list(VALUATION_TIERS.keys()), index=default_tier_index)

# Provide a custom valuation input
custom_valuation_str = st.text_input("Or enter a custom valuation ($):", "")
custom_valuation = 0.0
if custom_valuation_str.strip():
    custom_valuation = parse_dollar_string(custom_valuation_str)

# Determine which valuation to use
tier_valuation, tier_time_horizon = VALUATION_TIERS[selected_tier]
if custom_valuation > 0:
    # If user provided a custom valuation, use that; otherwise use the tier
    valuation_in_use = custom_valuation
    time_horizon_in_use = tier_time_horizon  # or prompt for a custom horizon as well if desired
else:
    valuation_in_use = tier_valuation
    time_horizon_in_use = tier_time_horizon

# --- Now get the user's investment amount, also as a formatted text input ---
investment_str = st.text_input("Enter your investment amount ($):", "")
investment = 0
if investment_str.strip():
    investment = parse_dollar_string(investment_str)

# --- Only show results if investment is non-zero ---
if investment > 0:
    after_tax_return = calculate_after_tax_return(
        investment,
        valuation_in_use,
        time_horizon_in_use,
        pre_money_valuation,
        capital_raised
    )
    # Show result
    st.subheader(f"Projected After-Tax Return ({selected_tier if custom_valuation<=0 else 'Custom Valuation'}):")
    st.markdown(
        f"<h2 style='color: #1f77b4;'>Your return: {format_dollar_value(after_tax_return)}</h2>",
        unsafe_allow_html=True
    )

    # Also do a comparison across all tiers to see what they'd be
    st.subheader("Comparison Across Valuation Tiers")
    results = {}
    for tier, (val, horizon) in VALUATION_TIERS.items():
        ret = calculate_after_tax_return(
            investment, val, horizon,
            pre_money_valuation, capital_raised
        )
        # Format the result
        results[tier] = ret

    # Convert to a DataFrame for a bar chart
    df = pd.DataFrame.from_dict(results, orient='index', columns=['After-Tax Return'])
    df['After-Tax Return'] = df['After-Tax Return'].apply(format_dollar_value)
    st.dataframe(df)

    # If you prefer a numeric bar_chart, we can store numeric (unformatted) in parallel:
    numeric_results = {k: v for k, v in results.items()}
    st.bar_chart(pd.DataFrame.from_dict(numeric_results, orient='index', columns=['After-Tax Return']))

else:
    st.warning("Please enter an investment amount to see projected returns.")
