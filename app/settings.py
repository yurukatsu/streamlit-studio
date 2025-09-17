from typing import Any, Dict

import streamlit as st


class SessionStateManager:
    @staticmethod
    def set(key: str, value: Any, *, overwrite: bool = True):
        if key not in st.session_state:
            st.session_state[key] = value
        elif overwrite:
            st.session_state[key] = value

    @classmethod
    def post(cls, session_states: Dict[str, Any], *, overwrite: bool = True):
        for key, value in session_states.items():
            cls.set(key, value, overwrite=overwrite)

    @staticmethod
    def get(key: str) -> Any:
        return st.session_state.get(key, None)

    @staticmethod
    def delete(key: str):
        if key in st.session_state:
            del st.session_state[key]

    @classmethod
    def clear(cls):
        for key in st.session_state.keys():
            cls.delete(key)


class Settings:
    username = st.secrets["USERNAME"]
    password = st.secrets["PASSWORD"]
    debug = st.secrets.get("DEBUG", False)

    default_session_states = {
        "auth": {
            "authenticated": False,
        },
        "s3_browser": {
            "s3_current_path": "/",
            "s3_current_bucket": None,
            "s3_current_object_prefix": "",
        },
    }

    @classmethod
    def initialize(cls):
        for _, session_states in cls.default_session_states.items():
            SessionStateManager.post(session_states, overwrite=False)


class AzureSettings:
    endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"]
    api_key = st.secrets["AZURE_OPENAI_API_KEY"]
    api_version = st.secrets.get("OPENAI_API_VERSION", "2024-12-01-preview")


class AWSSettings:
    access_key_id = st.secrets["AWS_ACCESS_KEY_ID"]
    secret_access_key = st.secrets["AWS_SECRET_ACCESS_KEY"]
    region_name = st.secrets.get("AWS_REGION_NAME", "ap-northeast-1")
