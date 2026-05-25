# Bykea Ride Analytics Dashboard

A Streamlit data analytics dashboard for exploring synthetic ride-hailing operations inspired by Bykea, a Pakistani mobility and logistics startup.

The dashboard generates 8,000 synthetic ride records inside the app and visualizes operational performance across demand, revenue, payments, cities, vehicle types, drivers, cancellations, and rider retention.

## Live App Preview

Run locally with:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Project Highlights

- Fully synthetic dataset generated in Python
- No external CSV or database required
- Streamlit dashboard with custom Bykea-themed CSS
- Plotly interactive charts
- KPI cards for executive-level metrics
- Sidebar filters for city, vehicle type, payment method, status, and date range
- Cached data generation and aggregations for better performance
- Heavily documented code with interview notes throughout

## Dashboard Sections

1. Header and Bykea branding
2. KPI row for total rides, revenue, average fare, distance, and cancellation rate
3. Daily ride volume and revenue trend
4. Hourly, weekly, and payment method analysis
5. City and pickup-area deep dive
6. Fare distribution and distance-vs-fare analysis
7. Peak vs off-peak impact analysis
8. Vehicle type comparison
9. Driver leaderboard and rating distribution
10. Cancellation reason and cancellation heatmap analysis
11. Monthly performance summary
12. Simplified rider cohort retention heatmap

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- NumPy
- Plotly Express
- Plotly Graph Objects

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Dataset

The app creates synthetic ride data with fields such as:

- Ride ID
- City
- Pickup area
- Driver ID
- Rider ID
- Ride date
- Distance
- Duration
- Fare
- Payment method
- Ride status
- Driver and rider ratings
- Peak-hour flag
- Vehicle type
- Cancellation reason

The generated data covers rides from January 2024 to December 2024 across Karachi, Lahore, and Islamabad.

## Why This Project Matters

This dashboard demonstrates how data analytics can support ride-hailing operations by answering questions such as:

- Which cities and pickup areas generate the most revenue?
- When does demand peak during the day?
- How much do peak hours affect fares and revenue?
- Which vehicle types perform best?
- What are the main causes of cancellations?
- Are riders returning after their first ride?
- Which drivers are top performers?

## Project Structure

```text
.
├── app.py
├── requirements.txt
└── README.md
```

## Author

Built by **Furqan Halari**  
FAST-NUCES Karachi  
Data Science Intern Application Project

