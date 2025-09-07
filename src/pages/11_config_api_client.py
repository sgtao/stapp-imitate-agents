# config_api_client.py
import json
import time

import streamlit as st

from components.ApiRequestHeader import ApiRequestHeader
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


def _update_api_origin():
    """
    _update_api_origin: Callback function of "API Server Origin" input
    """
    st.session_state.api_origin = st.session_state._api_origin_input
    st.session_state.config_list = []
    st.warning("Clear config list")
    time.sleep(3)
    st.rerun()


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🧪 {APP_TITLE}")
    # インスタンス化
    request_header = ApiRequestHeader()
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
        if st.button("Check Ready to access API-Server"):
            try:
                uri = request_inputs.make_uri(path="/api/v0/hello")
                response = api_requestor.send_request(url=uri, method="GET")
                response_viewer.render_viewer(response)
                st.success("Success: Access to API Server")

                # Get a list of Config files
                uri = request_inputs.make_uri(path="/api/v0/configs")
                response = api_requestor.send_request(url=uri, method="GET")
                st.session_state.config_list = (
                    response_viewer.extract_response_value(response)
                )

                # reloase This Screen
                time.sleep(3)
                st.rerun()

            except Exception as e:
                st.error(f"Error Access to API Searver: {e}")
                st.info("Please Run API Server!!")
    else:
        # ユーザー入力：APIリクエストの指定項目
        method = request_inputs.render_method_selector()
        use_dynamic_inputs = request_inputs.render_use_dynamic_checkbox()
        uri = request_inputs.render_uri_input()

        # ヘッダー入力セクション
        header_dict = {}
        with st.expander("リクエストヘッダー設定"):
            request_header.render_editor()
            # ヘッダー情報を辞書形式で取得
            header_dict = request_header.get_header_dict()

        # リクエストボディ入力（POST, PUTの場合のみ表示）
        request_body = request_inputs.render_body_input()

        # リクエスト送信ボタン
        if st.button("リクエストを送信"):
            try:
                # 確定情報のセット
                st.session_state.uri = uri
                st.session_state.method = method
                st.session_state.req_body = request_body
                st.session_state.use_dynamic_inputs = use_dynamic_inputs

                # URIとリクエストボディのJSON形式検証
                sent_uri = uri
                sent_body = request_body
                if st.session_state.use_dynamic_inputs:
                    sent_uri = api_requestor.replace_uri(st.session_state, uri)
                    if request_body:
                        sent_body = api_requestor.replace_body(
                            st.session_state, request_body
                        )

                # st.text(sent_body)
                body_json = json.loads(sent_body) if request_body else None

                # APIリクエスト送信
                response = api_requestor.send_request(
                    sent_uri, method, header_dict, body_json
                )

                # レスポンス表示
                if response:
                    st.subheader("レスポンス")
                    response_viewer.render_viewer(response)
            except Exception as e:
                # ユーザー向けメッセージ
                st.error(
                    "リクエスト中にエラーが発生しました。詳細は以下をご確認ください。"
                )
                # 詳細な例外情報を表示
                st.exception(e)


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
