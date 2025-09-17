import time

import streamlit as st
from settings import SessionStateManager, Settings

from ._base import BaseComponent


class LoginForm(BaseComponent):
    @classmethod
    def is_authenticated(cls, input_username: str, input_password: str) -> bool:
        return (
            input_username == Settings.username and input_password == Settings.password
        )

    @classmethod
    def sign_in(cls):
        st.title("Sign In")

        input_username = st.text_input("Username")
        input_password = st.text_input("Password", type="password")

        if st.button("Sign In"):
            if cls.is_authenticated(input_username, input_password):
                SessionStateManager.set("authenticated", True)
                st.toast("Successfully signed in!")
                time.sleep(1.0)
                st.rerun()
            else:
                st.error("Invalid username or password")

    @classmethod
    def render(cls):
        cls.sign_in()
