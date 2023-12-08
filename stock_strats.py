import streamlit as st
import yfinance as yf
import pandas as pd

from datetime import date
from typing import Iterator
from itertools import accumulate, pairwise
import operator

st.title("Stock Strategy Comparison")

@st.cache_data
def get_stocks_range(ticker: str, start: date, end: date):
    return yf.download(ticker, start, end)

with st.sidebar:
    initial_invest = st.number_input("Initial investment:", 0., value = 100.)
    ticker = st.text_input("Enter the ticker:", value = "^IXIC")
    type = st.selectbox("When to calculate:", ["Adj Close", "Open", "Close", "High", "Low"])
    start_date = st.date_input("Start Date", date.fromisoformat("2020-01-01"))
    end_date = st.date_input("End Date", "today")

data = get_stocks_range(ticker, start_date, end_date)
data.reset_index(inplace = True)

def running_ratio(iter):
    return [n / p for p, n in pairwise(iter)]

def earnings_state(initial: float, data: Iterator[float]) -> list[float]:
    gain = accumulate(running_ratio(data), operator.mul, initial = initial)
    diff = [n - p for p, n in pairwise(gain)]
    return diff

def earnings_path(initial: float, data: Iterator[float]) -> list[float]:
    diff = [initial * ratio - initial for ratio in running_ratio(data)]
    return diff

state_values = earnings_state(initial_invest, iter(data[type]))
path_values = earnings_path(initial_invest, iter(data[type]))

stock_chart_data = pd.DataFrame({
    "Date": data["Date"],
    "State": accumulate(state_values, initial = initial_invest),
    "Path": accumulate(path_values, initial = initial_invest)
})

diff_df = pd.DataFrame({
    "Date": data["Date"],
    "Change in Stock Value": data[type].diff()
})

chart_tab_strats, chart_tab_raw, chart_tab_change = st.tabs(["Strategy Comparison", "Raw Stock Value", "Stock Value Change"])
with chart_tab_strats:
    st.line_chart(stock_chart_data, x = "Date", y = ["State", "Path"])
with chart_tab_raw:
    st.line_chart(data, x = "Date", y = type)
with chart_tab_change:
    st.line_chart(diff_df, x = "Date", y = "Change in Stock Value")
