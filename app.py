import streamlit as st
import pandas as pd
import plotly.express as px
from venn import venn  # Importing venn library
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO

# -------------------- Load the Data -------------------- #
file_path = "database.xlsx"
df = pd.read_excel(file_path)

# Load hierarchy data
hierarchy_file_path = "hierarchy.xlsx"
hierarchy_df = pd.read_excel(hierarchy_file_path)

# -------------------- Streamlit App Configuration -------------------- #
st.set_page_config(
    page_title="Governance Operations Analytics Tool",
    page_icon=":bar_chart:",
    layout="wide",
)

# -------------------- Load and Display Logo -------------------- #
logo = Image.open("Logo.png").convert("RGBA")
logo = logo.resize((100, 100))
buffered = BytesIO()
logo.save(buffered, format="PNG")
logo_base64 = base64.b64encode(buffered.getvalue()).decode()
st.markdown(
    f"""
    <div style='display: flex; align-items: center;'>
        <img src='data:image/png;base64,{logo_base64}' style='width:100px; margin-right: 10px;'>
        <h1 style='margin: 0;'>Governance Operations Analytics Tool (GoAT)</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Tab Navigation -------------------- #
tabs = st.tabs(["Dashboard", "Keywords", "About"])

# -------------------- About Tab -------------------- #
with tabs[2]:
    st.header("About")
    st.markdown(
        """
        <div style='font-family: Arial, sans-serif; font-size: 1rem; line-height: 1.6;'>
            <p>The <strong>Governance Operations Analytics Tool (GoAT)</strong> allows for targeted searches...</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------- Dashboard Tab -------------------- #
with tabs[0]:
    st.subheader("GoAT Dashboard")

    # Filters Section
    col1, col2 = st.columns([1, 3])
    with col1:
        # Lending Instrument Filter
        landing_instr = st.multiselect(
            "Select Lending Instrument",
            options=df["LNDNG_INSTR_LONG_NAME"].unique(),
            default=df["LNDNG_INSTR_LONG_NAME"].unique(),
            key="landing_instr",
        )

        # Region Filter
        region_options = df[df["LNDNG_INSTR_LONG_NAME"].isin(landing_instr)]["Region"].unique()
        region = st.multiselect(
            "Select Region",
            options=region_options,
            default=region_options if len(region_options) > 0 else [],
            key="region",
        )

        # Keywords Filter
        project_types = st.multiselect(
            "Filter by Keywords",
            options=hierarchy_df["Hierarchy Name"].unique(),
            default=[],
            key="project_types",
        )
        
        # AND/OR Filter
        and_or_filter = st.radio(
            "Select filter type for Keywords",
            options=["AND", "OR"],
            index=0,
            key="and_or_filter",
        )

    # Apply Filters and Display Metrics
    with col2:
        if not region:
            filtered_df = pd.DataFrame()
        else:
            filtered_df = df[
                df["LNDNG_INSTR_LONG_NAME"].isin(landing_instr)
                & df["Region"].isin(region)
            ]

        if project_types:
            if and_or_filter == "AND":
                for project_type in project_types:
                    filtered_df = filtered_df[filtered_df[project_type] == "Yes"]
            elif and_or_filter == "OR":
                filtered_df = filtered_df[filtered_df[project_types].eq("Yes").any(axis=1)]

        total_projects = filtered_df.shape[0]
        st.metric(label="Total Number of Projects", value=total_projects)

        # Graph Tabs
        graph_tabs = ["Project Status", "Lending Instrument", "Download Data", "Project View"]
        if 2 <= len(project_types) <= 4:
            graph_tabs.append("Keyword Search Venn")

        graph_tabs = st.tabs(graph_tabs)

        # Project Status Tab
        with graph_tabs[0]:
            if not filtered_df.empty:
                grouped_df1 = filtered_df.groupby(['PROJ_APPRVL_FY', 'PROJ_STAT_NAME'])['PROJ_ID'].nunique().reset_index()
                grouped_df1.columns = ['Approval FY', 'Project Status', 'Number of Projects']
                fig1 = px.bar(grouped_df1, x='Approval FY', y='Number of Projects', color='Project Status', title='Project Status')
                st.plotly_chart(fig1, use_container_width=True)

        # Lending Instrument Tab
        with graph_tabs[1]:
            if not filtered_df.empty:
                grouped_df2 = filtered_df.groupby(['PROJ_APPRVL_FY', 'LNDNG_INSTR_LONG_NAME'])['PROJ_ID'].nunique().reset_index()
                grouped_df2.columns = ['Approval FY', 'Lending Instrument', 'Number of Projects']

                fig2 = px.bar(
                    grouped_df2,
                    x='Approval FY',
                    y='Number of Projects',
                    color='Lending Instrument',
                    title='Lending Instrument',
                )
                st.plotly_chart(fig2, use_container_width=True)

        # Download Data Tab
        with graph_tabs[2]:
            columns_to_display = list(df.columns[: df.columns.get_loc("DLI_DLR") + 1])
            st.write("### Download Projects")
            if filtered_df.empty:
                st.write("No project found.")
            else:
                st.dataframe(filtered_df[columns_to_display])

        # Venn Diagram Tab
        if 2 <= len(project_types) <= 4:
            with graph_tabs[4]:
                project_sets = {}
                for keyword in project_types:
                    project_sets[keyword] = set(df[df[keyword] == 'Yes']['PROJ_ID'])

                plt.figure(figsize=(1.5, 1.5))
                venn(project_sets)
                plt.legend(
                    labels=project_sets.keys(),
                    loc="upper center",
                    bbox_to_anchor=(0.5, 1.001),
                    frameon=True,
                    ncol=len(project_sets),
                    fontsize=10
                )
                plt.subplots_adjust(left=0.05, right=0.95, top=0.98, bottom=0.05)
                st.pyplot(plt)

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

# -------------------- Keywords Tab -------------------- #
with tabs[1]:
    keyword_tabs = st.tabs(["Available Hierarchies", "Add New Keywords", "Delete Hierarchy"])

    # Available Hierarchies Tab
    with keyword_tabs[0]:
        if not hierarchy_df.empty:
            sunburst_df = hierarchy_df.copy()
            sunburst_df['Keyword'] = sunburst_df['Keyword'].apply(lambda x: ' '.join([word.capitalize() for word in x.split()]))
            sunburst_df['Keyword'] = sunburst_df['Keyword'].apply(lambda x: x.replace(' ', '<br>'))

            fig_sunburst = px.sunburst(
                sunburst_df,
                path=['Hierarchy Name', 'Keyword'],
                values=None,
                width=800,
                height=600,
            )
            st.plotly_chart(fig_sunburst, use_container_width=False)

    # Add New Keywords Tab
    with keyword_tabs[1]:
        with st.form("add_keyword_form"):
            hierarchy_name = st.text_input("Enter Hierarchy Name (e.g., PIM)")
            full_name = st.text_input("Enter Full Name (e.g., Public Investment Management)")
            new_keywords = st.text_input("Enter Keywords (comma separated)")

            submitted = st.form_submit_button("Add Keyword")

            if submitted:
                if not hierarchy_name or not full_name or not new_keywords:
                    st.error("All fields are compulsory. Please fill in all fields.")
                else:
                    keywords_list = [kw.strip() for kw in new_keywords.split(",")]
                    new_data = pd.DataFrame({
                        'Hierarchy Name': [hierarchy_name] * len(keywords_list),
                        'Full Name': [full_name] * len(keywords_list),
                        'Keyword': keywords_list
                    })
                    hierarchy_df = pd.concat([hierarchy_df, new_data], ignore_index=True)
                    hierarchy_df.to_excel(hierarchy_file_path, index=False)
                    st.success(f"Keywords added successfully to hierarchy '{hierarchy_name}'.")

    # Delete Hierarchy Tab
    with keyword_tabs[2]:
        hierarchy_to_delete = st.selectbox("Select a Hierarchy to Delete", hierarchy_df["Hierarchy Name"].unique())

        if st.button("Delete Hierarchy"):
            hierarchy_df = hierarchy_df[hierarchy_df["Hierarchy Name"] != hierarchy_to_delete]
            hierarchy_df.to_excel(hierarchy_file_path, index=False)
            st.success(f"Hierarchy '{hierarchy_to_delete}' deleted successfully.")

