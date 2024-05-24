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


def display_msg(role: str, content: str, url: str = None, **_kwargs):
    container = st.chat_message(role, avatar=state.cfg["avatars"][role])
    if url:
        container.image(url, caption=content)
    else:
        container.write(content)


def main():
    if "bot" not in state:
        state.bot = ChatBot(client=state.client, cfg=state.cfg)
    bot = state.bot
    if "history" not in state:
        state.history = []

    # Print history
    for msg in state.history:
        display_msg(**msg)

    # Chat input
    question = _bottom.chat_input("Write a question")

    if question:
        # Display question
        user_msg = {"role": "user", "content": question}
        state.history.append(user_msg)
        display_msg(**user_msg)

        # Display spinner while assistant is typing
        with st.spinner("Generating answer..."):
            response = bot.chat(state.history)

        # Display answer(s)
        for bot_msg in response:
            display_msg(**bot_msg)
            state.history.append(bot_msg)

    with st.sidebar:
        st.write("model:")
        bot.text["model"] = st.selectbox("select model", list(bot.text["models"]), label_visibility="collapsed")
        st.write("tools:")
        bot.text["active"] = st.checkbox("generate text", key="text", value=True)
        bot.image["active"] = st.checkbox("generate image", key="image", value=True)


if __name__ == "__main__":
    st.set_page_config(
        page_title="xrs",
        page_icon=":random:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    if "cfg" not in state:
        state.cfg = load_cfg()
    if "OPENAI_API_KEY" in os.environ:
        state.client = get_client(api_type=state.cfg["api_type"], api_key=os.environ["OPENAI_API_KEY"])
    if "client" in state and check_client(state.client) is True:
        main()
    else:
        st.switch_page("pages/login.py")
