import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

# Palette
PURPLE   = "#7030A0"
PURPLES  = ["#7030A0","#9B59B6","#C39BD3","#D7BDE2","#EAD7F7",
            "#5B2C6F","#A569BD","#884EA0","#76448A","#6C3483",
            "#BDC3C7","#ABB2B9","#7F8C8D","#5D6D7E","#34495E",
            "#F39C12","#E67E22","#E74C3C","#27AE60","#2980B9"]


def load(file_path):
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        st.stop()

    tx = pd.read_excel(file_path, sheet_name="Transactions")
    tx["Remarks"] = tx["Remarks"].astype(str)
    cats = pd.read_excel(file_path, sheet_name="Categories", header=None)
    cats.columns = ["Type", "Spend", "Percent"]
    cats = cats.iloc[1:]
    cats = cats[cats["Type"] != "Total"]
    cats["Spend"] = pd.to_numeric(cats["Spend"], errors="coerce").fillna(0)
    cats = cats[cats["Spend"] > 0].reset_index(drop=True)

    tx["Date"] = pd.to_datetime(tx["Date"])
    tx["Spend"] = pd.to_numeric(tx["Spend"], errors="coerce").fillna(0)
    return tx, cats


def get_prev_month(month, year):
    current_date = datetime.strptime(f"01-{month}-{year}", "%d-%B-%Y")
    prev_date = (current_date - timedelta(days=1)).strftime("%B-%Y")
    prev_month, prev_year = prev_date.split("-")
    return prev_month, prev_year


def metric_row(tx, cats, prev_tx):
    total   = tx["Spend"].sum()
    top_cat = cats.loc[cats["Spend"].idxmax(), "Type"] if not cats.empty else "—"
    avg_day = tx.groupby("Date")["Spend"].sum().mean()
    txn_cnt = len(tx)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💸 Total Spent", f"₹{total:,.0f}")
    c2.metric("🔥 Top Category", top_cat)
    c3.metric("📅 Avg Daily Spend", f"₹{avg_day:,.0f}")
    c4.metric("🧾 Transactions", txn_cnt)

    if prev_tx is not None:
        salary_idx = prev_tx[prev_tx["Description"].str.contains("salary", case=False, na=False)].index
        next_salary_idx = tx[tx["Description"].str.contains("salary", case=False, na=False)].index
        if not salary_idx.empty and not next_salary_idx.empty:
            salary = float(prev_tx.loc[salary_idx[0], "Remarks"])
            total_expense = prev_tx.loc[salary_idx[0] + 1:, "Spend"].sum()
            total_expense += tx.loc[:next_salary_idx[0], "Spend"].sum()
            diff = salary - total_expense
            if diff > 0:
                c5.metric("💰 Budget Status", f":green[▲ ₹{abs(diff):,.0f}]")
            elif diff < 0:
                c5.metric("💰 Budget Status", f":red[▼ ₹{abs(diff):,.0f}]")
            else:
                c5.metric("💰 Budget Status", f":blue[‐ ₹{abs(diff):,.0f}]")


def category_treemap(tx):
    df = tx.copy()
    df["Type"] = df["Type"].fillna("Others")
    df["Description"] = df["Description"].fillna("Unknown")
    df = df[df["Spend"] > 0]

    fig = px.treemap(
        df,
        path=["Type", "Description"],
        values="Spend",
        color="Spend",
        color_continuous_scale=[[0, "#F3E5F5"], [1, PURPLE]],
        hover_data={"Spend": ":,.0f"}
    )
    fig.update_traces(
        texttemplate="<b>%{label}</b><br>₹%{value:,.0f}",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"
    )
    fig.update_layout(
        title=dict(text="Category Treemap", font=dict(size=16, color=PURPLE)),
        margin=dict(t=50, b=10, l=10, r=10),
        height=500,
        coloraxis_showscale=False
    )
    return fig


def spend_by_category_bar_graph(cats):
    cats_sorted = cats.sort_values("Spend", ascending=True)
    fig = go.Figure(go.Bar(
        x=cats_sorted["Spend"],
        y=cats_sorted["Type"],
        orientation="h",
        marker=dict(
            color=cats_sorted["Spend"],
            colorscale=[[0, "#D7BDE2"], [1, PURPLE]],
            line=dict(width=0)
        ),
        text=cats_sorted["Spend"].apply(lambda x: f"₹{x:,.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Category Breakdown", font=dict(size=16, color=PURPLE)),
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False),
        margin=dict(t=50, b=10, l=10, r=80),
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def daily_spending_trend(tx):
    daily = tx.groupby("Date")["Spend"].sum().reset_index()
    daily["7d_avg"] = daily["Spend"].rolling(7, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["Date"], y=daily["Spend"],
        name="Daily Spend",
        marker_color="#D7BDE2",
        hovertemplate="%{x|%d %b}<br>₹%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["7d_avg"],
        name="7-day Avg",
        line=dict(color=PURPLE, width=2.5),
        hovertemplate="%{x|%d %b}<br>Avg ₹%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Daily Spending Trend", font=dict(size=16, color=PURPLE)),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eee"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=10, l=10, r=10),
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        barmode="overlay"
    )
    return fig


