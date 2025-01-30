import streamlit as st
import pandas as pd

# Default Constants
default_safe_raise = 25_000_000
default_capital_raised = 53_000_000
default_pre_money_valuation = 250_000_000
default_capital_gains_tax = 20.0
default_medicare_surtax = 3.8

# Valuation tiers
VALUATION_TIERS = {
    "Very Low (1B)": (1_000_000_000, 1),
    "Low (8-10B)": (9_000_000_000, 3),
    "Mid (36B)": (36_000_000_000, 5),
    "High (80-90B)": (85_000_000_000, 6),
    "Very High (150B)": (150_000_000_000, 7),
}

# Sidebar to adjust assumptions
st.sidebar.header("Adjustable Assumptions")
safe_raise = st.sidebar.number_input("SAFE Raise ($):", min_value=0, value=default_safe_raise, step=1_000_000, format="%d")
capital_raised = st.sidebar.number_input("Total Capital Raised to Date ($):", min_value=0, value=default_capital_raised, step=1_000_000, format="%d")
pre_money_valuation = st.sidebar.number_input("Pre-Money Valuation ($):", min_value=0, value=default_pre_money_valuation, step=10_000_000, format="%d")

# New input field for manual valuation adjustment
custom_valuation_str = st.sidebar.text_input("Enter a custom valuation (e.g., 1B, 500M, 1000000000):", "1B")
time_horizon = st.sidebar.number_input("Enter the time horizon (years):", min_value=1, step=1, format="%d")

# Function to convert user input into numerical valuation
def parse_valuation(input_str):
    multipliers = {"B": 1_000_000_000, "M": 1_000_000}
    input_str = input_str.replace(",", "").strip().upper()
    for key, value in multipliers.items():
        if input_str.endswith(key):
            return int(float(input_str[:-1]) * value)
    return int(input_str)

custom_valuation = parse_valuation(custom_valuation_str)

# Tax rates
capital_gains_tax = st.sidebar.slider("Capital Gains Tax (%):", min_value=0.0, max_value=50.0, value=default_capital_gains_tax) / 100
medicare_surtax = st.sidebar.slider("Medicare Surtax (%):", min_value=0.0, max_value=10.0, value=default_medicare_surtax) / 100

# Fixed percentages
upfront_fee_percent = 0.02  # 2%
preferred_return_rate = 0.08  # 8%
carry_percent = 0.20  # 20%

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

# Streamlit app
st.title("Multi-Level Investment Return Calculator")
st.subheader("Enter multiple investment amounts to compare returns")

investment_input = st.text_area("Enter investment amounts separated by commas (e.g., 10000, 50000, 100000)")
investments = [int(i.strip()) for i in investment_input.split(',') if i.strip().isdigit()]

if investments:
    results = []
    for investment in investments:
        valuation = custom_valuation if custom_valuation else pre_money_valuation
        after_tax_return = calculate_after_tax_return(
            investment, valuation, time_horizon, pre_money_valuation, capital_raised
        )
        results.append({
            "Investment ($)": f"${investment:,}",
            "Custom Valuation ($)": f"${valuation:,}",
            "Projected After-Tax Return ($)": f"${after_tax_return:,.2f}"
        })

    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    # Chart
    st.subheader("Comparison of Returns Across Investment Amounts")
    chart_data = df_results.pivot(index="Custom Valuation ($)", columns="Investment ($)", values="Projected After-Tax Return ($)")
    st.bar_chart(chart_data)
else:
    st.warning("Please enter at least one investment amount.")
