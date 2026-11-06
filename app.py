import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Palo Alto Networks - Attrition Analysis", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Attrition_Flag"] = (df["Attrition"] == "Yes").astype(int)
    df["Tenure_Group"] = pd.cut(
        df["YearsAtCompany"],
        bins=[-1, 2, 5, 10, 50],
        labels=["0-2 Years", "3-5 Years", "6-10 Years", "10+ Years"]
    )
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 70],
        labels=["18-25", "26-35", "36-45", "46+"]
    )
    return df

df = load_data()

st.title("📊 Workforce Attrition & Risk Hotspot Analysis")
st.markdown("**Palo Alto Networks | HR Analytics Dashboard**")

# Sidebar Filters
st.sidebar.header("Filter Workforce Data")
dept_filter = st.sidebar.multiselect(
    "Select Department",
    options=df["Department"].unique(),
    default=df["Department"].unique()
)
filtered_df = df[df["Department"].isin(dept_filter)]

# KPIs
total_emp = len(filtered_df)
attrition_count = filtered_df["Attrition_Flag"].sum()
attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0

early_df = filtered_df[filtered_df["YearsAtCompany"] <= 2]
early_rate = (early_df["Attrition_Flag"].mean() * 100) if len(early_df) > 0 else 0

ot_df = filtered_df[filtered_df["OverTime"] == "Yes"]
ot_rate = (ot_df["Attrition_Flag"].mean() * 100) if len(ot_df) > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", f"{total_emp:,}")
col2.metric("Overall Attrition Rate", f"{attrition_rate:.1f}%", f"{attrition_count} Left", delta_color="inverse")
col3.metric("Early-Tenure Attrition (≤2 Yrs)", f"{early_rate:.1f}%")
col4.metric("Overtime Worker Attrition", f"{ot_rate:.1f}%")

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Attrition Overview",
    "2️⃣ Department & Role Hotspots",
    "3️⃣ Demographic Explorer",
    "4️⃣ Tenure & Workload Analysis"
])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            filtered_df, names="Attrition", title="Overall Workforce Retention vs. Attrition",
            color="Attrition", color_discrete_map={"No": "#2E86C1", "Yes": "#E74C3C"}, hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        dept_attr = filtered_df.groupby("Department")["Attrition_Flag"].mean().reset_index()
        dept_attr["Attrition_Rate"] = dept_attr["Attrition_Flag"] * 100
        fig_dept = px.bar(
            dept_attr, x="Department", y="Attrition_Rate", title="Attrition Rate by Department (%)",
            text_auto=".1f", color="Attrition_Rate", color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_dept, use_container_width=True)

with tab2:
    role_attr = filtered_df.groupby(["Department", "JobRole"])["Attrition_Flag"].agg(["count", "mean"]).reset_index()
    role_attr["Attrition_Rate"] = role_attr["mean"] * 100
    role_attr = role_attr.sort_values("Attrition_Rate", ascending=True)
    fig_role = px.bar(
        role_attr, x="Attrition_Rate", y="JobRole", color="Department", orientation="h",
        title="Attrition Rate by Job Role & Department (Risk Hotspots)", text_auto=".1f"
    )
    st.plotly_chart(fig_role, use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)
    with c1:
        age_attr = filtered_df.groupby("Age_Group", observed=False)["Attrition_Flag"].mean().reset_index()
        age_attr["Attrition_Rate"] = age_attr["Attrition_Flag"] * 100
        fig_age = px.bar(
            age_attr, x="Age_Group", y="Attrition_Rate", title="Attrition Rate by Age Group (%)",
            text_auto=".1f", color_discrete_sequence=["#8E44AD"]
        )
        st.plotly_chart(fig_age, use_container_width=True)
    with c2:
        fig_inc = px.box(
            filtered_df, x="Attrition", y="MonthlyIncome", color="Attrition",
            title="Monthly Income Distribution by Attrition Status",
            color_discrete_map={"No": "#2E86C1", "Yes": "#E74C3C"}
        )
        st.plotly_chart(fig_inc, use_container_width=True)

with tab4:
    c1, c2 = st.columns(2)
    with c1:
        ten_attr = filtered_df.groupby("Tenure_Group", observed=False)["Attrition_Flag"].mean().reset_index()
        ten_attr["Attrition_Rate"] = ten_attr["Attrition_Flag"] * 100
        fig_ten = px.bar(
            ten_attr, x="Tenure_Group", y="Attrition_Rate", title="Attrition Rate by Company Tenure (%)",
            text_auto=".1f", color_discrete_sequence=["#D35400"]
        )
        st.plotly_chart(fig_ten, use_container_width=True)
    with c2:
        ot_attr = filtered_df.groupby("OverTime")["Attrition_Flag"].mean().reset_index()
        ot_attr["Attrition_Rate"] = ot_attr["Attrition_Flag"] * 100
        fig_ot = px.bar(
            ot_attr, x="OverTime", y="Attrition_Rate", title="Impact of Overtime on Attrition (%)",
            text_auto=".1f", color="OverTime", color_discrete_map={"No": "#27AE60", "Yes": "#C0392B"}
        )
        st.plotly_chart(fig_ot, use_container_width=True)