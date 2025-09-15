# ApiClient.py
# import json
import streamlit as st

from functions.ApiRequestor import ApiRequestor


class ApiClient:
    def __init__(self):
        # セッション状態の初期化
        if "action_resps" not in st.session_state:
            st.session_state.action_resps = []
        if "num_resps" not in st.session_state:
            st.session_state.num_resps = len(st.session_state.action_resps)

    def post_api_server(self, uri, config_file="", messages=[]):
        """
        APIサーバーへconfig_fileのPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        num_inputs = st.session_state.get("num_inputs", 0)
        user_inputs = {}

        for i in range(num_inputs):
            user_key = f"user_input_{i}"
            if user_key in st.session_state:
                user_inputs[user_key] = st.session_state[user_key]
            else:
                st.warning(f"Session state key '{user_key}' not found.")

        try:
            api_requestor = ApiRequestor()
            response = api_requestor.send_api_request(
                uri=uri,
                method="POST",
                config_file=config_file,
                num_inputs=num_inputs,
                user_inputs=user_inputs,
                messages=messages,
            )
            # if success, set parameters to session_state for save YAML
            st.session_state.uri = uri
            st.session_state.metohd = "POST"
            st.success("Successfully connected to API Server.")
            return response
        except Exception as e:
            raise e
