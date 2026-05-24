import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date, time

DAILY_PLAN_FILE = Path("daily_flight_plan.csv")

PLAN_COLUMNS = [
    "Flight No",
    "Airline",
    "Type",
    "From",
    "To",
    "Scheduled Time",
    "Passengers",
    "Gate",
    "Counter / Belt",
    "Staff Required",
    "Vehicle Required",
    "Arrangement Notes",
    "Status",
]


# -----------------------------
# Data Functions
# -----------------------------
def load_plan() -> pd.DataFrame:
    if DAILY_PLAN_FILE.exists():
        return pd.read_csv(DAILY_PLAN_FILE)
    return pd.DataFrame(columns=PLAN_COLUMNS)


def save_plan(df: pd.DataFrame) -> None:
    df.to_csv(DAILY_PLAN_FILE, index=False)


def calculate_arrangements(row: dict) -> dict:
    passengers = int(row.get("Passengers", 0) or 0)
    flight_type = row.get("Type", "Departure")

    if passengers <= 80:
        staff = 3
        vehicle = "1 airport van"
    elif passengers <= 160:
        staff = 5
        vehicle = "1 van + 1 luggage team"
    else:
        staff = 8
        vehicle = "2 vans + 2 luggage teams"

    if flight_type == "Arrival":
        row["Counter / Belt"] = "Belt 1"
        row["Arrangement Notes"] = "Passenger receiving, baggage handling, transport coordination."
    else:
        row["Counter / Belt"] = "Counter 1"
        row["Arrangement Notes"] = "Check-in support, boarding coordination, gate readiness."

    row["Staff Required"] = staff
    row["Vehicle Required"] = vehicle
    row["Status"] = "Planned"
    return row


def detect_gate_conflicts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    if "Operational Command" not in df.columns:
        df["Operational Command"] = "Clear"

    df["Scheduled Time"] = pd.to_datetime(df["Scheduled Time"], errors="coerce")
    df["Gate"] = df["Gate"].astype(str).str.upper().str.strip()

    conflict_mask = df.duplicated(subset=["Gate", "Scheduled Time"], keep=False)

    df.loc[conflict_mask, "Status"] = "Conflict"
    df.loc[
        conflict_mask,
        "Operational Command",
    ] = "Gate-time conflict detected. Reassign gate or change schedule before operation."

    df.loc[~conflict_mask, "Operational Command"] = "Clear for operation."

    return df


