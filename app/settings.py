from pathlib import Path
from typing import Dict
from uuid import uuid4

import streamlit as st


class SessionState:
    def __init__(self, session_states: Dict[str, str]):
        self.session_states = session_states

    @staticmethod
    def set(key, value):
        if key not in st.session_state:
            st.session_state[key] = value

    def initialize(self):
        for key, value in self.session_states.items():
            self.set(key, value)
