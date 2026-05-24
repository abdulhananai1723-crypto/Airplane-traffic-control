else:
    search_value = flight_search.strip().upper()

    checked_df = detect_gate_conflicts(plan_df)
    save_plan(checked_df)

    result_df = checked_df[
        checked_df["Flight No"].astype(str).str.upper().str.strip() == search_value
    ]

    if result_df.empty:
        st.error("Is flight number ka koi record nahi mila.")
    else:
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
