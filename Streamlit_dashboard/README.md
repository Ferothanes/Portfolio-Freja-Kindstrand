# 🔐 Kryptokollen - Real-Time Crypto Dashboard

## 📌 Project Overview

Kryptokollen is a prototype data platform built to stream and visualize live cryptocurrency data in real-time. The product is designed for users in the Nordic region who want to monitor their favorite cryptocurrencies effortlessly through a clean and informative dashboard.

This project was developed as part of a Data Engineering program, focusing on collaborative team practices using Git, GitHub, and agile methodologies.

## 🎯 Objectives

- Stream live crypto data using a producer-consumer pipeline.
- Visualize key metrics through an interactive dashboard.
- Build a modular and scalable data architecture.
- Collaborate in a team using GitHub Projects and agile principles.
- Practice clean code practices and version control in teams.

## 🧱 Project Architecture

- **Producer**: Fetches data from [CoinMarketCap API](https://coinmarketcap.com/api/) at 30–60 second intervals.
- **Connect API Module**: Reusable code for API requests, separated from the producer logic.
- **Consumer**: Consumes data and stores/transforms it for dashboard visualization.
- **Dashboard**: Built using tools like Streamlit or similar to display:
  - Price (in multiple currencies)
  - Volume and volume change
  - Price change
  - Additional statistics

  ## 🔄 Data Flow

1. **Producer** pulls data from CoinMarketCap API.
2. **Connect API Module** handles all HTTP requests.
3. **Consumer** ingests and processes the data.
4. **Dashboard** displays the processed data in real-time.