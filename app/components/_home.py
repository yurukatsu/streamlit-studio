import streamlit as st

from ._base import BaseComponent


class HomePage(BaseComponent):
    name = "home page"

    @classmethod
    def body(cls):
        st.title("Home Page")
        st.write("Welcome to the Home Page!")

    @classmethod
    def render(cls):
        cls.body()
