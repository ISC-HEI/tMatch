
import streamlit as st

def protect():
    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("pages/login.py")
