# config_api_client.py
# import json
import time

import streamlit as st

from components.ApiRequestInputs import ApiRequestInputs
from components.ResponseViewer import ResponseViewer
from components.SideMenus import SideMenus
from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Config Api Client"


def initial_session_state():
    # セッション状態の初期化
    if "config_list" not in st.session_state:
        st.session_state.config_list = []
    if "config_file" not in st.session_state:
        st.session_state.config_file = ""


def _update_api_origin():
    """
    _update_api_origin: Callback function of "API Server Origin" input
    """
    st.session_state.api_origin = st.session_state._api_origin_input
    st.session_state.config_list = []
    st.warning("Clear config list")
    time.sleep(3)
    st.rerun()


def post_api_server(uri, config_file="", messages=[]):
    """
    APIサーバーへconfig_fileのPOSTリクエストを発行します
    """
    api_requestor = ApiRequestor()
    method = "POST"
    header_dict = {"Content-Type": "application/json"}
    # リクエストボディ入力（POST, PUTの場合のみ表示）
    # request_body = """
    #     {
    #         "config_file": "assets/001_get_simple_api_test.yaml"
    #     }
    # """
    if config_file == "":
        raise "Please set Config file"

    request_body = {
        "config_file": config_file,
        "num_user_inputs": st.session_state.num_inputs,
        "user_inputs": {},
        "messages": messages,
    }
    for i in range(st.session_state.num_inputs):
        user_key = f"user_input_{i}"
        if user_key in st.session_state:
            value = st.session_state[user_key]
            request_body["user_inputs"][user_key] = value
        else:
            st.warning(f"Session state key '{user_key}' not found.")
    body_json = request_body

    try:
        response = api_requestor.send_request(
            uri,
            method,
            header_dict,
            body_json,
        )
        response.raise_for_status()  # HTTPエラーをチェック
        st.success(
            """
            Successfully connected to API Server.
            """
        )
        return response
    except Exception as e:
        # st.error(f"Failed to `POST` to API Server: {e}")
        raise e


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🧪 {APP_TITLE}")
    # インスタンス化
    request_inputs = ApiRequestInputs(api_origin="http://localhost:3000")
    response_viewer = ResponseViewer()
    api_requestor = ApiRequestor()

    # Setup to access API-Server
    # request_inputs.render_api_origin_input()
    st.text_input(
        label="API Server Origin",
        key="_api_origin_input",
        value=st.session_state.api_origin,
        on_change=_update_api_origin,
    )

    if len(st.session_state.config_list) == 0:
        if st.button("Check Ready to access API-Server", type="primary"):
            try:
                uri = request_inputs.make_uri(path="/api/v0/hello")
                response = api_requestor.send_request(url=uri, method="GET")
                # response_viewer.render_viewer(response)
                st.success("Success: Access to API Server")
            except Exception as e:
                st.error(f"Cannot Access to API Searver: {e}")
                st.info("Please Run API Server!!")

            try:
                # Get a list of Config files
                uri = request_inputs.make_uri(path="/api/v0/configs")
                response = api_requestor.send_request(url=uri, method="GET")
                # st.session_state.config_list = (
                _config_list = response_viewer.extract_response_value(
                    response=response, path="results"
                )
                st.session_state.config_list = _config_list
                # reloase This Screen
                time.sleep(3)
                st.rerun()

            except Exception as e:
                st.warning(f"Not Found Config list: {e}")

    else:
        config_file = st.selectbox(
            "Select Config file",
            st.session_state.config_list,
        )

        if config_file != "":
            # Get a list of Config files
            uri = request_inputs.make_uri(path="/api/v0/config-title")
            method = "POST"
            header_dict = {"Content-Type": "application/json"}
            # リクエストボディ入力（POST, PUTの場合のみ表示）
            # request_body = """
            #     {
            #         "config_file": "assets/001_get_simple_api_test.yaml"
            #     }
            # """
            request_body = {"config_file": config_file}
            try:
                response = api_requestor.send_request(
                    uri,
                    method,
                    header_dict,
                    request_body,
                )
                response.raise_for_status()  # HTTPエラーをチェック

                title = response_viewer.extract_response_value(
                    response=response, path="results.title"
                )
                note = response_viewer.extract_response_value(
                    response=response, path="results.note"
                )
                st.info(
                    f"""
                        - Title: {title}
                        - Note: {note}
                        """
                )
            except Exception as e:
                st.warning(f"Cannot find Title or Note in config_file: {e}")

        if st.button("Load Config", type="primary"):
            st.session_state.config_file = config_file
        st.write(f"used config file: {st.session_state.config_file}")

        # リクエスト送信ボタン
        if st.session_state.config_file != "":
            api_response = None
            messages = []
            user_message = st.text_input(
                label="User Message",
                placeholder="Please input message , when request message",
            )
            col1, col2, col3 = st.columns(3)
            try:
                with col1:
                    if st.button(
                        "Request service", type="secondary", icon="🚀"
                    ):
                        # APIリクエスト送信
                        uri = request_inputs.make_uri(path="/api/v0/service")
                        api_response = post_api_server(
                            uri, st.session_state.config_file
                        )
                with col2:
                    if st.button("Request message", type="secondary", icon="🎟️"):
                        # APIリクエスト送信
                        if user_message != "":
                            messages.append(
                                {"role": "user", "content": user_message}
                            )
                        uri = request_inputs.make_uri(path="/api/v0/messages")
                        api_response = post_api_server(
                            uri,
                            st.session_state.config_file,
                            messages,
                        )
                with col3:
                    if st.button("Rerun (`R`)", icon="🏃"):
                        st.rerun()

            except Exception as e:
                # ユーザー向けメッセージ
                st.error(
                    "リクエスト中にエラー発生。詳細は以下をご確認ください。"
                )
                # 詳細な例外情報を表示
                st.exception(e)

            # レスポンス表示
            if api_response:
                st.subheader("API レスポンス")
                response_viewer.render_viewer(api_response)


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
