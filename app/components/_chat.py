import streamlit as st

from ._base import BaseComponent
from ._navbar import NavigationBar


class ChatBotPage(BaseComponent):
    name = "ChatBotPage"

    def render(self):
        NavigationBar.render(self.name)
        st.title("Chat Bot")
        st.write("This is the chat bot page.")
