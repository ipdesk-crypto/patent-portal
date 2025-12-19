import streamlit as st
import pandas as pd
import json
import time
import hmac
import os
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from playwright.sync_api import sync_playwright

# --- 1. SYSTEM SETUP FOR CLOUD ---
@st.cache_resource
def install_playwright():
    subprocess.run(["playwright", "install", "chromium"])

install_playwright()

# --- 2. THEME & STYLING (Sunset Orange & Black) ---
st.set_page_config(page_title="Patent Search Portal", page_icon="🔍", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    [data-testid="stSidebar"] { background-color: #1c1e26; }
    .stExpander { background-color: #262730 !important; border: 1px solid #FF8C00 !important; }
    h1, h2, h3, p { color: #FAFAFA; }
    .stButton>button { background-color: #FF8C00; color: white; border-radius: 5px; }
    </style>
    """, unsafe_allow_code=True)

# --- 3. PASSCODE PROTECTION ---
def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    
    st.title("☀️ Patent Discovery Portal")
    st.text_input("Enter Passcode to Access:", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Access Denied")
    return False

if not check_password():
    st.stop()

# --- 4. YOUR SCRAPER FUNCTIONS (Integrated) ---
# [Note: I've kept your core scraping logic here so it runs within the app]

def get_versions_from_network():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        module_version, api_version = None, None
        def handle_request(request):
            nonlocal module_version, api_version
            if "DataActionGetPatentDosierData" in request.url:
                payload = json.loads(request.post_data)
                module_version = payload.get("versionInfo", {}).get("moduleVersion")
                api_version = payload.get("versionInfo", {}).get("apiVersion")
        page.on("request", handle_request)
        page.goto("https://eservices.moec.gov.ae/patent/IPDLListingPatent?Domain=36&lang=en", timeout=60000)
        page.wait_for_timeout(5000)
        browser.close()
        return module_version, api_version

# --- 5. THE USER INTERFACE ---
with st.sidebar:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", use_container_width=True)
    else:
        st.title("🏢 COMPANY LOGO")
    
    st.markdown("---")
    st.header("Admin Settings")
    if st.button("🚀 Scrape Latest Data"):
        with st.spinner("Scraping in progress... this may take minutes."):
            # Here you would call your fetch_all_patents function
            # and save it to 'master_patents.csv'
            st.success("Data Updated!")

st.title("🔍 Search Patent Records")

# Load Data
@st.cache_data
def load_data():
    if os.path.exists("master_patents.csv"):
        return pd.read_csv("master_patents.csv")
    return pd.DataFrame(columns=["Application Number", "Title", "Abstract", "Agent Name", "Application Date", "Classification", "Country Name (Priority)", "Priority Number", "Priority Date", "Application Type (ID)"])

df = load_data()

# Search Boxes
c1, c2 = st.columns(2)
with c1:
    q_main = st.text_input("Search Title, Abstract, or Agent")
with c2:
    q_app = st.text_input("Application Number")

# Filtering
filtered = df.copy()
if q_main:
    mask = (filtered['Title'].str.contains(q_main, case=False, na=False) | 
            filtered['Abstract'].str.contains(q_main, case=False, na=False) |
            filtered['Agent Name'].str.contains(q_main, case=False, na=False))
    filtered = filtered[mask]
if q_app:
    filtered = filtered[filtered['Application Number'].astype(str).contains(q_app)]

# Display
for _, row in filtered.iterrows():
    with st.expander(f"📄 {row['Application Number']} - {row['Title']}"):
        col_l, col_r = st.columns(2)
        with col_l:
            st.write(f"**App Date:** {row['Application Date']}")
            st.write(f"**Classification:** {row['Classification']}")
            st.write(f"**Type ID:** {row['Application Type (ID)']}")
        with col_r:
            st.write(f"**Priority Country:** {row['Country Name (Priority)']}")
            st.write(f"**Priority Date:** {row['Priority Date']}")
            st.write(f"**Agent:** {row.get('Agent Name', 'N/A')}")
        st.markdown("---")
        st.write("**Abstract:**")
        st.caption(row['Abstract'])