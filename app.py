import streamlit as st
from streamlit import session_state as state
from streamlit import _bottom

import os
import sys

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, PATH)

from src.client import get_client, check_client
from src.bot import ChatBot
from src.config import load_cfg


def display_msg(msg):
    with st.chat_message(msg["role"], avatar=state.cfg["avatars"][msg["role"]]):
        st.write(msg["content"])
        if "url" in msg:
            st.image(msg["url"])


def main():
    if "bot" not in state:
        state.bot = ChatBot(client=state.client, cfg=state.cfg)
    bot = state.bot
    if "history" not in state:
        state.history = []

    # Chat input
    with st.container():
        question = _bottom.chat_input("Skriv en fråga")

        if question:
            state.history.append({"role": "user", "content": question})

            # Display history
            for msg in state.history:
                display_msg(msg)

            # Add placeholder to history while assistant is typing
            with st.chat_message("assistant", avatar=state.cfg["avatars"]["assistant"]):
                placeholder = st.image("assets/loading.gif")

            # Get answer(s)
            response = bot.chat(state.history)

            # Display answer(s)
            for i, answer in enumerate(response):
                if i == 0:
                    if answer["role"] == "system":
                        placeholder.markdown("System message:")
                        display_msg(answer)
                    else:
                        placeholder.markdown(answer["content"])
                else:
                    display_msg(answer)

                if "url" in answer:
                    st.image(answer["url"])

                state.history.append(answer)


if __name__ == "__main__":
    st.set_page_config(
        page_title="xrs",
        page_icon=":random:",
        layout="wide",
    )
    if "cfg" not in state:
        state.cfg = load_cfg()
    if "OPENAI_API_KEY" in os.environ:
        state.client = get_client(api_type=state.cfg["api_type"], api_key=os.environ["OPENAI_API_KEY"])
    if "client" in state and check_client(state.client) is True:
        main()
    else:
        st.switch_page("pages/login.py")
