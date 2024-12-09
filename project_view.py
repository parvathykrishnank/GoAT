# Project View Tab
        with graph_tabs[3]:
            st.write("### Project Details")
            search_query = st.text_input("Search for Project Name", placeholder="Enter project name or part of it")

            if filtered_df.empty:
                st.write("No projects found.")
            else:
                if search_query:
                    search_results = filtered_df[
                        filtered_df['PROJ_DISPLAY_NAME'].str.contains(search_query, case=False, na=False)
                    ]
                else:
                    search_results = filtered_df

                if search_results.empty:
                    st.write("No projects match your search query.")
                else:
                    for index, row in search_results.iterrows():
                        with st.expander(f"{row['PROJ_DISPLAY_NAME']} - Click to view details", expanded=False):
                            st.markdown(
                                f"""
                                <div style='font-family: Arial, sans-serif; font-size: 1rem; line-height: 1.6; padding: 10px;'>
                                    <p><strong>Project ID:</strong> {row['PROJ_ID']}</p>
                                    <p><strong>Project Name:</strong> {row['PROJ_DISPLAY_NAME']}</p>
                                    <p><strong>Approval Year:</strong> {row['PROJ_APPRVL_FY']}</p>
                                    <p><strong>Status:</strong> {row['PROJ_STAT_NAME']}</p>
                                    <p><strong>Lending Instrument:</strong> {row['LNDNG_INSTR_LONG_NAME']}</p>
                                    <p><strong>Region:</strong> {row['Region']}</p>
                                    <p><strong>Country:</strong> {row['CNTRY_SHORT_NAME']}</p>
                                    <p><strong>Lead GP:</strong> {row['LEAD_GP_NAME']}</p>
                                    <p><strong>Commitment Amount (USD):</strong> ${row['CMT_AMT']:,.2f}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            # Green box for climate-related data in a single line
                            st.markdown(
                                f"""
                                <div style='background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 10px; margin-bottom: 10px;'>
                                    <div style='font-size: 1rem; line-height: 1.6; display: flex; gap: 15px;'>
                                        <span><strong>Climate Financing (%):</strong> {row['Climate Financing (%)']}</span>
                                        <span><strong>Adaptation (%):</strong> {row['Adaptation (%)']}</span>
                                        <span><strong>Mitigation (%):</strong> {row['Mitigation (%)']}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            # Indicators Section
                            indicators = row['Indicators']

                            if isinstance(indicators, str):
                                if indicators.strip().lower() == "not available":
                                    # Display "Not Available" in red
                                    st.markdown(
                                        f"""
                                        <div style='font-family: Arial, sans-serif; font-size: 1rem; color: red;'>
                                            <strong>Indicators:</strong> Not Available
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    # Try splitting the string into a list based on common delimiters
                                    indicator_list = [item.strip().strip("[]'") for item in indicators.split(",") if item.strip()]
                                    if indicator_list:
                                        st.markdown(
                                            "<strong>Indicators:</strong>",
                                            unsafe_allow_html=True,
                                        )
                                        st.markdown(
                                            "<ul style='font-family: Arial, sans-serif; font-size: 0.9rem; line-height: 1.6;'>" +
                                            "".join([f"<li>{indicator}</li>" for indicator in indicator_list]) +
                                            "</ul>",
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        # Fallback if splitting doesn't work
                                        st.markdown(
                                            f"""
                                            <div style='font-family: Arial, sans-serif; font-size: 1rem; color: gray;'>
                                                <strong>Indicators:</strong> Data not available or improperly formatted.
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                            else:
                                # Fallback for non-string types
                                st.markdown(
                                    f"""
                                    <div style='font-family: Arial, sans-serif; font-size: 1rem; color: gray;'>
                                        <strong>Indicators:</strong> Data not available or improperly formatted.
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )