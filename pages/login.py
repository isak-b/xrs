import streamlit as st
from streamlit import session_state as state

import os
import sys

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, PATH)

from src.api import get_client, check_client
from src.config import load_cfg


def submit():
    state.client = get_client(api_type=state.cfg["api_type"], api_key=state.api_key)
    if check_client(state.client) is True:
        st.switch_page("app.py")
    else:
        # Invalid client
        state.attempts += 1
        state.api_key = ""


def main():
    if "api_key" not in state:
        state.api_key = ""
    if "attempts" not in state:
        state.attempts = 0

    # Login page
    form = st.form(key="api_form")
    state.api_key = form.text_input(label="🔑 OpenAI API Key:", type="password")
    st.markdown(
        """<style> [data-testid="stFormSubmitButton"] {display: none;} </style>""",
        unsafe_allow_html=True,
    )
    submit_button = form.form_submit_button("Submit")
    if submit_button:
        submit()
    if state.attempts > 0:
        st.write(":red[Invalid key, try again!]")
        st.write("###", state.api_key)


if __name__ == "__main__":
    if "cfg" not in state:
        state.cfg = load_cfg()
    st.set_page_config(
        page_title="xrs",
        page_icon=":random:",
        layout="wide",
    )
    main()
