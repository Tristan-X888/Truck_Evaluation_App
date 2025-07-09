
import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="Truck Evaluation Dashboard", layout="wide")

st.title("🚚 Advanced Truck Evaluation Dashboard")
st.markdown("**Decide whether to KEEP, SELL, or INSPECT trucks based on operational, financial, and mechanical data.**")

uploaded_files = st.file_uploader("📂 Upload All Required Excel Files", type="xlsx", accept_multiple_files=True)

if uploaded_files:
    file_dict = {f.name: f for f in uploaded_files}

    try:
        maintenance = pd.read_excel(file_dict["maintenancepo-truck.xlsx"])
        finance = pd.read_excel(file_dict["truck-finance.xlsx"])
        distance = pd.read_excel(file_dict["vehicle-distance-traveled.xlsx"])
        odometer = pd.read_excel(file_dict["truck-odometer-data-week-.xlsx"])
        stub = pd.read_excel(file_dict["stub-data.xlsx"])
        truck_paper = pd.read_excel(file_dict["truck-paper.xlsx"])

        def clean_unit_id(x):
            if pd.isna(x): return None
            return x.strip().replace("SPOT-", "").upper().replace("  ", " ").replace("-", " ")

        maint_summary = (
            maintenance.groupby("unit_id")
            .agg(total_repairs=("amount", "count"),
                 total_company_cost=("company_covered", "sum"),
                 avg_cost_per_repair=("company_covered", "mean"))
            .reset_index()
        )
        maint_summary["unit_id_clean"] = maint_summary["unit_id"].apply(clean_unit_id)

        finance["ownership_type"] = finance["ownership_type"].str.lower().str.strip()
        finance_summary = finance[["unit_id", "ownership_type", "monthly_payment",
                                   "balloon_payment", "status", "purchase_amount"]].copy()
        finance_summary["unit_id_clean"] = finance_summary["unit_id"].apply(clean_unit_id)
        finance_summary["ownership_class"] = finance_summary["ownership_type"].apply(
            lambda x: "owned" if "own" in str(x) else "leased/financed")
        finance_summary["est_remaining_payments"] = finance_summary["monthly_payment"].apply(
            lambda x: x * 12 if x and x > 0 else 0)
        finance_summary["total_estimated_liability"] = finance_summary["est_remaining_payments"] + finance_summary["balloon_payment"].fillna(0)

        distance_clean = distance.dropna(subset=["unit_id", "distance"])
        distance_summary = (
            distance_clean.groupby("unit_id")
            .agg(total_distance_km=("distance", "sum"),
                 avg_daily_distance_km=("distance", "mean"),
                 data_points=("distance", "count"))
            .reset_index()
        )
        distance_summary["unit_id_clean"] = distance_summary["unit_id"].apply(clean_unit_id)

        combined = (
            maint_summary.merge(finance_summary, on="unit_id_clean", how="outer")
                         .merge(distance_summary, on="unit_id_clean", how="outer")
        )

        def evaluate_truck(row):
            if row["total_company_cost"] > 30000 and row["total_distance_km"] < 100000:
                return "SELL"
            elif row["total_company_cost"] < 15000 and row["ownership_class"] == "owned":
                return "KEEP"
            elif row["total_distance_km"] > 200000 and row["total_company_cost"] < 20000:
                return "KEEP"
            else:
                return "INSPECT"

        combined["evaluation_decision"] = combined.apply(evaluate_truck, axis=1)

        st.success("✅ Evaluation completed! Use filters and charts below to explore the data.")

        # Sidebar Filters
        st.sidebar.header("🔎 Filter Options")
        decision_filter = st.sidebar.multiselect("Filter by Decision", options=combined["evaluation_decision"].unique(), default=combined["evaluation_decision"].unique())
        ownership_filter = st.sidebar.multiselect("Filter by Ownership", options=combined["ownership_class"].unique(), default=combined["ownership_class"].unique())

        filtered = combined[
            (combined["evaluation_decision"].isin(decision_filter)) &
            (combined["ownership_class"].isin(ownership_filter))
        ]

        st.dataframe(filtered.sort_values(by="evaluation_decision"))

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            pie_chart = px.pie(filtered, names="evaluation_decision", title="Truck Decision Distribution")
            st.plotly_chart(pie_chart, use_container_width=True)

        with col2:
            bar_chart = px.bar(filtered, x="unit_id_clean", y="total_company_cost", color="evaluation_decision",
                               title="Repair Cost by Truck", labels={"unit_id_clean": "Truck"})
            st.plotly_chart(bar_chart, use_container_width=True)

        st.line_chart(filtered.set_index("unit_id_clean")[["total_company_cost", "total_distance_km"]])

        # ✅ Correct Excel Export
        st.markdown("### 📥 Export Filtered Results")
        buffer = io.BytesIO()
        filtered.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)

        st.download_button(
            label="Download as Excel",
            data=buffer,
            file_name="filtered_truck_evaluation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
