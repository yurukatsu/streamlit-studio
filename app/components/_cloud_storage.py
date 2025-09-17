import streamlit as st

from ._base import BaseComponent


class CloudStoragePage(BaseComponent):
    name = "CloudStoragePage"

    @classmethod
    def render(cls):
        st.title("Cloud Storage")
        st.write("This is the page to manage cloud storage")
