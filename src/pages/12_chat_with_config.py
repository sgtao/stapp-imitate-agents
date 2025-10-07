# 12_chat_with_config.py
import time

import streamlit as st

from components.ApiClient import ApiClient
from components.ChatMessage import ChatMessage
from components.ClientController import ClientController
from components.ConfigFiles import ConfigFiles
from components.ResponseViewer import ResponseViewer
from components.SideMenus import SideMenus

# from functions.ApiRequestor import ApiRequestor
from functions.AppLogger import AppLogger

# APP_TITLE = "APIクライアントアプリ"
APP_TITLE = "Chat with Config"


def initial_session_state():
    # セッション状態の初期化
    if "config_file_path" not in st.session_state:
        st.session_state.config_file_path = ""


def post_messages_with_config(
    uri="http://localhost:3000/api/v0/messages",
    messages=[],
):
    # time.sleep(3)
    # response_messaeg = {"role": "assistant", "content": "Hello again!"}
    # if len(messages) > 0:
    #     return messages[-1]
    # else:
    #     return response_messaeg
    # APIリクエスト送信
    api_client = ApiClient()
    client_controller = ClientController()
    response_viewer = ResponseViewer()
    # clear action_results
    # st.session_state.action_results = []
    action_results = []

    for index in range(len(st.session_state.action_configs)):
        action_config = client_controller.get_action_config(index)
        action_config = client_controller.replace_action_config(
            action_config=action_config, action_results=action_results
        )

        # print(f"index({index}): {action_config}")

        response = api_client.post_msg_with_action_config(
            action_config=action_config,
            messages=messages,
        )

        # print(f"response: {response.json()}")

        api_response = response_viewer.extract_response_value(
            response=response,
            path=action_config.get("user_property_path", "."),
        )
        # st.session_state.action_results.append(api_response)
        action_results.append(api_response)
        st.session_state.action_results = action_results

    # print(f"api_response: {api_response}")
    return api_response


class ChatModal:
    @st.dialog("Chat Modal.", width="large")
    def modal(self, type, messages):
        st.write(f"Modal for {type}:")
        if type == "copy_response":
            if len(messages) > 0:
                self.copy_action(message=messages[-1])
            else:
                st.warning("Message not found!")
            self._modal_closer()
        else:
            st.write("No Definition.")

    def _modal_closer(self):
        if st.button(label="Close Modal"):
            st.info("モーダルを閉じます...")
            time.sleep(1)
            st.rerun()

    # 『Copy』モーダル：
    def copy_action(self, message):
        with st.expander("Last message", expanded=False):
            with st.container(horizontal_alignment="right"):
                st.write("右上にコピーアイコンがあります👇")
                st.code(message.get("content", ""))


def main():
    st.page_link("main.py", label="Back to Home", icon="🏠")

    st.title(f"💬 {APP_TITLE}")
    # インスタンス化
    chat_message = ChatMessage()
    client_controller = ClientController()
    config_files = ConfigFiles()

    # assets/privatesフォルダからyamlファイルを選択
    if not config_files:
        st.warning(
            "No YAML config files in assets and private. Please add some."
        )
        return

    selected_config_file = config_files.render_config_selector()

    # 選択されたコンフィグファイルを読み込む
    if st.button("Load Config."):
        config = config_files.load_config_from_yaml(selected_config_file)
        config_files.render_config_viewer(selected_config_file, config)
        client_controller.set_action_configs(config)
        st.session_state.config_file_path = selected_config_file
        chat_message.reset()

    # Chat with Config
    with st.container(height="stretch"):
        chat_message.display_chat_history()

        # ユーザー入力
        diff_config = st.session_state.config_file_path != selected_config_file
        if prompt := st.chat_input(
            placeholder="メッセージを入力してください:",
            disabled=diff_config,
        ):
            chat_message.add(role="user", content=prompt)

            # アシスタントの応答
            with st.chat_message("assistant"):
                with st.spinner("考え中..."):
                    assistant_response = post_messages_with_config(
                        messages=chat_message.get_messages(),
                    )

                    chat_message.add(
                        role="assistant",
                        content=assistant_response,
                    )
                    st.rerun()
    # page footer
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(
            label="Copy Response",
            help="Copy last response",
            icon="📋",
        ):
            chat_modal = ChatModal()
            chat_modal.modal(
                type="copy_response",
                messages=chat_message.get_messages(),
            )
    with col2:
        pass
    with col3:
        pass
    with col4:
        pass


if __name__ == "__main__":
    initial_session_state()
    app_logger = AppLogger(APP_TITLE)
    app_logger.app_start()
    side_menus = SideMenus()
    side_menus.render_api_client_menu()
    main()
