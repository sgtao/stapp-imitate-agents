# config_api_client.py
# import json
import streamlit as st

from components.ApiClient import ApiClient
from components.ApiRequestInputs import ApiRequestInputs
from components.ConfigApiSelector import ConfigApiSelector
from components.ResponseViewer import ResponseViewer
from components.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Config Api Client"


def initial_session_state():
    # セッション状態の初期化
    # if "api_origin" not in st.session_state:
    #     st.session_state.api_origin = "http://localhost:3000"
    # if "config_list" not in st.session_state:
    #     st.session_state.config_list = []
    if "config_file" not in st.session_state:
        st.session_state.config_file = ""
    if "api_response" not in st.session_state:
        st.session_state.api_response = None
    # if "action_resps" not in st.session_state:
    #     st.session_state.action_resps = []
    # if "num_resps" not in st.session_state:
    #     st.session_state.num_resps = len(st.session_state.action_resps)


# def post_api_server(uri, config_file="", messages=[]):
#     """
#     APIサーバーへconfig_fileのPOSTリクエストを発行します
#     - 内部は、ApiRequestor.send_api_request を呼び出すラッパー
#     """
#     num_inputs = st.session_state.get("num_inputs", 0)
#     user_inputs = {}

#     for i in range(num_inputs):
#         user_key = f"user_input_{i}"
#         if user_key in st.session_state:
#             user_inputs[user_key] = st.session_state[user_key]
#         else:
#             st.warning(f"Session state key '{user_key}' not found.")

#     try:
#         api_requestor = ApiRequestor()
#         response = api_requestor.send_api_request(
#             uri=uri,
#             method="POST",
#             config_file=config_file,
#             num_inputs=num_inputs,
#             user_inputs=user_inputs,
#             messages=messages,
#         )
#         # if success, set parameters to session_state for save YAML
#         st.session_state.uri = uri
#         st.session_state.metohd = "POST"
#         st.success("Successfully connected to API Server.")
#         return response
#     except Exception as e:
#         raise e


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"🧪 {APP_TITLE}")
    # インスタンス化
    request_inputs = ApiRequestInputs(api_origin="http://localhost:3000")
    response_viewer = ResponseViewer()
    # api_requestor = ApiRequestor()
    config_api_selector = ConfigApiSelector()
    api_client = ApiClient()

    try:
        # Setup to access API-Server
        config_file = config_api_selector.render_selector()

        if config_file == "":
            st.warning("Please check to access API Server!")
            return
        else:
            # Render selected config tilte and note
            config_api_selector.render_config_title(config_file)

            if st.button("Set Config", type="primary"):
                st.session_state.config_file = config_file

        # リクエスト送信ボタン
        if st.session_state.config_file != "":
            st.write(f"used config file: {st.session_state.config_file}")
            api_response = st.session_state.api_response
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
                        api_response = api_client.post_api_server(
                            uri, st.session_state.config_file
                        )
                with col2:
                    if st.button(
                        "Request message", type="secondary", icon="🎟️"
                    ):
                        # APIリクエスト送信
                        if user_message != "":
                            messages.append(
                                {"role": "user", "content": user_message}
                            )
                        uri = request_inputs.make_uri(path="/api/v0/messages")
                        api_response = api_client.post_api_server(
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
                st.session_state.action_resps.append(api_response.json())
                st.session_state.num_resps = len(st.session_state.action_resps)
                st.session_state.api_response = api_response

    except Exception as e:
        st.error(f"Error occured! {e}")


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
