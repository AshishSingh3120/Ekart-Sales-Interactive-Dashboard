import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Reading CSV file
df = pd.read_csv(
    r'C:\Users\Ashish Singh\Desktop\New folder\Ekart data\Sales_Data_10k.csv'
)
# Page configuration
st.set_page_config(
    page_title="Ekart Sales Dashboard",
    layout="wide"
)
# Custom CSS to remove extra top padding and prevent clipping
st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Dashboard Header
col1, col2,= st.columns([1, 5,])

with col1:
    try:
        image = Image.open(
            r'C:\Users\Ashish Singh\Desktop\New folder\Ekart data\img1.png'
        )
        st.image(image, width=150)
    except Exception:
        st.write("📦**Ekart**")


    # Fixed missing '<' in <center> tag
    html_title = """
        <style>
        .title-test {
            color: white;
            font-weight: bold;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        </style>
        <h1 class="title-test">Ekart Sales Dashboard</h1>
    """
    with col2:
      st.markdown(html_title, unsafe_allow_html=True)
      #For Date STamp
    Col3=st.columns([1])[0]# Create a single column for the date box
with Col3:
    last_updated= datetime.now().strftime("%d %B %Y, %I:%M %p")
    st.markdown(
        f"<div style='font-size: 13px; color: #A0A0A0; line-height: 1.4;'>"
        f"<strong>Last updated:</strong><br>{last_updated}"
        f"</div>",
        unsafe_allow_html=True
    )
st.divider()

# Calculate Total Sales & Region-Wise Grouped Data
total_sales = df["Net_Sales"].sum()

# Format to 2 decimal places -> "$15.31M"
formatted_sales = f"${total_sales / 1_000_000:.2f}M"

total_profit = df["Profit"].sum()
formatted_total_profit = f"${total_profit / 1_000_000:.2f}M"
Avg_order_value = total_sales / df['Order_ID'].nunique()  # Calculate Average Order Value   
Total_orders = df['Order_ID'].nunique()  # Calculate Total Orders
formatted_Total_orders = f"{Total_orders/1_000:.2f}K"
# Top Row: Date + Total Sales KPI Card
kpi1, kpi2, kpi3, kpi4,kpi5 = st.columns([1,1, 1, 1,1])
with kpi1:
    st.metric(
        label="Total Revenue",
        value=f"${formatted_sales}"
    )
with kpi2:
    st.metric(
        label="Total Orders",
        value=f"{formatted_Total_orders}"
    )
with kpi3:
    st.metric(
        label="Total Customers",
        value=f"{df['Customer_ID'].nunique():,}"
    )
with kpi4:
    st.metric(
        label="Total Profit",
        value=f"{formatted_total_profit}"
    )    
    with kpi5:
     st.metric(
        label="Average Order Value ($)", 
        value=f"${Avg_order_value:,.2f}"
    ) 
# Prepare chronological monthly sales data first
df["Order_Date"] = pd.to_datetime(df["Order_Date"], dayfirst=True, errors="coerce")
df["month_sort"] = df["Order_Date"].dt.to_period("M")
df["month_year"] = df["Order_Date"].dt.strftime("%b'%y")

result = (
    df.groupby(["month_sort", "month_year"])[["Net_Sales", "Profit"]]
    .sum()
    .reset_index()
    .sort_values("month_sort")
)

# Create 2 equal horizontal columns
import plotly.graph_objects as go

ch1 = st.columns([1])[0]  # Create a single column for the chart
with ch1:
    fig1 = go.Figure()

    # 1. Bottom line (Profit) - fills down to y=0 (the bottom axis)
    fig1.add_trace(
        go.Scatter(
            x=result["month_year"],
            y=result["Profit"],
            name="Profit",
            mode="lines+markers",
            line=dict(color="#00CC96", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 204, 150, 0.2)",  # Greenish fill under Profit
        )
    )

    # 2. Top line (Net Sales) - fills down to the Profit line
    fig1.add_trace(
        go.Scatter(
            x=result["month_year"],
            y=result["Net_Sales"],
            name="Revenue",
            mode="lines+markers",
            line=dict(color="#636EFA", width=2),
            fill="tonexty",
            fillcolor="rgba(99, 110, 250, 0.2)",  # Bluish fill between Profit & Net Sales
        )
    )

    fig1.update_layout(
        title="Monthly Sales & Profit Trend",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        legend_title="Metric",
        template="plotly_dark",
        height=450,
        margin=dict(l=60, r=20, t=60, b=60),
    )
    fig1.update_xaxes(
        tickmode="array",
        tickvals=result["month_year"],
        ticktext=result["month_year"],
        tickangle=-45,
    )
    st.plotly_chart(fig1, use_container_width=True)
