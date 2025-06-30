import streamlit as st
import pandas as pd
from linkedin_scraper import scrape_linkedin_profiles

st.set_page_config(page_title="LinkedIn Sourcing Agent", layout="wide")

st.title("🔎 LinkedIn Sourcing Agent Dashboard")

# Sidebar Inputs
st.sidebar.header("Search Parameters")
job_role = st.sidebar.text_input("Job Role / Keywords", "Data Scientist")
num_profiles = st.sidebar.slider("Number of Profiles to Fetch", 1, 20, 5)

# Run Scraper Button
if st.sidebar.button("Run Sourcing Agent"):
    with st.spinner('Scraping LinkedIn profiles...'):
        df = scrape_linkedin_profiles(job_role, num_profiles)
        st.success(f"Scraped {len(df)} profiles successfully!")

# Display Data Table if CSV exists
try:
    df = pd.read_csv("profiles.csv")
    st.subheader("👥 Candidate Profiles")
    st.dataframe(df, use_container_width=True)

    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='linkedin_profiles.csv',
        mime='text/csv',
    )

    # Search Functionality
    st.subheader("🔍 Filter Profiles")
    search_term = st.text_input("Search by Name / Title / Location")
    if search_term:
        filtered_df = df[df.apply(lambda row: search_term.lower() in row.to_string().lower(), axis=1)]
        st.write(filtered_df)

except FileNotFoundError:
    st.info("👉 Run the sourcing agent to fetch profiles.")

