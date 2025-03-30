import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import time
from constants import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)
import plotly.graph_objects as go

# Exchange rates for currency conversion
USD_TO_SEK = 10.7
USD_TO_NOK = 11
USD_TO_DKK = 7

# --------------------------- DATABASE CONNECTION --------------------------- #
# PostgreSQL database connection
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(connection_string)

# Fetch the latest XRP prices from the database
#WHERE timestamp >= NOW() - INTERVAL '24 hours'
query = '''SELECT coin, price_usd, updated, timestamp 
FROM "XRP" 
ORDER BY timestamp DESC;'''  # Considering adding LIMIT?




with engine.connect() as connect:
    df = pd.read_sql(query, connect)

# Convert timestamp column to datetime format
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Set timestamp as the index (helps filtering based on time intervals)
df.set_index("timestamp", inplace=True)
st.markdown("<h1 style='font-size: 25px; color: #000000;'>The Cointainers</h1>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
# --------------------------- STREAMLIT LAYOUT --------------------------- #
# Create columns
col1, col2 = st.columns(2)

# Display log
with col1:
    st.image("https://cryptologos.cc/logos/xrp-xrp-logo.png", width=150)

# Display title
with col2:
    st.markdown("# XRP Coin Data")

# --------------------------- CURRENCY SELECTION --------------------------- #
# Dropdown menu currency (USD, SEK, NOK, DKK)
currency = st.selectbox("Select a currency:", ["USD", "SEK", "NOK", "DKK"])

# Function to convert price based on selected currency
def convert_price(price_usd, currency):
    rates = {"SEK": USD_TO_SEK, "NOK": USD_TO_NOK, "DKK": USD_TO_DKK, "USD": 1}
    return price_usd * rates[currency]

# Apply the conversion function to all rows in the dataset
df["price"] = df["price_usd"].apply(lambda x: convert_price(x, currency))

# Add a currency column to indicate the selected currency
df["currency"] = currency

# --------------------------- DISPLAY LATEST DATA --------------------------- #
st.markdown("## Latest Data")
# Display the latest data in a table
st.dataframe(df[["coin", "price", "currency", "updated"]])

# --------------------------- PRICE CHANGE CALCULATION --------------------------- #
# Function to calculate price change over a given time interval
def calculate_price_change(df, minutes):
    start_time = df.index.max() - pd.Timedelta(minutes=minutes)  # Calculate start time
    df_filtered = df[df.index >= start_time]  # Filter dataset based on start time

    # Ensures there are at least two data points for comparison
    if len(df_filtered) > 1:
        first_price = df_filtered["price"].iloc[-1]  # Oldest price in the filtered dataset
        last_price = df_filtered["price"].iloc[0]  # Most recent price in the filtered dataset
        return ((first_price - last_price) / last_price) * 100  # Percentage change
    return 0  # Return 0 if not enough data

# Define time intervals to analyze price (in minutes)
time_intervals = [5, 10, 20, 30, 40, 50, 60] 

# Calculate price changes for each time interval
price_changes = {f"{min} min": calculate_price_change(df, min) for min in time_intervals}

# --------------------------- DISPLAY PRICE CHANGES --------------------------- #
st.markdown("### Price Changes")

# Create a 2x2 grid layout to display percentage changes
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)
columns = [row1_col1, row1_col2, row2_col1, row2_col2]

# Display percentage change for each time interval
for col, (period, change) in zip(columns, price_changes.items()):
    color = "green" if change >= 0 else "red"  # Color code: green for positive, red for negative
    direction = "↗" if change >= 0 else "↘"  # Arrow indicator based on change direction
    
    # Display price change percentage with styling
    col.markdown(f"<p style='color: {color}; font-size:37px; font-weight:bold;'>{direction} {change:.2f}%</p>", unsafe_allow_html=True)
    col.write(period)  # Show the corresponding time period label


# --------------------------- GRAPH: PRICE CHANGES OVER TIME --------------------------- #
fig = go.Figure()

# Plot price changes over the defined time intervals
for i in range(1, len(time_intervals)):
    color = 'green' if price_changes[f"{time_intervals[i]} min"] >= 0 else 'red'  # Define color based on change direction
    
    # Add a line plot for price changes between intervals
    fig.add_trace(go.Scatter(
        x=[time_intervals[i-1], time_intervals[i]],  # X-axis: Time intervals
        y=[price_changes[f"{time_intervals[i-1]} min"], price_changes[f"{time_intervals[i]} min"]],  # Y-axis: Price changes
        mode='lines+markers',  # Display as lines with markers
        line=dict(color=color, width=3),  # Line style
        marker=dict(size=8, color='black', line=dict(width=2)),  # Marker style
        name=f"{time_intervals[i-1]}-{time_intervals[i]} min"  # Label for legend
    ))

# Graph layout
fig.update_layout(
    title="Price Changes for XRP Over Different Time Intervals",
    xaxis_title="Time Period (minutes)",
    yaxis_title="Price Change (%)",
    hovermode="x unified"  # Enable hover mode for better interaction
)

st.plotly_chart(fig) # Display the graph

# --------------------------- AUTO REFRESH --------------------------- #
# Wait 30 seconds before reloading the page
time.sleep(30)
st.rerun()
