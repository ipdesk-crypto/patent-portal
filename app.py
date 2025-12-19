import streamlit as st
import pandas as pd
import hmac
import os

# --- 1. SOPHISTICATED BRANDING & UI (Black & Orange) ---
st.set_page_config(page_title="Patent Discovery Portal", layout="wide")

st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Center the login box */
    [data-testid="stForm"] {
        border: 2px solid #FF8C00 !important;
        border-radius: 15px;
        background-color: #1c1e26;
        padding: 30px;
        max-width: 450px;
        margin: auto;
    }

    /* Primary Buttons (Branded Orange) */
    div.stButton > button:first-child {
        background-color: #FF8C00;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #E67E00;
        border: none;
        color: white;
    }

    /* Inputs and Dataframes */
    .stTextInput input {
        background-color: #262730;
        color: white;
        border: 1px solid #444;
    }
    [data-testid="stSidebar"] { background-color: #000000; border-right: 1px solid #FF8C00; }
    .stExpander { background-color: #1c1e26 !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CUSTOM LOGIN INTERFACE ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    # Branding on Login Page
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.markdown("<h2 style='text-align: center; color: #FF8C00;'>Internal Search Portal</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            password = st.text_input("Security Passcode", type="password")
            submit = st.form_submit_button("UNLOCk ACCESS")
            
            if submit:
                if hmac.compare_digest(password, st.secrets["password"]):
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("🚫 Access Denied")
    return False

if not check_password():
    st.stop()

# --- 3. MAIN APP (AFTER LOGIN) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("---")
    st.markdown("<p style='color: #FF8C00; font-weight: bold;'>SYSTEM STATUS: ONLINE</p>", unsafe_allow_html=True)
    st.info("Database: master_patents.csv")

st.title("🔍 Patent Database Query")

if os.path.exists("master_patents.csv"):
    df = pd.read_csv("master_patents.csv")
    
    # Sophisticated Search Layout
    with st.container():
        st.markdown("### Search Filters")
        c1, c2, c3 = st.columns(3)
        with c1:
            q_app_num = st.text_input("Application #")
            q_agent = st.text_input("Agent Name")
        with c2:
            q_title = st.text_input("Title Keyword")
            q_country = st.text_input("Priority Country")
        with c3:
            q_type = st.text_input("Application Type")
            q_class = st.text_input("Classification")

    # Filtering Logic
    filtered = df.copy()
    if q_app_num: filtered = filtered[filtered['Application Number'].astype(str).str.contains(q_app_num, case=False, na=False)]
    if q_title: filtered = filtered[filtered['Title'].str.contains(q_title, case=False, na=False)]
    if q_agent: filtered = filtered[filtered['Agent Name'].str.contains(q_agent, case=False, na=False)]
    if q_country: filtered = filtered[filtered['Country Name (Priority)'].str.contains(q_country, case=False, na=False)]
    if q_type: filtered = filtered[filtered['Application Type (ID)'].astype(str).str.contains(q_type, na=False)]
    if q_class: filtered = filtered[filtered['Classification'].str.contains(q_class, case=False, na=False)]

    # --- 4. BRANDED RESULTS ---
    st.markdown(f"<h4 style='color: #FF8C00;'>Matches Found: {len(filtered)}</h4>", unsafe_allow_html=True)
    
    # Modern Table Display
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    # Detailed View in Branded Expanders
    for _, row in filtered.iterrows():
        with st.expander(f"📙 {row['Application Number']} | {row['Title']}"):
            st.write(f"**Abstract:** {row['Abstract']}")
            st.markdown(f"<span style='color: #FF8C00;'>Priority Number: {row['Priority Number']}</span>", unsafe_allow_html=True)

else:
    st.warning("Please upload 'master_patents.csv' to the GitHub repository to begin.")
