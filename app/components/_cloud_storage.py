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
            "s3_current_path", f"/{st.session_state.s3_current_bucket}/{prefix}"
        )

    @staticmethod
    def back():
        """一つ上の階層へ戻る"""
        prefix = st.session_state.s3_current_object_prefix
        if prefix == "":
            # バケット一覧に戻る
            st.session_state.s3_current_bucket = None
            st.session_state.s3_current_path = "/"
            st.rerun()

        # 末尾の "/" を除去して一階層戻る
        parent = "/".join(prefix.rstrip("/").split("/")[:-1])
        parent = parent + "/" if parent else ""

        st.session_state.s3_current_object_prefix = parent
        st.session_state.s3_current_path = (
            f"/{st.session_state.s3_current_bucket}/{parent}"
        )
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
        cols = st.columns(2)
        for bucket in bucket_names:
            with cols[0]:
                st.write(bucket)
            with cols[1]:
                if st.button(
                    "",
                    icon=":material/arrow_forward:",
                    key=f"bucket-{bucket}",
                    use_container_width=True,
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

    staticmethod
    def upload_file(bucket: str, prefix: str):
        """現在のフォルダにファイルをアップロード"""
        s3 = get_s3_client()
        uploaded_file = st.file_uploader("ファイルをアップロード", type=None)

        if uploaded_file is not None:
            key = prefix + uploaded_file.name
            # S3 にアップロード
            s3.upload_fileobj(uploaded_file, bucket, key)
            uploaded_file = None
            st.success(f"✅ アップロード成功: {key}")

    @staticmethod
    def show_objects(bucket: str, prefix: str):
        s3 = get_s3_client()

        S3Browser.upload_file(bucket, prefix)

        st.divider()

        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter="/")

        # フォルダ一覧
        if "CommonPrefixes" in response:
            st.write("📂 フォルダ")
            for p in response["CommonPrefixes"]:
                folder = p["Prefix"]
                folder_name = folder[len(prefix) :].rstrip("/")
                if st.button(f"➡️ {folder_name}", key=f"folder-{folder}"):
                    S3State.set_prefix(folder)
                    st.rerun()

        # ファイル一覧
        if "Contents" in response:
            st.write("📄 ファイル")
            for obj in response["Contents"]:
                key = obj["Key"]
                if key.endswith("/"):  # フォルダダミーは除外
                    continue
                filename = key[len(prefix) :]
                size_kb = obj["Size"] / 1024
                col1, col2, col3 = st.columns([5, 2, 1])
                col1.write(filename)
                col2.write(f"{size_kb:.1f} KB")

                # if col3.button("⬇️ DL", key=f"dl-{key}"):
                #     buffer = io.BytesIO()
                #     s3.download_fileobj(bucket, key, buffer)
                #     buffer.seek(0)
                #     st.download_button(
                #         label=f"{filename} を保存",
                #         data=buffer,
                #         file_name=filename,
                #         mime="application/octet-stream",
                #         key=f"download-{key}"
                #     )
                url = S3Browser.generate_presigned_url(bucket, key)
                col3.write(f"[Download]({url})")

    @classmethod
    def header(cls):
        disable = st.session_state.s3_current_path == "/"
        if st.button(
            st.session_state.s3_current_path,
            icon=":material/arrow_back:",
            disabled=disable,
            use_container_width=True,
        ):
            S3State.back()

    @classmethod
    def body(cls):
        if st.session_state.s3_current_path == "/":
            buckets = cls.list_buckets()
            cls.show_bucket_list(buckets)
        else:
            cls.show_objects(
                st.session_state.s3_current_bucket,
                st.session_state.s3_current_object_prefix,
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