# -----------------------------
# Page Config & Styling
# -----------------------------
st.set_page_config(
    page_title="Airport Operations Control Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f7fb;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b);
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 16px;
        color: #475569;
        margin-bottom: 24px;
    }

    .section-box {
        background: white;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0px 4px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
    }

    .small-label {
        color: #64748b;
        font-size: 14px;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 22px;
        font-weight: 700;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8, #1e40af);
        color: white;
    }

    h1, h2, h3 {
        color: #0f172a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-title">✈️ Airport Operations Control Center</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Professional dashboard for daily arrivals, departures, staff planning, gate allocation, and airport coordination.</div>',
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar Menu
# -----------------------------
menu = st.sidebar.radio(
    "Operations Menu",
    [
        "1. Daily Flight Entry",
        "2. Generate Arrangements",
        "3. View Final Plan",
        "4. Edit / Update Plan",
        "5. Delete Flight",
        "6. Data Check Up",
    ],
)

plan_df = load_plan()


# -----------------------------
# 1. Daily Flight Entry
# -----------------------------
if menu == "1. Daily Flight Entry":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Daily Flight Entry")
    st.info("Sab se pehle aaj ki incoming aur outgoing flights enter karein.")

    incoming_count = st.number_input("Aaj kitni flights aani hain?", min_value=0, step=1)
    outgoing_count = st.number_input("Aaj kitni flights jani hain?", min_value=0, step=1)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Flight Details")

    with st.form("daily_flight_entry_form"):
        new_rows = []

        st.markdown("### Arrivals / Aani wali flights")
        for i in range(int(incoming_count)):
            st.markdown(f"**Arrival Flight {i + 1}**")
            col1, col2, col3 = st.columns(3)

            with col1:
                flight_no = st.text_input(f"Flight No {i + 1}", key=f"arr_flight_{i}")
                airline = st.text_input(f"Airline {i + 1}", key=f"arr_airline_{i}")

            with col2:
                origin = st.text_input(f"From {i + 1}", key=f"arr_from_{i}")
                arrival_time = st.time_input(f"Arrival Time {i + 1}", key=f"arr_time_{i}")

            with col3:
                passengers = st.number_input(
                    f"Passengers {i + 1}", min_value=0, step=1, key=f"arr_pass_{i}"
                )
                gate = st.text_input(f"Gate {i + 1}", key=f"arr_gate_{i}")

            new_rows.append(
                {
                    "Flight No": flight_no.upper(),
                    "Airline": airline,
                    "Type": "Arrival",
                    "From": origin,
                    "To": "Current Airport",
                    "Scheduled Time": datetime.combine(date.today(), arrival_time).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "Passengers": passengers,
                    "Gate": gate,
                }
            )

        st.markdown("### Departures / Jani wali flights")
        for i in range(int(outgoing_count)):
            st.markdown(f"**Departure Flight {i + 1}**")
            col1, col2, col3 = st.columns(3)

            with col1:
                flight_no = st.text_input(f"Flight No {i + 1}", key=f"dep_flight_{i}")
                airline = st.text_input(f"Airline {i + 1}", key=f"dep_airline_{i}")

            with col2:
                destination = st.text_input(f"To / Destination {i + 1}", key=f"dep_to_{i}")
                departure_time = st.time_input(f"Departure Time {i + 1}", key=f"dep_time_{i}")

            with col3:
                passengers = st.number_input(
                    f"Passengers {i + 1}", min_value=0, step=1, key=f"dep_pass_{i}"
                )
                gate = st.text_input(f"Gate {i + 1}", key=f"dep_gate_{i}")

            new_rows.append(
                {
                    "Flight No": flight_no.upper(),
                    "Airline": airline,
                    "Type": "Departure",
                    "From": "Current Airport",
                    "To": destination,
                    "Scheduled Time": datetime.combine(date.today(), departure_time).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "Passengers": passengers,
                    "Gate": gate,
                }
            )

        submitted = st.form_submit_button("Save Today’s Flight Entry")

        if submitted:
            valid_rows = [row for row in new_rows if row["Flight No"] and row["Airline"]]

            if not valid_rows:
                st.error("Kam az kam aik valid flight zaroor enter karein.")
            else:
                arranged_rows = [calculate_arrangements(row) for row in valid_rows]
                new_df = pd.DataFrame(arranged_rows, columns=PLAN_COLUMNS)
                save_plan(new_df)
                st.success("Today’s flights saved and initial arrangements generated.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 2. Generate Arrangements
# -----------------------------
elif menu == "2. Generate Arrangements":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Generate Arrangements")

    if plan_df.empty:
        st.info("Pehle Daily Flight Entry karein.")
    else:
        arranged_df = plan_df.copy()
        arranged_df = arranged_df.apply(
            lambda row: calculate_arrangements(row.to_dict()), axis=1, result_type="expand"
        )
        arranged_df = arranged_df[PLAN_COLUMNS]
        save_plan(arranged_df)

        st.success("Arrangements generated successfully.")
        st.dataframe(arranged_df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 3. View Final Plan
# -----------------------------
elif menu == "3. View Final Plan":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Final Daily Operations Plan")

    if plan_df.empty:
        st.info("No daily plan found.")
    else:
        plan_df["Scheduled Time"] = pd.to_datetime(plan_df["Scheduled Time"], errors="coerce")
        plan_df = plan_df.sort_values("Scheduled Time")

        total_arrivals = len(plan_df[plan_df["Type"] == "Arrival"])
        total_departures = len(plan_df[plan_df["Type"] == "Departure"])
        total_staff = pd.to_numeric(plan_df["Staff Required"], errors="coerce").fillna(0).sum()
        total_passengers = pd.to_numeric(plan_df["Passengers"], errors="coerce").fillna(0).sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Arrivals", total_arrivals)
        col2.metric("Departures", total_departures)
        col3.metric("Total Staff", int(total_staff))
        col4.metric("Passengers", int(total_passengers))

        st.divider()
        st.dataframe(plan_df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 4. Edit / Update Plan
# -----------------------------
elif menu == "4. Edit / Update Plan":
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("Edit / Update Plan")

    if plan_df.empty:
        st.info("No records available.")
    else:
        edited_df = st.data_editor(plan_df, use_container_width=True, num_rows="dynamic")

        if st.button("Save Changes"):
            save_plan(edited_df)
            st.success("Plan updated successfully.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# 5. Delete Flight
# -----------------------------
elif menu == "5. Delete Flight":
    st.subheader("Delete Flight")

    if plan_df.empty:
        st.info("No records available.")
    else:
        plan_df["Label"] = (
            plan_df["Flight No"].astype(str)
            + " | "
            + plan_df["Type"].astype(str)
            + " | "
            + plan_df["Scheduled Time"].astype(str)
        )

        selected = st.selectbox(
            "Select flight to delete",
            plan_df["Label"].tolist(),
        )

        if st.button("Delete Selected Flight"):
            plan_df = plan_df[plan_df["Label"] != selected].drop(columns=["Label"])
            plan_df = detect_gate_conflicts(plan_df)
            save_plan(plan_df)
            st.success("Flight deleted successfully.")
            st.rerun()

elif menu == "6. Data Check Up":
    st.subheader("Data Check Up")
    st.info("Flight number enter karein, system us flight ka complete record show karega.")

    if plan_df.empty:
        st.warning("No flight data available. Pehle Daily Flight Entry karein.")
    else:
        flight_search = st.text_input("Enter Flight Number", placeholder="Example: PK-1723")

        if st.button("Check Flight Data"):
            if not flight_search.strip():
                st.error("Please flight number enter karein.")
            else:
                search_value = flight_search.strip().upper()
                result_df = plan_df[
                    plan_df["Flight No"].astype(str).str.upper().str.strip() == search_value
                ]

                if result_df.empty:
                    st.error("Is flight number ka koi record nahi mila.")
                else:
                    result_df = detect_gate_conflicts(result_df)
                    st.success("Flight record found.")

                    flight = result_df.iloc[0]

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Flight No", flight["Flight No"])
                    col2.metric("Type", flight["Type"])
                    col3.metric("Status", flight["Status"])

                    st.divider()

                    st.write("### Complete Flight Details")
                    st.dataframe(result_df, use_container_width=True)

                    st.write("### Operational Command")
                    if flight["Status"] == "Conflict":
                        st.error(flight["Operational Command"])
                    else:
                        st.success(flight["Operational Command"])
