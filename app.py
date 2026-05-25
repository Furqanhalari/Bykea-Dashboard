import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Bykea Ride Analytics Dashboard",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)


BYKEA_ORANGE = "#FF6B00"
DARK_NAVY = "#1A1A2E"
LIGHT_GREY = "#F8F9FA"
MID_GREY = "#E9ECEF"
TEXT_GREY = "#6C757D"
GREEN = "#1DB954"
BLUE = "#4A90D9"
LIGHT_ORANGE = "#FFF1E8"


st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {LIGHT_GREY};
        }}

        [data-testid="stSidebar"] {{
            background-color: {DARK_NAVY};
        }}

        [data-testid="stSidebar"] * {{
            color: white;
        }}

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown p {{
            color: white !important;
        }}

        [data-testid="stSidebar"] .stMultiSelect div,
        [data-testid="stSidebar"] .stDateInput div {{
            color: {DARK_NAVY};
        }}

        h1, h2, h3 {{
            color: {DARK_NAVY};
            font-weight: 800;
        }}

        .bykea-sidebar-title {{
            color: {BYKEA_ORANGE} !important;
            font-size: 1.7rem;
            font-weight: 900;
            margin-bottom: 0.1rem;
        }}

        .bykea-sidebar-subtitle {{
            color: #D6D6E7 !important;
            font-size: 0.9rem;
            margin-bottom: 1.1rem;
        }}

        .section-divider {{
            border: 0;
            height: 2px;
            background: {BYKEA_ORANGE};
            margin: 0.65rem 0 1.15rem 0;
        }}

        .thin-divider {{
            border: 0;
            height: 1px;
            background: {BYKEA_ORANGE};
            margin: 1rem 0;
        }}

        .kpi-card {{
            background: white;
            border-left: 6px solid {BYKEA_ORANGE};
            border-radius: 8px;
            box-shadow: 0 4px 14px rgba(26, 26, 46, 0.09);
            padding: 1rem 1.1rem;
            min-height: 118px;
        }}

        .kpi-label {{
            color: {TEXT_GREY};
            font-size: 0.84rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0;
        }}

        .kpi-value {{
            color: {DARK_NAVY};
            font-size: 1.55rem;
            font-weight: 900;
            margin-top: 0.35rem;
            line-height: 1.15;
        }}

        .kpi-delta-positive {{
            color: {GREEN};
            font-size: 0.86rem;
            font-weight: 700;
            margin-top: 0.35rem;
        }}

        .kpi-delta-negative {{
            color: #D64545;
            font-size: 0.86rem;
            font-weight: 700;
            margin-top: 0.35rem;
        }}

        .mini-metric {{
            background: white;
            border-left: 5px solid {BYKEA_ORANGE};
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(26, 26, 46, 0.08);
            padding: 0.9rem;
            margin-bottom: 0.7rem;
        }}

        .mini-metric-title {{
            color: {TEXT_GREY};
            font-size: 0.78rem;
            font-weight: 700;
        }}

        .mini-metric-value {{
            color: {DARK_NAVY};
            font-size: 1.2rem;
            font-weight: 900;
        }}

        .footer-text {{
            text-align: center;
            color: {DARK_NAVY};
            font-weight: 800;
            margin-top: 0.8rem;
        }}

        .footer-subtext {{
            text-align: center;
            color: {TEXT_GREY};
            font-size: 0.88rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def generate_ride_data(n_rows: int = 8000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    city_area_map = {
        "Karachi": ["DHA", "Gulshan", "Clifton", "PECHS", "Nazimabad", "Saddar", "Korangi", "Lyari", "Malir"],
        "Lahore": ["Gulberg", "DHA Lahore", "Johar Town", "Model Town", "Bahria", "Cantt"],
        "Islamabad": ["F-7", "F-10", "G-9", "Blue Area", "I-8", "E-11", "Bahria Islamabad"],
    }
    ride_ids = [f"RD{i:05d}" for i in range(1, n_rows + 1)]

    cities = rng.choice(["Karachi", "Lahore", "Islamabad"], size=n_rows, p=[0.50, 0.30, 0.20])

    pickup_areas = [rng.choice(city_area_map[city]) for city in cities]

    driver_ids = rng.choice([f"DR{i:04d}" for i in range(1, 401)], size=n_rows)
    rider_ids = rng.choice([f"R{i:04d}" for i in range(1, 1201)], size=n_rows)

    start = pd.Timestamp("2024-01-01 00:00:00")
    end = pd.Timestamp("2024-12-31 23:00:00")
    total_hours = int((end - start).total_seconds() // 3600)
    ride_dates = start + pd.to_timedelta(rng.integers(0, total_hours + 1, size=n_rows), unit="h")

    distance_km = np.clip(rng.exponential(scale=5, size=n_rows), 0.5, 40).round(2)

    duration_mins = (distance_km * rng.uniform(3, 6, size=n_rows) + rng.uniform(2, 10, size=n_rows)).round(1)

    hours = pd.DatetimeIndex(ride_dates).hour
    is_peak_hour = np.isin(hours, [7, 8, 9, 17, 18, 19, 20])

    fare = 50 + distance_km * rng.uniform(13, 18, size=n_rows)
    fare = np.where(is_peak_hour, fare * 1.30, fare).round(0)

    payment_methods = rng.choice(["Cash", "Bykea Pay", "Card"], size=n_rows, p=[0.55, 0.30, 0.15])

    statuses = rng.choice(["Completed", "Cancelled", "In Progress"], size=n_rows, p=[0.80, 0.15, 0.05])

    driver_ratings = np.clip(rng.normal(4.3, 0.4, size=n_rows), 1, 5).round(2)
    rider_ratings = np.clip(rng.normal(4.1, 0.5, size=n_rows), 1, 5).round(2)
    vehicle_types = rng.choice(["Bike", "Cargo", "Rickshaw"], size=n_rows, p=[0.70, 0.20, 0.10])

    reasons = ["Driver no show", "Rider cancelled", "No driver available", "Price too high", "Wrong location"]
    cancellation_reason = np.where(statuses == "Cancelled", rng.choice(reasons, size=n_rows), "")

    df = pd.DataFrame(
        {
            "ride_id": ride_ids,
            "city": cities,
            "pickup_area": pickup_areas,
            "driver_id": driver_ids,
            "rider_id": rider_ids,
            "ride_date": ride_dates,
            "distance_km": distance_km,
            "duration_mins": duration_mins,
            "fare": fare,
            "payment_method": payment_methods,
            "status": statuses,
            "driver_rating": driver_ratings,
            "rider_rating": rider_ratings,
            "is_peak_hour": is_peak_hour,
            "vehicle_type": vehicle_types,
            "cancellation_reason": cancellation_reason,
        }
    )

    df["date"] = df["ride_date"].dt.date
    df["hour"] = df["ride_date"].dt.hour
    df["month"] = df["ride_date"].dt.to_period("M").astype(str)
    df["month_name"] = df["ride_date"].dt.month_name()
    df["day_name"] = df["ride_date"].dt.day_name()
    df["hour_bucket"] = pd.cut(
        df["hour"],
        bins=[-1, 5, 11, 16, 20, 23],
        labels=["Night", "Morning", "Afternoon", "Evening", "Night"],
        ordered=False,
    )

    # Sort by date for cleaner trend calculations and deterministic display.
    df = df.sort_values("ride_date").reset_index(drop=True)
    return df




@st.cache_data(show_spinner=False)
def build_daily_trend(filtered_df: pd.DataFrame) -> pd.DataFrame:
    # GROUP BY date and aggregate rides and revenue to create a time-series table.
    daily = (
        filtered_df.groupby("date")
        .agg(ride_count=("ride_id", "count"), revenue=("fare", "sum"))
        .reset_index()
        .sort_values("date")
    )
    # Use a rolling 7-day average to smooth weekday noise and reveal the trend.
    daily["rolling_7d_rides"] = daily["ride_count"].rolling(window=7, min_periods=1).mean()
    # Convert revenue to thousands so it can share a visual scale more easily.
    daily["revenue_k"] = daily["revenue"] / 1000
    return daily


@st.cache_data(show_spinner=False)
def build_monthly_summary(filtered_df: pd.DataFrame) -> pd.DataFrame:
    # Build numeric monthly metrics with named aggregation for readable columns.
    monthly = (
        filtered_df.groupby("month")
        .agg(
            total_rides=("ride_id", "count"),
            total_revenue=("fare", "sum"),
            avg_fare=("fare", "mean"),
            avg_distance=("distance_km", "mean"),
            cancellation_rate=("status", lambda s: (s == "Cancelled").mean() * 100),
        )
        .reset_index()
    )

    top_city = filtered_df.groupby("month")["city"].agg(lambda s: s.value_counts().idxmax()).reset_index(name="top_city")

    # Find the top payment method per month to show payment behavior by period.
    top_payment = (
        filtered_df.groupby("month")["payment_method"]
        .agg(lambda s: s.value_counts().idxmax())
        .reset_index(name="top_payment_method")
    )

    # Merge the categorical summaries onto the numeric monthly table.
    monthly = monthly.merge(top_city, on="month", how="left").merge(top_payment, on="month", how="left")

    # Convert YYYY-MM to a friendly month name while preserving chronological sort.
    monthly["month_name"] = pd.to_datetime(monthly["month"]).dt.month_name()
    monthly = monthly[
        [
            "month_name",
            "total_rides",
            "total_revenue",
            "avg_fare",
            "avg_distance",
            "cancellation_rate",
            "top_city",
            "top_payment_method",
        ]
    ]
    return monthly


@st.cache_data(show_spinner=False)
def build_cohort_matrix(filtered_df: pd.DataFrame) -> pd.DataFrame:
    rider_months = filtered_df[["rider_id", "month"]].drop_duplicates()

    # Identify each rider's first observed ride month in the filtered period.
    first_month = rider_months.groupby("rider_id")["month"].min().reset_index(name="cohort_month")

    # Attach the cohort month to every later active month for the same rider.
    cohort_data = rider_months.merge(first_month, on="rider_id", how="left")

    # Convert month strings to period objects so month differences are arithmetic,
    # not fragile string comparisons.
    cohort_data["activity_period"] = pd.PeriodIndex(cohort_data["month"], freq="M")
    cohort_data["cohort_period"] = pd.PeriodIndex(cohort_data["cohort_month"], freq="M")
    cohort_data["period_number"] = (
        cohort_data["activity_period"].astype("int64") - cohort_data["cohort_period"].astype("int64")
    )

    # Count unique returning riders for each cohort and age.
    retention = (
        cohort_data.groupby(["cohort_month", "period_number"])["rider_id"]
        .nunique()
        .reset_index(name="active_riders")
    )

    matrix = retention.pivot(index="cohort_month", columns="period_number", values="active_riders").fillna(0)
    matrix.index = pd.to_datetime(matrix.index).strftime("%b 2024")
    matrix.columns = [f"M+{int(col)}" for col in matrix.columns]
    return matrix


def style_figure(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0.02, "xanchor": "left", "font": {"size": 17, "color": DARK_NAVY}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"size": 12, "color": DARK_NAVY},
        margin={"l": 20, "r": 20, "t": 60, "b": 30},
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def render_kpi(label: str, value: str, delta: str, positive: bool = True) -> None:
    delta_class = "kpi-delta-positive" if positive else "kpi-delta-negative"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="{delta_class}">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_mini_metric(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="mini-metric">
            <div class="mini-metric-title">{title}</div>
            <div class="mini-metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



df = generate_ride_data()

with st.sidebar:
    # Sidebar title uses the Bykea brand color and communicates dashboard purpose.
    st.markdown('<div class="bykea-sidebar-title">🛵 Bykea Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="bykea-sidebar-subtitle">Data Science Intern Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

    # Filter controls let users slice the marketplace by geography, product,
    # payment behavior, operational status, and time period.
    st.markdown("### 📊 Filters")
    selected_cities = st.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))
    selected_vehicles = st.multiselect("Vehicle Type", sorted(df["vehicle_type"].unique()), default=sorted(df["vehicle_type"].unique()))
    selected_payments = st.multiselect("Payment Method", sorted(df["payment_method"].unique()), default=sorted(df["payment_method"].unique()))
    selected_statuses = st.multiselect("Status", sorted(df["status"].unique()), default=["Completed"])
    date_range = st.date_input(
        "Date Range",
        value=(pd.Timestamp("2024-01-01").date(), pd.Timestamp("2024-12-31").date()),
        min_value=pd.Timestamp("2024-01-01").date(),
        max_value=pd.Timestamp("2024-12-31").date(),
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = pd.Timestamp("2024-01-01").date(), pd.Timestamp("2024-12-31").date()

    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
    st.markdown("### 📈 Dataset Info")


base_filtered = df[
    df["city"].isin(selected_cities)
    & df["vehicle_type"].isin(selected_vehicles)
    & df["payment_method"].isin(selected_payments)
    & df["status"].isin(selected_statuses)
].copy()

# Apply the date filter once and reuse this filtered DataFrame everywhere.
filtered_df = base_filtered[(base_filtered["date"] >= start_date) & (base_filtered["date"] <= end_date)].copy()


with st.sidebar:
    st.write(f"Rows: **{len(filtered_df):,}**")
    if not filtered_df.empty:
        st.write(f"Range: **{filtered_df['date'].min()} to {filtered_df['date'].max()}**")
    else:
        st.write("Range: **No data**")
    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)
    st.markdown('<p style="color:#B9B9C9;font-size:0.78rem;">Built by Furqan Halari</p>', unsafe_allow_html=True)


# SECTION 0 - HEADER: Introduce the dashboard and its operational purpose.
st.title("🛵 Bykea Ride Analytics Dashboard")
st.markdown(f"<p style='color:{TEXT_GREY};font-size:1.05rem;'>Operational insights for ride-hailing performance</p>", unsafe_allow_html=True)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
# INTERVIEW NOTE: A dashboard header frames the business context before users
# inspect individual metrics.

if filtered_df.empty:
    st.warning("No data for selected filters")
    st.stop()
# INTERVIEW NOTE: Empty-state handling is part of production dashboard quality.

date_span_days = max((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1, 1)
previous_end = pd.Timestamp(start_date) - pd.Timedelta(days=1)
previous_start = previous_end - pd.Timedelta(days=date_span_days - 1)
previous_df = base_filtered[
    (pd.to_datetime(base_filtered["date"]) >= previous_start)
    & (pd.to_datetime(base_filtered["date"]) <= previous_end)
].copy()

# Calculate current KPIs from the filtered DataFrame.
total_rides = len(filtered_df)
total_revenue = filtered_df["fare"].sum()
avg_fare = filtered_df["fare"].mean()
avg_distance = filtered_df["distance_km"].mean()
cancellation_rate = (filtered_df["status"].eq("Cancelled").mean() * 100) if total_rides else 0

# Compare ride volume with the previous period using the same filter slice.
previous_rides = len(previous_df)
ride_delta_pct = ((total_rides - previous_rides) / previous_rides * 100) if previous_rides else 0
delta_text = f"{ride_delta_pct:+.1f}% vs previous period" if previous_rides else "No previous-period data"

kpi_cols = st.columns(5)
with kpi_cols[0]:
    render_kpi("Total Rides", f"{total_rides:,}", delta_text, ride_delta_pct >= 0)
with kpi_cols[1]:
    render_kpi("Total Revenue", f"PKR {total_revenue:,.0f}", "Marketplace earning volume", True)
with kpi_cols[2]:
    render_kpi("Average Fare", f"PKR {avg_fare:,.0f}", "Pricing per ride", True)
with kpi_cols[3]:
    render_kpi("Average Distance", f"{avg_distance:.2f} km", "Trip length signal", True)
with kpi_cols[4]:
    render_kpi("Cancellation Rate", f"{cancellation_rate:.1f}%", "Lower is better", cancellation_rate <= 15)



# SECTION 2 - TREND ANALYSIS: Build a dual-axis daily trend for rides and revenue.
st.markdown("## 📈 Daily Ride Volume Trend")
daily_trend = build_daily_trend(filtered_df)

trend_fig = make_subplots(specs=[[{"secondary_y": True}]])
trend_fig.add_trace(
    go.Scatter(
        x=daily_trend["date"],
        y=daily_trend["ride_count"],
        mode="lines",
        name="Daily rides",
        line={"color": BYKEA_ORANGE, "width": 2.8},
        hovertemplate="Date=%{x}<br>Rides=%{y:,}<extra></extra>",
    ),
    secondary_y=False,
)
trend_fig.add_trace(
    go.Scatter(
        x=daily_trend["date"],
        y=daily_trend["rolling_7d_rides"],
        mode="lines",
        name="7-day average",
        line={"color": "#8A8A8A", "width": 1.5},
        hovertemplate="Date=%{x}<br>7-day avg=%{y:.1f}<extra></extra>",
    ),
    secondary_y=False,
)
trend_fig.add_trace(
    go.Scatter(
        x=daily_trend["date"],
        y=daily_trend["revenue_k"],
        mode="lines",
        name="Revenue (PKR k)",
        line={"color": GREEN, "width": 2.4, "dash": "dash"},
        hovertemplate="Date=%{x}<br>Revenue=PKR %{y:.1f}k<extra></extra>",
    ),
    secondary_y=True,
)

# Detect the peak day from the filtered trend and annotate it automatically.
peak_day = daily_trend.loc[daily_trend["ride_count"].idxmax()]
trend_fig.add_annotation(
    x=peak_day["date"],
    y=peak_day["ride_count"],
    text=f"Peak: {int(peak_day['ride_count'])} rides",
    showarrow=True,
    arrowhead=2,
    arrowcolor=BYKEA_ORANGE,
    bgcolor="white",
    bordercolor=BYKEA_ORANGE,
)
trend_fig.update_yaxes(title_text="Daily ride count", secondary_y=False)
trend_fig.update_yaxes(title_text="Revenue (PKR thousands)", secondary_y=True)
trend_fig = style_figure(trend_fig, "Daily rides, revenue, and 7-day demand smoothing")
st.plotly_chart(trend_fig, use_container_width=True)
# INTERVIEW NOTE: Dual-axis charts compare related metrics with different units.
# Use them carefully when the goal is pattern comparison, not exact scale comparison.


# SECTION 3 - THREE COLUMNS: Show demand timing, weekly seasonality, and payments.
col1, col2, col3 = st.columns(3)

with col1:
    # GROUP BY hour to reveal when ride demand is highest during the day.
    hourly = filtered_df.groupby("hour").size().reset_index(name="rides")
    hourly_fig = px.bar(
        hourly,
        x="hour",
        y="rides",
        color="rides",
        color_continuous_scale=["#FFE0CC", BYKEA_ORANGE],
        labels={"hour": "Hour of day", "rides": "Rides"},
    )
    peak_hour_row = hourly.loc[hourly["rides"].idxmax()]
    hourly_fig.add_annotation(
        x=int(peak_hour_row["hour"]),
        y=int(peak_hour_row["rides"]),
        text="Peak hour",
        showarrow=True,
        arrowcolor=BYKEA_ORANGE,
        bgcolor="white",
    )
    hourly_fig = style_figure(hourly_fig, "⏰ Hourly Demand Heatmap")
    hourly_fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(hourly_fig, use_container_width=True)


with col2:
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = (
        filtered_df.groupby("day_name")
        .agg(ride_count=("ride_id", "count"), avg_fare=("fare", "mean"))
        .reindex(weekday_order)
        .reset_index()
    )
    dow_long = dow.melt(id_vars="day_name", value_vars=["ride_count", "avg_fare"], var_name="metric", value_name="value")
    dow_fig = px.bar(
        dow_long,
        y="day_name",
        x="value",
        color="metric",
        barmode="group",
        orientation="h",
        color_discrete_map={"ride_count": BYKEA_ORANGE, "avg_fare": BLUE},
        labels={"day_name": "", "value": "Value", "metric": "Metric"},
        category_orders={"day_name": weekday_order},
    )
    dow_fig = style_figure(dow_fig, "📅 Day of Week Performance")
    st.plotly_chart(dow_fig, use_container_width=True)
    # INTERVIEW NOTE: Weekly seasonality shows which days need more driver supply,
    # marketing pushes, or pricing attention.

with col3:
    # Count rides by payment method to understand how customers pay in practice.
    payment_split = filtered_df["payment_method"].value_counts().reset_index()
    payment_split.columns = ["payment_method", "rides"]
    payment_fig = px.pie(
        payment_split,
        names="payment_method",
        values="rides",
        hole=0.55,
        color="payment_method",
        color_discrete_map={"Cash": BYKEA_ORANGE, "Bykea Pay": GREEN, "Card": DARK_NAVY},
    )
    payment_fig.update_traces(textinfo="percent+label", hovertemplate="%{label}<br>Rides=%{value:,}<br>Share=%{percent}<extra></extra>")
    payment_fig = style_figure(payment_fig, "💳 Payment Method Split")
    st.plotly_chart(payment_fig, use_container_width=True)



# SECTION 4 - CITY DEEP DIVE: Compare markets and pinpoint pickup areas.
city_col, area_col = st.columns(2)

with city_col:
    city_perf = (
        filtered_df.groupby("city")
        .agg(rides=("ride_id", "count"), revenue=("fare", "sum"), avg_fare=("fare", "mean"))
        .reset_index()
    )
    city_perf["revenue_k"] = city_perf["revenue"] / 1000
    city_long = city_perf.melt(id_vars="city", value_vars=["rides", "revenue_k", "avg_fare"], var_name="metric", value_name="value")
    city_fig = px.bar(
        city_long,
        x="city",
        y="value",
        color="metric",
        barmode="group",
        color_discrete_sequence=[BYKEA_ORANGE, GREEN, BLUE],
        labels={"city": "City", "value": "Value", "metric": "Metric"},
    )
    city_fig = style_figure(city_fig, "🏙️ City Performance Comparison")
    st.plotly_chart(city_fig, use_container_width=True)


with area_col:
    # GROUP BY pickup area and city to find revenue hotspots for driver placement.
    top_areas = (
        filtered_df.groupby(["pickup_area", "city"])["fare"]
        .sum()
        .reset_index(name="revenue")
        .sort_values("revenue", ascending=False)
        .head(12)
    )
    area_fig = px.bar(
        top_areas.sort_values("revenue"),
        x="revenue",
        y="pickup_area",
        color="city",
        orientation="h",
        color_discrete_map={"Karachi": BYKEA_ORANGE, "Lahore": GREEN, "Islamabad": BLUE},
        labels={"pickup_area": "Pickup area", "revenue": "Revenue (PKR)", "city": "City"},
    )
    area_fig.update_traces(hovertemplate="Area=%{y}<br>Revenue=PKR %{x:,.0f}<extra></extra>")
    area_fig = style_figure(area_fig, "📍 Top 12 Pickup Areas by Revenue")
    st.plotly_chart(area_fig, use_container_width=True)
    # INTERVIEW NOTE: Pickup area analysis tells operations where drivers should
    # wait, where incentives may work, and where local demand is concentrated.


# SECTION 5 - FARE AND DISTANCE ANALYSIS: Inspect pricing distribution and logic.
fare_col, scatter_col = st.columns(2)

with fare_col:
    # Plot fare distribution to detect skew, outliers, and common price bands.
    fare_fig = px.histogram(
        filtered_df,
        x="fare",
        nbins=40,
        color_discrete_sequence=[BYKEA_ORANGE],
        labels={"fare": "Fare (PKR)", "count": "Rides"},
    )
    mean_fare = filtered_df["fare"].mean()
    median_fare = filtered_df["fare"].median()
    fare_fig.add_vline(x=mean_fare, line_color=GREEN, line_width=2, annotation_text=f"Mean {mean_fare:.0f}")
    fare_fig.add_vline(x=median_fare, line_color=BLUE, line_width=2, annotation_text=f"Median {median_fare:.0f}")
    fare_fig = style_figure(fare_fig, "💸 Fare Distribution")
    st.plotly_chart(fare_fig, use_container_width=True)


with scatter_col:
    scatter_fig = px.scatter(
        filtered_df.sample(min(len(filtered_df), 2500), random_state=7),
        x="distance_km",
        y="fare",
        color="city",
        size="driver_rating",
        color_discrete_map={"Karachi": BYKEA_ORANGE, "Lahore": GREEN, "Islamabad": BLUE},
        labels={"distance_km": "Distance (km)", "fare": "Fare (PKR)", "driver_rating": "Driver rating"},
        hover_data=["ride_id", "vehicle_type", "status"],
    )

    slope, intercept = np.polyfit(filtered_df["distance_km"], filtered_df["fare"], 1)
    x_line = np.linspace(filtered_df["distance_km"].min(), filtered_df["distance_km"].max(), 100)
    scatter_fig.add_trace(
        go.Scatter(
            x=x_line,
            y=slope * x_line + intercept,
            mode="lines",
            name="Trendline",
            line={"color": DARK_NAVY, "width": 2},
            hovertemplate="Trend fare=PKR %{y:.0f}<extra></extra>",
        )
    )
    scatter_fig = style_figure(scatter_fig, "📏 Distance vs Fare Scatter")
    st.plotly_chart(scatter_fig, use_container_width=True)



# SECTION 6 - PEAK VS OFF-PEAK: Quantify surge-hour impact on rides and revenue.
st.markdown("## ⚡ Peak Hour Impact Analysis")
peak_df = filtered_df.copy()
peak_df["period_type"] = np.where(peak_df["is_peak_hour"], "Peak", "Off-peak")
period_summary = (
    peak_df.groupby("period_type")
    .agg(avg_fare=("fare", "mean"), total_rides=("ride_id", "count"), revenue=("fare", "sum"))
    .reset_index()
)
period_summary["revenue_share"] = period_summary["revenue"] / period_summary["revenue"].sum() * 100

peak_metric_cols = st.columns(6)
for idx, period in enumerate(["Peak", "Off-peak"]):
    row = period_summary[period_summary["period_type"] == period].iloc[0]
    with peak_metric_cols[idx * 3]:
        render_mini_metric(f"{period} Avg Fare", f"PKR {row['avg_fare']:,.0f}")
    with peak_metric_cols[idx * 3 + 1]:
        render_mini_metric(f"{period} Rides", f"{row['total_rides']:,.0f}")
    with peak_metric_cols[idx * 3 + 2]:
        render_mini_metric(f"{period} Revenue Share", f"{row['revenue_share']:.1f}%")

# Stack hourly rides by peak category to show the daily shape of surge demand.
hour_period = peak_df.groupby(["hour", "period_type"]).size().reset_index(name="rides")
peak_fig = px.bar(
    hour_period,
    x="hour",
    y="rides",
    color="period_type",
    color_discrete_map={"Peak": BYKEA_ORANGE, "Off-peak": "#BFC3CA"},
    labels={"hour": "Hour", "rides": "Rides", "period_type": "Period"},
)
peak_fig = style_figure(peak_fig, "Hourly ride mix by peak and off-peak periods")
st.plotly_chart(peak_fig, use_container_width=True)


st.markdown("## 🛺 Vehicle Type Analysis")
vehicle_summary = (
    filtered_df.groupby("vehicle_type")
    .agg(
        total_rides=("ride_id", "count"),
        avg_fare=("fare", "mean"),
        avg_distance=("distance_km", "mean"),
        cancellation_rate=("status", lambda s: (s == "Cancelled").mean() * 100),
    )
    .reset_index()
)


radar_metrics = ["total_rides", "avg_fare", "avg_distance", "cancellation_rate"]
radar_norm = vehicle_summary.copy()
for metric in radar_metrics:
    max_value = radar_norm[metric].max()
    radar_norm[metric] = radar_norm[metric] / max_value if max_value else 0

vehicle_cols = st.columns(3)
for col, vehicle in zip(vehicle_cols, ["Bike", "Cargo", "Rickshaw"]):
    row = vehicle_summary[vehicle_summary["vehicle_type"] == vehicle]
    if not row.empty:
        row = row.iloc[0]
        with col:
            render_mini_metric(f"{vehicle} Rides", f"{row['total_rides']:,.0f}")
            render_mini_metric(f"{vehicle} Avg Fare", f"PKR {row['avg_fare']:,.0f}")
            render_mini_metric(f"{vehicle} Avg Distance", f"{row['avg_distance']:.2f} km")
            render_mini_metric(f"{vehicle} Cancellation", f"{row['cancellation_rate']:.1f}%")

radar_fig = go.Figure()
for vehicle, color in zip(["Bike", "Cargo", "Rickshaw"], [BYKEA_ORANGE, GREEN, BLUE]):
    row = radar_norm[radar_norm["vehicle_type"] == vehicle]
    if not row.empty:
        values = row[radar_metrics].iloc[0].tolist()
        radar_fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=["Total rides", "Avg fare", "Avg distance", "Cancellation rate", "Total rides"],
                fill="toself",
                name=vehicle,
                line={"color": color},
            )
        )
radar_fig.update_layout(polar={"radialaxis": {"visible": True, "range": [0, 1]}}, showlegend=True)
radar_fig = style_figure(radar_fig, "Vehicle comparison radar chart")
st.plotly_chart(radar_fig, use_container_width=True)

driver_col, rating_col = st.columns(2)

with driver_col:
    driver_board = (
        filtered_df.groupby("driver_id")
        .agg(rides=("ride_id", "count"), total_earnings=("fare", "sum"), avg_rating=("driver_rating", "mean"))
        .reset_index()
        .sort_values("total_earnings", ascending=False)
        .head(15)
    )
    driver_board["rank"] = range(1, len(driver_board) + 1)
    driver_board = driver_board[["rank", "driver_id", "rides", "total_earnings", "avg_rating"]]

    # Highlight top 3 rows in light orange so the best performers stand out.
    def highlight_top_three(row):
        return [f"background-color: {LIGHT_ORANGE}" if row["rank"] <= 3 else "" for _ in row]

    st.markdown("### 🏆 Top 15 Drivers Leaderboard")
    st.dataframe(
        driver_board.style.apply(highlight_top_three, axis=1).format(
            {"total_earnings": "PKR {:,.0f}", "avg_rating": "{:.2f}"}
        ),
        use_container_width=True,
        hide_index=True,
    )

with rating_col:
    # Plot driver rating distribution and add qualitative zones for interpretation.
    rating_fig = px.histogram(
        filtered_df,
        x="driver_rating",
        nbins=25,
        color_discrete_sequence=[BYKEA_ORANGE],
        labels={"driver_rating": "Driver rating"},
    )
    rating_fig.add_vrect(x0=1, x1=4.0, fillcolor="#FFD6D6", opacity=0.25, line_width=0, annotation_text="Poor")
    rating_fig.add_vrect(x0=4.0, x1=4.5, fillcolor="#FFF3CD", opacity=0.25, line_width=0, annotation_text="Good")
    rating_fig.add_vrect(x0=4.5, x1=5.0, fillcolor="#D8F5DF", opacity=0.25, line_width=0, annotation_text="Excellent")
    rating_fig = style_figure(rating_fig, "⭐ Driver Rating Distribution")
    st.plotly_chart(rating_fig, use_container_width=True)


# SECTION 9 - CANCELLATION ANALYSIS: Diagnose failed ride attempts.
cancel_col, cancel_heat_col = st.columns(2)

with cancel_col:
    # Filter to cancelled rides because cancellation reason is blank otherwise.
    cancelled = filtered_df[filtered_df["status"] == "Cancelled"]
    if cancelled.empty:
        st.warning("No data for selected filters")
    else:
        reason_counts = cancelled["cancellation_reason"].value_counts().reset_index()
        reason_counts.columns = ["reason", "rides"]
        reason_fig = px.bar(
            reason_counts.sort_values("rides"),
            x="rides",
            y="reason",
            orientation="h",
            color="reason",
            color_discrete_sequence=[BYKEA_ORANGE, GREEN, BLUE, "#B56576", DARK_NAVY],
            labels={"rides": "Cancelled rides", "reason": "Reason"},
        )
        reason_fig = style_figure(reason_fig, "❌ Cancellation Reasons Breakdown")
        reason_fig.update_layout(showlegend=False)
        st.plotly_chart(reason_fig, use_container_width=True)

with cancel_heat_col:
    cancel_rate = (
        filtered_df.groupby(["city", "hour_bucket"])["status"]
        .apply(lambda s: (s == "Cancelled").mean() * 100)
        .reset_index(name="cancel_rate")
    )
    cancel_matrix = cancel_rate.pivot(index="city", columns="hour_bucket", values="cancel_rate").fillna(0)
    bucket_order = ["Morning", "Afternoon", "Evening", "Night"]
    cancel_matrix = cancel_matrix[[col for col in bucket_order if col in cancel_matrix.columns]]
    cancel_heat_fig = px.imshow(
        cancel_matrix,
        color_continuous_scale=["white", BYKEA_ORANGE],
        labels={"x": "Hour bucket", "y": "City", "color": "Cancellation %"},
        text_auto=".1f",
        aspect="auto",
    )
    cancel_heat_fig = style_figure(cancel_heat_fig, "📊 Cancellation Rate by City and Hour")
    st.plotly_chart(cancel_heat_fig, use_container_width=True)


# SECTION 10 - MONTHLY TREND TABLE: Summarize executive reporting metrics.
st.markdown("## 📆 Monthly Performance Summary")
monthly_summary = build_monthly_summary(filtered_df)

styled_monthly = monthly_summary.style.background_gradient(subset=["total_revenue"], cmap="Greens").format(
    {
        "total_revenue": "PKR {:,.0f}",
        "avg_fare": "PKR {:,.0f}",
        "avg_distance": "{:.2f} km",
        "cancellation_rate": "{:.1f}%",
    }
)
st.dataframe(
    styled_monthly,
    use_container_width=True,
    hide_index=True,
    column_config={
        "month_name": st.column_config.TextColumn("Month"),
        "total_rides": st.column_config.NumberColumn("Total Rides", format="%d"),
        "total_revenue": st.column_config.NumberColumn("Total Revenue"),
        "avg_fare": st.column_config.NumberColumn("Avg Fare"),
        "avg_distance": st.column_config.NumberColumn("Avg Distance"),
        "cancellation_rate": st.column_config.NumberColumn("Cancellation Rate"),
        "top_city": st.column_config.TextColumn("Top City"),
        "top_payment_method": st.column_config.TextColumn("Top Payment Method"),
    },
)


# SECTION 11 - COHORT INSIGHT: Show simplified rider retention by first ride month.
st.markdown("## 🔄 Rider Activity Cohort (Simplified)")
cohort_matrix = build_cohort_matrix(filtered_df)
cohort_fig = px.imshow(
    cohort_matrix,
    color_continuous_scale=["white", BYKEA_ORANGE],
    labels={"x": "Months after first ride", "y": "First ride cohort", "color": "Active riders"},
    text_auto=".0f",
    aspect="auto",
)
cohort_fig = style_figure(cohort_fig, "Rider return activity by first-ride cohort")
st.plotly_chart(cohort_fig, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown('<div class="footer-text">🛵 Bykea Ride Analytics Dashboard | Built by Furqan Halari</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-subtext">FAST-NUCES Karachi | Data Science Intern Application | 2026</div>', unsafe_allow_html=True)


