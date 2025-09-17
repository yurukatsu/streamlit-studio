import streamlit as st

from ._base import BaseComponent


class NavigationBar(BaseComponent):
    name = "NavigationBar"
    sidebar_logo_path = "https://github.com/yurukatsu/streamlit-studio/blob/master/app/assets/images/favicon.png?raw=true"

    @classmethod
    def render(cls):
        with st.sidebar:
            st.image(cls.sidebar_logo_path, use_container_width=True)

            st.page_link(
                "main.py",
                label="Home",
                icon=":material/home:",
                help="Go to Home Page",
                width="stretch",
            )

            st.page_link(
                "pages/chatbot.py",
                label="Chatbot",
                icon=":material/chat:",
                help="Go to Chatbot Page",
                width="stretch",
            )
