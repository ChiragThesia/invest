import streamlit as st

# Default Constants
default_safe_raise = 25_000_000
default_capital_raised = 53_000_000
default_pre_money_valuation = 250_000_000
default_upfront_fee_percent = 2.0
default_preferred_return_rate = 8.0
default_carry_percent = 20.0
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

safe_raise = st.sidebar.number_input(
    "SAFE Raise ($):", min_value=0, value=default_safe_raise, step=1_000_000, format="%d"
)
capital_raised = st.sidebar.number_input(
    "Total Capital Raised to Date ($):", min_value=0, value=default_capital_raised, step=1_000_000, format="%d"
)
pre_money_valuation = st.sidebar.number_input(
    "Pre-Money Valuation ($):", min_value=0, value=default_pre_money_valuation, step=10_000_000, format="%d"
)

valuation_multiplier = st.number_input(
    "Enter multiple of pre-money valuation:", min_value=1.0, value=1.0, step=0.1
)

capital_gains_tax = st.sidebar.slider(
    "Capital Gains Tax (%):", min_value=0.0, max_value=50.0, value=default_capital_gains_tax
) / 100
medicare_surtax = st.sidebar.slider(
    "Medicare Surtax (%):", min_value=0.0, max_value=10.0, value=default_medicare_surtax
) / 100

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

st.title("Rain AI Investment Return Calculator")

investment = st.number_input(
    "Enter your investment amount ($):", min_value=1000, step=1000, format="%d", key="investment"
)

valuation = pre_money_valuation * valuation_multiplier

if investment:
    after_tax_return = calculate_after_tax_return(
        investment, valuation, 5, pre_money_valuation, capital_raised
    )

    st.subheader(f"Projected After-Tax Return at {valuation_multiplier}x Pre-Money Valuation:")
    st.markdown(f"<h2 style='color: #1f77b4;'>Your return: ${after_tax_return:,.2f}</h2>", unsafe_allow_html=True)
else:
    st.warning("Please enter an investment amount to see projected returns.")