def source_split_pie_chart(tx):
    src = tx.groupby("Source")["Spend"].sum().reset_index()
    fig = px.pie(
        src, names="Source", values="Spend",
        color_discrete_sequence=PURPLES,
        hole=0.4
    )
    fig.update_traces(
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"
    )
    fig.update_layout(
        title=dict(text="Spend by Source", font=dict(size=16, color=PURPLE)),
        showlegend=False,
        margin=dict(t=50, b=10, l=10, r=10),
        height=320
    )
    return fig


def parents_family_distribution_pie_chart(cats):
    PARENTS_CATS = {"Bills (P)", "Parents", "Medicines (P)"}
    FAMILY_CATS  = {"Cash Withdrawal", "EMI", "Rent", "Food", "Entertainment",
                    "Groceries", "Bills", "Personal", "Shopping", "Investment",
                    "Insurance", "Fuel", "Travel", "Medicines"}

    df = cats.copy()
    df["Group"] = df["Type"].apply(
        lambda x: "Parents" if x in PARENTS_CATS else "Family" if x in FAMILY_CATS else None
    )
    df = df[df["Group"].notna()].groupby("Group")["Spend"].sum().reset_index()

    fig = go.Figure(go.Pie(
        labels=df["Group"],
        values=df["Spend"],
        hole=0.55,
        marker=dict(colors=PURPLES[:2], line=dict(color="#1a1a2e", width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Parents vs Family Spending", font=dict(size=16, color=PURPLE)),
        showlegend=False,
        margin=dict(t=50, b=10, l=10, r=10),
        height=350
    )
    return fig


def top_transactions(tx, n=8):
    top = tx.nlargest(n, "Spend")[["Date", "Description", "Type", "Source", "Spend"]].copy()
    top["Date"] = top["Date"].dt.strftime("%d %b")
    top["Spend"] = top["Spend"].apply(lambda x: f"₹{x:,.0f}")
    top["Description"] = top["Description"].str[:50]
    return top


def cumulative(tx):
    daily = tx.groupby("Date")["Spend"].sum().reset_index().sort_values("Date")
    daily["Cumulative"] = daily["Spend"].cumsum()

    fig = go.Figure(go.Scatter(
        x=daily["Date"], y=daily["Cumulative"],
        fill="tozeroy",
        fillcolor="rgba(112,48,160,0.15)",
        line=dict(color=PURPLE, width=2.5),
        hovertemplate="%{x|%d %b}<br>Total so far: ₹%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text="Cumulative Spend Over Month", font=dict(size=16, color=PURPLE)),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eee"),
        margin=dict(t=50, b=10, l=10, r=10),
        height=300,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# Main function
def visualize_dashboard(year, month):
    file_path = f"{year}/{month} Expense Tracker.xlsx"
    tx, cats = load(file_path)

    prev_month, prev_year = get_prev_month(month, year)
    prev_file_path = f"{prev_year}/{prev_month} Expense Tracker.xlsx"
    if os.path.exists(prev_file_path):
        prev_tx, _ = load(prev_file_path)
    else:
        prev_tx = None

    st.markdown(f"### 📊 {month} {year} — Expense Dashboard")
    st.markdown("---")

    # Row 0 — KPI metrics
    metric_row(tx, cats, prev_tx)
    st.markdown("---")

    # Row 1 — Heatmap for category breakdown
    st.plotly_chart(category_treemap(tx), width="stretch")
    
    # Row 2 — Bar chart with category breakdown
    st.plotly_chart(spend_by_category_bar_graph(cats), width="stretch")

    # Row 3 — Daily trend full width
    st.plotly_chart(daily_spending_trend(tx), width="stretch")

    # Row 4 — Source split + Cumulative
    st.plotly_chart(cumulative(tx), width="stretch")

    # Row 5 - Source split + Parents and Family Distribution
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(source_split_pie_chart(tx), width="stretch")
    with col2:
        st.plotly_chart(parents_family_distribution_pie_chart(cats), width="stretch")

    # Row 6 — Top transactions table
    st.markdown("#### 🔥 Top Transactions")
    top = top_transactions(tx)
    st.dataframe(top, width="stretch", hide_index=True)

    # Row 7 — Raw data expander
    with st.expander("📋 View All Transactions"):
        st.dataframe(tx, width="stretch", hide_index=True)