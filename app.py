elif menu == "Manage Takeoff / Landing":
    st.subheader("Manage Takeoff & Landing")

    if df.empty:
        st.info("No records available.")
    else:
        operation_filter = st.selectbox(
            "Show flights",
            ["All", "Takeoff", "Landing"]
        )

        filtered_df = df.copy()

        if operation_filter != "All":
            filtered_df = filtered_df[filtered_df["Operation"] == operation_filter]

        st.dataframe(filtered_df, use_container_width=True)

        st.divider()

        selected_flight = st.selectbox(
            "Select Flight",
            filtered_df["Flight No"].tolist()
        )

        flight_index = df[df["Flight No"] == selected_flight].index[0]

        new_operation = st.selectbox(
            "Operation",
            ["Takeoff", "Landing"],
            index=0 if df.loc[flight_index, "Operation"] == "Takeoff" else 1
        )

        new_status = st.selectbox(
            "Status",
            ["Scheduled", "Delayed", "Boarding", "Departed", "Landed", "Cancelled"],
            index=["Scheduled", "Delayed", "Boarding", "Departed", "Landed", "Cancelled"]
            .index(df.loc[flight_index, "Status"])
        )

        new_gate = st.text_input("Gate", value=str(df.loc[flight_index, "Gate"]))

        new_remarks = st.text_area(
            "Remarks",
            value=str(df.loc[flight_index, "Remarks"])
        )

        if st.button("Update Flight"):
            df.loc[flight_index, "Operation"] = new_operation
            df.loc[flight_index, "Status"] = new_status
            df.loc[flight_index, "Gate"] = new_gate
            df.loc[flight_index, "Remarks"] = new_remarks

            save_data(df)
            st.success("Flight updated successfully.")
            st.rerun()
