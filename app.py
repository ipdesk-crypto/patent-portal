import streamlit as st
import pandas as pd
import hmac
import os
import io

# --- 1. PAGE CONFIG & SOPHISTICATED CSS ---
st.set_page_config(page_title="Executive Patent Portal", layout="wide")

st.markdown("""
    <style>
    /* Professional Dark Background */
    .stApp { background-color: #0E1117; color: #FFFFFF; font-family: 'Inter', sans-serif; }
    
    /* Center and Style the Login Card */
    [data-testid="stForm"] {
        border: 1px solid #FF8C00 !important;
        border-radius: 8px;
        background-color: #161b22;
        padding: 40px;
        max-width: 500px;
        margin: auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Branded Orange Buttons */
    div.stButton > button, div.stDownloadButton > button {
        background-color: #FF8C00 !important;
        color: #000000 !important;
        border-radius: 4px !important;
        border: none !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        width: 100%;
        transition: 0.3s ease all;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #FFB347 !important;
        transform: translateY(-2px);
    }

    /* Input Fields Branding */
    .stTextInput input {
        background-color: #0d1117 !important;
        color: #FF8C00 !important;
        border: 1px solid #30363d !important;
    }

    /* Sidebar and Table Customization */
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 2px solid #FF8C00; }
    .stDataFrame { border: 1px solid #30363d; border-radius: 8px; }
    h1, h2, h3 { color: #FF8C00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE ACCESS GATEWAY ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Fixed for logo.jpeg extension
        if os.path.exists("logo.jpeg"):
            st.image("logo.jpeg", use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>SECURITY GATEWAY</h2>", unsafe_allow_html=True)
        
        with st.form("login_gateway"):
            pwd = st.text_input("Enter Passcode", type="password")
            if st.form_submit_button("AUTHENTICATE SYSTEM"):
                if hmac.compare_digest(pwd, st.secrets["password"]):
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials. Access Denied.")
    return False

if not check_password():
    st.stop()

# --- 3. MAIN DASHBOARD ---
with st.sidebar:
    # Fixed for logo.jpeg extension
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", use_container_width=True)
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #FF8C00; font-weight: bold;'>PORTAL STATUS: ACTIVE</p>", unsafe_allow_html=True)
    
    # Reset Button
    if st.button("🔄 Clear All Filters"):
        for key in st.session_state.keys():
            if key.startswith('search_'):
                st.session_state[key] = ""
        st.rerun()

st.title("🔍 Patent Database Query Engine")

# --- 4. DATA LOADING & MULTI-FIELD SEARCH ---
if os.path.exists("master_patents.csv"):
    try:
        df = pd.read_csv("master_patents.csv")
        
        # 10 Query Fields Layout
        st.markdown("### Search Parameters")
        c1, c2, c3 = st.columns(3)
        with c1:
            q_app_num = st.text_input("Application Number", key="search_1")
            q_agent = st.text_input("Agent Name", key="search_2")
            q_date = st.text_input("Application Date (YYYY-MM-DD)", key="search_3")
            q_type = st.text_input("Application Type (ID)", key="search_4")
        with c2:
            q_title = st.text_input("Title Keyword", key="search_5")
            q_country = st.text_input("Country (Priority)", key="search_6")
            q_prio_num = st.text_input("Priority Number", key="search_7")
        with c3:
            q_abstract = st.text_input("Abstract Keyword", key="search_8")
            q_class = st.text_input("Classification", key="search_9")
            q_prio_date = st.text_input("Priority Date (YYYY-MM-DD)", key="search_10")

        # Filtering Logic
        f = df.copy()
        if q_app_num: f = f[f['Application Number'].astype(str).str.contains(q_app_num, case=False, na=False)]
        if q_title: f = f[f['Title'].str.contains(q_title, case=False, na=False)]
        if q_abstract: f = f[f['Abstract'].str.contains(q_abstract, case=False, na=False)]
        if q_agent: f = f[f['Agent Name'].str.contains(q_agent, case=False, na=False)]
        if q_date: f = f[f['Application Date'].astype(str).str.contains(q_date, na=False)]
        if q_class: f = f[f['Classification'].str.contains(q_class, case=False, na=False)]
        if q_country: f = f[f['Country Name (Priority)'].str.contains(q_country, case=False, na=False)]
        if q_prio_num: f = f[f['Priority Number'].astype(str).str.contains(q_prio_num, na=False)]
        if q_prio_date: f = f[f['Priority Date'].astype(str).str.contains(q_prio_date, na=False)]
        if q_type: f = f[f['Application Type (ID)'].astype(str).str.contains(q_type, na=False)]

        # --- 5. RESULTS & EXPORT ---
        st.markdown("---")
        res_col, dl_col = st.columns([3, 1])
        with res_col:
            st.subheader(f"Results: {len(f)} Records Found")
        
        with dl_col:
            # Excel Export Feature
            towrite = io.BytesIO()
            f.to_excel(towrite, index=False, header=True)
            towrite.seek(0)
            st.download_button(
                label="📥 Download to Excel",
                data=towrite,
                file_name="patent_export.xlsx",
                mime="application/vnd.ms-excel"
            )

        st.dataframe(f, use_container_width=True, hide_index=True)

        # Detailed View Expanders
        for _, row in f.head(50).iterrows(): # Limit display for performance
            with st.expander(f"📙 {row['Application Number']} — {row['Title']}"):
                st.write(f"**Abstract:** {row['Abstract']}")
                st.write(f"**Agent:** {row['Agent Name']} | **Type:** {row['Application Type (ID)']}")

    except Exception as e:
        st.error(f"Data Loading Error: {e}")
        st.info("Ensure 'master_patents.csv' is properly formatted and not empty.")
else:
    st.warning("⚠️ Waiting for 'master_patents.csv' to be uploaded to GitHub.")
