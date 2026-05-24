import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time

DATA_FILE = Path("flight_schedule.csv")
COLUMNS = [
    "Flight No",
    "Airline",
    "From",
    "To",
    "Operation",
    "Scheduled Time",
    "Status",
    "Gate",
    "Remarks",
]


def load_data() -> pd.DataFrame:
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


def add_flight(record: dict) -> None:
    df = load_data()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    save_data(df)


st.set_page_config(page_title="Flight Schedule Manager", page_icon="✈️", layout="wide")

st.title("✈️ Flight Takeoff & Landing Schedule Manager")
st.caption("Maintain flight departure and arrival schedules using Python and Streamlit.")

menu = st.sidebar.radio(
    "Menu",
    ["Dashboard", "Add Flight", "View / Edit Schedule", "Delete Flight"],
)

df = load_data()

if menu == "Dashboard":
    st.subheader("Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Flights", len(df))
    col2.metric("Takeoffs", len(df[df["Operation"] == "Takeoff"]) if not df.empty else 0)
    col3.metric("Landings", len(df[df["Operation"] == "Landing"]) if not df.empty else 0)

    st.divider()

    if df.empty:
        st.info("No flight records yet. Add your first flight from the sidebar.")
    else:
        st.subheader("Upcoming Schedule")
        df_display = df.copy()
        df_display["Scheduled Time"] = pd.to_datetime(df_display["Scheduled Time"], errors="coerce")
        df_display = df_display.sort_values("Scheduled Time")
        st.dataframe(df_display, use_container_width=True)

elif menu == "Add Flight":
    st.subheader("Add Flight")

    with st.form("add_flight_form"):
        col1, col2 = st.columns(2)

        with col1:
            flight_no = st.text_input("Flight No", placeholder="PK-301")
            airline = st.text_input("Airline", placeholder="PIA")
            origin = st.text_input("From", placeholder="Karachi")
            destination = st.text_input("To", placeholder="Lahore")
            operation = st.selectbox("Operation", ["Takeoff", "Landing"])

        with col2:
            schedule_date = st.date_input("Date", value=date.today())
            schedule_time = st.time_input("Time", value=time(12, 0))
            status = st.selectbox("Status", ["Scheduled", "Delayed", "Boarding", "Departed", "Landed", "Cancelled"])
            gate = st.text_input("Gate", placeholder="A1")
            remarks = st.text_area("Remarks", placeholder="Optional notes")

        submitted = st.form_submit_button("Save Flight")

        if submitted:
            if not flight_no or not airline or not origin or not destination:
                st.error("Please fill Flight No, Airline, From, and To fields.")
            else:
                scheduled_dt = datetime.combine(schedule_date, schedule_time)
                record = {
                    "Flight No": flight_no.upper(),
                    "Airline": airline,
                    "From": origin,
                    "To": destination,
                    "Operation": operation,
                    "Scheduled Time": scheduled_dt.strftime("%Y-%m-%d %H:%M"),
                    "Status": status,
                    "Gate": gate,
                    "Remarks": remarks,
                }
                add_flight(record)
                st.success("Flight added successfully.")

elif menu == "View / Edit Schedule":
    st.subheader("View / Edit Schedule")

    if df.empty:
        st.info("No records available.")
    else:
        operation_filter = st.selectbox("Filter by operation", ["All", "Takeoff", "Landing"])
        status_filter = st.selectbox("Filter by status", ["All"] + sorted(df["Status"].dropna().unique().tolist()))

        filtered_df = df.copy()
        if operation_filter != "All":
            filtered_df = filtered_df[filtered_df["Operation"] == operation_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]

        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            num_rows="dynamic",
        )

        if st.button("Save Edited Schedule"):
            # Simple save: replaces full file only when no filter is active.
            # For filtered editing, keep this app simple and ask user to clear filters first.
            if operation_filter != "All" or status_filter != "All":
                st.warning("Clear filters before saving edits to avoid accidental data loss.")
            else:
                save_data(edited_df)
                st.success("Schedule updated successfully.")

elif menu == "Delete Flight":
    st.subheader("Delete Flight")

    if df.empty:
        st.info("No records available.")
    else:
        df["Label"] = df["Flight No"] + " | " + df["Operation"] + " | " + df["Scheduled Time"].astype(str)
        selected = st.selectbox("Select flight to delete", df["Label"].tolist())

        if st.button("Delete Selected Flight"):
            df = df[df["Label"] != selected].drop(columns=["Label"])
            save_data(df)
            st.success("Flight deleted successfully.")
            st.rerun()
