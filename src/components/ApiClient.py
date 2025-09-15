# ApiClient.py
# import json
import streamlit as st

from functions.ApiRequestor import ApiRequestor


class ApiClient:
    def __init__(self):
        # セッション状態の初期化
        if "api_response" not in st.session_state:
            # st.session_state.api_response = None
            self.clr_api_response()
        if "action_resps" not in st.session_state:
            st.session_state.action_resps = []
        if "num_resps" not in st.session_state:
            st.session_state.num_resps = len(st.session_state.action_resps)

    def post_api_server(self, uri, config_file="", messages=[]):
        """
        APIサーバーへconfig_fileのPOSTリクエストを発行します
        - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
        """
        st.session_state.api_response = None
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
            self.save_api_response(response)
            return response
        except Exception as e:
            raise e

    def get_api_response(self):
        return st.session_state.api_response

    def save_api_response(self, response):
        prev_num_resps = len(st.session_state.action_resps)
        st.session_state.api_response = response
        st.session_state.action_resps.append(response.json())
        st.session_state.num_resps = prev_num_resps + 1

    def clr_api_response(self):
        st.session_state.api_response = None

