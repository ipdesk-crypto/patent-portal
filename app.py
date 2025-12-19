import streamlit as st
import pandas as pd
import hmac
import os
import io

# --- 1. EXECUTIVE BRANDING & UI ---
st.set_page_config(page_title="Patent Discovery Portal", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text */
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Sophisticated Login Card */
    [data-testid="stForm"] {
        border: 1px solid #FF8C00 !important;
        border-radius: 4px;
        background-color: #161b22;
        padding: 40px;
        max-width: 500px;
        margin: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    /* Professional Orange Buttons */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        border-radius: 2px !important;
        border: none !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        height: 3em;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #e67e00 !important;
        box-shadow: 0 0 10px #FF8C00;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #000000 !important; 
        border-right: 2px solid #FF8C00; 
    }
    
    /* Search Input Contrast */
    .stTextInput input {
        background-color: #0d1117 !important;
        color: #FF8C00 !important;
        border: 1px solid #30363d !important;
    }

    /* Headers */
    h1, h2, h3 { color: #FF8C00 !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE GATEWAY ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.markdown("<h3 style='text-align: center;'>EXECUTIVE ACCESS ONLY</h3>", unsafe_allow_html=True)
        
        with st.form("login_gateway"):
            pwd = st.text_input("Security Passcode", type="password")
            if st.form_submit_button("AUTHENTICATE"):
                if hmac.compare_digest(pwd, st.secrets["password"]):
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    return False

if not check_password():
    st.stop()

# --- 3. DASHBOARD CONTENT ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("<br><h4 style='text-align: center; color: #FF8C00;'>Patent Discovery v2.0</h4>", unsafe_allow_html=True)
    st.markdown("---")

st.title("🔍 Database Query Engine")

if os.path.exists("master_patents.csv"):
    try:
        df = pd.read_csv("master_patents.csv")
        
        # Advanced Multi-Criteria Filter
        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                f_app = st.text_input("Application No.")
                f_agent = st.text_input("Agent/Legal Representative")
            with c2:
                f_title = st.text_input("Patent Title Keywords")
                f_country = st.text_input("Priority Country")
            with c3:
                f_type = st.text_input("App Type (ID)")
                f_class = st.text_input("Classification Code")

        # Core Search Logic
        results = df.copy()
        if f_app: results = results[results['Application Number'].astype(str).str.contains(f_app, case=False, na=False)]
        if f_title: results = results[results['Title'].str.contains(f_title, case=False, na=False)]
        if f_agent: results = results[results['Agent Name'].str.contains(f_agent, case=False, na=False)]
        if f_country: results = results[results['Country Name (Priority)'].str.contains(f_country, case=False, na=False)]
        if f_type: results = results[results['Application Type (ID)'].astype(str).str.contains(f_type, na=False)]
        if f_class: results = results[results['Classification'].str.contains(f_class, case=False, na=False)]

        # --- 4. EXPORT AND DISPLAY ---
        st.markdown(f"**Found {len(results)} matching records**")
        
        # Excel Download Feature
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            results.to_excel(writer, index=False, sheet_name='Search_Results')
        
        st.download_button(
            label="📥 EXPORT SEARCH TO EXCEL",
            data=buffer.getvalue(),
            file_name="patent_search_results.xlsx",
            mime="application/vnd.ms-excel"
        )

        st.dataframe(results, use_container_width=True, hide_index=True)

    except pd.errors.EmptyDataError:
        st.error("The data file 'master_patents.csv' is currently empty. Please upload a populated file to GitHub.")
else:
    st.warning("⚠️ Critical: 'master_patents.csv' not found in repository.")