view1, dwn1 = st.columns([1.4, 0.8], vertical_alignment="center")
with view1:
    with st.expander("View Full Monthly Sales & Profit Trend Report"):
        st.dataframe(result[["month_year", "Net_Sales", "Profit"]], use_container_width=True, hide_index=True)

with dwn1:
    st.download_button(
        label="Get Data",
        data=result[["month_year", "Net_Sales"]].to_csv(index=False).encode("utf-8"),
        file_name="Monthly_Sales_Trend.csv",
        mime="text/csv",
        use_container_width=True,
        key="btn_monthly_csv"
    )
    # Define order_status_df BEFORE creating ch2, ch3
order_status_df = (
    df.groupby("Order_Status")
    .agg(Total_Orders=("Order_ID", "nunique"))
    .reset_index()
    .sort_values("Total_Orders", ascending=False)
)
# Create 2 columns side-by-side in one line
ch2, ch3 = st.columns([1.3, 1])
region_sales = (
    df.groupby("Region")
    .agg(
        Revenue =("Net_Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
    .sort_values("Revenue", ascending=False)
)# Left Column: Grouped Bar Chart
with ch2:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=region_sales["Region"],
            y=region_sales["Revenue"],
            name="Total Sales ($)",
            text=region_sales["Revenue"],
            texttemplate="%{text:.2s}",
            textposition="outside",
            marker_color="#636EFA",
            offsetgroup=0
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=region_sales["Region"],
            y=region_sales["Profit"],
            name="Total Profit",
            text=region_sales["Profit"],
            texttemplate="%{text:.2s}",
            textposition="outside",
            marker_color="#00CC96",
            offsetgroup=1
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Revenue & Profit by Region",
        barmode="group",
        template="plotly_dark",
        height=460,
        margin=dict(l=60, r=60, t=80, b=60),
        xaxis_title="Region",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Extra headroom so '5.5M' and '3,557' labels at the top don't touch the top axis line
    fig.update_yaxes(title_text="Total Sales ($)", secondary_y=False, range=[0, region_sales["Revenue"].max() * 1.15])
    fig.update_yaxes(title_text="Total Profit", secondary_y=True, showgrid=False, range=[0, region_sales["Profit"].max() * 1.15])

    st.plotly_chart(fig, use_container_width=True)

# Right Column: Pie / Donut Chart (MUST be at the exact same indent level as `with ch2:`)
with ch3:
    fig_status = px.pie(
        order_status_df,
        names="Order_Status",
        values="Total_Orders",
        title="Orders by Status",
        hole=0.45,
        template="plotly_dark",
        height=460
    )
    fig_status.update_traces(textposition="inside", textinfo="percent+label")
    fig_status.update_layout(
        margin=dict(l=20, r=20, t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_status, use_container_width=True)
# Bottom Section: Full Data Table & Download Button
view2, dwn2, view3, dwn3 = st.columns([1.4, 0.8, 1.4, 0.8], vertical_alignment="center")

with view2:
    with st.expander("View Full Region Wise Sales Report"):
        st.dataframe(region_sales, use_container_width=True, hide_index=True)

with dwn2:
    st.download_button(
        label="Get Data",
        data=result.drop(columns=["month_sort"], errors="ignore").to_csv(index=False).encode("utf-8"),
        file_name="Monthly_Sales_Trend.csv",
        mime="text/csv",
        key="btn_monthly_csv_unique_2"
    )
with view3:
    with st.expander("Order_Status_Distribution Report"):
        st.dataframe( order_status_df, use_container_width=True, hide_index=True)

with dwn3:
    st.download_button(
        label="Get Data",
        data= order_status_df.to_csv(index=False).encode("utf-8"),
        file_name="Order_Status_Distribution.csv",
        mime="text/csv",
        use_container_width=True,
        key="btn_order_status_download"
    )
   # Make sure this line is NOT indented inside another 'with' block!
ch4,  = st.columns([1.4], vertical_alignment="center")

Categorywise_sales = (
    df.groupby("Product_Category")
    .agg(
        Revenue=("Net_Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
    .sort_values(by="Revenue", ascending=True)  # Highest category at top
)

with ch4:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=Categorywise_sales["Profit"],
            y=Categorywise_sales["Product_Category"],
            orientation="h",
            name="Total Profit ($)",
            text=Categorywise_sales["Profit"],
            texttemplate="%{text:.2s}",
            textposition="outside",
            marker_color="#00CC96",
        )
    )

    fig.add_trace(
        go.Bar(
            x=Categorywise_sales["Revenue"],
            y=Categorywise_sales["Product_Category"],
            orientation="h",
            name="Revenue ($)",
            text=Categorywise_sales["Revenue"],
            texttemplate="%{text:.2s}",
            textposition="outside",
            marker_color="#636EFA",
        )
    )

    fig.update_layout(
        title=dict(text="Revenue & Profit by Category", y=0.95),
        barmode="group",
        template="plotly_dark",
        height=460,
        margin=dict(l=140, r=50, t=90, b=50),  # Extra top & left margin prevents overlap
        xaxis_title="Amount ($)",
        yaxis_title="Product Category",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
    )

    fig.update_xaxes(range=[0, Categorywise_sales["Revenue"].max() * 1.18])

    st.plotly_chart(fig, use_container_width=True)
# Bottom Section: Full Data Table & Download Button
view4, dwn4 = st.columns([1.4, 0.8], vertical_alignment="center")
with view4:
    with st.expander("View Categorywise_sales Report"):
        st.dataframe(Categorywise_sales, use_container_width=True, hide_index=True)

with dwn4:
    st.download_button(
        label="Get Data",
        data=Categorywise_sales.to_csv(index=False).encode("utf-8"),
        file_name="Categorywise_Sales.csv",
        mime="text/csv",
        key="btn_categorywise_sales_download" )
import plotly.graph_objects as go

# 1. Aggregate total sales by Product and sort descending (largest at top)
product_sales = (
    df.groupby("Product_Name")["Net_Sales"]  # <-- Replace "Product_Name" if your column name differs
    .sum()
    .reset_index()
    .sort_values(by="Net_Sales", ascending=False)
)

top_5_products = product_sales.head(5)
bottom_5_products = product_sales.tail(5)

# 2. Create two side-by-side columns
col_top, col_bottom = st.columns(2)

with col_top:
    fig_top = go.Figure(
        go.Funnel(
            y=top_5_products["Product_Name"],
            x=top_5_products["Net_Sales"],
            textinfo="value+percent initial",
            texttemplate="%{x:.2s} (%{percentInitial:.1%})",
            marker=dict(color="#636EFA"),
            connector=dict(line=dict(color="rgba(255, 255, 255, 0.2)", width=1)),
        )
    )
    fig_top.update_layout(
        title="Top 5 Products by Revenue",
        template="plotly_dark",
        height=420,
        margin=dict(l=150, r=30, t=60, b=40),  # Extra left margin for longer product names
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col_bottom:
    fig_bottom = go.Figure(
        go.Funnel(
            y=bottom_5_products["Product_Name"],
            x=bottom_5_products["Net_Sales"],
            textinfo="value+percent initial",
            texttemplate="%{x:.2s} (%{percentInitial:.1%})",
            marker=dict(color="#EF553B"),
            connector=dict(line=dict(color="rgba(255, 255, 255, 0.2)", width=1)),
        )
    )
    fig_bottom.update_layout(
        title="Bottom 5 Products by Revenue",
        template="plotly_dark",
        height=420,
        margin=dict(l=150, r=30, t=60, b=40),
    )
    st.plotly_chart(fig_bottom, use_container_width=True)