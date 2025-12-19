import streamlit as st
import pandas as pd
import os, hmac, subprocess

# --- INSTALL BROWSERS ---
@st.cache_resource
def install_playwright():
    subprocess.run(["playwright", "install", "chromium"])

install_playwright()

# --- SUNSET THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    [data-testid="stSidebar"] { background-color: #1c1e26; }
    .stExpander { background-color: #262730 !important; border: 1px solid #FF8C00 !important; }
    h1, h2, h3, p { color: #FAFAFA; }
    </style>
    """, unsafe_allow_code=True)

# --- PASSCODE ---
def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.title("☀️ Patent Discovery Portal")
    st.text_input("Enter Passcode:", type="password", on_change=password_entered, key="password")
    return False

if not check_password():
    st.stop()

# --- SIDEBAR & LOGO ---
with st.sidebar:
    # Look for logo in main directory instead of assets folder
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🏢 COMPANY LOGO")
    
    if st.button("🚀 Scrape Latest Data"):
        st.info("Starting Scraper...")
        # Your fetch_all_patents code here

# --- SEARCH & RESULTS ---
st.title("🔍 Patent Search")

# Load existing CSV if it exists
if os.path.exists("master_patents.csv"):
    df = pd.read_csv("master_patents.csv")
    query = st.text_input("Search Title, Abstract, or Agent Name")
    
    if query:
        # Search all columns for the query
        filtered = df[df.apply(lambda row: query.lower() in str(row).lower(), axis=1)]
        
        for _, row in filtered.iterrows():
            with st.expander(f"📄 {row['Application Number']} - {row['Title']}"):
                # Show all details
                st.write(f"**Abstract:** {row['Abstract']}")
                st.write(f"**Agent Name:** {row.get('Agent Name', 'N/A')}")
                st.write(f"**App Date:** {row['Application Date']}")
                st.write(f"**Classification:** {row['Classification']}")
                st.write(f"**Priority Country:** {row['Country Name (Priority)']}")
                st.write(f"**Priority Number:** {row['Priority Number']}")
                st.write(f"**Priority Date:** {row['Priority Date']}")
                st.write(f"**Type ID:** {row['Application Type (ID)']}")
else:
    st.warning("Database empty. Click 'Scrape' in sidebar.")
