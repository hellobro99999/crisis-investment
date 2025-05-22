import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# ------------------------------
# Helper Functions
# ------------------------------
def fetch_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=False)
    if data.empty:
        return pd.DataFrame()

    if len(tickers) == 1:
        adj_close = data[['Adj Close']].rename(columns={'Adj Close': tickers[0]})
    else:
        adj_close = data['Adj Close']
    
    return adj_close

def simulate_portfolio(data, allocations, initial_investment):
    normalized = data / data.iloc[0]
    weighted = normalized * allocations
    portfolio = weighted.sum(axis=1) * initial_investment
    return portfolio

def calculate_metrics(portfolio):
    returns = portfolio.pct_change().dropna()
    total_return = (portfolio.iloc[-1] / portfolio.iloc[0]) - 1
    volatility = returns.std() * (252 ** 0.5)
    sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5)
    max_drawdown = ((portfolio / portfolio.cummax()) - 1).min()
    return total_return, volatility, sharpe_ratio, max_drawdown

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(layout="wide")
st.title("📉 Crisis Investing Backtesting Simulator")

# Preset Crisis Periods
events = {
    "COVID-19 Crash (2020)": ("2020-02-01", "2020-12-31"),
    "Global Financial Crisis (2008)": ("2007-10-01", "2009-06-01"),
    "2020 US Elections": ("2020-09-01", "2021-03-01"),
    "Custom Dates": (None, None)
}

selected_event = st.sidebar.selectbox("Select Historical Event", list(events.keys()))

if selected_event == "Custom Dates":
    start_date = st.sidebar.date_input("Start Date", datetime.date(2020, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.date(2020, 12, 31))
else:
    start_date = datetime.datetime.strptime(events[selected_event][0], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(events[selected_event][1], "%Y-%m-%d")

st.sidebar.markdown("---")

# Suggested Stock Options
def_tickers = ["SPY", "QQQ", "GLD", "AAPL", "MSFT", "TSLA"]
all_stock_options = st.sidebar.multiselect("Select stocks/ETFs to invest in", options=def_tickers, default=["AAPL", "MSFT"])

if not all_stock_options:
    st.error("Please select at least one stock/ETF.")
    st.stop()

ticker_list = all_stock_options

# Dynamic allocations
def_alloc = [round(100/len(ticker_list), 2) for _ in ticker_list]
default_alloc = ", ".join(map(str, def_alloc))
alloc_input = st.sidebar.text_input("Allocations (%) (comma separated, sum to 100)", default_alloc)

try:
    allocations = [float(x)/100 for x in alloc_input.split(",")]
except ValueError:
    st.error("Allocations must be numeric values separated by commas.")
    st.stop()

if len(allocations) != len(ticker_list):
    st.error("Number of allocations must match number of tickers.")
    st.stop()

if not abs(sum(allocations) - 1) < 1e-3:
    st.error("Allocations must sum up to 100%.")
    st.stop()

initial_investment = st.sidebar.number_input("Initial Investment ($)", value=10000, step=100)

# ------------------------------
# Run Simulation
# ------------------------------
st.subheader(f"Simulating: {selected_event}")
data = fetch_data(ticker_list, start_date, end_date)
if data.empty:
    st.error("Failed to fetch data. Please check tickers or date range.")
    st.stop()

portfolio = simulate_portfolio(data, allocations, initial_investment)
total_return, volatility, sharpe, drawdown = calculate_metrics(portfolio)

# ------------------------------
# Display Results
# ------------------------------
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Return", f"{total_return*100:.2f}%")
    st.metric("Volatility (Annual)", f"{volatility*100:.2f}%")
with col2:
    st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    st.metric("Max Drawdown", f"{drawdown*100:.2f}%")

st.line_chart(portfolio, use_container_width=True)

# ------------------------------
# Real-Time Investment Tracker
# ------------------------------
st.subheader("💼 Live Investment Value")
live_value = st.slider("Adjust hypothetical live value ($)", min_value=0, max_value=int(portfolio.max()*1.2), value=int(portfolio.iloc[-1]), step=100)
change_from_original = ((live_value - initial_investment) / initial_investment) * 100
st.metric("Change from Initial Investment", f"{change_from_original:.2f}%")

# ------------------------------
# New Interactive Features
# ------------------------------
st.subheader("📈 Interactive Strategy Tools")

if st.button("💰 Buy More (Add $1,000)"):
    initial_investment += 1000
    portfolio = simulate_portfolio(data, allocations, initial_investment)
    st.success("You added $1,000 more to your portfolio.")

if st.button("🚪 Sell All"):
    st.warning("You sold your entire portfolio.")
    st.metric("Final Value", f"${portfolio.iloc[-1]:,.2f}")

# Show benchmarks (optional)
if st.checkbox("Compare with S&P 500 (SPY)"):
    benchmark = fetch_data(["SPY"], start_date, end_date)
    benchmark_portfolio = simulate_portfolio(benchmark, [1], initial_investment)
    comparison = pd.DataFrame({"Your Portfolio": portfolio, "S&P 500": benchmark_portfolio})
    st.line_chart(comparison, use_container_width=True)

# ------------------------------
# Behavioral Insights
# ------------------------------
st.subheader("Behavioral Insights")
st.markdown("""
- **Did you sell during the dip or hold through the crisis?**
- **Would you have outperformed a buy-and-hold strategy?**
- **What emotions might you have experienced during major drops?**

Use this simulation to reflect on your investment behavior during stressful periods.
""")

# ------------------------------
# Historical Context
# ------------------------------
st.subheader("Historical Context")
if selected_event == "COVID-19 Crash (2020)":
    st.markdown("""
    - **Feb 2020**: Market starts falling rapidly  
    - **Mar 2020**: Lockdowns & panic selling  
    - **Apr 2020**: Massive Fed intervention  
    - **Late 2020**: Recovery and vaccine optimism
    """)
elif selected_event == "Global Financial Crisis (2008)":
    st.markdown("""
    - **Sep 2008**: Lehman Brothers collapses  
    - **Oct 2008**: Markets tank, volatility spikes  
    - **2009**: Stimulus begins, markets recover slowly
    """)
elif selected_event == "2020 US Elections":
    st.markdown("""
    - **Pre-election**: High uncertainty  
    - **Post-election**: Market rallies on result clarity  
    - **Early 2021**: Stimulus and vaccine rollout boost markets    
    """)
else:
    st.markdown("Use your custom dates to explore market behavior during any period of interest.")
