import io

import streamlit as st
from botocore.exceptions import ClientError
from settings import SessionStateManager
from utils.s3 import get_s3_client

from ._base import BaseComponent


class S3State:
    """S3ブラウザーの状態管理"""

    @staticmethod
    def init():
        SessionStateManager.post(
            {
                "s3_current_bucket": None,
                "s3_current_path": "/",  # UI表示用
                "s3_current_object_prefix": "",  # S3 list_objects_v2 用
            },
            overwrite=False,
        )

    @staticmethod
    def set_bucket(bucket: str):
        SessionStateManager.set("s3_current_bucket", bucket)
        SessionStateManager.set("s3_current_path", f"/{bucket}/")
        SessionStateManager.set("s3_current_object_prefix", "")

    @staticmethod
    def set_prefix(prefix: str):
        """フォルダをクリックしたとき"""
        SessionStateManager.set("s3_current_object_prefix", prefix)
        SessionStateManager.set(
            "s3_current_path", f"/{SessionStateManager.get('s3_current_bucket')}/{prefix}"
        )

    @staticmethod
    def back():
        """一つ上の階層へ戻る"""
        prefix = SessionStateManager.get("s3_current_object_prefix")
        if prefix == "":
            SessionStateManager.set("s3_current_bucket", None)
            SessionStateManager.set("s3_current_path", "/")
            st.rerun()

        parent = "/".join(prefix.rstrip("/").split("/")[:-1])
        parent = parent + "/" if parent else ""

        SessionStateManager.set("s3_current_object_prefix", parent)
        SessionStateManager.set("s3_current_path", f"/{SessionStateManager.get('s3_current_bucket')}/{parent}")
        st.rerun()


class S3Browser:
    """S3のUIブラウザー"""

    @staticmethod
    def list_buckets() -> list[str]:
        s3 = get_s3_client()
        response = s3.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]

    @staticmethod
    def list_objects(bucket: str, prefix: str):
        s3 = get_s3_client()
        try:
            return s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")
        except ClientError as e:
            st.error(f"オブジェクト一覧の取得に失敗しました: {e}")
            return {}

    @staticmethod
    def show_bucket_list(bucket_names: list[str]):
        for bucket in bucket_names:
            if st.button(
                bucket,
                icon=":material/cloud:",
                key=f"bucket-{bucket}",
            ):
                S3State.set_bucket(bucket)
                st.rerun()

    @staticmethod
    def generate_presigned_url(bucket: str, key: str, expires_in: int = 300) -> str:
        """指定オブジェクトの署名付きURLを生成（デフォルト5分有効）"""
        s3 = get_s3_client()
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in
        )

    @staticmethod
    @st.dialog("Upload your file")
    def upload_file(bucket: str, prefix: str):
        """現在のフォルダにファイルをアップロード"""
        s3 = get_s3_client()
        uploaded_file = st.file_uploader("ファイルをアップロード", type=None)

        if uploaded_file is not None:
            key = prefix + uploaded_file.name
            s3.upload_fileobj(uploaded_file, bucket, key)
            uploaded_file = None
            st.success(f"Success file upload: {key}", icon=":material/check_circle:")
            st.rerun()

    @staticmethod
    @st.dialog("Create new folder")
    def create_folder(bucket: str, prefix: str):
        """現在のフォルダにサブフォルダを作成"""
        s3 = get_s3_client()
        with st.form("create_folder_form"):
            new_folder = st.text_input("New folder name", "")
            submitted = st.form_submit_button("Create", icon=":material/create_new_folder:")
            if submitted and new_folder:
                folder_key = prefix + new_folder.strip("/") + "/"
                s3.put_object(Bucket=bucket, Key=folder_key)
                st.success(f"Folder created: {folder_key}", icon=":material/check_circle:")
                st.rerun()

    @classmethod
    def show_objects(cls, bucket: str, prefix: str):
        s3 = get_s3_client()
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")

        colA, colB = st.columns(2)
        if colA.button("", key="upload_btn", icon=":material/file_upload:", width="stretch"):
            cls.upload_file(bucket, prefix)
        if colB.button("", key="create_btn", icon=":material/create_new_folder:", width="stretch"):
            cls.create_folder(bucket, prefix)

        # フォルダ一覧
        if "CommonPrefixes" in response:
            st.write("Folders")
            for p in response["CommonPrefixes"]:
                folder = p["Prefix"]
                folder_name = folder[len(prefix) :].rstrip("/")
                if st.button(folder_name, key=f"folder-{folder}", icon=":material/folder:", width="content"):
                    S3State.set_prefix(folder)
                    st.rerun()

        # ファイル一覧
        if "Contents" in response:
            st.write("Files")
            for obj in response["Contents"]:
                key = obj["Key"]
                if key.endswith("/"):  # フォルダダミーは除外
                    continue
                filename = key[len(prefix) :]
                size_kb = obj["Size"] / 1024
                col1, col2, col3 = st.columns([5, 2, 1])
                col1.write(filename)
                col2.write(f"{size_kb:.1f} KB")

                url = cls.generate_presigned_url(bucket, key)
                col3.write(f"[Download]({url})")

    @classmethod
    def header(cls):
        disable = SessionStateManager.get("s3_current_path") == "/"
        if st.button(
            SessionStateManager.get("s3_current_path"),
            icon=":material/arrow_back:",
            disabled=disable,
        ):
            S3State.back()

    @classmethod
    def body(cls):
        if SessionStateManager.get("s3_current_path") == "/":
            buckets = cls.list_buckets()
            cls.show_bucket_list(buckets)
        else:
            cls.show_objects(
                SessionStateManager.get("s3_current_bucket"),
                SessionStateManager.get("s3_current_object_prefix"),
            )

    @classmethod
    def render(cls):
        cls.header()
        cls.body()


class CloudStoragePage(BaseComponent):
    name = "CloudStoragePage"

    @classmethod
    def render(cls):
        S3State.init()
        S3Browser.render()
