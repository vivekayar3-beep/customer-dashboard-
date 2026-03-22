import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data
from model import train_model

# =========================
# PAGE SETUP
# =========================
st.set_page_config(page_title="Customer Dashboard", layout="wide")
st.title("🚀 Advanced Customer Analytics Dashboard")

# =========================
# LOAD DATA
# =========================
df = load_data()

# =========================
# 🗺️ CITY COORDINATES
# =========================
city_coords = {
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.7041, 77.1025],
    "Bangalore": [12.9716, 77.5946],
    "Chennai": [13.0827, 80.2707],
    "Ahmedabad": [23.0225, 72.5714],
    "Hyderabad": [17.3850, 78.4867],
    "Pune": [18.5204, 73.8567],
    "Kolkata": [22.5726, 88.3639]
}

df['lat'] = df['city'].map(lambda x: city_coords.get(x, [None, None])[0])
df['lon'] = df['city'].map(lambda x: city_coords.get(x, [None, None])[1])

# =========================
# 🔍 FILTERS
# =========================
st.sidebar.header("🔍 Filters")

category = st.sidebar.multiselect("Category", df['product_category'].unique(), default=df['product_category'].unique())
gender = st.sidebar.multiselect("Gender", df['gender'].unique(), default=df['gender'].unique())
city = st.sidebar.multiselect("City", df['city'].unique(), default=df['city'].unique())
membership = st.sidebar.multiselect("Membership Tier", df['membership_tier'].unique(), default=df['membership_tier'].unique())
payment = st.sidebar.multiselect("Payment Method", df['payment_method'].unique(), default=df['payment_method'].unique())

age_range = st.sidebar.slider(
    "Age Range",
    int(df['age'].min()),
    int(df['age'].max()),
    (int(df['age'].min()), int(df['age'].max()))
)

# Apply filters
filtered_df = df[
    (df['product_category'].isin(category)) &
    (df['gender'].isin(gender)) &
    (df['city'].isin(city)) &
    (df['membership_tier'].isin(membership)) &
    (df['payment_method'].isin(payment)) &
    (df['age'].between(age_range[0], age_range[1]))
]

st.write(f"📊 Showing {len(filtered_df)} records")

# =========================
# 📊 KPI CARDS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Revenue", f"{filtered_df['total_spend'].sum():,.0f}")
col2.metric("👥 Customers", filtered_df['customer_id'].nunique())
col3.metric("📈 Avg Spend", f"{filtered_df['total_spend'].mean():,.2f}")

# =========================
# 🗺️ MAP
# =========================
st.subheader("🗺️ Customer Map")

if not filtered_df.empty:
    map_df = filtered_df.dropna(subset=['lat', 'lon'])

    if not map_df.empty:
        city_summary = map_df.groupby(['city', 'lat', 'lon'])['total_spend'].sum().reset_index()

        fig_map = px.scatter_mapbox(
            city_summary,
            lat="lat",
            lon="lon",
            size="total_spend",
            color="total_spend",
            hover_name="city",
            zoom=4
        )

        fig_map.update_layout(mapbox_style="open-street-map")

        st.plotly_chart(fig_map, use_container_width=True, key="map_chart")

# =========================
# 📄 DATA
# =========================
st.subheader("📄 Data")
st.dataframe(filtered_df)

st.download_button(
    "📥 Download Filtered Data",
    filtered_df.to_csv(index=False),
    "filtered_data.csv"
)

# =========================
# 📊 TABS
# =========================
tabs = st.tabs(["📊 Basic", "📈 Advanced", "📉 Distribution", "🧠 Insights"])

# =========================
# 📊 BASIC
# =========================
with tabs[0]:
    if not filtered_df.empty:
        cat_data = filtered_df.groupby('product_category')['total_spend'].sum().reset_index()

        st.plotly_chart(px.bar(cat_data, x='product_category', y='total_spend'), key="bar_chart")
        st.plotly_chart(px.line(cat_data, x='product_category', y='total_spend'), key="line_chart")
        st.plotly_chart(px.area(cat_data, x='product_category', y='total_spend'), key="area_chart")
        st.plotly_chart(px.pie(cat_data, names='product_category', values='total_spend', hole=0.4), key="donut_chart")

# =========================
# 📈 ADVANCED
# =========================
with tabs[1]:
    if not filtered_df.empty:
        st.plotly_chart(px.scatter(filtered_df, x='age', y='total_spend', color='gender'), key="scatter_chart")

        st.plotly_chart(px.scatter(
            filtered_df,
            x='age',
            y='total_spend',
            size='total_spend',
            color='product_category'
        ), key="bubble_chart")

        st.plotly_chart(px.treemap(filtered_df, path=['product_category', 'city'], values='total_spend'), key="treemap_chart")

        radar = filtered_df.groupby('product_category')['total_spend'].mean().reset_index()

        st.plotly_chart(px.line_polar(radar, r='total_spend', theta='product_category', line_close=True), key="radar_chart")

# =========================
# 📉 DISTRIBUTION
# =========================
with tabs[2]:
    if not filtered_df.empty:
        st.plotly_chart(px.histogram(filtered_df, x='total_spend'), key="hist_chart")
        st.plotly_chart(px.box(filtered_df, x='gender', y='total_spend'), key="box_chart")

        pivot = filtered_df.pivot_table(
            values='total_spend',
            index='city',
            columns='product_category',
            aggfunc='sum'
        ).fillna(0)

        st.plotly_chart(px.imshow(pivot), key="heatmap_chart")

# =========================
# 🧠 INSIGHTS
# =========================
with tabs[3]:
    if not filtered_df.empty:
        stacked = filtered_df.groupby(['product_category', 'gender'])['total_spend'].sum().reset_index()

        st.plotly_chart(px.bar(stacked, x='product_category', y='total_spend', color='gender'), key="stacked_chart")

        water = filtered_df.groupby('product_category')['total_spend'].sum().reset_index()

        st.plotly_chart(px.bar(water, x='product_category', y='total_spend'), key="waterfall_chart")

        gantt_df = filtered_df[['customer_id', 'age']].head(10)
        gantt_df['Start'] = pd.Timestamp('2024-01-01')
        gantt_df['End'] = pd.Timestamp('2024-01-01') + pd.to_timedelta(gantt_df['age'], unit='D')

        st.plotly_chart(px.timeline(gantt_df, x_start="Start", x_end="End", y="customer_id"), key="gantt_chart")

# =========================
# 🏆 TOP CUSTOMERS
# =========================
if not filtered_df.empty:
    st.subheader("🏆 Top 10 Customers")
    st.dataframe(filtered_df.sort_values(by='total_spend', ascending=False).head(10))

# =========================
# 🤖 ML
# =========================
st.subheader("🤖 Machine Learning")

if st.button("Train Model"):
    model, acc = train_model()
    st.success(f"Model Accuracy: {acc:.2f}")

# =========================
# 🔮 PREDICT
# =========================
st.subheader("🔮 Predict Customer Value")

age = st.number_input("Age", 18, 70)
spend = st.number_input("Total Spend", 0, 100000)

if st.button("Predict"):
    threshold = df['total_spend'].quantile(0.75)

    if spend >= threshold:
        st.success("💰 High Value Customer")
    else:
        st.warning("Normal Customer")