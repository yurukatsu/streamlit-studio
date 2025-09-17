import streamlit as st

from ._base import BaseComponent


class ChatBotPage(BaseComponent):
    name = "ChatBotPage"

    @classmethod
    def render(cls):
        st.title("Chat Bot")
        st.write("This is the chat bot page.")
