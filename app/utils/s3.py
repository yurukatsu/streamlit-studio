import boto3
import streamlit as st
from settings import AWSSettings


@st.cache_resource
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWSSettings.access_key_id,
        aws_secret_access_key=AWSSettings.secret_access_key,
        region_name=AWSSettings.region_name,
    )
